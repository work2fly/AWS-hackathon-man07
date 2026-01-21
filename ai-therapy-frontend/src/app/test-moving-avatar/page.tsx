'use client';

/**
 * TEST PAGE - Moving Mouth Avatar
 * Isolated testing environment - SAFE!
 * 🏆 Breaking Barriers UK 2026 compliant
 */

import { useState } from 'react';
import { BabylonAvatar } from '@/components/client/BabylonAvatarTest';

export default function TestMovingAvatarPage() {
  const [isActive, setIsActive] = useState(true);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [volumeLevel, setVolumeLevel] = useState(50);

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50 p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-purple-900 mb-2">
            🧪 Moving Mouth Avatar - TEST PAGE
          </h1>
          <p className="text-gray-600">
            Isolated testing environment - Safe to experiment!
          </p>
          <div className="mt-2 inline-block bg-green-100 text-green-800 px-4 py-2 rounded-full text-sm font-medium">
            ✅ This won't affect production code
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Avatar Display */}
          <div className="bg-white rounded-xl shadow-2xl p-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              3D Avatar Preview
            </h2>
            
            {/* Avatar Container */}
            <div className="relative w-full h-[500px] bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg overflow-hidden">
              <BabylonAvatar
                isActive={isActive}
                isSpeaking={isSpeaking}
                isListening={isListening}
                volumeLevel={volumeLevel}
                modelUrl="https://models.readyplayer.me/692c94887b7a88e1f63f3d82.glb?pose=A&morphTargets=ARKit"
              />
            </div>

            {/* Status Display */}
            <div className="mt-4 p-4 bg-gray-50 rounded-lg">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="font-semibold">Active:</span>
                  <span className={`ml-2 ${isActive ? 'text-green-600' : 'text-gray-400'}`}>
                    {isActive ? '✅ Yes' : '❌ No'}
                  </span>
                </div>
                <div>
                  <span className="font-semibold">Speaking:</span>
                  <span className={`ml-2 ${isSpeaking ? 'text-green-600' : 'text-gray-400'}`}>
                    {isSpeaking ? '🗣️ Yes' : '❌ No'}
                  </span>
                </div>
                <div>
                  <span className="font-semibold">Listening:</span>
                  <span className={`ml-2 ${isListening ? 'text-blue-600' : 'text-gray-400'}`}>
                    {isListening ? '👂 Yes' : '❌ No'}
                  </span>
                </div>
                <div>
                  <span className="font-semibold">Volume:</span>
                  <span className="ml-2 text-purple-600 font-bold">
                    {volumeLevel}%
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Controls Panel */}
          <div className="space-y-6">
            {/* State Controls */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h3 className="text-xl font-bold text-gray-900 mb-4">
                🎮 Avatar Controls
              </h3>

              {/* Active Toggle */}
              <div className="mb-6">
                <label className="flex items-center justify-between cursor-pointer">
                  <span className="text-gray-700 font-medium">Active State</span>
                  <button
                    onClick={() => setIsActive(!isActive)}
                    className={`relative inline-flex h-8 w-14 items-center rounded-full transition-colors ${
                      isActive ? 'bg-green-500' : 'bg-gray-300'
                    }`}
                  >
                    <span
                      className={`inline-block h-6 w-6 transform rounded-full bg-white transition-transform ${
                        isActive ? 'translate-x-7' : 'translate-x-1'
                      }`}
                    />
                  </button>
                </label>
              </div>

              {/* Speaking Toggle */}
              <div className="mb-6">
                <label className="flex items-center justify-between cursor-pointer">
                  <span className="text-gray-700 font-medium">Speaking</span>
                  <button
                    onClick={() => {
                      setIsSpeaking(!isSpeaking);
                      if (!isSpeaking) setIsListening(false);
                    }}
                    className={`relative inline-flex h-8 w-14 items-center rounded-full transition-colors ${
                      isSpeaking ? 'bg-green-500' : 'bg-gray-300'
                    }`}
                  >
                    <span
                      className={`inline-block h-6 w-6 transform rounded-full bg-white transition-transform ${
                        isSpeaking ? 'translate-x-7' : 'translate-x-1'
                      }`}
                    />
                  </button>
                </label>
                <p className="text-xs text-gray-500 mt-1">
                  Watch the mouth move and head gestures!
                </p>
              </div>

              {/* Listening Toggle */}
              <div className="mb-6">
                <label className="flex items-center justify-between cursor-pointer">
                  <span className="text-gray-700 font-medium">Listening</span>
                  <button
                    onClick={() => {
                      setIsListening(!isListening);
                      if (!isListening) setIsSpeaking(false);
                    }}
                    className={`relative inline-flex h-8 w-14 items-center rounded-full transition-colors ${
                      isListening ? 'bg-blue-500' : 'bg-gray-300'
                    }`}
                  >
                    <span
                      className={`inline-block h-6 w-6 transform rounded-full bg-white transition-transform ${
                        isListening ? 'translate-x-7' : 'translate-x-1'
                      }`}
                    />
                  </button>
                </label>
                <p className="text-xs text-gray-500 mt-1">
                  Watch the gentle nodding!
                </p>
              </div>

              {/* Volume Slider */}
              <div className="mb-6">
                <label className="block text-gray-700 font-medium mb-2">
                  Volume Level: {volumeLevel}%
                </label>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={volumeLevel}
                  onChange={(e) => setVolumeLevel(Number(e.target.value))}
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-purple-600"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Higher volume = more intense animations
                </p>
              </div>
            </div>

            {/* Quick Test Scenarios */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h3 className="text-xl font-bold text-gray-900 mb-4">
                ⚡ Quick Test Scenarios
              </h3>

              <div className="space-y-3">
                <button
                  onClick={() => {
                    setIsActive(true);
                    setIsSpeaking(true);
                    setIsListening(false);
                    setVolumeLevel(80);
                  }}
                  className="w-full px-4 py-3 bg-green-500 hover:bg-green-600 text-white rounded-lg font-medium transition"
                >
                  🗣️ Speaking (High Volume)
                </button>

                <button
                  onClick={() => {
                    setIsActive(true);
                    setIsSpeaking(true);
                    setIsListening(false);
                    setVolumeLevel(30);
                  }}
                  className="w-full px-4 py-3 bg-green-400 hover:bg-green-500 text-white rounded-lg font-medium transition"
                >
                  🗣️ Speaking (Low Volume)
                </button>

                <button
                  onClick={() => {
                    setIsActive(true);
                    setIsSpeaking(false);
                    setIsListening(true);
                    setVolumeLevel(0);
                  }}
                  className="w-full px-4 py-3 bg-blue-500 hover:bg-blue-600 text-white rounded-lg font-medium transition"
                >
                  👂 Listening
                </button>

                <button
                  onClick={() => {
                    setIsActive(true);
                    setIsSpeaking(false);
                    setIsListening(false);
                    setVolumeLevel(0);
                  }}
                  className="w-full px-4 py-3 bg-purple-500 hover:bg-purple-600 text-white rounded-lg font-medium transition"
                >
                  😌 Idle (Breathing)
                </button>

                <button
                  onClick={() => {
                    setIsActive(false);
                    setIsSpeaking(false);
                    setIsListening(false);
                    setVolumeLevel(0);
                  }}
                  className="w-full px-4 py-3 bg-gray-400 hover:bg-gray-500 text-white rounded-lg font-medium transition"
                >
                  ⏸️ Inactive
                </button>
              </div>
            </div>

            {/* What to Look For */}
            <div className="bg-gradient-to-r from-yellow-50 to-orange-50 border-2 border-yellow-200 rounded-xl p-6">
              <h3 className="text-lg font-bold text-yellow-900 mb-3">
                👀 What to Look For:
              </h3>
              <ul className="space-y-2 text-sm text-yellow-800">
                <li className="flex items-start">
                  <span className="mr-2">✅</span>
                  <span><strong>Speaking:</strong> Mouth opens/closes (smile scales), head moves, hands gesture</span>
                </li>
                <li className="flex items-start">
                  <span className="mr-2">✅</span>
                  <span><strong>Listening:</strong> Gentle head nod, occasional blinks, attentive posture</span>
                </li>
                <li className="flex items-start">
                  <span className="mr-2">✅</span>
                  <span><strong>Idle:</strong> Breathing animation (body scales), subtle movements</span>
                </li>
                <li className="flex items-start">
                  <span className="mr-2">✅</span>
                  <span><strong>Volume:</strong> Higher volume = more intense movements</span>
                </li>
              </ul>
            </div>

            {/* Navigation */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h3 className="text-lg font-bold text-gray-900 mb-3">
                🔗 Navigation
              </h3>
              <div className="space-y-2">
                <a
                  href="/"
                  className="block w-full px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg text-center font-medium transition"
                >
                  ← Back to Main App
                </a>
                <a
                  href="/voice-real"
                  className="block w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-center font-medium transition"
                >
                  Test Voice Page →
                </a>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-8 text-center text-sm text-gray-500">
          <p>🏆 Breaking Barriers UK 2026 - Safe Testing Environment</p>
          <p className="mt-1">This page is isolated and won't affect your production code</p>
        </div>
      </div>
    </div>
  );
}
