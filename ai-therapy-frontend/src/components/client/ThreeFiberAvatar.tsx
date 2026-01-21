'use client';

/**
 * React Three Fiber 3D Avatar with Lip Sync
 * 🏆 Breaking Barriers UK 2026 compliant
 * Uses Ready Player Me avatar with realistic animations
 */

import { useEffect, useRef, useState } from 'react';
import { Canvas, useFrame, useLoader } from '@react-three/fiber';
import { OrbitControls, useGLTF, useAnimations } from '@react-three/drei';
import * as THREE from 'three';

interface AvatarModelProps {
  isSpeaking: boolean;
  isListening: boolean;
  volumeLevel: number;
  modelUrl: string;
}

function AvatarModel({ isSpeaking, isListening, volumeLevel, modelUrl }: AvatarModelProps) {
  const group = useRef<THREE.Group>(null);
  const { scene, animations } = useGLTF(modelUrl);
  const { actions } = useAnimations(animations, group);
  
  const [mixer] = useState(() => new THREE.AnimationMixer(scene));
  const headRef = useRef<THREE.Object3D | null>(null);
  const mouthRef = useRef<THREE.SkinnedMesh | null>(null);
  
  // Find head and mouth bones/meshes
  useEffect(() => {
    scene.traverse((child) => {
      if (child.name.toLowerCase().includes('head')) {
        headRef.current = child;
      }
      if (child instanceof THREE.SkinnedMesh) {
        // Check for morph targets (for facial animation)
        if (child.morphTargetDictionary && child.morphTargetInfluences) {
          console.log('Found mesh with morph targets:', child.name);
          console.log('Morph targets:', Object.keys(child.morphTargetDictionary));
          mouthRef.current = child;
        }
      }
    });
  }, [scene]);

  // Animation loop - ENHANCED with more visible movements
  useFrame((state, delta) => {
    if (!group.current) return;
    
    const time = state.clock.elapsedTime;
    
    // STRONGER breathing animation
    group.current.position.y = Math.sin(time * 1.5) * 0.03; // 3x stronger
    
    // STRONGER body sway - ALWAYS ACTIVE
    if (isSpeaking) {
      group.current.rotation.y = Math.sin(time * 1.5) * 0.2; // 2x stronger
      group.current.rotation.x = Math.sin(time * 1.8) * 0.08;
      group.current.position.x = Math.sin(time * 2) * 0.03;
    } else if (isListening) {
      group.current.rotation.y = Math.sin(time * 0.8) * 0.12;
      group.current.rotation.x = 0.1 + Math.sin(time * 1.2) * 0.06;
    } else {
      // IDLE - still visible movement
      group.current.rotation.y = Math.sin(time * 0.6) * 0.08;
      group.current.rotation.x = Math.sin(time * 0.5) * 0.04;
    }
    
    // Head movement based on state - MUCH STRONGER
    if (headRef.current) {
      if (isSpeaking) {
        // VERY Active talking movement
        headRef.current.rotation.x = Math.sin(time * 4) * 0.25; // Much stronger
        headRef.current.rotation.y = Math.sin(time * 3) * 0.3;
        headRef.current.rotation.z = Math.sin(time * 3.5) * 0.15;
        headRef.current.position.y = Math.sin(time * 5) * 0.02; // Bob up/down
      } else if (isListening) {
        // Strong attentive nodding
        headRef.current.rotation.x = 0.15 + Math.sin(time * 2) * 0.12;
        headRef.current.rotation.y = Math.sin(time * 1.2) * 0.15;
      } else {
        // Visible idle movement
        headRef.current.rotation.x = Math.sin(time * 0.8) * 0.08;
        headRef.current.rotation.y = Math.sin(time * 0.6) * 0.1;
      }
    }
    
    // Lip sync with morph targets - MUCH STRONGER
    if (mouthRef.current && mouthRef.current.morphTargetInfluences) {
      const influences = mouthRef.current.morphTargetInfluences;
      const dict = mouthRef.current.morphTargetDictionary;
      
      if (isSpeaking) {
        // VERY STRONG mouth animation
        const fastWave = Math.sin(time * 15); // Faster
        const slowWave = Math.sin(time * 4);
        const mouthValue = Math.max(0, (fastWave * 0.6 + 0.6) * (slowWave * 0.4 + 0.8));
        
        // Try ALL possible morph target names with STRONG influence
        const mouthTargets = [
          'mouthOpen', 'jawOpen', 'viseme_aa', 'viseme_O', 'A', 'aa',
          'mouthSmile', 'viseme_E', 'viseme_I', 'viseme_U'
        ];
        
        for (const targetName of mouthTargets) {
          if (dict && dict[targetName] !== undefined) {
            influences[dict[targetName]] = mouthValue * 0.9; // Much stronger (was 0.7)
            console.log(`Setting ${targetName} to ${mouthValue * 0.9}`);
          }
        }
      } else {
        // Close mouth smoothly
        if (dict) {
          Object.keys(dict).forEach((key) => {
            if (key.toLowerCase().includes('mouth') || 
                key.toLowerCase().includes('jaw') ||
                key.toLowerCase().includes('viseme')) {
              influences[dict[key]] *= 0.8; // Smooth decay
            }
          });
        }
      }
      
      // STRONGER eye blinking
      const blinkTargets = ['eyeBlinkLeft', 'eyeBlinkRight', 'blink', 'eyesClosed'];
      const shouldBlink = Math.sin(time * 0.4) > 0.97; // More frequent
      for (const targetName of blinkTargets) {
        if (dict && dict[targetName] !== undefined) {
          influences[dict[targetName]] = shouldBlink ? 1 : 0;
        }
      }
    }
    
    mixer.update(delta);
  });

  return (
    <group ref={group}>
      <primitive object={scene} scale={2.2} position={[0, -1.6, 0]} />
    </group>
  );
}

