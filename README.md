# AI Career Mentor 🚀

A production-ready Python application that analyzes resumes, extracts skills, matches career roles, and identifies skill gaps using NLP and embeddings—entirely offline and free.

## Overview

AI Career Mentor is a FastAPI-based backend system that helps job seekers understand their career fit across different roles. It uses advanced NLP techniques including text extraction, skill matching, and semantic embeddings to provide personalized career recommendations.

## Features

✨ **Core Features:**
- 📄 PDF resume upload and parsing
- 🎯 Intelligent skill extraction with keyword and partial matching
- 🔄 Career role matching with detailed gap analysis
- 📊 Embedding-based semantic similarity scoring
- 🏆 Scoring system for role matching
- 🔍 Comprehensive skill categorization
- 📋 Multiple job role templates

✅ **Non-Requirements Met:**
- ❌ No OpenAI API (completely free)
- ❌ No frontend needed (API-first design)
- ✅ Fully local and offline
- ✅ Beginner-friendly code structure
- ✅ Production-grade architecture
- ✅ Modular and scalable design

## Project Structure

```
ai-career-mentor/
├── app/
│   ├── __init__.py
│   ├── main.py                      # FastAPI application
│   ├── routes/
│   │   ├── __init__.py
│   │   └── resume_routes.py        # API endpoints
│   ├── services/
│   │   ├── __init__.py
│   │   ├── resume_parser.py        # PDF text extraction
│   │   ├── skill_extractor.py      # Skill detection
│   │   ├── career_matcher.py       # Role matching & gap analysis
│   │   └── embedding_service.py    # Semantic embeddings
│   └── utils/
│       ├── __init__.py
│       └── text_cleaner.py         # Text preprocessing
├── data/
│   ├── skills_list.json            # Skills database (8 categories)
│   └── job_roles.json              # Job roles with requirements
├── models/                          # Placeholder for future models
├── temp_uploads/                    # Temporary resume storage
├── requirements.txt                 # Python dependencies
└── README.md                        # This file
```

## Installation & Setup

### 1. Clone/Create Project

```bash
cd d:\projects\Ai_Career mentor
```

### 2. Create Virtual Environment

```bash
python -m venv venv
```

### 3. Activate Virtual Environment

**On Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

**On Windows (CMD):**
```cmd
venv\Scripts\activate.bat
```

**On macOS/Linux:**
```bash
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Download spaCy Model

```bash
python -m spacy download en_core_web_sm
```

## Running the Application

### Start Development Server

```bash
uvicorn app.main:app --reload
```

The API will be available at: **http://localhost:8000**

### Interactive API Documentation

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## API Endpoints

### 1. Health Check
```
GET /
```
Returns API status.

**Response:**
```json
{
  "status": "healthy",
  "service": "AI Career Mentor API",
  "version": "1.0.0"
}
```

### 2. API Information
```
GET /info
```
Returns detailed API information and available endpoints.

### 3. Upload & Analyze Resume (Main Endpoint)
```
POST /api/upload-resume
```

**Request:**
- Form data with file upload (PDF only)
- Max file size: 10MB

**Response:**
```json
{
  "status": "success",
  "filename": "resume.pdf",
  "extracted_text_preview": "John Doe... Software Engineer with 5 years...",
  "detected_skills": ["python", "fastapi", "machine learning", "docker"],
  "detected_skills_count": 4,
  "matched_roles": [
    {
      "role": "ML Engineer",
      "match_percentage": 85.5,
      "required_match_percentage": 82.0,
      "nice_to_have_match_percentage": 90.0,
      "matched_required_skills": ["python", "machine learning"],
      "missed_required_skills": ["deep learning", "tensorflow"],
      "recommendation": "Highly Recommended - You're a great fit!",
      "total_matched_required": 2,
      "total_required_skills": 4
    }
  ],
  "top_3_recommended_roles": [...(first 3)],
  "common_missing_skills": ["tensorflow", "pytorch", "kubernetes"],
  "analysis_summary": {
    "total_skills_found": 4,
    "best_match_role": "ML Engineer",
    "best_match_percentage": 85.5,
    "top_missing_skills_count": 3
  }
}
```

### 4. Analyze Raw Text
```
POST /api/analyze-text
```

**Request:**
```json
{
  "text": "John Doe. Software Engineer with 5+ years of Python experience..."
}
```

**Response:** Same format as resume upload

### 5. Get Job Roles
```
GET /api/job-roles
```

Returns all available job roles and their requirements.

**Response:**
```json
{
  "status": "success",
  "roles": {
    "Data Scientist": {
      "required_skills_count": 7,
      "nice_to_have_count": 4,
      "required_skills": ["python", "pandas", "numpy", ...],
      "nice_to_have": ["tensorflow", "pytorch", ...]
    },
    ...
  }
}
```

## Testing with Postman

### 1. Create New Request

**URL:** `http://localhost:8000/api/upload-resume`
**Method:** `POST`

