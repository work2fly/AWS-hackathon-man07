# 3D Avatar Implementation Guide

## Overview

This implementation adds a 3D talking avatar to the AI therapy session interface using Ready.Player.Me. The avatar provides visual feedback during therapy sessions with lip-sync, animations, and responsive states.

🏆 **Breaking Barriers UK 2026 compliant** - Uses client-side rendering only, no AWS services required for avatar functionality.

## Implementation Approach

We've created **two avatar components**:

### 1. AvatarSimple (Recommended - No Dependencies)
- **File**: `src/components/client/AvatarSimple.tsx`
- **Method**: Uses Ready.Player.Me iframe embed
- **Pros**: 
  - No additional npm packages required
  - Lightweight and fast
  - Works immediately
  - Built-in animations
- **Cons**: 
  - Less customization
  - Requires iframe (some security policies may block)

### 2. Avatar3D (Advanced - Requires Dependencies)
- **File**: `src/components/client/Avatar3D.tsx`
- **Method**: Uses Three.js and React Three Fiber
- **Pros**: 
  - Full control over animations
  - Custom lip-sync
  - Better performance
  - More professional
- **Cons**: 
  - Requires npm packages
  - Larger bundle size
  - More complex setup

## Current Status

✅ **AvatarSimple** is currently integrated into SessionInterface.tsx  
⏳ **Avatar3D** is ready but requires dependency installation

## Required Dependencies (for Avatar3D only)

If you want to use the advanced Avatar3D component, install these packages:

```bash
npm install three @react-three/fiber @react-three/drei
```

Or with the specific Ready.Player.Me package:

```bash
npm install @readyplayerme/visage three @react-three/fiber @react-three/drei
```

## Switching Between Components

### To use AvatarSimple (current):
```typescript
import { AvatarSimple } from '@/components/client/AvatarSimple';

<AvatarSimple
  isActive={session.isActive}
  isSpeaking={isSpeaking}
  isListening={isRecording}
  volumeLevel={volumeLevel}
/>
```

### To use Avatar3D (after installing dependencies):
```typescript
import { Avatar3D } from '@/components/client/Avatar3D';

<Avatar3D
  isActive={session.isActive}
  isSpeaking={isSpeaking}
  isListening={isRecording}
  volumeLevel={volumeLevel}
  avatarUrl="https://models.readyplayer.me/YOUR_AVATAR_ID.glb"
/>
```

## Customizing the Avatar

### Option 1: Use Ready.Player.Me Creator
1. Visit https://readyplayer.me/
2. Create a custom avatar (free)
3. Get the `.glb` model URL
4. Replace the `avatarUrl` in the component

### Option 2: Use Default Avatar
The implementation includes a default professional therapist avatar that works out of the box.

## Features Implemented

✅ **Idle Animation**: Subtle breathing and head movements when not active  
✅ **Speaking State**: Avatar animates when AI is speaking  
✅ **Listening State**: Visual feedback when client is speaking  
✅ **Volume Reactive**: Avatar intensity changes with audio volume  
✅ **Loading State**: Smooth loading experience  
✅ **Fallback**: Graceful degradation to 2D avatar if 3D fails  
✅ **Mobile Support**: Responsive design for all devices  
✅ **Performance**: Optimized rendering and animations

## Integration Points

The avatar integrates with existing session state:

- **isActive**: Session is running
- **isSpeaking**: AI agent is currently speaking (audio playing)
- **isListening**: Client is currently speaking (microphone recording)
- **volumeLevel**: Audio volume level (0-100) for reactive animations

## Testing

To test the avatar:

1. Start the development server: `npm run dev`
2. Navigate to the client session interface
3. Click "Start Your Session"
4. Observe avatar states:
   - **Idle**: Before session starts
   - **Listening**: When you speak (microphone active)
   - **Speaking**: When AI responds (audio playing)

## Performance Considerations

### AvatarSimple Performance
- Minimal bundle impact (~5KB)
- Iframe loads asynchronously
- No impact on main thread

### Avatar3D Performance (if using)
- Three.js adds ~600KB to bundle
- React Three Fiber adds ~100KB
- Consider code splitting for production:

```typescript
import dynamic from 'next/dynamic';

const Avatar3D = dynamic(() => import('@/components/client/Avatar3D').then(mod => mod.Avatar3D), {
  ssr: false,
  loading: () => <div>Loading avatar...</div>
});
```

## Troubleshooting

### Avatar not loading
- Check network tab for CORS errors
- Verify avatar URL is accessible
- Check iframe security policies

### Animations not working
- Verify state props are being passed correctly
- Check browser console for errors
- Ensure WebGL is supported (for Avatar3D)

### Performance issues
- Use AvatarSimple instead of Avatar3D
- Reduce animation complexity
- Enable code splitting

## Future Enhancements

Potential improvements for future iterations:

- [ ] Real lip-sync using audio analysis
- [ ] Facial expressions based on sentiment
- [ ] Multiple avatar options for clients to choose
- [ ] Avatar customization in user profile
- [ ] Gesture animations for emphasis
- [ ] Eye tracking and gaze direction
- [ ] Emotion detection and responsive expressions

## Security & Privacy

- Avatar rendering happens entirely client-side
- No personal data sent to Ready.Player.Me
- Avatar models are static assets
- No tracking or analytics from avatar service

## Resources

- [Ready.Player.Me Documentation](https://docs.readyplayer.me/)
- [React Three Fiber Docs](https://docs.pmnd.rs/react-three-fiber/)
- [Three.js Documentation](https://threejs.org/docs/)

## Support

For issues or questions about the avatar implementation, check:
1. This documentation
2. Browser console for errors
3. Network tab for loading issues
4. Ready.Player.Me status page

---

**Implementation Date**: January 2026  
**Breaking Barriers UK 2026 Hackathon**  
**UKind Therapy Platform**