interface ThreeFiberAvatarProps {
  isActive: boolean;
  isSpeaking: boolean;
  isListening: boolean;
  volumeLevel: number;
  modelUrl?: string;
}

export function ThreeFiberAvatar({
  isActive,
  isSpeaking,
  isListening,
  volumeLevel,
  modelUrl = 'https://models.readyplayer.me/692c94887b7a88e1f63f3d82.glb?pose=A&morphTargets=ARKit'
}: ThreeFiberAvatarProps) {
  const [isLoading, setIsLoading] = useState(true);
  const [loadError, setLoadError] = useState(false);

  useEffect(() => {
    // Preload the model
    useGLTF.preload(modelUrl);
    
    // Simulate loading
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 2000);
    
    return () => clearTimeout(timer);
  }, [modelUrl]);

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
    <div className="relative w-full h-full overflow-visible">
      {isLoading && (
        <div className="absolute inset-0 flex items-center justify-center bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg z-10">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto mb-2"></div>
            <p className="text-sm text-gray-600">Loading 3D avatar...</p>
          </div>
        </div>
      )}

      <Canvas
        camera={{ position: [0, 0, 3], fov: 50 }}
        style={{ width: '100%', height: '100%', minHeight: '400px' }}
      >
        <ambientLight intensity={0.7} />
        <directionalLight position={[2, 3, 2]} intensity={0.5} />
        <pointLight position={[-2, 2, 2]} intensity={0.3} />
        
        <AvatarModel
          isSpeaking={isSpeaking}
          isListening={isListening}
          volumeLevel={volumeLevel}
          modelUrl={modelUrl}
        />
        
        <OrbitControls
          enableZoom={true}
          enablePan={false}
          minDistance={2}
          maxDistance={5}
          minPolarAngle={Math.PI / 4}
          maxPolarAngle={Math.PI / 2}
        />
      </Canvas>

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
                {isSpeaking ? 'Speaking' : isListening ? 'Listening' : 'Ready'}
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
