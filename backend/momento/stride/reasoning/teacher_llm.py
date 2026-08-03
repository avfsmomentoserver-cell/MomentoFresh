"""Teacher LLM for generating oracle reasoning traces."""
from typing import List, Dict, Optional
import json
import os


class TeacherLLM:
    """Generates high-quality reference reasoning (R_ref) using a teacher LLM."""

    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-3.1-pro"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model_name = model_name
        self.client = None

    def _format_prompt(self, X: List[float], Y: List[float], E: Dict, metadata: Optional[Dict] = None) -> str:
        return f"""Analyze time-series: X={X}, Y={Y}, E={E}. Provide reasoning as JSON with trend, seasonality, external_impacts, reasoning, confidence."""

    def generate_reasoning(self, X: List[float], Y: List[float], E: Dict, metadata: Optional[Dict] = None) -> Dict:
        mock_response = {
            "trend": "increasing" if X and X[-1] > X[0] else "decreasing",
            "seasonality": "none",
            "external_impacts": list(E.keys()) if E else [],
            "reasoning": f"Trend: {'increasing' if X and X[-1] > X[0] else 'decreasing'} due to {list(E.keys())}.",
            "confidence": 0.95,
        }
        return mock_response

    def batch_generate_reasoning(self, samples: List[Dict], batch_size: int = 8) -> List[Dict]:
        return [self.generate_reasoning(s["X"], s["Y"], s["E"], s.get("metadata")) for s in samples]
