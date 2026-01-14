# 🎭 Quick Guide: Download a Realistic Female Therapist Model

## ⚡ Fastest Method (5 minutes)

### Ready Player Me - No Download Needed!

1. **Open**: https://readyplayer.me/
2. **Click**: "Create Avatar"
3. **Select**: Full Body → Female
4. **Customize**:
   - Hair: Professional bun or short style
   - Outfit: Blazer or business attire
   - Face: Warm, friendly expression
   - Optional: Add glasses
5. **Get URL**: Copy the model URL (format: `https://models.readyplayer.me/[ID].glb`)
6. **Paste** into `SessionInterface.tsx` line 320

**That's it!** No download needed - use the URL directly.

---

## 📥 Alternative: Download and Host Locally

### Method 1: Sketchfab (Best Free Models)

**Step-by-step**:

1. **Visit**: https://sketchfab.com/3d-models?features=downloadable&sort_by=-likeCount

2. **Search**: "female character rigged"

3. **Apply Filters**:
   - ✅ Downloadable
   - ✅ Free
   - ✅ Rigged (for animations)

4. **Recommended Models** (search these titles):
   - "Business Woman Low Poly"
   - "Female Character Base"
   - "Professional Woman"
   - "Office Worker Female"

5. **Download**:
   - Click on a model
   - Click "Download 3D Model"
   - Select "glTF" format
   - Extract the ZIP file

6. **Place File**:
   - Copy the `.glb` file to: `ai-therapy-frontend/public/models/`
   - Rename to something simple like: `therapist.glb`

7. **Update Code**:
   ```typescript
   modelUrl="/models/therapist.glb"
   ```

---

### Method 2: Mixamo (High Quality)

**Step-by-step**:

1. **Visit**: https://www.mixamo.com/
2. **Sign in** with Adobe account (free)
3. **Browse Characters** → Filter by "Female"
4. **Select**: "Business Woman" or similar professional character
5. **Download**:
   - Format: FBX
   - Skin: With Skin
   - Click Download

6. **Convert to GLB**:
   - Visit: https://products.aspose.app/3d/conversion/fbx-to-glb
   - Upload your FBX file
   - Download the converted GLB

7. **Place File**: In `ai-therapy-frontend/public/models/`

8. **Update Code**: Use `/models/your-file.glb`

---

## 🎨 Specific Model Recommendations

### Free Models You Can Download Right Now:

1. **"Female Doctor" on Sketchfab**
   - Search: "female doctor free"
   - Professional medical appearance
   - Usually under 2MB

2. **"Business Woman" on Sketchfab**
   - Search: "business woman rigged free"
   - Professional attire
   - Good for therapy context

3. **"Professional Female Character" on CGTrader**
   - Visit: https://www.cgtrader.com/free-3d-models
   - Search: "female character"
   - Filter: Free

---

## 🔧 After Downloading

### Where to Put the File:
```
ai-therapy-frontend/
  └── public/
      └── models/
          └── therapist.glb  ← Put your file here
```

### How to Use It:

Open `ai-therapy-frontend/src/components/client/SessionInterface.tsx`

Find line ~320 and change:
```typescript
modelUrl="https://models.readyplayer.me/65e8c4f3d4c3b2a1f0e9d8c7.glb"
```

To:
```typescript
modelUrl="/models/therapist.glb"
```

Save the file and the dev server will auto-reload!

---

## ✅ Verification

Test your model before using:
1. Visit: https://gltf-viewer.donmccurdy.com/
2. Drag and drop your GLB file
3. Check if it looks good
4. Verify it's not too large (under 5MB)

---

## 🎯 My Recommendation

**For this hackathon, use Ready Player Me**:
- ✅ Fastest (5 minutes)
- ✅ No download needed
- ✅ Professional quality
- ✅ Customizable
- ✅ Direct URL usage
- ✅ Always accessible

Just create your avatar and use the URL directly!

---

## 🆘 Need Help?

If you're having trouble:
1. Check the browser console for errors
2. Verify the file is in the correct folder
3. Make sure the file is GLB format (not FBX or OBJ)
4. Try the Ready Player Me URL method instead

---

## 📝 Current Setup

I've already updated your code to use a Ready Player Me URL. 

**To use your own**:
1. Create avatar at https://readyplayer.me/
2. Copy the model URL
3. Replace the URL in SessionInterface.tsx line 320
4. Done!

🏆 **Breaking Barriers UK 2026 Compliant**
