'use client';

/**
 * Framer Motion Animated Avatar - SMOOTH & PROFESSIONAL
 * 🏆 Breaking Barriers UK 2026 compliant
 * Uses Framer Motion for buttery smooth animations
 */

import { motion } from 'framer-motion';
import { useEffect, useState } from 'react';

interface FramerAvatarProps {
  isActive: boolean;
  isSpeaking: boolean;
  isListening: boolean;
  volumeLevel: number;
}

export function FramerAvatar({
  isActive,
  isSpeaking,
  isListening,
  volumeLevel
}: FramerAvatarProps) {
  const [blinkState, setBlinkState] = useState(false);
  const [mouthOpen, setMouthOpen] = useState(0);

  // Random blinking
  useEffect(() => {
    const blinkInterval = setInterval(() => {
      setBlinkState(true);
      setTimeout(() => setBlinkState(false), 150);
    }, 3000 + Math.random() * 2000);

    return () => clearInterval(blinkInterval);
  }, []);

  // Mouth animation when speaking
  useEffect(() => {
    if (isSpeaking) {
      const mouthInterval = setInterval(() => {
        setMouthOpen(Math.random() * 0.8 + 0.2);
      }, 150);
      return () => clearInterval(mouthInterval);
    } else {
      setMouthOpen(0);
    }
  }, [isSpeaking]);

  return (
    <div className="relative w-full h-full flex items-center justify-center bg-gradient-to-br from-purple-50 via-blue-50 to-indigo-50 rounded-lg overflow-hidden">
      {/* Animated background particles */}
      <motion.div
        className="absolute inset-0"
        animate={{
          background: isSpeaking 
            ? ['radial-gradient(circle at 50% 50%, rgba(168, 85, 247, 0.1) 0%, transparent 50%)',
               'radial-gradient(circle at 60% 40%, rgba(168, 85, 247, 0.15) 0%, transparent 50%)',
               'radial-gradient(circle at 40% 60%, rgba(168, 85, 247, 0.1) 0%, transparent 50%)']
            : 'radial-gradient(circle at 50% 50%, rgba(168, 85, 247, 0.05) 0%, transparent 50%)'
        }}
        transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
      />

      {/* Avatar Container */}
      <motion.div
        className="relative z-10"
        animate={{
          scale: isSpeaking ? [1, 1.03, 1] : isListening ? [1, 1.01, 1] : 1,
          y: isSpeaking ? [0, -3, 0] : isListening ? [0, -2, 0] : [0, -1, 0],
        }}
        transition={{
          duration: isSpeaking ? 0.5 : isListening ? 1.5 : 3,
          repeat: Infinity,
          ease: 'easeInOut'
        }}
      >
        {/* Professional Avatar */}
        <div className="relative w-64 h-64">
          {/* Head */}
          <motion.div
            className="absolute inset-0 rounded-full bg-gradient-to-br from-amber-50 to-amber-100 shadow-2xl border-4 border-white"
            animate={{
              rotate: isSpeaking ? [-2, 2, -2] : isListening ? [-1, 1, -1] : 0,
            }}
            transition={{
              duration: isSpeaking ? 0.8 : 2,
              repeat: Infinity,
              ease: 'easeInOut'
            }}
          >
            {/* Professional hairstyle */}
            <div className="absolute -top-6 left-1/2 transform -translate-x-1/2 w-52 h-40 rounded-t-full bg-gradient-to-b from-gray-800 to-gray-700 shadow-lg" />
            <div className="absolute top-2 left-1/2 transform -translate-x-1/2 w-48 h-10 rounded-t-full bg-gradient-to-b from-gray-800 to-gray-700" />
            
            {/* Eyebrows */}
            <motion.div
              className="absolute top-18 left-11 w-14 h-2 rounded-full bg-gray-700"
              animate={{
                scaleY: isSpeaking ? [1, 1.2, 1] : 1,
                y: isSpeaking ? [0, -1, 0] : 0,
              }}
              transition={{ duration: 0.5, repeat: Infinity }}
            />
            <motion.div
              className="absolute top-18 right-11 w-14 h-2 rounded-full bg-gray-700"
              animate={{
                scaleY: isSpeaking ? [1, 1.2, 1] : 1,
                y: isSpeaking ? [0, -1, 0] : 0,
              }}
              transition={{ duration: 0.5, repeat: Infinity }}
            />
            
            {/* Eyes */}
            <div className="absolute top-22 left-11 flex space-x-20">
              {/* Left eye */}
              <div className="relative">
                <div className="w-11 h-11 rounded-full bg-white shadow-inner border border-gray-200">
                  <motion.div
                    className="absolute top-2 left-2 w-7 h-7 rounded-full bg-gradient-to-br from-blue-500 to-blue-700"
                    animate={{
                      x: isSpeaking ? [-1, 1, -1] : 0,
                      y: isSpeaking ? [-0.5, 0.5, -0.5] : 0,
                    }}
                    transition={{ duration: 0.8, repeat: Infinity }}
                  >
                    <div className="absolute top-1 left-1 w-3 h-3 rounded-full bg-white opacity-90" />
                    <div className="absolute bottom-1 right-1 w-2 h-2 rounded-full bg-white opacity-50" />
                  </motion.div>
                </div>
                {/* Eyelid for blinking */}
                <motion.div
                  className="absolute inset-0 w-11 h-6 rounded-t-full bg-amber-100 border-t border-gray-200"
                  initial={{ scaleY: 0, originY: 0 }}
                  animate={{ scaleY: blinkState ? 1 : 0 }}
                  transition={{ duration: 0.1 }}
                />
              </div>
              
              {/* Right eye */}
              <div className="relative">
                <div className="w-11 h-11 rounded-full bg-white shadow-inner border border-gray-200">
                  <motion.div
                    className="absolute top-2 left-2 w-7 h-7 rounded-full bg-gradient-to-br from-blue-500 to-blue-700"
                    animate={{
                      x: isSpeaking ? [-1, 1, -1] : 0,
                      y: isSpeaking ? [-0.5, 0.5, -0.5] : 0,
                    }}
                    transition={{ duration: 0.8, repeat: Infinity }}
                  >
                    <div className="absolute top-1 left-1 w-3 h-3 rounded-full bg-white opacity-90" />
                    <div className="absolute bottom-1 right-1 w-2 h-2 rounded-full bg-white opacity-50" />
                  </motion.div>
                </div>
                {/* Eyelid for blinking */}
                <motion.div
                  className="absolute inset-0 w-11 h-6 rounded-t-full bg-amber-100 border-t border-gray-200"
                  initial={{ scaleY: 0, originY: 0 }}
                  animate={{ scaleY: blinkState ? 1 : 0 }}
                  transition={{ duration: 0.1 }}
                />
              </div>
            </div>
            
            {/* Nose */}
            <div className="absolute top-32 left-1/2 transform -translate-x-1/2">
              <div className="w-6 h-9 bg-gradient-to-b from-amber-200 to-amber-300 rounded-b-lg shadow-md" />
              <div className="absolute bottom-0 left-0 w-2.5 h-2.5 rounded-full bg-amber-300" />
              <div className="absolute bottom-0 right-0 w-2.5 h-2.5 rounded-full bg-amber-300" />
            </div>
            
            {/* Mouth - SMOOTH ANIMATION! */}
            <div className="absolute top-40 left-1/2 transform -translate-x-1/2">
              {isSpeaking ? (
                // Talking mouth with smooth animation
                <motion.div
                  className="relative"
                  animate={{
                    scaleY: [1, 1 + mouthOpen, 1],
                  }}
                  transition={{ duration: 0.15 }}
                >
                  <div className="w-16 h-11 rounded-full bg-gradient-to-b from-red-300 to-red-400 shadow-inner border-2 border-red-500" />
                  {/* Teeth */}
                  <div className="absolute top-2 left-1/2 transform -translate-x-1/2 w-11 h-2 bg-white rounded-sm shadow-sm" />
                  {/* Tongue */}
                  <motion.div
                    className="absolute bottom-2 left-1/2 transform -translate-x-1/2 w-9 h-3 bg-red-400 rounded-full"
                    animate={{ scaleY: [1, 0.8, 1] }}
                    transition={{ duration: 0.3, repeat: Infinity }}
                  />
                </motion.div>
              ) : (
                // Professional smile
                <div className="relative">
                  <div className="w-18 h-3 border-b-3 border-gray-700 rounded-b-full" />
                  <div className="absolute -top-1 left-3 w-3 h-2 bg-red-300 rounded-full opacity-60" />
                  <div className="absolute -top-1 right-3 w-3 h-2 bg-red-300 rounded-full opacity-60" />
                </div>
              )}
            </div>
            
            {/* Cheeks with subtle animation */}
            <motion.div
              className="absolute top-32 left-5 w-9 h-9 rounded-full bg-pink-200 opacity-30 blur-sm"
              animate={{ opacity: isSpeaking ? [0.3, 0.5, 0.3] : 0.3 }}
              transition={{ duration: 0.8, repeat: Infinity }}
            />
            <motion.div
              className="absolute top-32 right-5 w-9 h-9 rounded-full bg-pink-200 opacity-30 blur-sm"
              animate={{ opacity: isSpeaking ? [0.3, 0.5, 0.3] : 0.3 }}
              transition={{ duration: 0.8, repeat: Infinity }}
            />
            
            {/* Ears */}
            <div className="absolute top-24 -left-2 w-7 h-11 rounded-full bg-gradient-to-r from-amber-200 to-amber-100 shadow-md" />
            <div className="absolute top-24 -right-2 w-7 h-11 rounded-full bg-gradient-to-l from-amber-200 to-amber-100 shadow-md" />
          </motion.div>
        </div>
        
        {/* Neck */}
        <div className="w-28 h-16 mx-auto bg-gradient-to-b from-amber-100 to-amber-200 shadow-md" style={{ clipPath: 'polygon(30% 0%, 70% 0%, 100% 100%, 0% 100%)' }} />
        
        {/* Professional attire */}
        <div className="relative w-72 h-52 mx-auto -mt-4">
          {/* Blazer */}
          <div className="absolute inset-0 bg-gradient-to-b from-indigo-700 to-indigo-800 rounded-t-3xl shadow-2xl">
            {/* White shirt collar */}
            <div className="absolute top-0 left-1/2 transform -translate-x-1/2 w-32 h-12 bg-white rounded-t-lg shadow-inner" />
            {/* Tie */}
            <div className="absolute top-10 left-1/2 transform -translate-x-1/2 w-7 h-24 bg-gradient-to-b from-purple-600 to-purple-700 shadow-lg" style={{ clipPath: 'polygon(50% 0%, 0% 15%, 20% 100%, 80% 100%, 100% 15%)' }} />
            
            {/* Lapels */}
            <div className="absolute top-10 left-10 w-18 h-36 bg-gradient-to-br from-indigo-800 to-indigo-900 transform -rotate-12 rounded-tl-3xl" />
            <div className="absolute top-10 right-10 w-18 h-36 bg-gradient-to-bl from-indigo-800 to-indigo-900 transform rotate-12 rounded-tr-3xl" />
            
            {/* Buttons */}
            <div className="absolute top-20 left-1/2 transform -translate-x-1/2 space-y-5">
              <div className="w-3.5 h-3.5 rounded-full bg-gray-300 shadow-md" />
              <div className="w-3.5 h-3.5 rounded-full bg-gray-300 shadow-md" />
            </div>
          </div>
          
          {/* Arms with smooth animation */}
          <motion.div
            className="absolute -left-16 top-14 w-16 h-40 bg-gradient-to-b from-indigo-700 to-indigo-800 rounded-full shadow-xl"
            style={{ transformOrigin: 'top center' }}
            animate={{
              rotate: isSpeaking ? [-3, -12, -3] : [-3, -5, -3],
            }}
            transition={{
              duration: isSpeaking ? 0.6 : 2,
              repeat: Infinity,
              ease: 'easeInOut'
            }}
          >
            <div className="absolute -bottom-2 left-1/2 transform -translate-x-1/2 w-11 h-11 rounded-full bg-gradient-to-br from-amber-100 to-amber-200 shadow-lg" />
          </motion.div>
          
          <motion.div
            className="absolute -right-16 top-14 w-16 h-40 bg-gradient-to-b from-indigo-700 to-indigo-800 rounded-full shadow-xl"
            style={{ transformOrigin: 'top center' }}
            animate={{
              rotate: isSpeaking ? [3, 12, 3] : [3, 5, 3],
            }}
            transition={{
              duration: isSpeaking ? 0.6 : 2,
              repeat: Infinity,
              ease: 'easeInOut'
            }}
          >
            <div className="absolute -bottom-2 left-1/2 transform -translate-x-1/2 w-11 h-11 rounded-full bg-gradient-to-br from-amber-100 to-amber-200 shadow-lg" />
          </motion.div>
        </div>
      </motion.div>

      {/* Status indicator */}
      <motion.div
        className="absolute bottom-6 left-1/2 transform -translate-x-1/2 z-20"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div className="bg-white backdrop-blur-sm rounded-full px-5 py-2.5 shadow-2xl border-2 border-purple-200">
          <div className="flex items-center space-x-2">
            <motion.div
              className={`w-3 h-3 rounded-full ${
                isSpeaking ? 'bg-green-500' : isListening ? 'bg-blue-500' : 'bg-purple-400'
              }`}
              animate={{
                scale: isSpeaking || isListening ? [1, 1.3, 1] : 1,
              }}
              transition={{ duration: 0.8, repeat: Infinity }}
            />
            <span className="text-sm font-medium text-gray-700">
              {isSpeaking ? 'Speaking' : isListening ? 'Listening' : 'Ready'}
            </span>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
