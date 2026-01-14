'use client';

/**
 * Simple Reliable 3D Avatar
 * Guaranteed to work - minimal dependencies
 * 🏆 Breaking Barriers UK 2026 compliant
 */

import { useEffect, useRef } from 'react';

interface SimpleAvatarProps {
  isActive: boolean;
  isSpeaking: boolean;
  isListening: boolean;
  volumeLevel: number;
}

export function SimpleAvatar({ 
  isActive, 
  isSpeaking, 
  isListening, 
  volumeLevel 
}: SimpleAvatarProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationRef = useRef<number | undefined>(undefined);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Set canvas size
    canvas.width = canvas.offsetWidth;
    canvas.height = canvas.offsetHeight;

    let time = 0;

    const animate = () => {
      time += 0.016; // ~60fps

      // Clear canvas
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // Center position
      const centerX = canvas.width / 2;
      const centerY = canvas.height / 2;

      // Draw professional female therapist avatar
      
      // Head
      ctx.fillStyle = '#fdbcb4';
      ctx.beginPath();
      ctx.arc(centerX, centerY - 80, 60, 0, Math.PI * 2);
      ctx.fill();

      // Hair
      ctx.fillStyle = '#3d2817';
      ctx.beginPath();
      ctx.arc(centerX, centerY - 90, 62, 0, Math.PI, true);
      ctx.fill();

      // Hair bun
      ctx.beginPath();
      ctx.arc(centerX, centerY - 130, 25, 0, Math.PI * 2);
      ctx.fill();

      // Eyes
      ctx.fillStyle = '#ffffff';
      ctx.beginPath();
      ctx.arc(centerX - 20, centerY - 85, 8, 0, Math.PI * 2);
      ctx.fill();
      ctx.beginPath();
      ctx.arc(centerX + 20, centerY - 85, 8, 0, Math.PI * 2);
      ctx.fill();

      // Pupils (with animation)
      ctx.fillStyle = '#2c1810';
      const pupilOffset = isSpeaking ? Math.sin(time * 3) * 2 : 0;
      ctx.beginPath();
      ctx.arc(centerX - 20 + pupilOffset, centerY - 85, 4, 0, Math.PI * 2);
      ctx.fill();
      ctx.beginPath();
      ctx.arc(centerX + 20 + pupilOffset, centerY - 85, 4, 0, Math.PI * 2);
      ctx.fill();

      // Eyebrows
      ctx.strokeStyle = '#3d2817';
      ctx.lineWidth = 3;
      ctx.beginPath();
      ctx.moveTo(centerX - 30, centerY - 100);
      ctx.lineTo(centerX - 10, centerY - 102);
      ctx.stroke();
      ctx.beginPath();
      ctx.moveTo(centerX + 10, centerY - 102);
      ctx.lineTo(centerX + 30, centerY - 100);
      ctx.stroke();

      // Nose
      ctx.strokeStyle = '#e0a89a';
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(centerX, centerY - 75);
      ctx.lineTo(centerX - 5, centerY - 65);
      ctx.stroke();

      // Smile (animated when speaking)
      const smileIntensity = isSpeaking ? 1 + Math.sin(time * 8) * 0.3 : 1;
      ctx.strokeStyle = '#c97064';
      ctx.lineWidth = 3;
      ctx.beginPath();
      ctx.arc(centerX, centerY - 50, 20 * smileIntensity, 0.2, Math.PI - 0.2);
      ctx.stroke();

      // Neck
      ctx.fillStyle = '#fdbcb4';
      ctx.fillRect(centerX - 20, centerY - 20, 40, 30);

      // Collar (white shirt)
      ctx.fillStyle = '#ffffff';
      ctx.beginPath();
      ctx.moveTo(centerX - 35, centerY + 10);
      ctx.lineTo(centerX - 25, centerY + 30);
      ctx.lineTo(centerX + 25, centerY + 30);
      ctx.lineTo(centerX + 35, centerY + 10);
      ctx.closePath();
      ctx.fill();

      // Blazer (navy)
      ctx.fillStyle = '#1e3a5f';
      ctx.beginPath();
      ctx.moveTo(centerX - 50, centerY + 20);
      ctx.lineTo(centerX - 60, centerY + 150);
      ctx.lineTo(centerX + 60, centerY + 150);
      ctx.lineTo(centerX + 50, centerY + 20);
      ctx.closePath();
      ctx.fill();

      // Blazer lapels
      ctx.fillStyle = '#152a45';
      ctx.beginPath();
      ctx.moveTo(centerX - 50, centerY + 20);
      ctx.lineTo(centerX - 20, centerY + 60);
      ctx.lineTo(centerX - 30, centerY + 20);
      ctx.closePath();
      ctx.fill();
      ctx.beginPath();
      ctx.moveTo(centerX + 50, centerY + 20);
      ctx.lineTo(centerX + 20, centerY + 60);
      ctx.lineTo(centerX + 30, centerY + 20);
      ctx.closePath();
      ctx.fill();

      // Buttons
      ctx.fillStyle = '#333333';
      for (let i = 0; i < 3; i++) {
        ctx.beginPath();
        ctx.arc(centerX, centerY + 50 + i * 25, 4, 0, Math.PI * 2);
        ctx.fill();
      }

      // Glasses
      ctx.strokeStyle = '#1a1a1a';
      ctx.lineWidth = 3;
      ctx.beginPath();
      ctx.arc(centerX - 20, centerY - 85, 15, 0, Math.PI * 2);
      ctx.stroke();
      ctx.beginPath();
      ctx.arc(centerX + 20, centerY - 85, 15, 0, Math.PI * 2);
      ctx.stroke();
      // Bridge
      ctx.beginPath();
      ctx.moveTo(centerX - 5, centerY - 85);
      ctx.lineTo(centerX + 5, centerY - 85);
      ctx.stroke();

      // Glow effect when speaking
      if (isSpeaking) {
        const glowIntensity = 0.3 + (volumeLevel / 200);
        ctx.shadowBlur = 20 + volumeLevel / 5;
        ctx.shadowColor = `rgba(168, 85, 247, ${glowIntensity})`;
        ctx.strokeStyle = `rgba(168, 85, 247, ${glowIntensity})`;
        ctx.lineWidth = 2;
        ctx.strokeRect(10, 10, canvas.width - 20, canvas.height - 20);
        ctx.shadowBlur = 0;
      }

      animationRef.current = requestAnimationFrame(animate);
    };

    animate();

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [isSpeaking, isListening, volumeLevel]);

  return (
    <div className="relative w-full h-full">
      <canvas
        ref={canvasRef}
        className="w-full h-full rounded-lg bg-gradient-to-br from-purple-50 to-purple-100"
        style={{ minHeight: '400px' }}
      />

      {/* Status indicator */}
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

      {/* Ambient pulse when active */}
      {isActive && (
        <div className="absolute inset-0 rounded-lg bg-purple-400 animate-ping opacity-5 pointer-events-none"></div>
      )}
    </div>
  );
}
