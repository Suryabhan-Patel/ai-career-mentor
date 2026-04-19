"""
Resume processing routes for FastAPI application.
Integrates FAISS for semantic similarity-based role matching.
"""

import os
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import logging
from pathlib import Path

from app.services.resume_parser import extract_text_from_pdf
from app.services.skill_extractor import SkillExtractor
from app.services.career_matcher import CareerMatcher
from app.services.embedding_service import EmbeddingService
from app.services.embedding_utils import EmbeddingModel, encode_single_text
from app.services.faiss_index import FAISSIndexManager
from app.services.ai_explainer import AIExplainer
from app.utils.text_cleaner import clean_text

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["resume"])

# Initialize services
skill_extractor = SkillExtractor()
career_matcher = CareerMatcher()
embedding_service = EmbeddingService()
ai_explainer = AIExplainer()

# Initialize FAISS-based semantic search
embedding_model = EmbeddingModel(model_name="all-MiniLM-L6-v2")
faiss_manager = None

# Define role descriptions for semantic search
ROLE_DESCRIPTIONS = {
    "Data Scientist": "Data scientist with expertise in machine learning, statistical analysis, Python programming, deep learning, and building predictive models",
    "Data Analyst": "Data analyst skilled in SQL, Python, data visualization, Business Intelligence tools like Tableau and Power BI, and exploratory data analysis",
    "ML Engineer": "Machine learning engineer who develops and deploys ML models, works with frameworks like PyTorch and TensorFlow, handles production ML systems",
    "Backend Developer": "Backend developer building APIs, managing databases, SQL, web services, microservices, and server-side application architecture",
    "Frontend Developer": "Frontend developer creating user interfaces, JavaScript, React, TypeScript, HTML/CSS, and modern web development practices",
    "DevOps Engineer": "DevOps engineer managing infrastructure, containerization with Docker, Kubernetes, CI/CD pipelines, cloud platforms like AWS",
    "AI Engineer": "AI engineer specializing in artificial intelligence, NLP, LLMs, Transformers, advanced neural networks, and AI system architecture",
    "Full Stack Developer": "Full stack developer proficient in both frontend and backend technologies, web development, databases, and complete application development",
}

# Temporary upload directory
UPLOAD_DIR = "temp_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def initialize_faiss_index():
    """Initialize FAISS index once at startup."""
    global faiss_manager
    try:
        print(f"[DEBUG] Starting FAISS initialization... embedding_model={embedding_model is not None}")
        print(f"[DEBUG] Embedding dim: {embedding_model.embedding_dim if embedding_model else 'N/A'}")
        
        faiss_manager = FAISSIndexManager(embedding_model)
        print(f"[DEBUG] FAISSIndexManager created: {faiss_manager is not None}")
        
        if faiss_manager.build_index(ROLE_DESCRIPTIONS):
            logger.info("✓ FAISS index initialized and ready for semantic search")
            print("[DEBUG] ✓ FAISS index built successfully")
            stats = faiss_manager.get_index_stats()
            logger.info(f"  Indexed roles: {stats['num_roles']}, Embedding dim: {stats['embedding_dim']}")
            print(f"[DEBUG] FAISS stats - roles: {stats['num_roles']}, trained: {stats['is_trained']}")
        else:
            logger.warning("⚠ FAISS index build failed, falling back to text-based matching")
            print("[DEBUG] ✗ FAISS index build failed")
            faiss_manager = None
    except Exception as e:
        logger.error(f"Error initializing FAISS: {str(e)}")
        print(f"[DEBUG] Exception during FAISS init: {str(e)}")
        import traceback
        traceback.print_exc()
        faiss_manager = None


# Initialize FAISS index on module import
initialize_faiss_index()


@router.get("/health")
async def health_check():
    """
    Health check endpoint with system status.
    
    Returns:
        JSON with service status and FAISS availability
    """
    faiss_enabled = faiss_manager is not None and faiss_manager.is_trained
    
    return JSONResponse(
        content={
            "status": "healthy",
            "services": {
                "pdf_parsing": "operational",
                "skill_extraction": "operational",
                "faiss_semantic_search": "operational" if faiss_enabled else "unavailable",
                "fallback_matching": "operational"
            },
            "faiss_status": {
                "enabled": faiss_enabled,
                "roles_indexed": faiss_manager.get_index_stats()["num_roles"] if faiss_manager else 0,
                "embedding_model": "all-MiniLM-L6-v2",
                "embedding_dimension": faiss_manager.embedding_dim if faiss_manager else 0
            }
        },
        status_code=200
    )