### 2. Configure Request

- **Tab: Body**
  - Select: `form-data`
  - Key: `file` (type: File)
  - Value: Select your PDF resume file

### 3. Send Request

Click **Send** and review the response.

### Alternative: Using cURL

```bash
curl -X POST "http://localhost:8000/api/upload-resume" \
  -H "accept: application/json" \
  -F "file=@resume.pdf"
```

### Testing Text Analysis

```bash
curl -X POST "http://localhost:8000/api/analyze-text" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Python developer with 3 years of FastAPI and Docker experience"
  }'
```

## Available Job Roles

The system includes 7 predefined job roles:

1. **Data Scientist** - 7 required skills, 4 nice-to-have
2. **ML Engineer** - 7 required skills, 4 nice-to-have
3. **Backend Developer** - 7 required skills, 5 nice-to-have
4. **Frontend Developer** - 7 required skills, 4 nice-to-have
5. **Data Analyst** - 6 required skills, 3 nice-to-have
6. **DevOps Engineer** - 7 required skills, 4 nice-to-have
7. **AI Engineer** - 6 required skills, 5 nice-to-have

## Skill Categories

Skills are organized into 8 categories:

- **Programming** (14 languages)
- **Web Development** (17 frameworks/tools)
- **Data Science** (11 libraries/concepts)
- **AI/Machine Learning** (12 frameworks/concepts)
- **Databases** (11 database systems)
- **Cloud & DevOps** (11 services/tools)
- **Tools & Frameworks** (9 tools)

## Algorithm Details

### Skill Extraction
1. **Exact Matching** - Direct word-for-word comparison
2. **Partial Matching** - Multi-word skill detection (e.g., "machine learning")
3. **Categorization** - Skills organized by domain

### Role Matching Scoring
```
Overall Score = (Required Match % × 0.7) + (Nice-to-Have Match % × 0.3)
```

**Recommendation Levels:**
- 80-100%: "Highly Recommended - You're a great fit!"
- 60-80%: "Recommended - You have most required skills"
- 40-60%: "Consider Applying - Some skills need development"
- <40%: "Develop More Skills - This role requires significant skill growth"

### Embedding-Based Matching
- **Model:** Sentence Transformers (all-MiniLM-L6-v2)
- **Method:** Cosine Similarity
- **Dimension:** 384-dimensional vectors
- **Caching:** Automatic embedding cache for performance
- **Future:** FAISS support for large-scale matching

## Code Quality Features

✅ **Clean Code Architecture:**
- Modular service-based design
- Comprehensive docstrings
- Type hints throughout
- Logging for debugging
- Error handling with meaningful messages
- Function-based approach (no long scripts)

📈 **Production Features:**
- CORS middleware enabled
- Request validation
- File size limits (10MB)
- Temporary file cleanup
- Exception handling
- Structured logging
- Health check endpoint

## Environment Variables (Optional)

Create a `.env` file for custom configurations:

```
LOG_LEVEL=info
MAX_FILE_SIZE=10485760  # 10MB in bytes
UPLOAD_DIR=temp_uploads
EMBEDDING_MODEL=all-MiniLM-L6-v2
```

## Logging

Logs are output to console with the following format:
```
2024-01-15 10:30:45,123 - app.main - INFO - Processing resume: resume.pdf
2024-01-15 10:30:46,456 - app.services.embedding_service - INFO - Loaded embedding model: all-MiniLM-L6-v2
```

## Performance Considerations

- **First run:** ~10-15 seconds (model download)
- **Resume processing:** ~2-5 seconds per file
- **Memory usage:** ~400MB (embedding model)
- **Caching:** Embeddings cached for repeated inputs

## Future Enhancements

🔮 **Potential Features:**
- FAISS indexing for large-scale similarity search
- User authentication and resume history
- Frontend dashboard
- Real-time websocket updates
- Database integration
- Advanced NLP models (distilBERT, RoBERTa)
- Multi-language support
- Resume score benchmarking

## Troubleshooting

### Issue: "Module not found" error
**Solution:** Ensure you're in the project root directory and virtual environment is activated.

