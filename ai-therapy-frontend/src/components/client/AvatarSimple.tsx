'use client';

// Simple 3D Avatar component using Ready.Player.Me iframe
// 🏆 Breaking Barriers UK 2026 compliant
// Lightweight alternative that doesn't require Three.js

import { useEffect, useRef, useState } from 'react';
import { Heart } from 'lucide-react';

interface AvatarSimpleProps {
  isActive: boolean;
  isSpeaking: boolean;
  isListening: boolean;
  volumeLevel: number;
}

export function AvatarSimple({ 
  isActive, 
  isSpeaking, 
  isListening, 
  volumeLevel 
}: AvatarSimpleProps) {
  const [avatarLoaded, setAvatarLoaded] = useState(false);
  const iframeRef = useRef<HTMLIFrameElement>(null);

  // Simple avatar URL - you can customize this
  // This uses Ready.Player.Me's viewer which handles rendering
  const avatarUrl = 'https://models.readyplayer.me/6571e4e3c3e5e5f3e3e5e5f3.glb';
  const viewerUrl = `https://demo.readyplayer.me/avatar?frameApi&url=${encodeURIComponent(avatarUrl)}`;

  useEffect(() => {
    if (!iframeRef.current) return;

    const handleMessage = (event: MessageEvent) => {
      if (event.data === 'v1.frame.ready') {
        setAvatarLoaded(true);
      }
    };

    window.addEventListener('message', handleMessage);
    return () => window.removeEventListener('message', handleMessage);
  }, []);

  // Send animation commands to iframe
  useEffect(() => {
    if (!iframeRef.current || !avatarLoaded) return;

    const message = {
      target: 'readyplayerme',
      type: 'subscribe',
      eventName: isSpeaking ? 'v1.avatar.talking' : isListening ? 'v1.avatar.listening' : 'v1.avatar.idle'
    };

    iframeRef.current.contentWindow?.postMessage(JSON.stringify(message), '*');
  }, [isSpeaking, isListening, avatarLoaded]);

  return (
    <div className="relative w-full h-full">
      {/* Loading state */}
      {!avatarLoaded && (
        <div className="absolute inset-0 flex items-center justify-center bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto mb-2"></div>
            <p className="text-sm text-gray-600">Loading your therapist...</p>
          </div>
        </div>
      )}

      {/* Ready.Player.Me iframe viewer */}
      <iframe
        ref={iframeRef}
        src={viewerUrl}
        className={`w-full h-full rounded-lg border-0 ${avatarLoaded ? 'opacity-100' : 'opacity-0'}`}
        allow="camera; microphone"
        style={{ 
          minHeight: '400px',
          transition: 'opacity 0.3s ease-in-out'
        }}
        onLoad={() => {
          // Fallback if message event doesn't fire
          setTimeout(() => setAvatarLoaded(true), 2000);
        }}
      />

      {/* Glow effect when speaking */}
      {isSpeaking && avatarLoaded && (
        <div 
          className="absolute inset-0 rounded-lg pointer-events-none"
          style={{
            boxShadow: `0 0 ${20 + volumeLevel / 5}px rgba(168, 85, 247, ${0.3 + volumeLevel / 200})`,
            transition: 'box-shadow 0.1s ease-out'
          }}
        />
      )}

      {/* Status indicator */}
      <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2">
        <div className="bg-white/90 backdrop-blur-sm rounded-full px-4 py-2 shadow-lg">
          <div className="flex items-center space-x-2">
            <div className={`w-2 h-2 rounded-full ${
              isSpeaking ? 'bg-green-500 animate-pulse' : 
              isListening ? 'bg-blue-500 animate-pulse' : 
              'bg-gray-400'
            }`} />
            <span className="text-xs font-medium text-gray-700">
              {isSpeaking ? 'Speaking' : isListening ? 'Listening' : 'Ready'}
            </span>
          </div>
        </div>
      </div>

      {/* Pulse animation when active */}
      {isActive && (
        <div className="absolute inset-0 rounded-lg bg-purple-400 animate-ping opacity-10 pointer-events-none"></div>
      )}
    </div>
  );
}
