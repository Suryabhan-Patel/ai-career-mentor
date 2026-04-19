"""
AI-powered career explanation and recommendation service using Google Gemini API.
Generates personalized insights for career role matches.
"""

import os
import json
import logging
from typing import Dict, List, Optional
import google.generativeai as genai
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)


class AIExplainer:
    def __init__(self):
        """Initialize Gemini API"""
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            logger.warning("GEMINI_API_KEY not found. Using fallback mode.")
            self.available = False
            return

        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel("gemini-3-flash-preview")
            self.available = True
            logger.info("Gemini API initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini API: {str(e)}")
            self.available = False

    def generate_career_explanation(
        self,
        role: str,
        matched_skills: List[str],
        missing_skills: List[str],
        match_percentage: float = 0
    ) -> Optional[Dict]:

        if not self.available:
            return self._get_fallback_explanation(role, matched_skills, missing_skills)

        try:
            # safer defaults
            matched_skills = matched_skills or []
            missing_skills = missing_skills or []

            matched_str = ", ".join(matched_skills[:6])
            missing_str = ", ".join(missing_skills[:6])

            prompt = f"""
You are a professional AI career mentor.

Candidate Profile:
- Target Role: {role}
- Match Score: {match_percentage:.1f}%
- Strong Skills: {matched_str}
- Missing Skills: {missing_str}

Your tasks:
1. Explain clearly why this candidate is suitable for the role.
2. Highlight their strongest skills.
3. Suggest 3-4 specific actions to improve their chances.

Rules:
- Be specific and personalized
- Avoid generic statements
- Do not mention missing data like "0 skills"
- Keep explanation 3-4 lines
- Recommendations must be practical

Return ONLY valid JSON:

{{
  "explanation": "your explanation",
  "recommendations": [
    "action 1",
    "action 2",
    "action 3"
  ]
}}
"""

            response = self.model.generate_content(prompt)

            if not response or not response.text:
                return self._get_fallback_explanation(role, matched_skills, missing_skills)

            text = response.text.strip()

            # extract JSON safely
            if "{" in text and "}" in text:
                text = text[text.find("{"): text.rfind("}") + 1]

            result = json.loads(text)

            if "explanation" not in result or "recommendations" not in result:
                return self._get_fallback_explanation(role, matched_skills, missing_skills)

            if not isinstance(result["recommendations"], list):
                result["recommendations"] = [result["recommendations"]]

            return result

        except Exception as e:
            logger.error(f"Gemini error: {str(e)}")
            return self._get_fallback_explanation(role, matched_skills, missing_skills)

    def _get_fallback_explanation(
        self,
        role: str,
        matched_skills: List[str],
        missing_skills: List[str]
    ) -> Dict:

        matched_skills = matched_skills or []
        missing_skills = missing_skills or []

        top_skills = ", ".join(matched_skills[:3]) if matched_skills else "relevant foundational skills"

        explanation = (
            f"Your profile aligns with the {role} role, particularly through your skills in {top_skills}. "
            f"With additional focus on advanced areas, you can significantly strengthen your profile."
        )

        recommendations = []

        if missing_skills:
            recommendations.append(f"Focus on learning: {', '.join(missing_skills[:3])}")

        recommendations.extend([
            "Build 2-3 real-world projects demonstrating your skills",
            "Practice problem-solving and case-based scenarios",
            "Explore tools and frameworks commonly used in this role"
        ])

        return {
            "explanation": explanation,
            "recommendations": recommendations[:4]
        }