@router.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    """
    Upload and process a PDF resume using semantic similarity search with FAISS.
    
    Returns:
        JSON response with extracted text, skills, matched roles (by semantic similarity),
        best match analysis, and skill gaps
    """
    file_path = None
    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are accepted")
        
        if file.size > 10 * 1024 * 1024:  # 10MB limit
            raise HTTPException(status_code=400, detail="File size exceeds 10MB limit")
        
        # Save uploaded file temporarily
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        logger.info(f"Processing resume: {file.filename}")
        
        # Extract text from PDF
        extracted_text = extract_text_from_pdf(file_path)
        
        if not extracted_text or extracted_text.strip() == "":
            raise HTTPException(status_code=400, detail="No text could be extracted from PDF")
        
        # Clean text
        cleaned_text = clean_text(extracted_text)
        
        # Extract skills
        skill_results = skill_extractor.extract_skills(cleaned_text)
        detected_skills = skill_results["all_skills"]
        
        # ===== SEMANTIC SEARCH WITH FAISS =====
        recommended_roles = []
        best_match_role = None
        best_match_percentage = 0
        
        if faiss_manager and faiss_manager.is_trained:
            logger.info("🔍 Using FAISS semantic search for role matching...")
            # Search for top matching roles using FAISS
            faiss_results = faiss_manager.search(cleaned_text, k=10)
            
            # Convert FAISS results to our format
            recommended_roles = [{
                "role": r["role_name"],
                "role_name": r["role_name"],
                "similarity_score": r["similarity_score"],
                "match_percentage": r["match_percentage"],
                "description": r["description"],
                "required_skills": r["required_skills"],
                "source": "semantic_search"
            } for r in faiss_results]
            
            if recommended_roles:
                best_match_role = recommended_roles[0]  # Store full object
                best_match_percentage = recommended_roles[0]["match_percentage"]
                logger.info(f"✓ Top match: {recommended_roles[0]['role']} ({best_match_percentage:.2f}%)")
        else:
            logger.warning("⚠ FAISS not available, using fallback keyword-based matching...")
            # Fallback: use legacy keyword matching
            matched_roles = career_matcher.match_roles(detected_skills)
            recommended_roles = matched_roles[:10]
            
            if recommended_roles:
                best_match_role = recommended_roles[0]  # Store full object
                best_match_percentage = recommended_roles[0]["match_percentage"]
        
        # Get top 3 recommended roles (excluding the best match which is at index 0)
        # If best match is from recommended_roles[0], we exclude it and take indices 1-3
        top_3_roles = recommended_roles[1:4] if len(recommended_roles) > 1 else recommended_roles[1:]
        
        # Calculate missing skills for each role
        for role in top_3_roles:
            role_skills_set = set(role.get("required_skills", []))
            detected_skills_set = set(detected_skills)
            missing = role_skills_set - detected_skills_set
            role["missed_required_skills"] = list(missing)
            role["matched_required_skills"] = list(role_skills_set & detected_skills_set)
        
        # Get union of missing skills from top 3 roles
        missing_skills_set = set()
        for role in top_3_roles:
            missing_skills_set.update(role.get("missed_required_skills", []))
        
        missing_skills = sorted(list(missing_skills_set))[:10]  # Top 10
        
        # Generate AI-powered career insights for best match
        ai_insights = None
        if best_match_role and isinstance(best_match_role, dict):
            try:
                best_role_name = best_match_role.get("role") or best_match_role.get("role_name")
                matched_role_skills = best_match_role.get("matched_required_skills", [])
                missing_role_skills = best_match_role.get("missed_required_skills", [])
                
                ai_insights = ai_explainer.generate_career_explanation(
                    role=best_role_name,
                    matched_skills=matched_role_skills,
                    missing_skills=missing_role_skills,
                    match_percentage=best_match_percentage
                )
            except Exception as e:
                logger.warning(f"Failed to generate AI insights: {str(e)}")
                ai_insights = None
        
        # Build response
        response = {
            "status": "success",
            "filename": file.filename,
            "extracted_text_preview": extracted_text[:500] + "..." if len(extracted_text) > 500 else extracted_text,
            "detected_skills": detected_skills,
            "detected_skills_count": len(detected_skills),
            "top_3_recommended_roles": top_3_roles,
            "all_recommended_roles": recommended_roles,
            "common_missing_skills": missing_skills,
            "ai_insights": ai_insights,
            "analysis_summary": {
                "total_skills_found": len(detected_skills),
                "best_match_role": best_match_role if best_match_role and isinstance(best_match_role, dict) else ("No match found" if isinstance(best_match_role, str) else None),
                "best_match_percentage": best_match_percentage,
                "top_missing_skills_count": len(missing_skills),
                "search_method": "semantic_faiss" if faiss_manager and faiss_manager.is_trained else "keyword_fallback"
            }
        }
        
        logger.info(f"✓ Resume analysis complete for {file.filename}")
        return JSONResponse(content=response, status_code=200)
    
    except HTTPException as e:
        logger.error(f"HTTP Error: {e.detail}")
        raise
    
    except Exception as e:
        logger.error(f"Error processing resume: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing resume: {str(e)}")
    
    finally:
        # Clean up temporary file
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                logger.warning(f"Failed to clean up temp file: {str(e)}")


