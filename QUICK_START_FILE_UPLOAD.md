# Quick Start Guide - File Upload Feature

## Prerequisites Check

Before running the application, ensure you have the required Python packages:

```bash
pip install PyPDF2 python-docx werkzeug
```

## Running the Application

### Step 1: Start the Backend
```bash
cd "e:\Machine Learning Project\ai_detector\Backend"
python app.py
```

You should see:
```
=============================================================
LOADING AI DETECTION MODELS
=============================================================

📚 Loading RoBERTa: Hello-SimpleAI/chatgpt-detector-roberta...
   ✅ RoBERTa loaded successfully

📚 Loading ML Ensemble (Random Forest + KNN)...
   ✅ ML Ensemble loaded successfully

=============================================================
MODELS LOADED - RoBERTa Weight: 70%, ML Weight: 30%
=============================================================

 * Running on http://127.0.0.1:5000
```

### Step 2: Start the Frontend
Open a new terminal:
```bash
cd "e:\Machine Learning Project\ai_detector\Frontend"
npm run dev
```

You should see:
```
  VITE v4.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

### Step 3: Open the Application
Open your browser and navigate to: **http://localhost:5173**

## Testing the File Upload Feature

### Test 1: Upload a PDF File
1. Click the **"File Upload"** tab
2. Drag a PDF file into the drop zone OR click "Choose File"
3. Verify the file preview appears with:
   - 📕 PDF icon
   - File name
   - File size in KB
4. Click **"Analyze File"** button
5. Wait for analysis (you'll see a spinner)
6. Verify results show:
   - AI vs Human probability
   - Gauge chart
   - File metadata (filename, type, word count)

### Test 2: Upload a DOCX File
1. Click the **"File Upload"** tab
2. Drag a DOCX file into the drop zone OR click "Choose File"
3. Verify the file preview appears with:
   - 📘 Word icon
   - File name
   - File size in KB
4. Click **"Analyze File"** button
5. Verify results are displayed correctly

### Test 3: Test Validation
1. Try uploading an invalid file type (e.g., .txt, .jpg)
   - Should show error: "Please upload a PDF or Word document (.pdf, .docx, .doc)"
2. Try uploading a file > 10MB
   - Should show error: "File size must be less than 10MB"

### Test 4: Mode Switching
1. Switch to "File Upload" mode
2. Upload a file
3. Switch back to "Text Input" mode
   - File should be cleared
4. Switch to "File Upload" mode again
   - Should show empty drop zone

### Test 5: Remove File
1. Upload a file
2. Click the **✕** button on the file preview
3. Verify the file is removed and drop zone reappears

## Sample Test Files

You can create test files or use existing documents:

### Create a Sample PDF (if needed):
1. Open Microsoft Word or Google Docs
2. Write some text (at least 100 words)
3. Save as PDF

### Create a Sample DOCX (if needed):
1. Open Microsoft Word
2. Write some text (at least 100 words)
3. Save as .docx

### Sample AI-Generated Text:
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

### Sample Human-Written Text:
```
I love going to the park on sunny days. The fresh air and green grass 
make me feel relaxed. Sometimes I bring my dog, and we play fetch 
together. It's simple, but it makes me happy. I also like to read a 
book under the big oak tree. The shade is perfect, and I can spend 
hours there without getting bored. On weekends, my friends join me, 
and we have picnics. Those are my favorite moments.
```

## Troubleshooting

### Backend Issues:

**Error: ModuleNotFoundError: No module named 'PyPDF2'**
```bash
pip install PyPDF2
```

**Error: ModuleNotFoundError: No module named 'docx'**
```bash
pip install python-docx
```

**Error: Port 5000 already in use**
- Stop any other applications using port 5000
- Or change the port in `app.py`: `app.run(debug=True, port=5001)`
- And update `vite.config.js` proxy to use the new port

### Frontend Issues:

**Error: Cannot find module './file-upload-styles.css'**
- Verify the file exists at: `Frontend/src/file-upload-styles.css`
- Check the import in `main.jsx`

**Error: Network request failed**
- Ensure the backend is running on port 5000
- Check the proxy configuration in `vite.config.js`

**File upload not working**
- Check browser console for errors (F12)
- Verify the `/predict-file` endpoint is accessible
- Test the backend directly: `curl -X POST http://localhost:5000/info`

## Expected Behavior

### Successful Upload:
1. File is validated ✅
2. File preview appears ✅
3. "Analyze File" button is enabled ✅
4. Loading spinner appears during analysis ✅
5. Results display with file metadata ✅
6. Gauge chart shows AI probability ✅

### Failed Upload:
1. Error message appears in red ❌
2. File is not processed ❌
3. User can try again with a different file

## Performance Notes

- **Small files** (< 1MB): Analysis takes 2-5 seconds
- **Medium files** (1-5MB): Analysis takes 5-15 seconds
- **Large files** (5-10MB): Analysis takes 15-30 seconds

The processing time depends on:
- File size
- Text extraction complexity
- Model inference time
- System performance

## Next Steps

After successful testing:
1. ✅ Feature is ready for production use
2. 📝 Consider adding more file formats (TXT, RTF)
3. 🎨 Customize styling if needed
4. 📊 Add analytics tracking
5. 🔒 Add authentication if required

## Support

If you encounter any issues:
1. Check the browser console (F12)
2. Check the backend terminal for errors
3. Verify all dependencies are installed
4. Review the FILE_UPLOAD_FEATURE.md documentation

---

**Status**: ✅ Ready to Test
**Last Updated**: 2025-12-13
