"""
Skill extraction from resume text using keyword matching.
"""

import json
from pathlib import Path
from typing import List, Dict
from app.utils.text_cleaner import clean_text, normalize_skill_name


class SkillExtractor:
    """Extract skills from resume text using keyword matching."""
    
    def __init__(self, skills_json_path: str = "data/skills_list.json"):
        """
        Initialize skill extractor with skills database.
        
        Args:
            skills_json_path (str): Path to skills_list.json file
        """
        self.skills_db = self._load_skills(skills_json_path)
        self.all_skills = self._flatten_skills()
    
    def _load_skills(self, skills_json_path: str) -> Dict:
        """
        Load skills from JSON file.
        
        Args:
            skills_json_path (str): Path to skills JSON file
            
        Returns:
            Dict: Skills organized by category
        """
        try:
            with open(skills_json_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Skills database not found: {skills_json_path}")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON in skills database: {skills_json_path}")
    
    def _flatten_skills(self) -> List[str]:
        """
        Flatten skills from categorized structure into single list.
        
        Returns:
            List[str]: All skills in lowercase
        """
        all_skills = []
        for category, skills in self.skills_db.items():
            all_skills.extend([skill.lower() for skill in skills])
        return sorted(list(set(all_skills)))  # Remove duplicates and sort
    
    def extract_skills(self, text: str) -> Dict[str, List[str]]:
        """
        Extract skills from resume text using keyword matching.
        
        Args:
            text (str): Resume text (should be cleaned)
            
        Returns:
            Dict: Detected skills organized by category with match type
        """
        cleaned_text = clean_text(text)
        detected_skills = {
            "exact_matches": [],
            "partial_matches": [],
            "all_skills": []
        }
        
        # Exact matching
        exact_matches = self._exact_matching(cleaned_text)
        detected_skills["exact_matches"] = exact_matches
        
        # Partial matching (for multi-word skills)
        partial_matches = self._partial_matching(cleaned_text)
        detected_skills["partial_matches"] = partial_matches
        
        # Combine and deduplicate
        all_detected = list(set(exact_matches + partial_matches))
        detected_skills["all_skills"] = sorted(all_detected)
        
        return detected_skills
    
    def _exact_matching(self, text: str) -> List[str]:
        """
        Find exact matches of skills in text.
        
        Args:
            text (str): Cleaned text to search
            
        Returns:
            List[str]: Matched skills
        """
        matched_skills = []
        words = set(text.split())
        
        for skill in self.all_skills:
            # Handle multi-word skills
            if ' ' in skill:
                if skill in text:
                    matched_skills.append(skill)
            else:
                if skill in words:
                    matched_skills.append(skill)
        
        return matched_skills
    
    def _partial_matching(self, text: str) -> List[str]:
        """
        Find partial/fuzzy matches of skills in text.
        
        Args:
            text (str): Cleaned text to search
            
        Returns:
            List[str]: Partially matched skills
        """
        matched_skills = []
        
        # For multi-word skills, check if substring exists
        for skill in self.all_skills:
            if ' ' in skill and skill not in matched_skills:
                # Check if parts of the skill exist
                parts = skill.split()
                if len(parts) >= 2:
                    # Check if both parts are in text
                    if all(part in text for part in parts):
                        matched_skills.append(skill)
        
        return matched_skills
    
    def get_skills_by_category(self, text: str) -> Dict[str, List[str]]:
        """
        Get extracted skills organized by original category.
        
        Args:
            text (str): Resume text
            
        Returns:
            Dict: Skills grouped by category
        """
        detected = self.extract_skills(text)
        all_detected = detected["all_skills"]
        
        categorized = {}
        for category, skills in self.skills_db.items():
            skills_lower = [s.lower() for s in skills]
            matched = [skill for skill in all_detected if skill in skills_lower]
            if matched:
                categorized[category] = matched
        
        return categorized
