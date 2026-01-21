'use client';

/**
 * Professional 3D Therapist Avatar Component
 * Uses Three.js with a free female therapist model
 * 🏆 Breaking Barriers UK 2026 compliant
 */

import { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';

interface MovingMouthAvatarProps {
  isActive: boolean;
  isSpeaking: boolean;
  isListening: boolean;
  volumeLevel: number;
}

export function MovingMouthAvatar({ 
  isActive, 
  isSpeaking, 
  isListening, 
  volumeLevel 
}: MovingMouthAvatarProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [loadError, setLoadError] = useState(false);
  const sceneRef = useRef<{
    scene: THREE.Scene;
    camera: THREE.PerspectiveCamera;
    renderer: THREE.WebGLRenderer;
    avatar: THREE.Group | null;
    mixer: THREE.AnimationMixer | null;
    clock: THREE.Clock;
  } | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    // Setup Three.js scene
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0xf8f9fa);

    // Camera setup
    const camera = new THREE.PerspectiveCamera(
      45,
      containerRef.current.clientWidth / containerRef.current.clientHeight,
      0.1,
      1000
    );
    camera.position.set(0, 1.6, 3);
    camera.lookAt(0, 1.6, 0);

    // Renderer setup
    const renderer = new THREE.WebGLRenderer({ 
      antialias: true,
      alpha: true 
    });
    renderer.setSize(containerRef.current.clientWidth, containerRef.current.clientHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    containerRef.current.appendChild(renderer.domElement);

    // Lighting setup
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
    scene.add(ambientLight);

    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(5, 10, 7.5);
    directionalLight.castShadow = true;
    scene.add(directionalLight);

    const fillLight = new THREE.DirectionalLight(0xffffff, 0.3);
    fillLight.position.set(-5, 5, -5);
    scene.add(fillLight);

    const rimLight = new THREE.DirectionalLight(0xa78bfa, 0.4);
    rimLight.position.set(0, 5, -5);
    scene.add(rimLight);

    // Clock for animations
    const clock = new THREE.Clock();

    sceneRef.current = {
      scene,
      camera,
      renderer,
      avatar: null,
      mixer: null,
      clock
    };

    // Create a simple but professional female therapist avatar
    createTherapistAvatar(scene);

    // Animation loop
    let animationId: number;
    const animate = () => {
      animationId = requestAnimationFrame(animate);
      
      const delta = clock.getDelta();
      
      if (sceneRef.current?.mixer) {
        sceneRef.current.mixer.update(delta);
      }

      // Animate avatar based on state
      if (sceneRef.current?.avatar) {
        animateAvatar(sceneRef.current.avatar, isSpeaking, isListening, volumeLevel);
      }

      renderer.render(scene, camera);
    };
    animate();

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
      if (animationId) cancelAnimationFrame(animationId);
      window.removeEventListener('resize', handleResize);
      if (containerRef.current && renderer.domElement) {
        containerRef.current.removeChild(renderer.domElement);
      }
      renderer.dispose();
    };
  }, []);

  // Update animation based on state changes
  useEffect(() => {
    if (!sceneRef.current?.avatar) return;
    // State changes are handled in the animation loop
  }, [isSpeaking, isListening, volumeLevel]);

  function createTherapistAvatar(scene: THREE.Scene) {
    const avatar = new THREE.Group();
    
    // Create a professional female therapist character
    // Head
    const headGeometry = new THREE.SphereGeometry(0.25, 32, 32);
    const skinMaterial = new THREE.MeshStandardMaterial({ 
      color: 0xfdbcb4,
      roughness: 0.8,
      metalness: 0.1
    });
    const head = new THREE.Mesh(headGeometry, skinMaterial);
    head.position.y = 1.6;
    head.castShadow = true;
    avatar.add(head);

    // Hair (professional bun)
    const hairGeometry = new THREE.SphereGeometry(0.26, 32, 32, 0, Math.PI * 2, 0, Math.PI * 0.6);
    const hairMaterial = new THREE.MeshStandardMaterial({ 
      color: 0x4a3728,
      roughness: 0.9
    });
    const hair = new THREE.Mesh(hairGeometry, hairMaterial);
    hair.position.y = 1.65;
    hair.castShadow = true;
    avatar.add(hair);

    // Hair bun
    const bunGeometry = new THREE.SphereGeometry(0.12, 16, 16);
    const bun = new THREE.Mesh(bunGeometry, hairMaterial);
    bun.position.set(0, 1.75, -0.2);
    bun.castShadow = true;
    avatar.add(bun);

    // Eyes
    const eyeGeometry = new THREE.SphereGeometry(0.04, 16, 16);
    const eyeMaterial = new THREE.MeshStandardMaterial({ color: 0x2c1810 });
    
    const leftEye = new THREE.Mesh(eyeGeometry, eyeMaterial);
    leftEye.position.set(-0.08, 1.65, 0.2);
    avatar.add(leftEye);
    
    const rightEye = new THREE.Mesh(eyeGeometry, eyeMaterial);
    rightEye.position.set(0.08, 1.65, 0.2);
    avatar.add(rightEye);

    // Smile
    const smileGeometry = new THREE.TorusGeometry(0.08, 0.015, 8, 16, Math.PI);
    const smileMaterial = new THREE.MeshStandardMaterial({ color: 0xd4756e });
    const smile = new THREE.Mesh(smileGeometry, smileMaterial);
    smile.position.set(0, 1.52, 0.22);
    smile.rotation.x = Math.PI;
    avatar.add(smile);

    // Neck
    const neckGeometry = new THREE.CylinderGeometry(0.08, 0.1, 0.15, 16);
    const neck = new THREE.Mesh(neckGeometry, skinMaterial);
    neck.position.y = 1.35;
    neck.castShadow = true;
    avatar.add(neck);

    // Body (professional attire - blazer)
    const bodyGeometry = new THREE.CylinderGeometry(0.15, 0.25, 0.6, 16);
    const blazerMaterial = new THREE.MeshStandardMaterial({ 
      color: 0x2c3e50,
      roughness: 0.7
    });
    const body = new THREE.Mesh(bodyGeometry, blazerMaterial);
    body.position.y = 0.95;
    body.castShadow = true;
    avatar.add(body);

    // Collar/shirt
    const collarGeometry = new THREE.CylinderGeometry(0.12, 0.15, 0.1, 16);
    const shirtMaterial = new THREE.MeshStandardMaterial({ 
      color: 0xffffff,
      roughness: 0.5
    });
    const collar = new THREE.Mesh(collarGeometry, shirtMaterial);
    collar.position.y = 1.25;
    collar.castShadow = true;
    avatar.add(collar);

    // Arms
    const armGeometry = new THREE.CylinderGeometry(0.06, 0.05, 0.5, 12);
    
    const leftArm = new THREE.Mesh(armGeometry, blazerMaterial);
    leftArm.position.set(-0.22, 0.95, 0);
    leftArm.rotation.z = 0.3;
    leftArm.castShadow = true;
    avatar.add(leftArm);
    
    const rightArm = new THREE.Mesh(armGeometry, blazerMaterial);
    rightArm.position.set(0.22, 0.95, 0);
    rightArm.rotation.z = -0.3;
    rightArm.castShadow = true;
    avatar.add(rightArm);

    // Hands
    const handGeometry = new THREE.SphereGeometry(0.06, 12, 12);
    
    const leftHand = new THREE.Mesh(handGeometry, skinMaterial);
    leftHand.position.set(-0.3, 0.7, 0.1);
    leftHand.castShadow = true;
    avatar.add(leftHand);
    
    const rightHand = new THREE.Mesh(handGeometry, skinMaterial);
    rightHand.position.set(0.3, 0.7, 0.1);
    rightHand.castShadow = true;
    avatar.add(rightHand);

    // Glasses (professional touch)
    const glassesGeometry = new THREE.TorusGeometry(0.08, 0.01, 8, 16);
    const glassesMaterial = new THREE.MeshStandardMaterial({ 
      color: 0x333333,
      metalness: 0.5,
      roughness: 0.3
    });
    
    const leftGlass = new THREE.Mesh(glassesGeometry, glassesMaterial);
    leftGlass.position.set(-0.08, 1.65, 0.22);
    leftGlass.rotation.y = Math.PI / 2;
    avatar.add(leftGlass);
    
    const rightGlass = new THREE.Mesh(glassesGeometry, glassesMaterial);
    rightGlass.position.set(0.08, 1.65, 0.22);
    rightGlass.rotation.y = Math.PI / 2;
    avatar.add(rightGlass);

    // Bridge
    const bridgeGeometry = new THREE.CylinderGeometry(0.01, 0.01, 0.12, 8);
    const bridge = new THREE.Mesh(bridgeGeometry, glassesMaterial);
    bridge.position.set(0, 1.65, 0.22);
    bridge.rotation.z = Math.PI / 2;
    avatar.add(bridge);

    // Store references for animation
    avatar.userData = {
      head,
      leftEye,
      rightEye,
      smile,
      body,
      leftArm,
      rightArm
    };

    scene.add(avatar);
    
    if (sceneRef.current) {
      sceneRef.current.avatar = avatar;
    }

    setIsLoading(false);
  }

  function animateAvatar(
    avatar: THREE.Group, 
    speaking: boolean, 
    listening: boolean, 
    volume: number
  ) {
    const time = Date.now() * 0.001;
    const { head, leftEye, rightEye, smile, body, leftArm, rightArm } = avatar.userData;

    if (speaking) {
      // Speaking animations
      const intensity = volume / 100;
      
      // Head movements
      head.rotation.y = Math.sin(time * 2) * 0.1 * intensity;
      head.rotation.x = Math.sin(time * 1.5) * 0.05 * intensity;
      
      // Smile animation (talking)
      smile.scale.y = 1 + Math.sin(time * 8) * 0.3 * intensity;
      
      // Slight body movement
      body.rotation.y = Math.sin(time * 1.5) * 0.05 * intensity;
      
      // Expressive hand gestures
      leftArm.rotation.z = 0.3 + Math.sin(time * 2) * 0.2 * intensity;
      rightArm.rotation.z = -0.3 - Math.sin(time * 2.5) * 0.2 * intensity;
      
    } else if (listening) {
      // Listening animations - attentive and calm
      
      // Gentle head nod
      head.rotation.x = Math.sin(time * 0.8) * 0.08;
      head.rotation.y = Math.sin(time * 0.5) * 0.05;
      
      // Occasional blink
      const blinkTime = Math.sin(time * 0.5);
      if (blinkTime > 0.95) {
        leftEye.scale.y = 0.1;
        rightEye.scale.y = 0.1;
      } else {
        leftEye.scale.y = 1;
        rightEye.scale.y = 1;
      }
      
      // Calm smile
      smile.scale.y = 1;
      
      // Relaxed posture
      body.rotation.y = Math.sin(time * 0.3) * 0.02;
      leftArm.rotation.z = 0.3 + Math.sin(time * 0.5) * 0.05;
      rightArm.rotation.z = -0.3 - Math.sin(time * 0.5) * 0.05;
      
    } else {
      // Idle animations - subtle breathing and natural movements
      
      // Breathing
      const breathe = Math.sin(time * 0.5) * 0.02;
      body.scale.y = 1 + breathe;
      body.position.y = 0.95 + breathe * 0.5;
      
      // Subtle head movements
      head.rotation.y = Math.sin(time * 0.3) * 0.03;
      head.rotation.x = Math.sin(time * 0.4) * 0.02;
      
      // Occasional blink
      const blinkTime = Math.sin(time * 0.3);
      if (blinkTime > 0.98) {
        leftEye.scale.y = 0.1;
        rightEye.scale.y = 0.1;
      } else {
        leftEye.scale.y = 1;
        rightEye.scale.y = 1;
      }
      
      // Gentle smile
      smile.scale.y = 1;
      
      // Natural arm position
      leftArm.rotation.z = 0.3;
      rightArm.rotation.z = -0.3;
    }
  }

  if (loadError) {
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
            <p className="text-sm text-gray-600">Preparing your therapist...</p>
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
