'use client';

// 3D Avatar component using Ready.Player.Me
// 🏆 Breaking Barriers UK 2026 compliant

import { useEffect, useRef, useState, Suspense } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, useGLTF } from '@react-three/drei';
import * as THREE from 'three';

interface Avatar3DProps {
  isActive: boolean;
  isSpeaking: boolean;
  isListening: boolean;
  volumeLevel: number;
  avatarUrl?: string;
}

// Default Ready.Player.Me avatar URL (gender-neutral, professional therapist look)
const DEFAULT_AVATAR_URL = 'https://models.readyplayer.me/6571e4e3c3e5e5f3e3e5e5f3.glb';

function AvatarModel({ 
  url, 
  isSpeaking, 
  isListening, 
  volumeLevel 
}: { 
  url: string; 
  isSpeaking: boolean; 
  isListening: boolean; 
  volumeLevel: number;
}) {
  const { scene, animations } = useGLTF(url);
  const mixerRef = useRef<THREE.AnimationMixer | null>(null);
  const actionsRef = useRef<{ [key: string]: THREE.AnimationAction }>({});
  const headRef = useRef<THREE.Object3D | null>(null);

  useEffect(() => {
    if (!scene) return;

    // Find the head bone for animations
    scene.traverse((child) => {
      if (child.name.toLowerCase().includes('head')) {
        headRef.current = child;
      }
    });

    // Setup animation mixer
    if (animations && animations.length > 0) {
      mixerRef.current = new THREE.AnimationMixer(scene);
      
      animations.forEach((clip) => {
        const action = mixerRef.current!.clip(clip);
        actionsRef.current[clip.name] = action;
      });
    }

    return () => {
      if (mixerRef.current) {
        mixerRef.current.stopAllAction();
      }
    };
  }, [scene, animations]);

  // Animate based on speaking/listening state
  useEffect(() => {
    const clock = new THREE.Clock();
    let animationId: number;

    const animate = () => {
      const delta = clock.getDelta();
      
      if (mixerRef.current) {
        mixerRef.current.update(delta);
      }

      // Head movements based on state
      if (headRef.current) {
        if (isSpeaking) {
          // Subtle head movements when speaking
          const intensity = volumeLevel / 100;
          headRef.current.rotation.y = Math.sin(Date.now() * 0.001) * 0.1 * intensity;
          headRef.current.rotation.x = Math.sin(Date.now() * 0.0015) * 0.05 * intensity;
        } else if (isListening) {
          // Gentle nodding when listening
          headRef.current.rotation.x = Math.sin(Date.now() * 0.0008) * 0.03;
        } else {
          // Idle breathing animation
          headRef.current.rotation.y = Math.sin(Date.now() * 0.0005) * 0.02;
        }
      }

      animationId = requestAnimationFrame(animate);
    };

    animate();

    return () => {
      if (animationId) {
        cancelAnimationFrame(animationId);
      }
    };
  }, [isSpeaking, isListening, volumeLevel]);

  return (
    <primitive 
      object={scene} 
      scale={2.5} 
      position={[0, -1.5, 0]} 
    />
  );
}

export function Avatar3D({ 
  isActive, 
  isSpeaking, 
  isListening, 
  volumeLevel,
  avatarUrl = DEFAULT_AVATAR_URL 
}: Avatar3DProps) {
  const [loadError, setLoadError] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    setIsLoading(true);
    setLoadError(false);
  }, [avatarUrl]);

  if (loadError) {
    // Fallback to 2D avatar
    return (
      <div className="relative w-full h-full flex items-center justify-center">
        <div className="w-40 h-40 rounded-full bg-gradient-to-br from-purple-400 via-purple-500 to-purple-600 flex items-center justify-center shadow-2xl">
          <span className="text-6xl">👨‍⚕️</span>
        </div>
        {isActive && (
          <div className="absolute inset-0 rounded-full bg-purple-400 animate-ping opacity-20"></div>
        )}
      </div>
    );
  }

  return (
    <div className="relative w-full h-full">
      {isLoading && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-100 rounded-lg">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto mb-2"></div>
            <p className="text-sm text-gray-600">Loading avatar...</p>
          </div>
        </div>
      )}
      
      <Canvas
        camera={{ position: [0, 0, 3], fov: 50 }}
        style={{ width: '100%', height: '100%' }}
        onCreated={() => setIsLoading(false)}
      >
        <Suspense fallback={null}>
          <ambientLight intensity={0.8} />
          <directionalLight position={[5, 5, 5]} intensity={1} />
          <directionalLight position={[-5, 5, -5]} intensity={0.5} />
          <pointLight position={[0, 2, 0]} intensity={0.5} />
          
          <AvatarModel
            url={avatarUrl}
            isSpeaking={isSpeaking}
            isListening={isListening}
            volumeLevel={volumeLevel}
          />
          
          <OrbitControls
            enableZoom={false}
            enablePan={false}
            minPolarAngle={Math.PI / 3}
            maxPolarAngle={Math.PI / 2}
            autoRotate={!isActive}
            autoRotateSpeed={0.5}
          />
        </Suspense>
      </Canvas>

      {/* Glow effect when speaking */}
      {isSpeaking && (
        <div 
          className="absolute inset-0 rounded-lg pointer-events-none"
          style={{
            boxShadow: `0 0 ${20 + volumeLevel / 5}px rgba(168, 85, 247, ${0.3 + volumeLevel / 200})`,
            transition: 'box-shadow 0.1s ease-out'
          }}
        />
      )}
    </div>
  );
}
