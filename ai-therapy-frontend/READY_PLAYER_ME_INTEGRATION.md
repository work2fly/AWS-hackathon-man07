# Ready Player Me 3D Avatar Integration

🏆 **Breaking Barriers UK 2026 compliant**

## Current Setup

The application now uses a realistic 3D avatar from Ready Player Me, loaded via Babylon.js.

### Model URL
```
https://models.readyplayer.me/692c94887b7a88e1f63f3d82.glb
```

### Implementation Details

**File**: `ai-therapy-frontend/src/components/client/SessionInterface.tsx`

The BabylonAvatar component is configured with the `modelUrl` prop:

```tsx
<BabylonAvatar
  isActive={session.isActive}
  isSpeaking={session.isActive && !isRecording && session.messageCount > 0}
  isListening={session.isActive && isRecording}
  volumeLevel={volumeLevel}
  modelUrl="https://models.readyplayer.me/692c94887b7a88e1f63f3d82.glb"
/>
```

### Features

✅ **Realistic 3D Model**: Professional female therapist avatar from Ready Player Me
✅ **Animated**: Head movements respond to speaking, listening, and idle states
✅ **Volume-Reactive**: Animations intensity changes based on audio volume
✅ **Camera Controls**: Users can zoom and rotate the camera
✅ **Fallback**: If the model fails to load, a built-in geometric avatar is displayed
✅ **Loading States**: Shows loading spinner while model downloads
✅ **Performance Optimized**: Babylon.js provides efficient rendering

### How It Works

1. **Model Loading**: The component uses `BABYLON.SceneLoader.ImportMeshAsync()` to load the GLB model
2. **Auto-Scaling**: The model is automatically scaled to fit the viewport
3. **Head Detection**: The component searches for head/neck/spine meshes for animation
4. **Animation**: The head mesh is animated in the render loop based on state

### Changing the Avatar

To use a different Ready Player Me avatar:

1. Visit https://readyplayer.me/
2. Create or select an avatar
3. Get the GLB model URL (format: `https://models.readyplayer.me/[ID].glb`)
4. Update the `modelUrl` prop in `SessionInterface.tsx`

### Using Local Models

To use a local GLB/GLTF model instead:

1. Place your model file in `ai-therapy-frontend/public/models/`
2. Update the `modelUrl` prop to: `modelUrl="/models/your-model.glb"`

### Troubleshooting

**Model not visible?**
- Check browser console (F12) for CORS or loading errors
- Verify the model URL is accessible
- Try a different Ready Player Me model URL

**Model too large/small?**
- The component auto-scales models, but you can adjust the scale factor in `BabylonAvatar.tsx`
- Look for: `const scale = 2 / maxDim;` and adjust the `2` value

**Animations not working?**
- The component tries to find head/neck/spine meshes automatically
- If your model has different naming, update the mesh detection logic in `loadExternalModel()`

**Performance issues?**
- Ready Player Me models are optimized for web use
- If still slow, try a simpler model or reduce polygon count

## Technical Details

### Dependencies
- `@babylonjs/core`: ^8.45.5
- `@babylonjs/loaders`: ^8.45.5

### Browser Compatibility
- Modern browsers with WebGL 2.0 support
- Chrome, Firefox, Safari, Edge (latest versions)

### Model Format Support
- GLB (recommended)
- GLTF
- FBX (requires conversion to GLB/GLTF)

## Next Steps

- Test the avatar in the browser at http://localhost:3000
- Click "Start Your Session" to see the avatar animate
- Verify animations respond to speaking/listening states
- Adjust camera position if needed

## Resources

- [Ready Player Me](https://readyplayer.me/) - Create custom avatars
- [Babylon.js Documentation](https://doc.babylonjs.com/) - 3D engine docs
- [GLB Model Viewer](https://gltf-viewer.donmccurdy.com/) - Test GLB files
