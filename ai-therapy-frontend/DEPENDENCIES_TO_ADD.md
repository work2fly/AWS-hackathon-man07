# Dependencies to Add for 3D Avatar

## Current Status

✅ **AvatarSimple** component is working WITHOUT any new dependencies  
⏳ **Avatar3D** component requires the dependencies below

## Required for Avatar3D (Advanced Version)

Add these to your `package.json` dependencies:

```json
{
  "dependencies": {
    "three": "^0.160.0",
    "@react-three/fiber": "^8.15.0",
    "@react-three/drei": "^9.92.0"
  }
}
```

## Installation Command

Run this command in the `ai-therapy-frontend` directory:

```bash
npm install three @react-three/fiber @react-three/drei
```

Or if you prefer yarn:

```bash
yarn add three @react-three/fiber @react-three/drei
```

## Optional: Ready.Player.Me SDK

For advanced features like custom avatar creation:

```bash
npm install @readyplayerme/visage
```

## Why These Packages?

- **three**: Core 3D rendering library (WebGL wrapper)
- **@react-three/fiber**: React renderer for Three.js
- **@react-three/drei**: Useful helpers and abstractions for React Three Fiber
- **@readyplayerme/visage**: (Optional) Official Ready.Player.Me SDK for advanced features

## Bundle Size Impact

| Package | Size (minified + gzipped) |
|---------|---------------------------|
| three | ~600 KB |
| @react-three/fiber | ~100 KB |
| @react-three/drei | ~150 KB |
| **Total** | **~850 KB** |

## Recommendation

For the hackathon, **stick with AvatarSimple** which:
- Works immediately (no installation needed)
- Zero bundle size impact
- Simpler to debug
- Faster to iterate

Switch to Avatar3D later if you need:
- Custom animations
- Better performance
- More control over rendering
- Advanced lip-sync features

## Current Implementation

The SessionInterface.tsx currently uses **AvatarSimple**, so the app works without installing any new packages.

To switch to Avatar3D:
1. Install the dependencies above
2. Change the import in SessionInterface.tsx:
   ```typescript
   // Change from:
   import { AvatarSimple } from '@/components/client/AvatarSimple';
   
   // To:
   import { Avatar3D } from '@/components/client/Avatar3D';
   ```
3. Update the component usage (props are the same)

---

**Note**: Since npm is not available in the current environment, these dependencies will need to be installed when you have access to a Node.js environment.
