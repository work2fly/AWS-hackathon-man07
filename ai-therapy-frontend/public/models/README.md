# 3D Models Folder

## How to Add Your Downloaded Model Here

If you download a GLB file, place it in this folder and reference it as:

```typescript
modelUrl="/models/your-model-name.glb"
```

## Quick Download Options

### Option 1: Ready Player Me (Recommended)
1. Visit: https://readyplayer.me/
2. Create a professional female avatar
3. Right-click the avatar preview → "Save image as" won't work
4. Instead, use the URL they provide directly in the code
5. Format: `https://models.readyplayer.me/[AVATAR-ID].glb`

### Option 2: Download from Sketchfab
1. Visit: https://sketchfab.com/
2. Search: "female character rigged"
3. Filter: Downloadable + Free
4. Download as GLB
5. Place the file here
6. Reference as: `/models/filename.glb`

### Option 3: Use These Free Models

**Professional Woman Models** (search on Sketchfab):
- "Business Woman" by various artists
- "Professional Female Character"
- "Office Worker Female"

## Example Usage

After placing a model file here (e.g., `therapist.glb`):

```typescript
<TherapistAvatarOptimized
  modelUrl="/models/therapist.glb"
  // ... other props
/>
```

## File Size Recommendations

- **Ideal**: Under 2MB
- **Maximum**: 5MB
- **Format**: GLB (preferred) or GLTF

Larger files will slow down loading time.

## Testing Your Model

Before adding to the app, test your model at:
https://gltf-viewer.donmccurdy.com/

This helps verify the model loads correctly and looks good.
