# Web App - New Features Update

## 🆕 CSV File Scanner & Selector

The web app now automatically scans and displays CSV files from the `data/` directory!

### New Features

#### 1. **Sidebar File Counter**
- Shows how many CSV files are available in real-time
- Example: "📂 3 CSV file(s) available in data/"
- Updates when you switch between modes

#### 2. **Upload Mode - File Selector**
When you select "Upload Report Card CSV":

**What you see:**
```
📂 Available CSV Files in Data Directory

Select a CSV file to analyze:
[Dropdown: -- Choose from available files --]
         [amin.csv]
         [rina.csv]  
         [jamil.csv]

🔍 Analyze Selected File

👁️ Preview Selected File (Expander)
┌─────────────────────────────────────┐
│ Shows first 10 rows of selected CSV │
│ Total Records: 23 | Columns: ...   │
└─────────────────────────────────────┘

---
Or upload your own CSV file:
[File Upload Widget]
```

**Features:**
- ✅ Dropdown list of all available CSV files
- ✅ Live preview of selected file (first 10 rows)
- ✅ Shows total records and column names
- ✅ "Analyze Selected File" button
- ✅ Automatic detection when new files added

#### 3. **Batch Mode - Enhanced File Display**
When you select "Batch Analysis":

**What you see:**
```
✓ Found 3 CSV file(s) in data/ directory

📁 Available Files (Expander)
1. amin.csv (23 records)
2. rina.csv (20 records)
3. jamil.csv (25 records)

---

Select CSV files to analyze:
☑️ amin.csv
☑️ rina.csv
☑️ jamil.csv

🔍 Analyze Selected Students
```

**Features:**
- ✅ Shows count of found files
- ✅ Lists all files with record counts
- ✅ Multi-select checkboxes
- ✅ Default selects first 3 files
- ✅ 🔄 Refresh Files button

### Workflow Examples

#### Example 1: Quick Analysis from Data Directory
```
1. Start app: .\run_webapp.ps1
2. Sidebar shows: "📂 3 CSV file(s) available"
3. Select "Upload Report Card CSV"
4. Choose "amin.csv" from dropdown
5. Preview appears automatically
6. Click "🔍 Analyze Selected File"
7. See instant results!
```

#### Example 2: Batch Compare Students
```
1. Select "Batch Analysis" mode
2. See all available files listed with record counts
3. Select which students to compare
4. Click "🔍 Analyze Selected Students"
5. View comparative rankings and charts
```

#### Example 3: Still Upload Your Own
```
1. Select "Upload Report Card CSV"
2. Scroll past the file selector
3. Use "Choose a CSV file to upload" 
4. Upload from anywhere on your computer
```

### Benefits

**Before:**
- Had to manually type file paths
- Couldn't see what files were available
- Had to remember exact filenames

**After:**
- ✅ See all available files instantly
- ✅ Select from dropdown (no typing!)
- ✅ Preview files before analyzing
- ✅ Know how many records in each file
- ✅ Sidebar shows file count at all times

### Technical Details

**File Scanning:**
- Scans `data/` directory on page load
- Filters for `.csv` files only
- Checks file existence automatically
- Updates when you refresh

**Preview Feature:**
- Shows first 10 rows
- Displays total record count
- Lists all column names
- Handles errors gracefully

**Performance:**
- Fast scanning (even with many files)
- No lag with large CSV files
- Preview loads instantly

### Use Cases

#### For Teachers
"I have 30 student CSV files in my data folder. The app shows me all 30, I select the 5 students I want to review today, and analyze them together."

#### For Administrators
"Every Monday, new weekly reports are added to data/. The sidebar shows me how many are available, and I can batch-process them all with a few clicks."

#### For Parents
"I put my child's report in the data folder. The app finds it automatically, I select it from the dropdown, preview it to make sure it's correct, then analyze."

### Compatibility

- ✅ Works with existing CSV files
- ✅ Supports any number of files in data/
- ✅ Compatible with all CSV formats
- ✅ No changes needed to your data

### Troubleshooting

**Q: Files don't appear in list?**
- Check they're in `data/` directory
- Ensure files have `.csv` extension
- Click 🔄 Refresh Files button

**Q: Preview shows error?**
- CSV might have formatting issues
- Try analyzing anyway (processor is robust)
- Check required columns are present

**Q: Sidebar shows "0 files"?**
- Add CSV files to `data/` directory
- Restart the app
- Check folder permissions

### Migration Guide

**If you were using file paths before:**
```python
# Old way (still works!)
filepath = input("Enter CSV path: ")

# New way (easier!)
# Just select from dropdown in web app
```

**No changes needed to:**
- Your existing CSV files
- File format or structure
- How you organize files
- The analysis process

Everything is **backward compatible**!

## 🎉 Try It Now!

```powershell
# Start the updated app
.\run_webapp.ps1

# Visit http://localhost:8501
# See the new file scanner in action!
```

---

**Updated:** December 2, 2025  
**Version:** 2.0 - Smart File Detection
