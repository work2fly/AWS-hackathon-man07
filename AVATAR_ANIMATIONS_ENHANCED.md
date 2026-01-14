# Enhanced Avatar Animations 🎭

🏆 **Breaking Barriers UK 2026 compliant**

## Overview

The 3D avatar now features significantly enhanced animations that make it more lifelike, expressive, and engaging during therapy sessions.

## Animation Features

### 🗣️ Speaking Animations (When AI is Talking)

**Head Movements:**
- Dynamic nodding and tilting based on volume level
- Multi-layered head rotations for natural speech patterns
- Minimum 30% animation intensity even at low volumes
- Head sway increases with volume (more expressive when louder)

**Jaw Movement:**
- Automatic jaw animation for Ready Player Me models
- Synchronized with speech speed (8-12 Hz based on volume)
- Simulates realistic talking motion

**Body Language:**
- Subtle body sway while speaking (shows confidence)
- Torso rotation for emphasis
- Natural weight shifting

**Hand Gestures:**
- Occasional hand movements every 2-3 seconds
- Smooth gesture animations (1.5 second duration)
- Arm and shoulder movements for expressiveness
- Random timing for natural feel

### 👂 Listening Animations (When User is Speaking)

**Attentive Posture:**
- Gentle head tilting (showing interest)
- Occasional nods (showing understanding)
- Slight forward lean (engaged posture)

**Head Movements:**
- Slower, more deliberate movements
- Multi-axis rotation for natural attention
- Periodic nods to show engagement

**Body Language:**
- Minimal body movement (focused attention)
- Slight forward lean
- Stable, grounded posture

### 😌 Idle Animations (Waiting State)

**Calm Presence:**
- Very subtle head movements
- Minimal body sway
- Occasional weight shifts
- Breathing animation

**Natural Behavior:**
- Random micro-movements
- Periodic posture adjustments
- Maintains welcoming presence

### 👁️ Universal Animations (All States)

**Blinking:**
- Automatic blinking every 3-5 seconds
- Smooth eyelid animation (0.15 second duration)
- Variable timing for natural feel
- Eye scaling simulation

**Eye Tracking:**
- Subtle eye movements
- Occasional looking around
- Maintains engagement without staring

**Breathing:**
- Constant subtle breathing motion
- Vertical body movement (1.5% amplitude)
- 1.2 Hz frequency (natural breathing rate)
- Always active regardless of state

## Technical Details

### Animation System

**Frame Rate:** 60 FPS target
**Update Method:** Real-time in render loop
**State Management:** React refs for animation state
**Timing:** Delta time based (0.016s per frame)

### Animation Parameters

```typescript
// Speaking
- Head rotation: ±15° Y, ±12° X, ±8° Z
- Talk speed: 8-12 Hz (volume dependent)
- Jaw movement: 0-10° (volume dependent)
- Body sway: ±5° Y, ±3° Z
- Gesture interval: 2-3 seconds

// Listening
- Head rotation: ±10° X, ±8° Y, ±5° Z
- Nod frequency: 0.3 Hz
- Body lean: ±3° X, ±2° Y

// Idle
- Head rotation: ±4° Y, ±3° X, ±2° Z
- Body sway: ±1.5° Y, ±1° Z
- Weight shift: Occasional ±2° Z

// Blinking
- Interval: 3-5 seconds (variable)
- Duration: 0.15 seconds
- Eye scale: 20-100% vertical

// Breathing
- Amplitude: 1.5% vertical
- Frequency: 1.2 Hz
- Always active
```

### Mesh Detection

The animation system automatically detects and animates:
- **Head/Neck**: Primary animation target
- **Jaw/Chin**: Talking movements
- **Eyes**: Blinking and tracking
- **Arms/Hands/Shoulders**: Gestures
- **Body/Torso**: Posture and sway

## How It Works

### 1. State Detection
```typescript
if (speaking) {
  // Expressive talking animations
} else if (listening) {
  // Attentive listening animations
} else {
  // Calm idle animations
}
```

