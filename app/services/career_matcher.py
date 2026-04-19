"""
Career role matching based on extracted skills.
"""

import json
from typing import List, Dict, Tuple
from pathlib import Path


class CareerMatcher:
    """Match extracted skills to career roles and identify gaps."""
    
    def __init__(self, job_roles_json_path: str = "data/job_roles.json"):
        """
        Initialize career matcher with job roles database.
        
        Args:
            job_roles_json_path (str): Path to job_roles.json file
        """
        self.job_roles = self._load_job_roles(job_roles_json_path)
    
    def _load_job_roles(self, job_roles_json_path: str) -> Dict:
        """
        Load job roles from JSON file.
        
        Args:
            job_roles_json_path (str): Path to job roles JSON file
            
        Returns:
            Dict: Job roles with required and nice-to-have skills
        """
        try:
            with open(job_roles_json_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Job roles database not found: {job_roles_json_path}")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON in job roles database: {job_roles_json_path}")
    
    def match_roles(self, detected_skills: List[str]) -> List[Dict]:
        """
        Match extracted skills to career roles.
        
        Args:
            detected_skills (List[str]): List of detected skills from resume
            
        Returns:
            List[Dict]: Matched roles sorted by match percentage
        """
        detected_skills_lower = [s.lower() for s in detected_skills]
        matched_roles = []
        
        for role_name, role_data in self.job_roles.items():
            required_skills = [s.lower() for s in role_data.get("required_skills", [])]
            nice_to_have = [s.lower() for s in role_data.get("nice_to_have", [])]
            
            # Calculate match percentages
            required_match = self._calculate_match(detected_skills_lower, required_skills)
            nice_match = self._calculate_match(detected_skills_lower, nice_to_have)
            
            # Overall score (70% required, 30% nice-to-have)
            overall_score = (required_match * 0.7) + (nice_match * 0.3)
            
            # Find missing skills
            missing_required = [s for s in required_skills if s not in detected_skills_lower]
            missing_nice = [s for s in nice_to_have if s not in detected_skills_lower]
            
            matched_roles.append({
                "role": role_name,
                "match_percentage": round(overall_score, 2),
                "required_match_percentage": round(required_match, 2),
                "nice_to_have_match_percentage": round(nice_match, 2),
                "matched_required_skills": [s for s in required_skills if s in detected_skills_lower],
                "missed_required_skills": missing_required,
                "matched_nice_skills": [s for s in nice_to_have if s in detected_skills_lower],
                "missed_nice_skills": missing_nice,
                "total_required_skills": len(required_skills),
                "total_matched_required": len([s for s in required_skills if s in detected_skills_lower]),
                "recommendation": self._get_recommendation(overall_score)
            })
        
        # Sort by match percentage (descending)
        matched_roles.sort(key=lambda x: x["match_percentage"], reverse=True)
        
        return matched_roles
    
    def _calculate_match(self, detected_skills: List[str], required_skills: List[str]) -> float:
        """
        Calculate match percentage between detected and required skills.
        
        Args:
            detected_skills (List[str]): Detected skills
            required_skills (List[str]): Required skills
            
        Returns:
            float: Match percentage (0-100)
        """
        if not required_skills:
            return 100.0
        
        matched_count = sum(1 for skill in required_skills if skill in detected_skills)
        percentage = (matched_count / len(required_skills)) * 100
        
        return percentage
    
    def _get_recommendation(self, score: float) -> str:
        """
        Get recommendation based on match score.
        
        Args:
            score (float): Match percentage
            
        Returns:
            str: Recommendation text
        """
        if score >= 80:
            return "Highly Recommended - You're a great fit!"
        elif score >= 60:
            return "Recommended - You have most required skills"
        elif score >= 40:
            return "Consider Applying - Some skills need development"
        else:
            return "Develop More Skills - This role requires significant skill growth"
    
    def get_skill_gaps(self, detected_skills: List[str], role_name: str) -> Dict:
        """
        Get detailed skill gaps for a specific role.
        
        Args:
            detected_skills (List[str]): Detected skills from resume
            role_name (str): Target role name
            
        Returns:
            Dict: Detailed skill gap analysis
        """
        if role_name not in self.job_roles:
            return {"error": f"Role '{role_name}' not found"}
        
        detected_skills_lower = [s.lower() for s in detected_skills]
        role_data = self.job_roles[role_name]
        required_skills = [s.lower() for s in role_data.get("required_skills", [])]
        nice_to_have = [s.lower() for s in role_data.get("nice_to_have", [])]
        
        return {
            "role": role_name,
            "have_required": [s for s in required_skills if s in detected_skills_lower],
            "missing_required": [s for s in required_skills if s not in detected_skills_lower],
            "have_nice": [s for s in nice_to_have if s in detected_skills_lower],
            "missing_nice": [s for s in nice_to_have if s not in detected_skills_lower],
            "priority_order": self._prioritize_missing(
                [s for s in required_skills if s not in detected_skills_lower]
            )
        }
    
    def _prioritize_missing(self, missing_skills: List[str]) -> List[str]:
        """
        Prioritize missing skills by importance (required before nice-to-have).
        
        Args:
            missing_skills (List[str]): List of missing skills
            
        Returns:
            List[str]: Prioritized list of skills to learn
        """
        return missing_skills  # Already in priority order (required skills first)
