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
  const [showControls, setShowControls] = useState(false);
  const [shoulderDown, setShoulderDown] = useState(-0.05);
  const [upperArmDown, setUpperArmDown] = useState(-0.15);
  const [foreArmIn, setForeArmIn] = useState(0.15);

  // Store arm values in a ref so loadExternalModel can access them
  const armValuesRef = useRef({ shoulderDown: -0.05, upperArmDown: -0.15, foreArmIn: 0.15 });

  // Update ref when state changes
  useEffect(() => {
    armValuesRef.current = { shoulderDown, upperArmDown, foreArmIn };
  }, [shoulderDown, upperArmDown, foreArmIn]);

  const sceneRef = useRef<{
    engine: BABYLON.Engine;
    scene: BABYLON.Scene;
    avatar: BABYLON.Mesh | null;
    head: BABYLON.Mesh | null;
    allMeshes: BABYLON.AbstractMesh[];
    skeleton: BABYLON.Skeleton | null;
    skinnedMesh: BABYLON.AbstractMesh | null;
    initialBoneRotations: Map<string, BABYLON.Vector3> | null;
  } | null>(null);

  const animationStateRef = useRef({
    blinkTimer: 0,
    talkTimer: 0,
    gestureTimer: 0,
    lastGesture: 0
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
      initialBoneRotations: null
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
          isSpeaking,
          isListening,
          volumeLevel
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
      console.log('=== Ready Player Me Arm Adjustment ===');
      console.log('Total meshes loaded:', meshes.length);

      if (result.skeletons && result.skeletons.length > 0) {
        const skeleton = result.skeletons[0];
        console.log('Skeleton found with', skeleton.bones.length, 'bones');

        // CRITICAL: Force skeleton to update by using needInitialSkinMatrix
        skeleton.needInitialSkinMatrix = true;
        
        // Find all skinned meshes and force them to use the skeleton properly
        result.meshes.forEach((mesh) => {
          if ((mesh as any).skeleton) {
            console.log('Found skinned mesh:', mesh.name);
            // Force the mesh to recalculate its bone matrices
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
        
        console.log('Using arm values:', { shoulderDownValue, upperArmDownValue, foreArmInValue });

        // Use the bone's linked transform node for rotation
        let adjusted = 0;

        const rotateBone = (bone: BABYLON.Bone | undefined, axis: BABYLON.Vector3, angle: number, name: string) => {
          if (!bone) return;
          
          console.log(`✓ Rotating ${name} by ${angle} radians`);
          
          // Get the transform node linked to this bone
          const transformNode = bone.getTransformNode();
          if (transformNode) {
            console.log(`  Using transform node: ${transformNode.name}`);
            // Rotate the transform node
            transformNode.rotate(axis, angle, BABYLON.Space.LOCAL);
          } else {
            console.log(`  No transform node, using bone directly`);
            // Fallback to bone rotation
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
          // If mesh has skeleton, force bone matrix update
          if ((m as any).skeleton) {
            const skel = (m as any).skeleton as BABYLON.Skeleton;
            skel.computeAbsoluteTransforms(true);
          }
        });

        console.log('=== Total arm bones adjusted:', adjusted, '===');

        if (sceneRef.current) {
          sceneRef.current.avatar = rootMesh as BABYLON.Mesh;
          sceneRef.current.head = (head || rootMesh) as BABYLON.Mesh;
          sceneRef.current.allMeshes = meshes;
          sceneRef.current.skeleton = skeleton;
          sceneRef.current.skinnedMesh = skinnedMesh;
          sceneRef.current.initialBoneRotations = null;
        }
      } else {
        console.log('No skeleton found, cannot adjust arms.');
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
    const deltaTime = 0.016;
    const state = animationStateRef.current;

    state.blinkTimer += deltaTime;
    state.talkTimer += deltaTime;
    state.gestureTimer += deltaTime;

    if (!head) return;

    // Enhanced breathing animation
    const breathingIntensity = speaking ? 0.015 : 0.008;
    const breathingSpeed = speaking ? 1.5 : 1.2;
    avatar.position.y = Math.sin(time * breathingSpeed) * breathingIntensity;

    if (speaking) {
      // More pronounced speaking animations
      const talkIntensity = Math.max(0.5, volume / 100);

      // Head movements - more natural and expressive
      if (head.name.toLowerCase().includes('head') && !head.name.toLowerCase().includes('eye')) {
        head.rotation.y = Math.sin(time * 2.0) * 0.15 * talkIntensity; // Side to side
        head.rotation.x = Math.sin(time * 2.5) * 0.12 * talkIntensity; // Nod up/down
        head.rotation.z = Math.sin(time * 1.8) * 0.08 * talkIntensity; // Tilt
      }

      // Body movements - subtle sway
      avatar.rotation.y = Math.sin(time * 1.2) * 0.05 * talkIntensity;
      
      // Add slight forward lean when speaking
      avatar.rotation.x = Math.sin(time * 1.5) * 0.02 * talkIntensity;
      
      // Shoulder movement simulation (if no skeleton)
      avatar.position.x = Math.sin(time * 1.8) * 0.01 * talkIntensity;
      
    } else if (listening) {
      const listenIntensity = 0.5;

      if (head.name.toLowerCase().includes('head') && !head.name.toLowerCase().includes('eye')) {
        head.rotation.x = Math.sin(time * 0.6) * 0.06 * listenIntensity;
        head.rotation.y = Math.sin(time * 0.4) * 0.05 * listenIntensity;
      }

      avatar.rotation.x = Math.sin(time * 0.5) * 0.02;
    } else {
      const idleIntensity = 0.3;

      if (head.name.toLowerCase().includes('head') && !head.name.toLowerCase().includes('eye')) {
        head.rotation.y = Math.sin(time * 0.3) * 0.03 * idleIntensity;
        head.rotation.x = Math.sin(time * 0.4) * 0.02 * idleIntensity;
      }

      avatar.rotation.y = Math.sin(time * 0.25) * 0.01;
    }
  }

  function reapplyArmRotations() {
    console.log('=== Reloading model with new arm values ===');
    console.log('New values from state:', { shoulderDown, upperArmDown, foreArmIn });
    
    // Update the ref BEFORE reloading
    armValuesRef.current = { shoulderDown, upperArmDown, foreArmIn };
    console.log('Updated armValuesRef to:', armValuesRef.current);
    
    if (!sceneRef.current?.scene || !modelUrl) {
      console.error('Missing scene or modelUrl');
      return;
    }

    // Remove existing meshes
    console.log('Disposing', sceneRef.current.allMeshes.length, 'meshes');
    sceneRef.current.allMeshes.forEach((mesh) => {
      mesh.dispose();
    });
    
    // Clear skeleton
    if (sceneRef.current.skeleton) {
      console.log('Disposing skeleton');
      sceneRef.current.skeleton.dispose();
    }

    // Reset refs
    sceneRef.current.allMeshes = [];
    sceneRef.current.avatar = null;
    sceneRef.current.head = null;
    sceneRef.current.skeleton = null;
    sceneRef.current.skinnedMesh = null;

    // Reload the model with new values
    console.log('Starting model reload...');
    setIsLoading(true);
    loadExternalModel(sceneRef.current.scene, modelUrl);
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
    <div className="relative w-full h-full">
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
        <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 z-20">
          <div className="bg-white/95 backdrop-blur-sm rounded-full px-4 py-2 shadow-lg border border-purple-100">
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

      {/* Arm Position Controls */}
      {modelUrl && !isLoading && (
        <div className="absolute top-4 right-4 z-20">
          <button
            onClick={() => setShowControls(!showControls)}
            className="bg-white/95 backdrop-blur-sm rounded-lg px-3 py-2 shadow-lg border border-purple-100 hover:bg-purple-50 transition-colors"
          >
            <span className="text-xs font-medium text-gray-700">⚙️ Adjust Arms</span>
          </button>

          {showControls && (
            <div className="mt-2 bg-white/95 backdrop-blur-sm rounded-lg p-4 shadow-lg border border-purple-100 min-w-[240px]">
              <div className="space-y-3">
                <div>
                  <label className="text-xs font-medium text-gray-700 block mb-1">
                    Shoulder Down: {shoulderDown.toFixed(2)}
                  </label>
                  <input
                    type="range"
                    min="-1"
                    max="1"
                    step="0.05"
                    value={shoulderDown}
                    onChange={(e) => setShoulderDown(parseFloat(e.target.value))}
                    className="w-full h-2 bg-purple-200 rounded-lg appearance-none cursor-pointer"
                  />
                </div>

                <div>
                  <label className="text-xs font-medium text-gray-700 block mb-1">
                    Upper Arm Down: {upperArmDown.toFixed(2)}
                  </label>
                  <input
                    type="range"
                    min="-1.5"
                    max="1.5"
                    step="0.05"
                    value={upperArmDown}
                    onChange={(e) => setUpperArmDown(parseFloat(e.target.value))}
                    className="w-full h-2 bg-purple-200 rounded-lg appearance-none cursor-pointer"
                  />
                </div>

                <div>
                  <label className="text-xs font-medium text-gray-700 block mb-1">
                    Forearm In: {foreArmIn.toFixed(2)}
                  </label>
                  <input
                    type="range"
                    min="-0.5"
                    max="0.5"
                    step="0.05"
                    value={foreArmIn}
                    onChange={(e) => setForeArmIn(parseFloat(e.target.value))}
                    className="w-full h-2 bg-purple-200 rounded-lg appearance-none cursor-pointer"
                  />
                </div>

                <button
                  onClick={() => {
                    console.log('Apply Changes button clicked');
                    reapplyArmRotations();
                    // Visual feedback
                    const btn = document.activeElement as HTMLButtonElement;
                    if (btn) {
                      btn.textContent = 'Applied!';
                      setTimeout(() => {
                        btn.textContent = 'Apply Changes';
                      }, 1000);
                    }
                  }}
                  className="w-full bg-purple-600 hover:bg-purple-700 text-white text-xs font-medium py-2 px-3 rounded-lg transition-colors"
                >
                  Apply Changes
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