### 2. Multi-Layer Animation
Each animation combines multiple sine waves for natural movement:
```typescript
head.rotation.y = 
  Math.sin(time * 1.8) * 0.15 * intensity +  // Primary movement
  Math.sin(time * 3.2) * 0.05 * intensity;   // Secondary detail
```

### 3. Volume Reactivity
Speaking animations scale with audio volume:
```typescript
const talkIntensity = Math.max(0.3, volume / 100);
const talkSpeed = 8 + (volume / 20);
```

### 4. Random Variation
Natural timing through randomization:
```typescript
const blinkInterval = 3 + Math.sin(time * 0.1) * 2; // 3-5 seconds
if (state.gestureTimer > 2.0 && Math.random() > 0.7) {
  // Trigger gesture
}
```

## Testing the Animations

### 1. Idle State
- Open http://localhost:3000
- Observe subtle breathing and micro-movements
- Watch for occasional blinks (every 3-5 seconds)
- Notice gentle head sway

### 2. Listening State
- Click "Start Your Session"
- Speak into your microphone
- Avatar should show attentive head tilts
- Occasional nods showing engagement
- Forward-leaning posture

### 3. Speaking State
- Wait for AI to respond
- Avatar should show dynamic head movements
- Watch for jaw movement (if model supports it)
- Notice hand gestures every few seconds
- Body sway synchronized with speech

## Customization

### Adjust Animation Intensity

Edit `BabylonAvatar.tsx` and modify these values:

```typescript
// Make talking more expressive
head.rotation.y = Math.sin(time * 1.8) * 0.20 * talkIntensity; // Increase from 0.15

// Make listening more subtle
head.rotation.x = Math.sin(time * 0.6) * 0.05 * listenIntensity; // Decrease from 0.1

// Change breathing intensity
const breathingIntensity = 0.025; // Increase from 0.015
```

### Adjust Animation Speed

```typescript
// Faster talking
const talkSpeed = 12 + (volume / 20); // Increase from 8

// Slower idle movements
head.rotation.y = Math.sin(time * 0.2) * 0.04; // Decrease from 0.3
```

### Disable Specific Animations

```typescript
// Disable hand gestures
if (false && state.gestureTimer > 2.0) { // Add false &&
  // Gesture code won't run
}

// Disable blinking
if (false && state.blinkTimer < blinkDuration) { // Add false &&
  // Blink code won't run
}
```

## Performance

**CPU Usage:** Minimal (simple math operations)
**GPU Usage:** Low (no complex shaders)
**Memory:** Negligible (state tracking only)
**Frame Rate:** Maintains 60 FPS on modern hardware

## Compatibility

✅ Works with Ready Player Me models
✅ Works with custom GLB/GLTF models
✅ Works with built-in geometric avatar
✅ Automatic mesh detection
✅ Graceful degradation if meshes not found

## Troubleshooting

### Animations Too Subtle
- Increase intensity multipliers in the code
- Check volume level is being detected
- Verify speaking/listening states are triggering

### Animations Too Intense
- Decrease rotation angles
- Reduce intensity multipliers
- Lower animation speeds

### Jaw Not Moving
- Model may not have jaw bones
- Check mesh names in browser console
- Try a different Ready Player Me model

### Gestures Not Showing
- Increase gesture frequency (lower timer threshold)
- Check arm/hand meshes are detected
- Verify model has arm bones

### Performance Issues
- Reduce animation complexity
- Disable some animation layers
- Lower frame rate target

## Future Enhancements

Potential additions:
- [ ] Lip-sync with phoneme detection
- [ ] Facial expressions (happy, concerned, thoughtful)
- [ ] Eye contact with camera
- [ ] More varied gesture library
- [ ] Emotion-based animation states
- [ ] Posture changes over time
- [ ] Breathing rate variation

## Resources

- [Babylon.js Animation Docs](https://doc.babylonjs.com/features/featuresDeepDive/animation)
- [Ready Player Me Models](https://readyplayer.me/)
- [Animation Principles](https://en.wikipedia.org/wiki/Twelve_basic_principles_of_animation)

---

**Status:** ✅ Enhanced animations active
**Next:** Test at http://localhost:3000 and start a session!
