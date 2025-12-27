# 🚀 Quick Start Guide

Get up and running with the Student Rating System in 5 minutes!

## Step 1: Install Dependencies (2 minutes)

```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install packages
pip install -r requirements.txt
```

**Note**: If you get an execution policy error on Windows:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Step 2: Configure Groq API (Optional - 1 minute)

For AI-powered suggestions, set up your Groq API key:

1. Get free API key from: https://console.groq.com/
2. Copy `.env.example` to `.env`
3. Add your API key to `.env`:
   ```
   GROQ_API_KEY=your_actual_key_here
   ```

**Skip this step** if you just want basic analysis without AI suggestions.

## Step 3: Test Setup (1 minute)

```bash
python test_setup.py
```

You should see:
```
🎉 ALL TESTS PASSED!
System is ready to use.
```

## Step 4: Run Your First Analysis (1 minute)

### Option A: Manual Entry
```bash
python app.py
```
- Select option 1
- Enter student data when prompted
- View results!

### Option B: CSV Import
```bash
python app.py
```
- Select option 4 to create sample CSV
- Select option 2 to analyze from CSV
- View results!

## 🎯 Example Analysis

Here's what you'll enter for a sample student:

```
Student ID: John Smith
Attendance: 85
Class Focus: 75
Exam Score: 72
Homework Quality: 8
Classwork Quality: 7
Problem Solving: 8
Communication: 7
Discipline: 8
```

You'll get:
- Overall rating (e.g., 74.5/100)
- Category breakdown with visual bars
- Weakest area identified
- Basic recommendations
- AI-powered improvement plan (if Groq configured)

## 💡 What to Do Next

1. **Analyze more students** to build up the model's learning
2. **Provide feedback** after each analysis to improve accuracy
3. **Check model performance** (Menu option 3) after 10+ students
4. **Review documentation**:
   - `README.md` - Complete guide
   - `MODEL_MONITORING_GUIDE.md` - How to improve the model

## 🆘 Troubleshooting

### "Module not found" error
```bash
# Make sure virtual environment is activated
.\venv\Scripts\Activate.ps1

# Reinstall dependencies
pip install -r requirements.txt
```

### Groq API not working
- System works fine without it (basic recommendations only)
- Check your API key in `.env` file
- Verify internet connection

### Test failures
Run individual tests to identify the issue:
```python
python test_setup.py
```

## 📚 Learning Path

**Day 1**: Run 5-10 student analyses, get familiar with the interface  
**Week 1**: Analyze 20+ students, provide feedback, check performance  
**Week 2**: Review `MODEL_MONITORING_GUIDE.md`, adjust weights if needed  
**Month 1**: Model should be well-adapted to your context

## 🎓 Pro Tips

- Always provide feedback - the model learns from you!
- Use consistent rating criteria across all students
- Check model performance weekly (Menu option 3)
- Save AI suggestions for documentation
- Track student progress over time

---

**Need Help?** Check `README.md` for detailed documentation!
