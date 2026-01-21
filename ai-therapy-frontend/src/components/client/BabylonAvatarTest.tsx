'use client';

/**
 * Professional Babylon.js 3D Avatar
 * High-quality rendering with better performance than Three.js
 */

import { useEffect, useRef, useState } from 'react';
import * as BABYLON from '@babylonjs/core';
import '@babylonjs/loaders';

interface BabylonAvatarProps {
  isActive: boolean;
  isSpeaking: boolean;
  isListening: boolean;
  volumeLevel: number;
  modelUrl?: string;
}

export function BabylonAvatar({
  isActive,
  isSpeaking,
  isListening,
  volumeLevel,
  modelUrl
}: BabylonAvatarProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [loadError, setLoadError] = useState(false);

  // Fixed arm position values (perfect pose)
  const armValuesRef = useRef({ shoulderDown: -0.05, upperArmDown: -0.15, foreArmIn: 0.15 });

  // Track current animation state via refs (so render loop can access latest values)
  const animPropsRef = useRef({ isSpeaking: false, isListening: false, volumeLevel: 0 });
  
  // Update refs when props change
  useEffect(() => {
    animPropsRef.current = { isSpeaking, isListening, volumeLevel };
  }, [isSpeaking, isListening, volumeLevel]);

  const sceneRef = useRef<{
    engine: BABYLON.Engine;
    scene: BABYLON.Scene;
    avatar: BABYLON.Mesh | null;
    head: BABYLON.Mesh | null;
    allMeshes: BABYLON.AbstractMesh[];
    skeleton: BABYLON.Skeleton | null;
    skinnedMesh: BABYLON.AbstractMesh | null;
    initialBoneRotations: Map<string, BABYLON.Vector3> | null;
    // Morph targets for facial animation
    faceMesh: BABYLON.Mesh | null;
    mouthOpenTarget: BABYLON.MorphTarget | null;
    leftEyeCloseTarget: BABYLON.MorphTarget | null;
    rightEyeCloseTarget: BABYLON.MorphTarget | null;
  } | null>(null);

  const animationStateRef = useRef({
    blinkTimer: 0,
    talkTimer: 0,
    gestureTimer: 0,
    lastGesture: 0,
    lastSpeaking: false,
    lastListening: false,
    animationAngle: 0,
    // Store base rotations for animation
    headBaseRotation: null as BABYLON.Vector3 | null,
    neckBaseRotation: null as BABYLON.Vector3 | null,
    leftArmBaseRotation: null as BABYLON.Vector3 | null,
    rightArmBaseRotation: null as BABYLON.Vector3 | null,
    leftForeArmBaseRotation: null as BABYLON.Vector3 | null,
    rightForeArmBaseRotation: null as BABYLON.Vector3 | null,
    leftHandBaseRotation: null as BABYLON.Vector3 | null,
    rightHandBaseRotation: null as BABYLON.Vector3 | null,
    initialized: false
  });

  useEffect(() => {
    if (!canvasRef.current) return;

    const engine = new BABYLON.Engine(canvasRef.current, true, {
      preserveDrawingBuffer: true,
      stencil: true,
      disableWebGL2Support: false
    });

    const scene = new BABYLON.Scene(engine);
    scene.clearColor = new BABYLON.Color4(0.97, 0.97, 0.98, 1);

    const camera = new BABYLON.ArcRotateCamera(
      'camera',
      -Math.PI / 2,
      Math.PI / 2.2,
      2.5,
      new BABYLON.Vector3(0, 1.4, 0),
      scene
    );
    camera.attachControl(canvasRef.current, true);
    camera.lowerRadiusLimit = 1.5;
    camera.upperRadiusLimit = 5;
    camera.lowerBetaLimit = Math.PI / 4;
    camera.upperBetaLimit = Math.PI / 2;

    const hemisphericLight = new BABYLON.HemisphericLight(
      'light',
      new BABYLON.Vector3(0, 1, 0),
      scene
    );
    hemisphericLight.intensity = 0.7;

    const directionalLight = new BABYLON.DirectionalLight(
      'dirLight',
      new BABYLON.Vector3(-1, -2, -1),
      scene
    );
    directionalLight.position = new BABYLON.Vector3(2, 3, 2);
    directionalLight.intensity = 0.5;

    sceneRef.current = {
      engine,
      scene,
      avatar: null,
      head: null,
      allMeshes: [],
      skeleton: null,
      skinnedMesh: null,
      initialBoneRotations: null,
      faceMesh: null,
      mouthOpenTarget: null,
      leftEyeCloseTarget: null,
      rightEyeCloseTarget: null
    };

    if (modelUrl) {
      loadExternalModel(scene, modelUrl);
    } else {
      createSimpleAvatar(scene);
    }

    engine.runRenderLoop(() => {
      if (sceneRef.current?.avatar) {
        animateAvatar(
          sceneRef.current.avatar,
          sceneRef.current.head,
          sceneRef.current.allMeshes,
          animPropsRef.current.isSpeaking,
          animPropsRef.current.isListening,
          animPropsRef.current.volumeLevel
        );
      }
      scene.render();
    });

    const handleResize = () => engine.resize();
    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      engine.dispose();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [modelUrl]);

  async function loadExternalModel(scene: BABYLON.Scene, url: string) {
    try {
      const result = await BABYLON.SceneLoader.ImportMeshAsync('', '', url, scene);

      const meshes = result.meshes;
      const rootMesh = meshes[0];

      // Scale and position
      const boundingInfo = rootMesh.getHierarchyBoundingVectors();
      const size = boundingInfo.max.subtract(boundingInfo.min);
      const maxDim = Math.max(size.x, size.y, size.z);
      const scale = 2 / maxDim;
      rootMesh.scaling = new BABYLON.Vector3(scale, scale, scale);
      rootMesh.position.y = 0;

      // Find head
      let head: BABYLON.Mesh | null = null;
      meshes.forEach((mesh) => {
        const name = mesh.name.toLowerCase();
        if (name.includes('head') || name.includes('neck')) {
          head = mesh as BABYLON.Mesh;
        }
      });
      if (!head && meshes.length > 1) head = meshes[1] as BABYLON.Mesh;

      // Arm pose fix (lower from A-frame) using bone.rotate (reliable for glTF)

      if (result.skeletons && result.skeletons.length > 0) {
        const skeleton = result.skeletons[0];
        console.log('🦴 Skeleton bones:', skeleton.bones.map(b => b.name));

        // CRITICAL: Force skeleton to update by using needInitialSkinMatrix
        skeleton.needInitialSkinMatrix = true;
        
        // Find all skinned meshes and force them to use the skeleton properly
        result.meshes.forEach((mesh) => {
          if ((mesh as any).skeleton) {
            (mesh as any).skeleton = skeleton;
          }
        });

        const getBone = (name: string) => skeleton.bones.find((b) => b.name === name);

        const lShoulder = getBone('LeftShoulder');
        const lArm = getBone('LeftArm');
        const lFore = getBone('LeftForeArm');

        const rShoulder = getBone('RightShoulder');
        const rArm = getBone('RightArm');
        const rFore = getBone('RightForeArm');

        // Pick a reference mesh that is actually skinned
        const skinnedMesh =
          (result.meshes.find((m) => (m as any).skeleton) as BABYLON.AbstractMesh) ||
          (rootMesh as BABYLON.AbstractMesh);

        // Tunables (radians) - use values from ref for dynamic updates
        const shoulderDownValue = armValuesRef.current.shoulderDown;
        const upperArmDownValue = armValuesRef.current.upperArmDown;
        const foreArmInValue = armValuesRef.current.foreArmIn;

        // Use the bone's linked transform node for rotation
        let adjusted = 0;

        const rotateBone = (bone: BABYLON.Bone | undefined, axis: BABYLON.Vector3, angle: number, name: string) => {
          if (!bone) return;
          
          const transformNode = bone.getTransformNode();
          if (transformNode) {
            transformNode.rotate(axis, angle, BABYLON.Space.LOCAL);
          } else {
            bone.rotate(axis, angle, BABYLON.Space.LOCAL, skinnedMesh);
          }
          
          adjusted++;
        };

        rotateBone(lShoulder, BABYLON.Axis.X, shoulderDownValue, 'LeftShoulder');
        rotateBone(rShoulder, BABYLON.Axis.X, shoulderDownValue, 'RightShoulder');
        rotateBone(lArm, BABYLON.Axis.X, upperArmDownValue, 'LeftArm');
        rotateBone(rArm, BABYLON.Axis.X, upperArmDownValue, 'RightArm');
        rotateBone(lFore, BABYLON.Axis.Y, foreArmInValue, 'LeftForeArm');
        rotateBone(rFore, BABYLON.Axis.Y, -foreArmInValue, 'RightForeArm');

        // Force skeleton update
        skeleton.computeAbsoluteTransforms(true);
        
        // Force all meshes to update their world matrices
        result.meshes.forEach((m) => {
          m.computeWorldMatrix(true);
          if ((m as any).skeleton) {
            const skel = (m as any).skeleton as BABYLON.Skeleton;
            skel.computeAbsoluteTransforms(true);
          }
        });

        // Find face mesh with morph targets for facial animation
        let faceMesh: BABYLON.Mesh | null = null;
        let mouthOpenTarget: BABYLON.MorphTarget | null = null;
        let leftEyeCloseTarget: BABYLON.MorphTarget | null = null;
        let rightEyeCloseTarget: BABYLON.MorphTarget | null = null;

        // First pass: Find the mesh with the MOST morph targets (usually the head)
        let maxTargets = 0;
        let headMeshWithMostTargets: BABYLON.Mesh | null = null;
        
        for (const mesh of meshes) {
          const m = mesh as BABYLON.Mesh;
          if (m.morphTargetManager && m.morphTargetManager.numTargets > 0) {
            if (m.morphTargetManager.numTargets > maxTargets) {
              maxTargets = m.morphTargetManager.numTargets;
              headMeshWithMostTargets = m;
            }
          }
        }
        
        // Use the mesh with most targets as the face mesh
        if (headMeshWithMostTargets) {
          faceMesh = headMeshWithMostTargets;
          
          const manager = faceMesh.morphTargetManager!;
          for (let i = 0; i < manager.numTargets; i++) {
            const target = manager.getTarget(i);
            const name = target.name.toLowerCase();
            
            if (!mouthOpenTarget && (name.includes('mouthopen') || name.includes('jawopen') || name === 'viseme_aa' || name === 'viseme_o' || name === 'a' || name === 'aa')) {
              mouthOpenTarget = target;
            }
            if (name.includes('eyeblinkleft') || (name.includes('eye') && name.includes('left') && name.includes('close'))) {
              leftEyeCloseTarget = target;
            }
            if (name.includes('eyeblinkright') || (name.includes('eye') && name.includes('right') && name.includes('close'))) {
              rightEyeCloseTarget = target;
            }
          }
        }

        if (sceneRef.current) {
          sceneRef.current.avatar = rootMesh as BABYLON.Mesh;
          sceneRef.current.head = (head || rootMesh) as BABYLON.Mesh;
          sceneRef.current.allMeshes = meshes;
          sceneRef.current.skeleton = skeleton;
          sceneRef.current.skinnedMesh = skinnedMesh;
          sceneRef.current.initialBoneRotations = null;
          sceneRef.current.faceMesh = faceMesh;
          sceneRef.current.mouthOpenTarget = mouthOpenTarget;
          sceneRef.current.leftEyeCloseTarget = leftEyeCloseTarget;
          sceneRef.current.rightEyeCloseTarget = rightEyeCloseTarget;
        }
      } else {
        if (sceneRef.current) {
          sceneRef.current.avatar = rootMesh as BABYLON.Mesh;
          sceneRef.current.head = (head || rootMesh) as BABYLON.Mesh;
          sceneRef.current.allMeshes = meshes;
          sceneRef.current.skeleton = null;
          sceneRef.current.skinnedMesh = null;
          sceneRef.current.initialBoneRotations = null;
        }
      }

      setIsLoading(false);
    } catch (error) {
      console.error('Error loading model:', error);
      setLoadError(true);
      createSimpleAvatar(scene);
    }
  }

  function createSimpleAvatar(scene: BABYLON.Scene) {
    const avatar = new BABYLON.Mesh('avatar', scene);

    const skinMaterial = new BABYLON.StandardMaterial('skin', scene);
    skinMaterial.diffuseColor = new BABYLON.Color3(0.99, 0.74, 0.71);
    skinMaterial.specularColor = new BABYLON.Color3(0.2, 0.2, 0.2);

    const hairMaterial = new BABYLON.StandardMaterial('hair', scene);
    hairMaterial.diffuseColor = new BABYLON.Color3(0.24, 0.16, 0.09);

    const blazerMaterial = new BABYLON.StandardMaterial('blazer', scene);
    blazerMaterial.diffuseColor = new BABYLON.Color3(0.12, 0.23, 0.37);

    const shirtMaterial = new BABYLON.StandardMaterial('shirt', scene);
    shirtMaterial.diffuseColor = new BABYLON.Color3(1, 1, 1);

    const glassesMaterial = new BABYLON.StandardMaterial('glasses', scene);
    glassesMaterial.diffuseColor = new BABYLON.Color3(0.1, 0.1, 0.1);
    glassesMaterial.specularColor = new BABYLON.Color3(0.5, 0.5, 0.5);

    const head = BABYLON.MeshBuilder.CreateSphere('head', { diameter: 0.5 }, scene);
    head.position.y = 1.6;
    head.material = skinMaterial;
    head.parent = avatar;

    const hair = BABYLON.MeshBuilder.CreateSphere(
      'hair',
      { diameter: 0.54, slice: 0.6 },
      scene
    );
    hair.position.y = 1.65;
    hair.material = hairMaterial;
    hair.parent = avatar;

    const bun = BABYLON.MeshBuilder.CreateSphere('bun', { diameter: 0.26 }, scene);
    bun.position = new BABYLON.Vector3(0, 1.78, -0.18);
    bun.material = hairMaterial;
    bun.parent = avatar;

    const eyeMaterial = new BABYLON.StandardMaterial('eye', scene);
    eyeMaterial.diffuseColor = new BABYLON.Color3(1, 1, 1);

    const pupilMaterial = new BABYLON.StandardMaterial('pupil', scene);
    pupilMaterial.diffuseColor = new BABYLON.Color3(0.17, 0.09, 0.06);

    const leftEye = BABYLON.MeshBuilder.CreateSphere('leftEye', { diameter: 0.07 }, scene);
    leftEye.position = new BABYLON.Vector3(-0.09, 1.65, 0.22);
    leftEye.material = eyeMaterial;
    leftEye.parent = avatar;

    const leftPupil = BABYLON.MeshBuilder.CreateSphere('leftPupil', { diameter: 0.04 }, scene);
    leftPupil.position = new BABYLON.Vector3(-0.09, 1.65, 0.24);
    leftPupil.material = pupilMaterial;
    leftPupil.parent = avatar;

    const rightEye = BABYLON.MeshBuilder.CreateSphere('rightEye', { diameter: 0.07 }, scene);
    rightEye.position = new BABYLON.Vector3(0.09, 1.65, 0.22);
    rightEye.material = eyeMaterial;
    rightEye.parent = avatar;

    const rightPupil = BABYLON.MeshBuilder.CreateSphere('rightPupil', { diameter: 0.04 }, scene);
    rightPupil.position = new BABYLON.Vector3(0.09, 1.65, 0.24);
    rightPupil.material = pupilMaterial;
    rightPupil.parent = avatar;

    const nose = BABYLON.MeshBuilder.CreateCylinder(
      'nose',
      { height: 0.08, diameterTop: 0.03, diameterBottom: 0.06 },
      scene
    );
    nose.position = new BABYLON.Vector3(0, 1.6, 0.24);
    nose.rotation.x = Math.PI / 2;
    nose.material = skinMaterial;
    nose.parent = avatar;

    const smile = BABYLON.MeshBuilder.CreateTorus(
      'smile',
      { diameter: 0.18, thickness: 0.018, tessellation: 16 },
      scene
    );
    smile.position = new BABYLON.Vector3(0, 1.52, 0.23);
    smile.rotation.x = Math.PI;
    const smileMaterial = new BABYLON.StandardMaterial('smileMat', scene);
    smileMaterial.diffuseColor = new BABYLON.Color3(0.79, 0.44, 0.39);
    smile.material = smileMaterial;
    smile.parent = avatar;

    const neck = BABYLON.MeshBuilder.CreateCylinder(
      'neck',
      { height: 0.18, diameterTop: 0.18, diameterBottom: 0.22 },
      scene
    );
    neck.position.y = 1.38;
    neck.material = skinMaterial;
    neck.parent = avatar;

    const collar = BABYLON.MeshBuilder.CreateCylinder(
      'collar',
      { height: 0.12, diameterTop: 0.26, diameterBottom: 0.32 },
      scene
    );
    collar.position.y = 1.26;
    collar.material = shirtMaterial;
    collar.parent = avatar;

    const blazer = BABYLON.MeshBuilder.CreateCylinder(
      'blazer',
      { height: 0.65, diameterTop: 0.32, diameterBottom: 0.56 },
      scene
    );
    blazer.position.y = 0.88;
    blazer.material = blazerMaterial;
    blazer.parent = avatar;

    const leftArm = BABYLON.MeshBuilder.CreateCylinder(
      'leftArm',
      { height: 0.55, diameter: 0.12 },
      scene
    );
    leftArm.position = new BABYLON.Vector3(-0.28, 0.78, 0);
    leftArm.rotation.z = 0.15;
    leftArm.material = blazerMaterial;
    leftArm.parent = avatar;

    const rightArm = BABYLON.MeshBuilder.CreateCylinder(
      'rightArm',
      { height: 0.55, diameter: 0.12 },
      scene
    );
    rightArm.position = new BABYLON.Vector3(0.28, 0.78, 0);
    rightArm.rotation.z = -0.15;
    rightArm.material = blazerMaterial;
    rightArm.parent = avatar;

    const leftHand = BABYLON.MeshBuilder.CreateSphere('leftHand', { diameter: 0.13 }, scene);
    leftHand.position = new BABYLON.Vector3(-0.34, 0.48, 0.05);
    leftHand.material = skinMaterial;
    leftHand.parent = avatar;

    const rightHand = BABYLON.MeshBuilder.CreateSphere('rightHand', { diameter: 0.13 }, scene);
    rightHand.position = new BABYLON.Vector3(0.34, 0.48, 0.05);
    rightHand.material = skinMaterial;
    rightHand.parent = avatar;

    const leftGlass = BABYLON.MeshBuilder.CreateTorus(
      'leftGlass',
      { diameter: 0.15, thickness: 0.012 },
      scene
    );
    leftGlass.position = new BABYLON.Vector3(-0.09, 1.65, 0.23);
    leftGlass.rotation.y = Math.PI / 2;
    leftGlass.material = glassesMaterial;
    leftGlass.parent = avatar;

    const rightGlass = BABYLON.MeshBuilder.CreateTorus(
      'rightGlass',
      { diameter: 0.15, thickness: 0.012 },
      scene
    );
    rightGlass.position = new BABYLON.Vector3(0.09, 1.65, 0.23);
    rightGlass.rotation.y = Math.PI / 2;
    rightGlass.material = glassesMaterial;
    rightGlass.parent = avatar;

    const bridge = BABYLON.MeshBuilder.CreateCylinder(
      'bridge',
      { height: 0.14, diameter: 0.012 },
      scene
    );
    bridge.position = new BABYLON.Vector3(0, 1.65, 0.23);
    bridge.rotation.z = Math.PI / 2;
    bridge.material = glassesMaterial;
    bridge.parent = avatar;

    if (sceneRef.current) {
      sceneRef.current.avatar = avatar;
      sceneRef.current.head = head;
      sceneRef.current.allMeshes = [avatar];
    }

    setIsLoading(false);
  }

  function animateAvatar(
    avatar: BABYLON.Mesh,
    head: BABYLON.Mesh | null,
    allMeshes: BABYLON.AbstractMesh[],
    speaking: boolean,
    listening: boolean,
    volume: number
  ) {
    const time = Date.now() * 0.001;
    const state = animationStateRef.current;

    // Debug log every 2 seconds
    state.talkTimer += 0.016;
    if (state.talkTimer > 2) {
      state.talkTimer = 0;
    }

    // Breathing animation - always active on root mesh
    const breathingIntensity = 0.006;
    const breathingSpeed = 1.5;
    avatar.position.y = Math.sin(time * breathingSpeed) * breathingIntensity;

    // Get skeleton for bone animations
    const skeleton = sceneRef.current?.skeleton;
    
    // Debug: log skeleton status once
    if (!state.initialized) {
      console.log('🦴 Animation init - skeleton:', !!skeleton, 'bones:', skeleton?.bones?.length);
    }
    
    if (skeleton) {
      // Find bones
      const headBone = skeleton.bones.find(b => b.name === 'Head');
      const neckBone = skeleton.bones.find(b => b.name === 'Neck');
      const leftArmBone = skeleton.bones.find(b => b.name === 'LeftArm');
      const rightArmBone = skeleton.bones.find(b => b.name === 'RightArm');
      const leftForeArmBone = skeleton.bones.find(b => b.name === 'LeftForeArm');
      const rightForeArmBone = skeleton.bones.find(b => b.name === 'RightForeArm');
      const leftHandBone = skeleton.bones.find(b => b.name === 'LeftHand');
      const rightHandBone = skeleton.bones.find(b => b.name === 'RightHand');
      
      // Store base rotations on first run
      if (!state.initialized) {
        console.log('🦴 Initializing bone rotations...');
        console.log('  Head bone:', !!headBone, 'has transform:', !!headBone?.getTransformNode());
        console.log('  LeftArm bone:', !!leftArmBone, 'has transform:', !!leftArmBone?.getTransformNode());
        console.log('  LeftForeArm bone:', !!leftForeArmBone, 'has transform:', !!leftForeArmBone?.getTransformNode());
        console.log('  LeftHand bone:', !!leftHandBone, 'has transform:', !!leftHandBone?.getTransformNode());
        
        if (headBone?.getTransformNode()) {
          state.headBaseRotation = headBone.getTransformNode()!.rotation.clone();
        }
        if (neckBone?.getTransformNode()) {
          state.neckBaseRotation = neckBone.getTransformNode()!.rotation.clone();
        }
        if (leftArmBone?.getTransformNode()) {
          state.leftArmBaseRotation = leftArmBone.getTransformNode()!.rotation.clone();
          console.log('  LeftArm base rotation:', state.leftArmBaseRotation);
        }
        if (rightArmBone?.getTransformNode()) {
          state.rightArmBaseRotation = rightArmBone.getTransformNode()!.rotation.clone();
        }
        if (leftForeArmBone?.getTransformNode()) {
          state.leftForeArmBaseRotation = leftForeArmBone.getTransformNode()!.rotation.clone();
        }
        if (rightForeArmBone?.getTransformNode()) {
          state.rightForeArmBaseRotation = rightForeArmBone.getTransformNode()!.rotation.clone();
        }
        if (leftHandBone?.getTransformNode()) {
          state.leftHandBaseRotation = leftHandBone.getTransformNode()!.rotation.clone();
        }
        if (rightHandBone?.getTransformNode()) {
          state.rightHandBaseRotation = rightHandBone.getTransformNode()!.rotation.clone();
        }
        state.initialized = true;
      }
      
      // Calculate animation offsets based on state
      let headOffsetX = 0, headOffsetY = 0, headOffsetZ = 0;
      let neckOffsetX = 0;
      let armOffsetX = 0;
      
      if (speaking) {
        // Speaking: Active head movement and arm gestures
        headOffsetX = Math.sin(time * 3.5) * 0.15;
        headOffsetY = Math.sin(time * 2.8) * 0.12;
        headOffsetZ = Math.sin(time * 2.0) * 0.08;
        neckOffsetX = Math.sin(time * 2.5) * 0.06;
        armOffsetX = Math.sin(time * 1.8) * 0.08;
      } else if (listening) {
        // Listening: Attentive nodding
        headOffsetX = 0.08 + Math.sin(time * 1.5) * 0.06; // Forward lean + nod
        headOffsetY = Math.sin(time * 0.8) * 0.05;
        neckOffsetX = Math.sin(time * 1.2) * 0.03;
      } else {
        // Idle: Subtle micro-movements
        headOffsetX = Math.sin(time * 0.5) * 0.02;
        headOffsetY = Math.sin(time * 0.4) * 0.025;
      }
      
      // Apply head animation
      if (headBone && state.headBaseRotation) {
        const headNode = headBone.getTransformNode();
        if (headNode) {
          headNode.rotation.x = state.headBaseRotation.x + headOffsetX;
          headNode.rotation.y = state.headBaseRotation.y + headOffsetY;
          headNode.rotation.z = state.headBaseRotation.z + headOffsetZ;
        }
      }
      
      // Apply neck animation
      if (neckBone && state.neckBaseRotation) {
        const neckNode = neckBone.getTransformNode();
        if (neckNode) {
          neckNode.rotation.x = state.neckBaseRotation.x + neckOffsetX;
        }
      }
      
      // Arm animation disabled - keeping avatar simple and natural
      // The head movement, blinking, and mouth animation provide enough life
    }
    
    // Body sway animation on root mesh - MORE VISIBLE
    if (speaking) {
      // Obvious body movement while talking
      avatar.rotation.y = Math.sin(time * 1.5) * 0.12;
      avatar.position.x = Math.sin(time * 2) * 0.015;
      // Add slight forward/back lean
      avatar.rotation.x = Math.sin(time * 1.8) * 0.03;
    } else if (listening) {
      // Attentive lean forward
      avatar.rotation.x = 0.06 + Math.sin(time * 0.8) * 0.025;
      avatar.rotation.y = Math.sin(time * 0.6) * 0.04;
      avatar.position.x = 0;
    } else {
      // Subtle idle movement
      avatar.rotation.y = Math.sin(time * 0.4) * 0.025;
      avatar.rotation.x = Math.sin(time * 0.3) * 0.01;
      avatar.position.x = 0;
    }

    // Morph target animations (mouth movement, blinking)
    // IMPORTANT: Iterate over ALL meshes to find and animate morph targets
    const allMeshesWithMorphs = allMeshes.filter(m => {
      const mesh = m as BABYLON.Mesh;
      return mesh.morphTargetManager && mesh.morphTargetManager.numTargets > 0;
    });

    // Mouth animation when speaking - ITERATE ALL MESHES
    if (speaking) {
      const fastWave = Math.sin(time * 8); // Slightly slower
      const slowWave = Math.sin(time * 2.5); // Slower variation
      const mouthValue = Math.max(0, (fastWave * 0.3 + 0.3) * (slowWave * 0.2 + 0.5)); // Reduced intensity
      
      let totalMouthTargetsAnimated = 0;
      
      for (const mesh of allMeshesWithMorphs) {
        const m = mesh as BABYLON.Mesh;
        const manager = m.morphTargetManager!;
        
        manager.enableNormalMorphing = true;
        manager.enableTangentMorphing = true;
        
        for (let i = 0; i < manager.numTargets; i++) {
          const target = manager.getTarget(i);
          const name = target.name.toLowerCase();
          
          if (name.includes('mouth') || name.includes('jaw') || 
              name.includes('viseme') || name === 'aa' || name === 'a' || 
              name === 'o' || name === 'e') {
            target.influence = mouthValue * 0.4;
            totalMouthTargetsAnimated++;
          }
        }
      }
    } else {
      // Close all mouth targets when not speaking
      for (const mesh of allMeshesWithMorphs) {
        const m = mesh as BABYLON.Mesh;
        const manager = m.morphTargetManager!;
        
        for (let i = 0; i < manager.numTargets; i++) {
          const target = manager.getTarget(i);
          const name = target.name.toLowerCase();
          
          if (name.includes('mouth') || name.includes('jaw') || 
              name.includes('viseme') || name === 'aa' || name === 'a' || 
              name === 'o' || name === 'e') {
            if (target.influence > 0.02) {
              target.influence *= 0.85;
            } else {
              target.influence = 0;
            }
          }
        }
      }
    }

    // Eye blinking animation - natural random blinks
    state.blinkTimer += 0.016;
    
    // Blink every 2-5 seconds randomly
    let shouldBlink = false;
    if (state.blinkTimer > 2.5) {
      if (Math.random() < 0.02) { // 2% chance each frame after 2.5s
        shouldBlink = true;
        state.blinkTimer = 0;
      }
    }
    // Force blink if it's been too long (max 5 seconds)
    if (state.blinkTimer > 5) {
      shouldBlink = true;
      state.blinkTimer = 0;
    }
    
    for (const mesh of allMeshesWithMorphs) {
      const m = mesh as BABYLON.Mesh;
      const manager = m.morphTargetManager!;
      
      for (let i = 0; i < manager.numTargets; i++) {
        const target = manager.getTarget(i);
        const name = target.name.toLowerCase();
        
        if (name.includes('eyeblink') || (name.includes('eye') && name.includes('close'))) {
          if (shouldBlink) {
            target.influence = 1;
          } else if (target.influence > 0) {
            // Quick blink down
            target.influence = Math.max(0, target.influence - 0.15);
          }
        }
      }
    }
  }

  if (loadError && !modelUrl) {
    return (
      <div className="relative w-full h-full flex items-center justify-center bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg">
        <div className="text-center">
          <div className="w-32 h-32 rounded-full bg-gradient-to-br from-purple-400 to-purple-600 flex items-center justify-center shadow-2xl mb-4">
            <span className="text-6xl">👩‍⚕️</span>
          </div>
          <p className="text-sm text-gray-600">Your therapist is ready</p>
        </div>
      </div>
    );
  }

  return (
    <div className="relative w-full h-full overflow-visible">
      {isLoading && (
        <div className="absolute inset-0 flex items-center justify-center bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg z-10">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto mb-2"></div>
            <p className="text-sm text-gray-600">
              {modelUrl ? 'Loading 3D model...' : 'Preparing your therapist...'}
            </p>
          </div>
        </div>
      )}

      <canvas
        ref={canvasRef}
        className="w-full h-full rounded-lg"
        style={{ minHeight: '400px', touchAction: 'none' }}
      />

      {isSpeaking && !isLoading && (
        <div
          className="absolute inset-0 rounded-lg pointer-events-none"
          style={{
            boxShadow: `0 0 ${30 + volumeLevel / 3}px rgba(168, 85, 247, ${0.4 + volumeLevel / 150})`,
            transition: 'box-shadow 0.1s ease-out'
          }}
        />
      )}

      {!isLoading && (
        <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 z-[100]">
          <div className="bg-white backdrop-blur-sm rounded-full px-4 py-2 shadow-2xl border-2 border-purple-200">
            <div className="flex items-center space-x-2">
              <div
                className={`w-2.5 h-2.5 rounded-full ${
                  isSpeaking
                    ? 'bg-green-500 animate-pulse'
                    : isListening
                      ? 'bg-blue-500 animate-pulse'
                      : 'bg-purple-400'
                }`}
              />
              <span className="text-xs font-medium text-gray-700">
                {isSpeaking ? 'Speaking' : isListening ? 'Listening' : 'Ready to help'}
              </span>
            </div>
          </div>
        </div>
      )}

      {isActive && !isLoading && (
        <div className="absolute inset-0 rounded-lg bg-purple-400 animate-ping opacity-5 pointer-events-none"></div>
      )}
    </div>
  );
}
