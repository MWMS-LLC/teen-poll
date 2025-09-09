# 🚀 Teen Poll MVP - Setup Guide

**Clean PostgreSQL setup with separate setup and results schemas! 🎉**

## 📋 What We Have:

1. **`schema_setup.sql`** - Creates categories, blocks, questions, options tables
2. **`schema_results.sql`** - Creates users, responses, checkbox_responses, other_responses tables  
3. **`import_setup.py`** - Imports CSV data into setup tables
4. **`main.py`** - FastAPI backend with all endpoints

## 🎯 Step-by-Step Setup:

### **Step 1: Create Setup Schema**
```bash
cd backend
python3.11 import_setup.py
```

**This will:**
- ✅ Create setup tables (categories, blocks, questions, options)
- ✅ Import all your CSV data
- ✅ Show summary of imported records

### **Step 2: Create Results Schema (One-time)**
```bash
psql -U postgres -h localhost -d teen_poll -f schema_results.sql
```

**This creates:**
- ✅ Users table (for age validation)
- ✅ Responses tables (for voting data)
- ✅ All necessary indexes

### **Step 3: Start the Backend**
```bash
python3.11 main.py
```

**You should see:**
- `INFO: Uvicorn running on http://0.0.0.0:8000`

### **Step 4: Test the API**
```bash
# Test categories endpoint
curl http://localhost:8000/api/categories

# Test blocks endpoint  
curl http://localhost:8000/api/categories/1/blocks

# Test questions endpoint
curl http://localhost:8000/api/blocks/1_1/questions
```

## 🔍 Schema Design:

### **Setup Tables** (imported once, never modified):
- `categories` - Poll categories
- `blocks` - Question blocks per category  
- `questions` - Questions per block
- `options` - Answer options per question

### **Results Tables** (created once, populated by users):
- `users` - User profiles with age validation
- `responses` - Single-choice votes
- `checkbox_responses` - Multi-select votes with weights
- `other_responses` - Free-text responses

**Note:** Results tables are denormalized and self-sufficient - they survive setup table changes!

## 🚀 Ready to Go!

**Run the import script and everything will work perfectly!**

**Clean, maintainable, and optimized! 🎯**