@router.post("/analyze-text")
async def analyze_resume_text(text: str):
    """
    Analyze raw resume text without PDF upload.
    
    Request body:
        {
            "text": "resume text..."
        }
    
    Returns:
        JSON response with analysis results
    """
    try:
        if not text or text.strip() == "":
            raise HTTPException(status_code=400, detail="Resume text cannot be empty")
        
        # Clean text
        cleaned_text = clean_text(text)
        
        # Extract skills
        skill_results = skill_extractor.extract_skills(cleaned_text)
        detected_skills = skill_results["all_skills"]
        
        # Match to career roles
        matched_roles = career_matcher.match_roles(detected_skills)
        
        # Extract best match from first result
        best_match_role = matched_roles[0] if matched_roles else None
        
        # Get top 3 recommended roles (excluding the best match which is at index 0)
        top_roles = matched_roles[1:4] if len(matched_roles) > 1 else matched_roles[1:]
        
        # Calculate missing skills
        missing_skills_set = set()
        for role in top_roles:
            missing_skills_set.update(role.get("missed_required_skills", []))
        
        missing_skills = sorted(list(missing_skills_set))
        
        # Generate AI-powered career insights for best match
        ai_insights = None
        if best_match_role:
            try:
                best_role_name = best_match_role.get("role") or best_match_role.get("role_name")
                matched_role_skills = best_match_role.get("matched_required_skills", [])
                missing_role_skills = best_match_role.get("missed_required_skills", [])
                
                ai_insights = ai_explainer.generate_career_explanation(
                    role=best_role_name,
                    matched_skills=matched_role_skills,
                    missing_skills=missing_role_skills,
                    match_percentage=best_match_role.get("match_percentage", 0)
                )
            except Exception as e:
                logger.warning(f"Failed to generate AI insights: {str(e)}")
                ai_insights = None
        
        response = {
            "status": "success",
            "detected_skills": detected_skills,
            "detected_skills_count": len(detected_skills),
            "matched_roles": matched_roles,
            "top_3_recommended_roles": top_roles,
            "common_missing_skills": missing_skills[:10],
            "ai_insights": ai_insights,
            "analysis_summary": {
                "total_skills_found": len(detected_skills),
                "best_match_role": best_match_role,
                "best_match_percentage": best_match_role["match_percentage"] if best_match_role else 0
            }
        }
        
        return JSONResponse(content=response, status_code=200)
    
    except HTTPException as e:
        logger.error(f"HTTP Error: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"Error analyzing text: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error analyzing text: {str(e)}")


@router.get("/job-roles")
async def get_job_roles():
    """
    Get list of all available job roles.
    
    Returns:
        JSON with all job roles and their requirements
    """
    try:
        roles = {}
        for role_name, role_data in career_matcher.job_roles.items():
            roles[role_name] = {
                "required_skills_count": len(role_data.get("required_skills", [])),
                "nice_to_have_count": len(role_data.get("nice_to_have", [])),
                "required_skills": role_data.get("required_skills", []),
                "nice_to_have": role_data.get("nice_to_have", [])
            }
        
        return JSONResponse(content={"status": "success", "roles": roles}, status_code=200)
    except Exception as e:
        logger.error(f"Error fetching job roles: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching job roles: {str(e)}")
