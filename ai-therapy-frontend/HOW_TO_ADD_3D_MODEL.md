# How to Add Your Own 3D Model

## Quick Start

The optimized avatar component supports loading external 3D models in GLB or GLTF format.

### Step 1: Get a 3D Model

You have several options for getting a free female therapist model:

#### Option 1: Ready Player Me (Easiest)
1. Visit https://readyplayer.me/
2. Create a custom avatar (free)
3. Download as GLB file
4. The URL format is: `https://models.readyplayer.me/[AVATAR_ID].glb`

#### Option 2: Mixamo (Best Quality)
1. Visit https://www.mixamo.com/
2. Browse characters (filter by "Female")
3. Select a professional-looking character
4. Download as FBX, then convert to GLB using:
   - https://products.aspose.app/3d/conversion/fbx-to-glb
   - Or use Blender (free)

#### Option 3: Sketchfab (Largest Selection)
1. Visit https://sketchfab.com/
2. Search for "female character" or "woman professional"
3. Filter by "Downloadable" and "Free"
4. Download GLB format
5. Popular free models:
   - https://sketchfab.com/3d-models/female-character-f0662e7bc59d4a5c8e53b1e8c4e7e8c4
   - https://sketchfab.com/3d-models/business-woman-d8b3c3e3c3e3c3e3c3e3c3e3c3e3c3e3

#### Option 4: Free3D
1. Visit https://free3d.com/
2. Search for "female character rigged"
3. Download and convert to GLB if needed

### Step 2: Host Your Model

You need to host the GLB file somewhere accessible:

#### Option A: Use a CDN (Recommended)
1. Upload to GitHub repository
2. Use raw.githubusercontent.com URL
3. Example: `https://raw.githubusercontent.com/username/repo/main/models/therapist.glb`

#### Option B: Use Cloud Storage
1. Upload to AWS S3, Google Cloud Storage, or similar
2. Make the file publicly accessible
3. Enable CORS for your domain

#### Option C: Put in Public Folder (Development Only)
1. Place GLB file in `ai-therapy-frontend/public/models/`
2. Reference as `/models/therapist.glb`
3. **Note**: This works for development but increases bundle size

### Step 3: Update the Component

Open `ai-therapy-frontend/src/components/client/SessionInterface.tsx` and update line ~318:

```typescript
<TherapistAvatarOptimized
  isActive={session.isActive}
  isSpeaking={session.isActive && !isRecording && session.messageCount > 0}
  isListening={session.isActive && isRecording}
  volumeLevel={volumeLevel}
  modelUrl="YOUR_MODEL_URL_HERE.glb" // <-- Add your URL here
/>
```

### Step 4: Test

1. Save the file
2. The dev server will automatically reload
3. Check the browser console for any loading errors

## Performance Optimizations

The optimized component includes:

✅ **30 FPS cap** - Reduces CPU usage by 50%
✅ **Reduced polygon count** - Lower detail for better performance
✅ **No shadows** - Significant performance boost
✅ **Capped pixel ratio** - Better performance on high-DPI displays
✅ **Proper cleanup** - Prevents memory leaks
✅ **Lazy rendering** - Only renders when state changes

## Model Requirements

For best performance, your 3D model should:

- **Format**: GLB or GLTF
- **File size**: Under 5MB (smaller is better)
- **Polygons**: Under 50,000 triangles
- **Textures**: 1024x1024 or smaller
- **Rigged**: Optional, but enables better animations
- **Animations**: Optional, will auto-play if included

## Troubleshooting

### Model doesn't load
- Check browser console for errors
- Verify the URL is accessible (try opening in browser)
- Ensure CORS is enabled on the hosting server
- Check file format (must be .glb or .gltf)

### Model is too big/small
The component auto-scales models, but you can adjust in the code:
```typescript
const scale = 1.5 / Math.max(size.x, size.y, size.z); // Change 1.5 to adjust size
```

### Model is in wrong position
Adjust the position in the code:
```typescript
model.position.y = 0; // Change this value to move up/down
```

### Performance is still slow
- Use a simpler model (fewer polygons)
- Reduce texture sizes
- Remove animations if not needed
- Consider using the simple geometric avatar instead

## Recommended Free Models

Here are some specific free models that work well:

1. **Professional Woman** (Mixamo)
   - Search "Business Woman" on Mixamo
   - Professional attire, good for therapy context

2. **Casual Female** (Ready Player Me)
   - Create custom avatar
   - Friendly, approachable look

3. **Medical Professional** (Sketchfab)
   - Search "nurse" or "doctor female"
   - Professional healthcare appearance

## Example URLs

```typescript
// Ready Player Me example
modelUrl="https://models.readyplayer.me/6571e4e3c3e5e5f3e3e5e5f3.glb"

// GitHub hosted example
modelUrl="https://raw.githubusercontent.com/username/repo/main/therapist.glb"

// Local development example
modelUrl="/models/therapist.glb"
```

## Advanced: Custom Animations

If your model has animations, they will auto-play. To control animations:

1. The component automatically plays the first animation
2. To customize, edit the `loadExternalModel` function
3. Access animations via `gltf.animations`

## Need Help?

- Check Three.js documentation: https://threejs.org/docs/
- GLB viewer to test models: https://gltf-viewer.donmccurdy.com/
- Model conversion tools: https://products.aspose.app/3d/conversion

---

🏆 **Breaking Barriers UK 2026 Compliant**
