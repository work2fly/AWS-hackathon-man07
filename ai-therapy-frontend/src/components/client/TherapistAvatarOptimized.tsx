'use client';

/**
 * Optimized 3D Therapist Avatar Component
 * Lightweight version with support for real 3D models
 * 🏆 Breaking Barriers UK 2026 compliant
 */

import { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

interface TherapistAvatarOptimizedProps {
  isActive: boolean;
  isSpeaking: boolean;
  isListening: boolean;
  volumeLevel: number;
  modelUrl?: string; // Optional: URL to GLB/GLTF model
}

export function TherapistAvatarOptimized({ 
  isActive, 
  isSpeaking, 
  isListening, 
  volumeLevel,
  modelUrl 
}: TherapistAvatarOptimizedProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [loadError, setLoadError] = useState(false);
  const animationFrameRef = useRef<number | undefined>(undefined);
  const sceneRef = useRef<{
    scene: THREE.Scene;
    camera: THREE.PerspectiveCamera;
    renderer: THREE.WebGLRenderer;
    avatar: THREE.Group | null;
    mixer: THREE.AnimationMixer | null;
    clock: THREE.Clock;
    head: THREE.Object3D | null;
  } | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    // Setup Three.js scene with optimizations
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0xf8f9fa);

    // Camera setup
    const camera = new THREE.PerspectiveCamera(
      45,
      containerRef.current.clientWidth / containerRef.current.clientHeight,
      0.1,
      100
    );
    camera.position.set(0, 1.6, 2.5);
    camera.lookAt(0, 1.5, 0);

    // Renderer setup with performance optimizations
    const renderer = new THREE.WebGLRenderer({ 
      antialias: true,
      alpha: true,
      powerPreference: 'high-performance' // Optimize for performance
    });
    renderer.setSize(containerRef.current.clientWidth, containerRef.current.clientHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2)); // Cap pixel ratio for performance
    renderer.shadowMap.enabled = false; // Disable shadows for performance
    containerRef.current.appendChild(renderer.domElement);

    // Simplified lighting (fewer lights = better performance)
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.7);
    scene.add(ambientLight);

    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.5);
    directionalLight.position.set(2, 3, 2);
    scene.add(directionalLight);

    // Clock for animations
    const clock = new THREE.Clock();

    sceneRef.current = {
      scene,
      camera,
      renderer,
      avatar: null,
      mixer: null,
      clock,
      head: null
    };

    // Load model or create simple avatar
    if (modelUrl) {
      loadExternalModel(scene, modelUrl);
    } else {
      createSimpleAvatar(scene);
    }

    // Optimized animation loop - only render when needed
    let lastTime = 0;
    const targetFPS = 30; // Limit to 30 FPS for better performance
    const frameInterval = 1000 / targetFPS;

    const animate = (currentTime: number) => {
      animationFrameRef.current = requestAnimationFrame(animate);
      
      const deltaTime = currentTime - lastTime;
      
      // Skip frame if not enough time has passed
      if (deltaTime < frameInterval) return;
      
      lastTime = currentTime - (deltaTime % frameInterval);
      
      const delta = clock.getDelta();
      
      if (sceneRef.current?.mixer) {
        sceneRef.current.mixer.update(delta);
      }

      // Animate avatar based on state (simplified)
      if (sceneRef.current?.head) {
        animateHead(sceneRef.current.head, isSpeaking, isListening, volumeLevel, currentTime);
      }

      renderer.render(scene, camera);
    };
    
    animationFrameRef.current = requestAnimationFrame(animate);

    // Handle window resize
    const handleResize = () => {
      if (!containerRef.current || !sceneRef.current) return;
      
      const width = containerRef.current.clientWidth;
      const height = containerRef.current.clientHeight;
      
      sceneRef.current.camera.aspect = width / height;
      sceneRef.current.camera.updateProjectionMatrix();
      sceneRef.current.renderer.setSize(width, height);
    };
    window.addEventListener('resize', handleResize);

    // Cleanup
    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
      window.removeEventListener('resize', handleResize);
      if (containerRef.current && renderer.domElement) {
        containerRef.current.removeChild(renderer.domElement);
      }
      
      // Dispose of Three.js resources
      scene.traverse((object) => {
        if (object instanceof THREE.Mesh) {
          object.geometry.dispose();
          if (Array.isArray(object.material)) {
            object.material.forEach(material => material.dispose());
          } else {
            object.material.dispose();
          }
        }
      });
      renderer.dispose();
    };
  }, [modelUrl]);

  function loadExternalModel(scene: THREE.Scene, url: string) {
    const loader = new GLTFLoader();
    
    loader.load(
      url,
      (gltf) => {
        const model = gltf.scene;
        
        // Scale and position model
        const box = new THREE.Box3().setFromObject(model);
        const size = box.getSize(new THREE.Vector3());
        const scale = 1.5 / Math.max(size.x, size.y, size.z);
        model.scale.setScalar(scale);
        
        // Center model
        box.setFromObject(model);
        const center = box.getCenter(new THREE.Vector3());
        model.position.sub(center);
        model.position.y = 0;
        
        scene.add(model);
        
        // Find head bone for animations
        let head: THREE.Object3D | null = null;
        model.traverse((child) => {
          const name = child.name.toLowerCase();
          if (name.includes('head') || name.includes('neck')) {
            head = child;
          }
        });
        
        // Setup animation mixer if animations exist
        let mixer: THREE.AnimationMixer | null = null;
        if (gltf.animations && gltf.animations.length > 0) {
          mixer = new THREE.AnimationMixer(model);
          // Play first animation
          const action = mixer.clipAction(gltf.animations[0]);
          action.play();
        }
        
        if (sceneRef.current) {
          sceneRef.current.avatar = model;
          sceneRef.current.mixer = mixer;
          sceneRef.current.head = head;
        }
        
        setIsLoading(false);
      },
      (progress) => {
        // Loading progress
        console.log(`Loading model: ${(progress.loaded / progress.total * 100).toFixed(0)}%`);
      },
      (error) => {
        console.error('Error loading model:', error);
        setLoadError(true);
        // Fallback to simple avatar
        createSimpleAvatar(scene);
      }
    );
  }

  function createSimpleAvatar(scene: THREE.Scene) {
    const avatar = new THREE.Group();
    
    // Professional female therapist avatar - Enhanced version
    
    // Head
    const headGeometry = new THREE.SphereGeometry(0.25, 20, 20);
    const skinMaterial = new THREE.MeshStandardMaterial({ 
      color: 0xfdbcb4,
      roughness: 0.7,
      metalness: 0.1
    });
    const head = new THREE.Mesh(headGeometry, skinMaterial);
    head.position.y = 1.6;
    avatar.add(head);

    // Hair (professional bun style)
    const hairGeometry = new THREE.SphereGeometry(0.27, 20, 20, 0, Math.PI * 2, 0, Math.PI * 0.65);
    const hairMaterial = new THREE.MeshStandardMaterial({ 
      color: 0x3d2817,
      roughness: 0.9
    });
    const hair = new THREE.Mesh(hairGeometry, hairMaterial);
    hair.position.y = 1.65;
    avatar.add(hair);

    // Hair bun
    const bunGeometry = new THREE.SphereGeometry(0.13, 16, 16);
    const bun = new THREE.Mesh(bunGeometry, hairMaterial);
    bun.position.set(0, 1.78, -0.18);
    avatar.add(bun);

    // Eyes
    const eyeGeometry = new THREE.SphereGeometry(0.035, 12, 12);
    const eyeWhiteMaterial = new THREE.MeshStandardMaterial({ color: 0xffffff });
    const eyePupilMaterial = new THREE.MeshStandardMaterial({ color: 0x2c1810 });
    
    // Left eye
    const leftEyeWhite = new THREE.Mesh(eyeGeometry, eyeWhiteMaterial);
    leftEyeWhite.position.set(-0.09, 1.65, 0.22);
    avatar.add(leftEyeWhite);
    
    const leftPupil = new THREE.Mesh(new THREE.SphereGeometry(0.02, 12, 12), eyePupilMaterial);
    leftPupil.position.set(-0.09, 1.65, 0.24);
    avatar.add(leftPupil);
    
    // Right eye
    const rightEyeWhite = new THREE.Mesh(eyeGeometry, eyeWhiteMaterial);
    rightEyeWhite.position.set(0.09, 1.65, 0.22);
    avatar.add(rightEyeWhite);
    
    const rightPupil = new THREE.Mesh(new THREE.SphereGeometry(0.02, 12, 12), eyePupilMaterial);
    rightPupil.position.set(0.09, 1.65, 0.24);
    avatar.add(rightPupil);

    // Eyebrows
    const eyebrowGeometry = new THREE.BoxGeometry(0.08, 0.015, 0.01);
    const eyebrowMaterial = new THREE.MeshStandardMaterial({ color: 0x3d2817 });
    
    const leftEyebrow = new THREE.Mesh(eyebrowGeometry, eyebrowMaterial);
    leftEyebrow.position.set(-0.09, 1.7, 0.23);
    leftEyebrow.rotation.z = -0.1;
    avatar.add(leftEyebrow);
    
    const rightEyebrow = new THREE.Mesh(eyebrowGeometry, eyebrowMaterial);
    rightEyebrow.position.set(0.09, 1.7, 0.23);
    rightEyebrow.rotation.z = 0.1;
    avatar.add(rightEyebrow);

    // Nose
    const noseGeometry = new THREE.ConeGeometry(0.03, 0.08, 8);
    const nose = new THREE.Mesh(noseGeometry, skinMaterial);
    nose.position.set(0, 1.6, 0.24);
    nose.rotation.x = Math.PI / 2;
    avatar.add(nose);

    // Smile
    const smileGeometry = new THREE.TorusGeometry(0.09, 0.018, 8, 16, Math.PI);
    const smileMaterial = new THREE.MeshStandardMaterial({ color: 0xc97064 });
    const smile = new THREE.Mesh(smileGeometry, smileMaterial);
    smile.position.set(0, 1.52, 0.23);
    smile.rotation.x = Math.PI;
    avatar.add(smile);

    // Neck
    const neckGeometry = new THREE.CylinderGeometry(0.09, 0.11, 0.18, 16);
    const neck = new THREE.Mesh(neckGeometry, skinMaterial);
    neck.position.y = 1.38;
    avatar.add(neck);

    // Collar/Shirt (white)
    const collarGeometry = new THREE.CylinderGeometry(0.13, 0.16, 0.12, 16);
    const shirtMaterial = new THREE.MeshStandardMaterial({ 
      color: 0xffffff,
      roughness: 0.6
    });
    const collar = new THREE.Mesh(collarGeometry, shirtMaterial);
    collar.position.y = 1.26;
    avatar.add(collar);

    // Blazer/Jacket (professional navy)
    const blazerGeometry = new THREE.CylinderGeometry(0.16, 0.28, 0.65, 16);
    const blazerMaterial = new THREE.MeshStandardMaterial({ 
      color: 0x1e3a5f,
      roughness: 0.7
    });
    const blazer = new THREE.Mesh(blazerGeometry, blazerMaterial);
    blazer.position.y = 0.88;
    avatar.add(blazer);

    // Blazer buttons
    const buttonGeometry = new THREE.SphereGeometry(0.02, 8, 8);
    const buttonMaterial = new THREE.MeshStandardMaterial({ 
      color: 0x333333,
      metalness: 0.5
    });
    
    for (let i = 0; i < 3; i++) {
      const button = new THREE.Mesh(buttonGeometry, buttonMaterial);
      button.position.set(0, 1.1 - i * 0.15, 0.28);
      avatar.add(button);
    }

    // Arms
    const armGeometry = new THREE.CylinderGeometry(0.06, 0.055, 0.55, 12);
    
    const leftArm = new THREE.Mesh(armGeometry, blazerMaterial);
    leftArm.position.set(-0.24, 0.88, 0);
    leftArm.rotation.z = 0.25;
    avatar.add(leftArm);
    
    const rightArm = new THREE.Mesh(armGeometry, blazerMaterial);
    rightArm.position.set(0.24, 0.88, 0);
    rightArm.rotation.z = -0.25;
    avatar.add(rightArm);

    // Hands
    const handGeometry = new THREE.SphereGeometry(0.065, 12, 12);
    
    const leftHand = new THREE.Mesh(handGeometry, skinMaterial);
    leftHand.position.set(-0.32, 0.62, 0.08);
    avatar.add(leftHand);
    
    const rightHand = new THREE.Mesh(handGeometry, skinMaterial);
    rightHand.position.set(0.32, 0.62, 0.08);
    avatar.add(rightHand);

    // Glasses (professional touch)
    const glassFrameGeometry = new THREE.TorusGeometry(0.075, 0.012, 8, 16);
    const glassMaterial = new THREE.MeshStandardMaterial({ 
      color: 0x1a1a1a,
      metalness: 0.6,
      roughness: 0.3
    });
    
    const leftGlass = new THREE.Mesh(glassFrameGeometry, glassMaterial);
    leftGlass.position.set(-0.09, 1.65, 0.23);
    leftGlass.rotation.y = Math.PI / 2;
    avatar.add(leftGlass);
    
    const rightGlass = new THREE.Mesh(glassFrameGeometry, glassMaterial);
    rightGlass.position.set(0.09, 1.65, 0.23);
    rightGlass.rotation.y = Math.PI / 2;
    avatar.add(rightGlass);

    // Bridge between glasses
    const bridgeGeometry = new THREE.CylinderGeometry(0.012, 0.012, 0.14, 8);
    const bridge = new THREE.Mesh(bridgeGeometry, glassMaterial);
    bridge.position.set(0, 1.65, 0.23);
    bridge.rotation.z = Math.PI / 2;
    avatar.add(bridge);

    // Earpieces
    const earGeometry = new THREE.CylinderGeometry(0.01, 0.01, 0.12, 8);
    
    const leftEar = new THREE.Mesh(earGeometry, glassMaterial);
    leftEar.position.set(-0.17, 1.65, 0.15);
    leftEar.rotation.y = -Math.PI / 4;
    avatar.add(leftEar);
    
    const rightEar = new THREE.Mesh(earGeometry, glassMaterial);
    rightEar.position.set(0.17, 1.65, 0.15);
    rightEar.rotation.y = Math.PI / 4;
    avatar.add(rightEar);

    scene.add(avatar);
    
    if (sceneRef.current) {
      sceneRef.current.avatar = avatar;
      sceneRef.current.head = head;
    }

    setIsLoading(false);
  }

  function animateHead(
    head: THREE.Object3D,
    speaking: boolean,
    listening: boolean,
    volume: number,
    time: number
  ) {
    const t = time * 0.001; // Convert to seconds
    
    if (speaking) {
      // Speaking - more pronounced movements
      const intensity = volume / 100;
      head.rotation.y = Math.sin(t * 2) * 0.1 * intensity;
      head.rotation.x = Math.sin(t * 1.5) * 0.05 * intensity;
    } else if (listening) {
      // Listening - gentle nod
      head.rotation.x = Math.sin(t * 0.8) * 0.08;
      head.rotation.y = Math.sin(t * 0.5) * 0.05;
    } else {
      // Idle - minimal movement
      head.rotation.y = Math.sin(t * 0.3) * 0.03;
      head.rotation.x = Math.sin(t * 0.4) * 0.02;
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
    <div className="relative w-full h-full">
      {/* Loading state */}
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

      {/* Three.js container */}
      <div 
        ref={containerRef} 
        className="w-full h-full rounded-lg overflow-hidden"
        style={{ minHeight: '400px' }}
      />

      {/* Glow effect when speaking */}
      {isSpeaking && !isLoading && (
        <div 
          className="absolute inset-0 rounded-lg pointer-events-none"
          style={{
            boxShadow: `0 0 ${30 + volumeLevel / 3}px rgba(168, 85, 247, ${0.4 + volumeLevel / 150})`,
            transition: 'box-shadow 0.1s ease-out'
          }}
        />
      )}

      {/* Status indicator */}
      {!isLoading && (
        <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 z-20">
          <div className="bg-white/95 backdrop-blur-sm rounded-full px-4 py-2 shadow-lg border border-purple-100">
            <div className="flex items-center space-x-2">
              <div className={`w-2.5 h-2.5 rounded-full ${
                isSpeaking ? 'bg-green-500 animate-pulse' : 
                isListening ? 'bg-blue-500 animate-pulse' : 
                'bg-purple-400'
              }`} />
              <span className="text-xs font-medium text-gray-700">
                {isSpeaking ? 'Speaking' : isListening ? 'Listening' : 'Ready to help'}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Ambient pulse when active */}
      {isActive && !isLoading && (
        <div className="absolute inset-0 rounded-lg bg-purple-400 animate-ping opacity-5 pointer-events-none"></div>
      )}
    </div>
  );
}
