# Debug Guide - File Upload Highlighting Issue

## Current Status
Added extensive console logging to debug why the highlighted text isn't showing for file uploads.

## How to Test

### Step 1: Open Browser Console
1. Go to http://localhost:5173
2. Press **F12** to open Developer Tools
3. Click the **"Console"** tab
4. Clear the console (click the 🚫 icon or press Ctrl+L)

### Step 2: Upload a File
1. Click the **"File Upload"** tab
2. Upload a DOCX or PDF file (preferably one with AI-generated text)
3. Click **"Analyze File"**

### Step 3: Check Console Output

You should see a sequence of console messages. Here's what to look for:

#### **During Upload:**
```
📄 File upload result: {is_ai: true, ai_probability: 0.8463, ...}
📝 Has extracted_text? true
📊 AI probability: 0.8463
📝 Extracted text length: 1234
📝 First 100 chars: Furthermore, the implementation of artificial intelligence...
✨ Generating highlighted text...
✅ Highlighted text generated, length: 5678
✅ First 200 chars of highlighted: <span class="ai-sentence-highlight">Furthermore...
✅ highlightedText state updated
```

#### **During Render:**
```
🎨 Render - highlightedText exists? true
🎨 Render - highlightedText length: 5678
🎨 Render - AI probability: 0.8463
🎨 Render - Should show highlight section? true
```

## Troubleshooting

### Problem 1: "Has extracted_text? false"
**Cause:** Backend isn't sending the extracted text
**Solution:** 
1. Check if backend has the latest code with `'extracted_text': text`
2. Restart the backend server:
   ```bash
   # Stop with Ctrl+C
   python app.py
   ```

### Problem 2: "No extracted_text in response"
**Cause:** Same as Problem 1
**Solution:** Restart backend

### Problem 3: Highlighted text generated but not showing
**Cause:** Render condition not met or CSS issue
**Check:**
1. Is AI probability > 0.3? (30%)
2. Is highlightedText state actually set?
3. Look for the render logs - "Should show highlight section? true"

**If "Should show highlight section? false":**
- Check if AI probability is too low (< 30%)
- Check if highlightedText is empty

**If "Should show highlight section? true" but still not visible:**
- Check browser Elements tab (F12 → Elements)
- Search for "highlighted-text-section"
- If it exists but not visible, it's a CSS issue
- If it doesn't exist, there's a React rendering issue

### Problem 4: Console shows errors
**Common Errors:**
- `Cannot read property 'substring' of undefined` → extracted_text is undefined
- `highlightAISentences is not defined` → Function not imported/defined
- Network error → Backend not running or wrong port

## Expected Behavior

### ✅ Success Indicators:
1. Console shows "Has extracted_text? **true**"
2. Console shows "Highlighted text generated, length: **[number]**"
3. Console shows "Should show highlight section? **true**"
4. Page shows "💡 AI-Suspected Sentences Highlighted" section
5. Text has red-highlighted sentences

### ❌ Failure Indicators:
1. Console shows "No extracted_text in response"
2. Console shows "Should show highlight section? **false**"
3. No highlighted text section visible on page
4. Errors in console

## Quick Fix Checklist

- [ ] Backend is running (`python app.py`)
- [ ] Backend has latest code with `'extracted_text': text`
- [ ] Frontend is running (`npm run dev`)
- [ ] Browser is showing http://localhost:5173
- [ ] Browser console is open (F12)
- [ ] Uploaded file has AI-generated text
- [ ] AI probability > 30%
- [ ] No errors in console

## Test Files

### Good Test File (High AI Probability):
Create a DOCX with this text:
```
Furthermore, the implementation of artificial intelligence in modern 
applications has revolutionized the way we approach complex problems. 
It is important to note that machine learning algorithms can leverage 
vast amounts of data to optimize decision-making processes. Moreover, 
the integration of neural networks has facilitated unprecedented 
advancements in natural language processing. Consequently, these 
cutting-edge technologies have transformed various industries, 
demonstrating remarkable capabilities in pattern recognition and 
predictive analytics.
```

Expected AI probability: **80-90%**

## Next Steps

1. **Follow the testing steps above**
2. **Copy the console output** (all the logs)
3. **Take a screenshot** of the page
4. **Share both** so we can diagnose the exact issue

The extensive logging will help us pinpoint exactly where the problem is!

---

**Created:** 2025-12-13
**Purpose:** Debug file upload highlighting feature
