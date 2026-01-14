# Ready Player Me Arm Position Fix 🦾

🏆 **Breaking Barriers UK 2026 compliant**

## Problem

The Ready Player Me model (https://models.readyplayer.me/692c94887b7a88e1f63f3d82.glb) has its hands/arms in a specific pose that may look unnatural for a therapy session.

## Solution

I've added code to programmatically adjust the arm bones when the model loads, rotating the shoulders and arms down to a more natural resting position.

## What Was Added

### Automatic Arm Adjustment

The code now detects and adjusts these bones:
- **Left/Right Shoulder** - Rotated down and forward
- **Left/Right Upper Arm** - Positioned naturally at sides
- **Left/Right Forearm** - Slight elbow bend

### Rotation Values Applied

```typescript
// Shoulders/Upper Arms
rotation.x = 0.3  // Forward tilt
rotation.z = ±0.4 // Down rotation (+ for left, - for right)

// Forearms
rotation.x = -0.2 // Slight bend at elbow
```

### Debug Logging

The code now logs to the browser console:
- Which arm bones were found and adjusted
- Total number of bones adjusted
- If no bones found, lists all available mesh names

## How to Test

### 1. Refresh Your Browser
- Go to http://localhost:3000
- Hard refresh: **Ctrl+Shift+R** (Windows) or **Cmd+Shift+R** (Mac)

### 2. Open Browser Console
- Press **F12** to open Developer Tools
- Click the **Console** tab
- Look for messages like:
  ```
  Adjusting arm positions for Ready Player Me model...
  Found left shoulder/arm: LeftShoulder
  Found right shoulder/arm: RightShoulder
  Adjusted 4 arm bones
  ```

### 3. Observe the Avatar
- Hands should be lower and more relaxed
- Arms should hang more naturally at sides
- Less "T-pose" or "hands up" appearance

## Troubleshooting

### If Arms Don't Move

**Check Console Output:**
1. Open browser console (F12)
2. Look for: "No arm bones found. Available meshes:"
3. This will list all bone names in the model

**Common Ready Player Me Bone Names:**
- `LeftShoulder` / `RightShoulder`
- `LeftUpperArm` / `RightUpperArm`
- `LeftLowerArm` / `RightLowerArm`
- `LeftHand` / `RightHand`

**If Different Names:**
The code searches for these patterns (case-insensitive):
- `leftshoulder`, `left_shoulder`, `leftupperarm`, `left_upper_arm`
- `rightshoulder`, `right_shoulder`, `rightupperarm`, `right_upper_arm`
- `leftlowerarm`, `left_lower_arm`, `leftforearm`, `left_forearm`
- `rightlowerarm`, `right_lower_arm`, `rightforearm`, `right_forearm`

### Adjusting the Rotation

If the arms need more or less adjustment, edit `BabylonAvatar.tsx`:

```typescript
// Make arms hang lower (increase z rotation)
mesh.rotation.z = 0.6;  // Was 0.4

// Make arms more forward (increase x rotation)
mesh.rotation.x = 0.5;  // Was 0.3

// Straighten arms (reduce forearm bend)
mesh.rotation.x = -0.1; // Was -0.2
```

### Alternative: Different Model Pose

If the current model's pose is too difficult to adjust, you can:

1. **Create a new Ready Player Me avatar** with a different pose:
   - Visit https://readyplayer.me/
   - Create avatar with "A-pose" or "relaxed" pose
   - Get the new GLB URL

2. **Update the model URL** in `SessionInterface.tsx`:
   ```tsx
   modelUrl="https://models.readyplayer.me/YOUR_NEW_ID.glb"
   ```

## Technical Details

### Bone Hierarchy

Ready Player Me models typically have this structure:
```
Armature
├── Hips
│   └── Spine
│       └── Spine1
│           └── Spine2
│               ├── LeftShoulder
│               │   └── LeftUpperArm
│               │       └── LeftLowerArm
│               │           └── LeftHand
│               └── RightShoulder
│                   └── RightUpperArm
│                       └── RightLowerArm
│                           └── RightHand
```

### Rotation Axes

- **X-axis**: Forward/backward tilt
- **Y-axis**: Left/right rotation
- **Z-axis**: Up/down rotation

### Rotation Units

- Values are in **radians**
- 0.4 radians ≈ 23 degrees
- 0.3 radians ≈ 17 degrees
- 0.2 radians ≈ 11 degrees

## Limitations

### Model-Specific Poses

Some Ready Player Me models have:
- **Baked animations** - Can't be changed programmatically
- **Specific poses** - May require different rotation values
- **Locked bones** - Some bones may not rotate

### Workarounds

If programmatic adjustment doesn't work well:

1. **Use a different Ready Player Me model** with better default pose
2. **Adjust camera angle** to minimize the issue
3. **Use the built-in geometric avatar** (remove `modelUrl` prop)
4. **Edit the model** in Blender and re-export with desired pose

## Expected Results

### Before Adjustment
- Arms may be raised or in T-pose
- Hands floating or positioned awkwardly
- Unnatural standing position

### After Adjustment
- ✅ Arms hanging naturally at sides
- ✅ Hands in relaxed position
- ✅ Professional, natural posture
- ✅ More appropriate for therapy session

## Next Steps

1. **Refresh browser** and check console logs
2. **Verify arms are adjusted** (check console for "Adjusted X arm bones")
3. **Fine-tune rotations** if needed
4. **Try different model** if current one doesn't work well

## Alternative Solutions

### Option 1: Camera Framing
Frame the camera to show only upper body (head and shoulders):
```typescript
camera.lowerBetaLimit = Math.PI / 2.5;
camera.upperBetaLimit = Math.PI / 2;
```

### Option 2: Different Model
Try a Ready Player Me model with "A-pose" or "relaxed" default pose

### Option 3: Custom Model
Use a custom GLB model with the exact pose you want

---

**Status:** ✅ Arm adjustment code added
**Next:** Refresh browser and check console logs to see if bones are detected
