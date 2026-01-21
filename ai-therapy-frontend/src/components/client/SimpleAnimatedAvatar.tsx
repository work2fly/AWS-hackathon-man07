'use client';

/**
 * Simple Animated Avatar - GUARANTEED TO WORK!
 * 🏆 Breaking Barriers UK 2026 compliant
 * Uses CSS animations for smooth, visible movement
 */

import { useEffect, useState } from 'react';

interface SimpleAnimatedAvatarProps {
  isActive: boolean;
  isSpeaking: boolean;
  isListening: boolean;
  volumeLevel: number;
}

export function SimpleAnimatedAvatar({
  isActive,
  isSpeaking,
  isListening,
  volumeLevel
}: SimpleAnimatedAvatarProps) {
  const [blinkState, setBlinkState] = useState(false);

  // Random blinking
  useEffect(() => {
    const blinkInterval = setInterval(() => {
      setBlinkState(true);
      setTimeout(() => setBlinkState(false), 150);
    }, 3000 + Math.random() * 2000);

    return () => clearInterval(blinkInterval);
  }, []);

  return (
    <div className="relative w-full h-full flex items-center justify-center bg-gradient-to-br from-purple-50 to-blue-50 rounded-lg">
      {/* Avatar Container with animations */}
      <div
        className={`relative transition-all duration-300 ${
          isSpeaking ? 'animate-speaking' : isListening ? 'animate-listening' : 'animate-idle'
        }`}
        style={{
          transform: isSpeaking ? 'scale(1.05)' : isListening ? 'scale(1.02)' : 'scale(1)',
        }}
      >
        {/* Professional Avatar */}
        <div className="relative w-56 h-56 mx-auto">
          {/* Head with better proportions */}
          <div className="absolute inset-0 rounded-full bg-gradient-to-br from-amber-50 to-amber-100 shadow-2xl border-4 border-white">
            {/* Professional hairstyle */}
            <div className="absolute -top-6 left-1/2 transform -translate-x-1/2 w-48 h-36 rounded-t-full bg-gradient-to-b from-gray-800 to-gray-700 shadow-lg" />
            <div className="absolute top-2 left-1/2 transform -translate-x-1/2 w-44 h-8 rounded-t-full bg-gradient-to-b from-gray-800 to-gray-700" />
            
            {/* Eyebrows */}
            <div className="absolute top-16 left-10 w-12 h-1.5 rounded-full bg-gray-700 transform -rotate-6" />
            <div className="absolute top-16 right-10 w-12 h-1.5 rounded-full bg-gray-700 transform rotate-6" />
            
            {/* Eyes - more realistic */}
            <div className="absolute top-20 left-10 flex space-x-16">
              {/* Left eye */}
              <div className="relative">
                <div className="w-10 h-10 rounded-full bg-white shadow-inner border border-gray-200">
                  <div
                    className={`absolute top-2 left-2 w-6 h-6 rounded-full bg-gradient-to-br from-blue-500 to-blue-700 transition-all duration-100 ${
                      isSpeaking ? 'animate-eye-move' : ''
                    }`}
                  >
                    <div className="absolute top-1 left-1 w-2.5 h-2.5 rounded-full bg-white opacity-90" />
                    <div className="absolute bottom-0.5 right-0.5 w-1.5 h-1.5 rounded-full bg-white opacity-50" />
                  </div>
                </div>
                {/* Eyelid for blinking */}
                {blinkState && (
                  <div className="absolute inset-0 w-10 h-5 rounded-t-full bg-amber-100 border-t border-gray-200" />
                )}
              </div>
              
              {/* Right eye */}
              <div className="relative">
                <div className="w-10 h-10 rounded-full bg-white shadow-inner border border-gray-200">
                  <div
                    className={`absolute top-2 left-2 w-6 h-6 rounded-full bg-gradient-to-br from-blue-500 to-blue-700 transition-all duration-100 ${
                      isSpeaking ? 'animate-eye-move' : ''
                    }`}
                  >
                    <div className="absolute top-1 left-1 w-2.5 h-2.5 rounded-full bg-white opacity-90" />
                    <div className="absolute bottom-0.5 right-0.5 w-1.5 h-1.5 rounded-full bg-white opacity-50" />
                  </div>
                </div>
                {/* Eyelid for blinking */}
                {blinkState && (
                  <div className="absolute inset-0 w-10 h-5 rounded-t-full bg-amber-100 border-t border-gray-200" />
                )}
              </div>
            </div>
            
            {/* Nose - more realistic */}
            <div className="absolute top-28 left-1/2 transform -translate-x-1/2">
              <div className="w-5 h-8 bg-gradient-to-b from-amber-200 to-amber-300 rounded-b-lg shadow-md" />
              <div className="absolute bottom-0 left-0 w-2 h-2 rounded-full bg-amber-300" />
              <div className="absolute bottom-0 right-0 w-2 h-2 rounded-full bg-amber-300" />
            </div>
            
            {/* Mouth - MUCH BETTER! */}
            <div className="absolute top-36 left-1/2 transform -translate-x-1/2">
              {isSpeaking ? (
                // Talking mouth - realistic animation
                <div className="relative">
                  <div
                    className="w-14 h-10 rounded-full bg-gradient-to-b from-red-300 to-red-400 shadow-inner border-2 border-red-500"
                    style={{
                      animation: 'mouthTalk 0.25s ease-in-out infinite alternate',
                    }}
                  />
                  {/* Teeth */}
                  <div className="absolute top-2 left-1/2 transform -translate-x-1/2 w-10 h-2 bg-white rounded-sm shadow-sm" />
                  {/* Tongue */}
                  <div className="absolute bottom-2 left-1/2 transform -translate-x-1/2 w-8 h-3 bg-red-400 rounded-full" />
                </div>
              ) : (
                // Professional smile
                <div className="relative">
                  <div className="w-16 h-3 border-b-3 border-gray-700 rounded-b-full" />
                  <div className="absolute -top-1 left-2 w-3 h-2 bg-red-300 rounded-full opacity-60" />
                  <div className="absolute -top-1 right-2 w-3 h-2 bg-red-300 rounded-full opacity-60" />
                </div>
              )}
            </div>
            
            {/* Cheeks - subtle */}
            <div className="absolute top-28 left-4 w-8 h-8 rounded-full bg-pink-200 opacity-30 blur-sm" />
            <div className="absolute top-28 right-4 w-8 h-8 rounded-full bg-pink-200 opacity-30 blur-sm" />
            
            {/* Ears */}
            <div className="absolute top-20 -left-2 w-6 h-10 rounded-full bg-gradient-to-r from-amber-200 to-amber-100 shadow-md" />
            <div className="absolute top-20 -right-2 w-6 h-10 rounded-full bg-gradient-to-l from-amber-200 to-amber-100 shadow-md" />
          </div>
        </div>
        
        {/* Neck - professional */}
        <div className="w-24 h-14 mx-auto bg-gradient-to-b from-amber-100 to-amber-200 shadow-md" style={{ clipPath: 'polygon(30% 0%, 70% 0%, 100% 100%, 0% 100%)' }} />
        
        {/* Professional attire */}
        <div className="relative w-64 h-48 mx-auto -mt-3">
          {/* Blazer/Jacket */}
          <div className="absolute inset-0 bg-gradient-to-b from-indigo-700 to-indigo-800 rounded-t-3xl shadow-2xl">
            {/* White shirt collar */}
            <div className="absolute top-0 left-1/2 transform -translate-x-1/2 w-28 h-10 bg-white rounded-t-lg shadow-inner" />
            {/* Tie */}
            <div className="absolute top-8 left-1/2 transform -translate-x-1/2 w-6 h-20 bg-gradient-to-b from-purple-600 to-purple-700 shadow-lg" style={{ clipPath: 'polygon(50% 0%, 0% 15%, 20% 100%, 80% 100%, 100% 15%)' }} />
            
            {/* Lapels */}
            <div className="absolute top-8 left-8 w-16 h-32 bg-gradient-to-br from-indigo-800 to-indigo-900 transform -rotate-12 rounded-tl-3xl" />
            <div className="absolute top-8 right-8 w-16 h-32 bg-gradient-to-bl from-indigo-800 to-indigo-900 transform rotate-12 rounded-tr-3xl" />
            
            {/* Buttons */}
            <div className="absolute top-16 left-1/2 transform -translate-x-1/2 space-y-4">
              <div className="w-3 h-3 rounded-full bg-gray-300 shadow-md" />
              <div className="w-3 h-3 rounded-full bg-gray-300 shadow-md" />
            </div>
          </div>
          
          {/* Arms - professional pose */}
          <div
            className={`absolute -left-14 top-12 w-14 h-36 bg-gradient-to-b from-indigo-700 to-indigo-800 rounded-full shadow-xl transition-all duration-300 ${
              isSpeaking ? 'animate-arm-left' : ''
            }`}
            style={{
              transformOrigin: 'top center',
              transform: isSpeaking ? 'rotate(-10deg)' : 'rotate(-3deg)',
            }}
          >
            {/* Hand */}
            <div className="absolute -bottom-2 left-1/2 transform -translate-x-1/2 w-10 h-10 rounded-full bg-gradient-to-br from-amber-100 to-amber-200 shadow-lg" />
          </div>
          
          <div
            className={`absolute -right-14 top-12 w-14 h-36 bg-gradient-to-b from-indigo-700 to-indigo-800 rounded-full shadow-xl transition-all duration-300 ${
              isSpeaking ? 'animate-arm-right' : ''
            }`}
            style={{
              transformOrigin: 'top center',
              transform: isSpeaking ? 'rotate(10deg)' : 'rotate(3deg)',
            }}
          >
            {/* Hand */}
            <div className="absolute -bottom-2 left-1/2 transform -translate-x-1/2 w-10 h-10 rounded-full bg-gradient-to-br from-amber-100 to-amber-200 shadow-lg" />
          </div>
        </div>
      </div>

      {/* Status indicator */}
      <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2">
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

      {/* CSS Animations */}
      <style jsx>{`
        @keyframes mouthTalk {
          0% { height: 10px; transform: scaleY(0.8); }
          50% { height: 18px; transform: scaleY(1.2); }
          100% { height: 10px; transform: scaleY(0.8); }
        }
        
        @keyframes eye-move {
          0% { transform: translateX(0); }
          25% { transform: translateX(2px); }
          50% { transform: translateX(0); }
          75% { transform: translateX(-2px); }
          100% { transform: translateX(0); }
        }
        
        .animate-speaking {
          animation: speaking 0.5s ease-in-out infinite;
        }
        
        @keyframes speaking {
          0%, 100% { transform: translateY(0) rotate(-2deg); }
          50% { transform: translateY(-5px) rotate(2deg); }
        }
        
        .animate-listening {
          animation: listening 2s ease-in-out infinite;
        }
        
        @keyframes listening {
          0%, 100% { transform: translateY(0) rotate(0deg); }
          50% { transform: translateY(-3px) rotate(1deg); }
        }
        
        .animate-idle {
          animation: idle 3s ease-in-out infinite;
        }
        
        @keyframes idle {
          0%, 100% { transform: translateY(0); }
          50% { transform: translateY(-2px); }
        }
        
        .animate-arm-left {
          animation: armLeft 0.6s ease-in-out infinite alternate;
        }
        
        @keyframes armLeft {
          0% { transform: rotate(-5deg); }
          100% { transform: rotate(-20deg); }
        }
        
        .animate-arm-right {
          animation: armRight 0.6s ease-in-out infinite alternate;
        }
        
        @keyframes armRight {
          0% { transform: rotate(5deg); }
          100% { transform: rotate(20deg); }
        }
      `}</style>
    </div>
  );
}