### Issue: Port 8000 already in use
**Solution:** 
```bash
uvicorn app.main:app --reload --port 8001
```

### Issue: Memory error with embeddings
**Solution:** The model requires ~400MB RAM. Ensure your system has sufficient memory.

### Issue: PDF extraction fails
**Solution:** Ensure PDF is not encrypted. Text-based PDFs work best (not scanned images).

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| FastAPI | 0.104.1 | Web framework |
| Uvicorn | 0.24.0 | ASGI server |
| Pydantic | 2.5.0 | Data validation |
| spaCy | 3.7.2 | NLP toolkit |
| scikit-learn | 1.3.2 | Machine learning |
| sentence-transformers | 2.2.2 | Embeddings |
| PyMuPDF | 1.23.8 | PDF processing |
| pandas | 2.1.3 | Data manipulation |
| numpy | 1.26.2 | Numerical computing |
| faiss-cpu | 1.7.4 | Vector similarity |

## License

This project is open source and available for educational and commercial use.

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review API documentation at `/docs`
3. Check console logs for error details

---

**Built with ❤️ for aspiring tech professionals**

Start your career journey with AI Career Mentor! 🚀
# Quick Setup: AI Career Insights Feature

## 1️⃣ Install Dependencies
```bash
pip install google-generativeai
```

Update `requirements.txt`:
```
google-generativeai>=0.3.0
```

## 2️⃣ Set API Key

### Option A: Environment Variable
```bash
# Linux/Mac
export GEMINI_API_KEY="your-key-here"

# Windows PowerShell
$env:GEMINI_API_KEY = "your-key-here"

# Windows CMD
set GEMINI_API_KEY=your-key-here
```

### Option B: .env File
Create `.env` in project root:
```
GEMINI_API_KEY=your-api-key-here
```

Then load in Python:
```python
from dotenv import load_dotenv
load_dotenv()
```

**Get Free API Key**: https://aistudio.google.com/apikey

## 3️⃣ Start Services

Backend:
```bash
cd d:\projects\Ai_Career mentor
source .venv/Scripts/activate  # or .venv\Scripts\activate on Windows
python -m uvicorn app.main:app --reload
```

Frontend:
```bash
cd frontend
npm run dev
```

## 4️⃣ Test the Feature

1. Open http://localhost:5174 in browser
2. Upload a resume (PDF)
3. Check for "Career Insights" section below "Your Best Career Match"
4. Should see:
   - "Why this role suits you" (explanation)
   - "How to improve" (recommendations list)

## ✅ Files Implemented

### Backend
- ✅ `app/services/ai_explainer.py` - NEW (complete service)
- ✅ `app/routes/resume_routes.py` - UPDATED (integration in both endpoints)

### Frontend
- ✅ `frontend/src/components/Result.jsx` - UPDATED (new section added)
- ✅ `frontend/src/index.css` - UPDATED (styling for insights)

### Documentation
- ✅ `FEATURE_AI_INSIGHTS.md` - Complete implementation guide
- ✅ `SETUP.md` - This file

## 🔍 Verify Installation

Check logs for success message:
```
✓ Gemini API initialized successfully
Successfully generated AI insights for <role_name>
```

## 🛠️ Troubleshooting

**Issue**: AI section not appearing
- Check browser console (F12 → Console)
- Verify `GEMINI_API_KEY` is set
- Check backend logs for errors

**Issue**: "GEMINI_API_KEY not found"
- Set environment variable correctly
- Restart backend server
- Verify key is valid at https://aistudio.google.com/apikey

**Issue**: Malformed JSON response
- Check Gemini API quotas
- Verify internet connection
- Check backend logs for API errors

## 📊 Response Example

```json
{
  "ai_insights": {
    "explanation": "You have strong Python and data analysis skills that align perfectly with a Data Scientist role. Your foundation in statistics and machine learning is evident, and with focused effort on deep learning frameworks, you'll be highly competitive.",
    "recommendations": [
      "Deepen expertise in PyTorch or TensorFlow for neural network applications",
      "Build an end-to-end machine learning project showcasing data pipeline management",
      "Study distributed systems concepts for handling large-scale data processing",
      "Obtain a certification in cloud platforms (AWS, GCP, or Azure)"
    ]
  }
}
```

## 🚀 Ready to Go!

Your AI Career Insights feature is now live. Users will receive personalized career guidance powered by Google Gemini!

---

For full documentation, see: `FEATURE_AI_INSIGHTS.md`
