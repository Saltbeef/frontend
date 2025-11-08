"""LLM agent orchestrator for house analysis."""

import os
import json
import time
from typing import Dict, Any, Optional
from datetime import datetime, timezone
import sys
from pathlib import Path

# Add parent directory to path to import rules
sys.path.insert(0, str(Path(__file__).parent.parent))

from rules import get_rules


class MockLLM:
    """Mock LLM for testing without API costs."""

    def analyze(self, prompt: str) -> str:
        """
        Generate mock analysis response.

        Args:
            prompt: Analysis prompt (ignored in mock)

        Returns:
            JSON string with mock analysis
        """
        return json.dumps({
            "category_scores": {
                "location": {
                    "score": 8.5,
                    "reasoning": "Mock analysis: Excellent central location with good transport links. Close to major attractions and amenities.",
                    "red_flags": ["High tourist area may mean noise issues"],
                    "recommendations": ["Verify noise insulation", "Check local parking availability"]
                },
                "property": {
                    "score": 7.5,
                    "reasoning": "Mock analysis: Well-maintained property with modern amenities. Good size for short-stay rentals.",
                    "red_flags": [],
                    "recommendations": ["Consider upgrading WiFi speed", "Add more photos of kitchen"]
                },
                "financial": {
                    "score": 8.0,
                    "reasoning": "Mock analysis: Strong revenue potential based on location. Pricing is competitive for the market.",
                    "red_flags": ["High competition in area"],
                    "recommendations": ["Dynamic pricing strategy recommended", "Calculate exact ROI with actual costs"]
                },
                "legal": {
                    "score": 7.0,
                    "reasoning": "Mock analysis: Standard short-stay regulations apply. License required but obtainable.",
                    "red_flags": ["Verify current licensing status", "Check HOA restrictions"],
                    "recommendations": ["Obtain legal opinion on local regulations", "Review insurance requirements"]
                }
            },
            "overall_assessment": "This property shows strong potential for short-stay rental investment. The location is excellent and the property condition is good. Main considerations are ensuring proper licensing and managing the competitive market.",
            "top_strengths": [
                "Prime central location",
                "Well-maintained property",
                "Strong revenue potential",
                "Good amenities for guests"
            ],
            "top_concerns": [
                "High competition in area",
                "Licensing requirements need verification",
                "Potential noise issues in tourist area"
            ],
            "investment_recommendation": "CONSIDER - Strong fundamentals but verify legal compliance and competitive positioning before proceeding"
        })


class ClaudeLLM:
    """Claude API integration for real analysis."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize Claude client."""
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable required")

        self.model = "claude-sonnet-4-5"
        self.api_url = "https://api.anthropic.com/v1/messages"

    def analyze(self, prompt: str) -> str:
        """
        Call Claude API for analysis.

        Args:
            prompt: Analysis prompt

        Returns:
            JSON string with analysis
        """
        import urllib.request
        import urllib.error

        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }

        body = {
            "model": self.model,
            "max_tokens": 8000,  # Increased for detailed v2.0.0 analyses with financial calculations
            "messages": [{
                "role": "user",
                "content": prompt
            }]
        }

        req = urllib.request.Request(
            self.api_url,
            data=json.dumps(body).encode('utf-8'),
            headers=headers,
            method='POST'
        )

        try:
            with urllib.request.urlopen(req, timeout=180) as response:  # Increased from 120s to 180s for 8000 token responses
                response_data = json.loads(response.read().decode('utf-8'))
                # Extract text from response
                content = response_data.get("content", [])
                if content and len(content) > 0:
                    return content[0].get("text", "")
                return ""
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            raise Exception(f"Claude API error: {e.code} {e.reason}\n{error_body}")


class OpenAILLM:
    """OpenAI API integration for real analysis."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize OpenAI client."""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable required")

        self.model = "gpt-4-turbo-preview"
        self.api_url = "https://api.openai.com/v1/chat/completions"

    def analyze(self, prompt: str) -> str:
        """
        Call OpenAI API for analysis.

        Args:
            prompt: Analysis prompt

        Returns:
            JSON string with analysis
        """
        import urllib.request
        import urllib.error

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        body = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "response_format": {"type": "json_object"}
        }

        req = urllib.request.Request(
            self.api_url,
            data=json.dumps(body).encode('utf-8'),
            headers=headers,
            method='POST'
        )

        try:
            with urllib.request.urlopen(req, timeout=180) as response:  # Increased from 120s to 180s for 8000 token responses
                response_data = json.loads(response.read().decode('utf-8'))
                choices = response_data.get("choices", [])
                if choices and len(choices) > 0:
                    return choices[0].get("message", {}).get("content", "")
                return ""
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            raise Exception(f"OpenAI API error: {e.code} {e.reason}\n{error_body}")


class HouseAnalysisAgent:
    """Orchestrator for house analysis using LLM."""

    def __init__(
        self,
        rules_version: str = "latest",
        llm_provider: str = "mock"
    ):
        """
        Initialize analysis agent.

        Args:
            rules_version: Version of rules to use (e.g., 'v1.0.0' or 'latest')
            llm_provider: LLM provider ('mock', 'claude', or 'openai')
        """
        self.rules = get_rules(rules_version)
        self.llm_provider = llm_provider

        # Initialize LLM client
        if llm_provider == "mock":
            self.llm = MockLLM()
        elif llm_provider == "claude":
            self.llm = ClaudeLLM()
        elif llm_provider == "openai":
            self.llm = OpenAILLM()
        else:
            raise ValueError(f"Unknown LLM provider: {llm_provider}")

    def analyze_house(
        self,
        house_data: Dict[str, Any],
        house_id: str,
        apify_dataset_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze a house using the configured rules and LLM.

        Args:
            house_data: Raw house data from Apify
            house_id: Unique identifier for the house
            apify_dataset_id: Optional Apify dataset ID for metadata

        Returns:
            Complete analysis result
        """
        start_time = time.time()

        # Generate analysis prompt
        prompt = self.rules.get_analysis_prompt(house_data)

        # Get LLM analysis
        print(f"Analyzing house {house_id} using {self.llm_provider}...")
        llm_response = self.llm.analyze(prompt)

        # Parse response
        try:
            # Extract JSON from response (handle markdown code blocks)
            response_text = llm_response.strip()
            if response_text.startswith("```"):
                # Remove markdown code block markers
                lines = response_text.split("\n")
                response_text = "\n".join(lines[1:-1]) if len(lines) > 2 else response_text

            analysis_data = json.loads(response_text)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse LLM response as JSON: {e}\n{llm_response}")

        # Calculate overall score
        category_scores = analysis_data.get("category_scores", {})
        score_values = {
            name: cat_data.get("score", 0.0)
            for name, cat_data in category_scores.items()
        }
        overall_score = self.rules.calculate_overall_score(score_values)

        # Build complete analysis result
        result = {
            "house_id": house_id,
            "analyzed_at": datetime.now(timezone.utc).isoformat(),
            "rules_version": self.rules.version,
            "overall_score": overall_score,
            "category_scores": category_scores,
            "overall_assessment": analysis_data.get("overall_assessment", ""),
            "top_strengths": analysis_data.get("top_strengths", []),
            "top_concerns": analysis_data.get("top_concerns", []),
            "investment_recommendation": analysis_data.get("investment_recommendation", ""),
            "metadata": {
                "processing_time_seconds": round(time.time() - start_time, 2),
                "llm_model": self.llm_provider,
            }
        }

        if apify_dataset_id:
            result["metadata"]["apify_dataset_id"] = apify_dataset_id

        return result

    def validate_analysis(self, analysis: Dict[str, Any]) -> bool:
        """
        Validate analysis result against schema.

        Args:
            analysis: Analysis result to validate

        Returns:
            True if valid

        Raises:
            ValueError: If validation fails
        """
        required_fields = [
            "house_id", "analyzed_at", "rules_version",
            "overall_score", "category_scores"
        ]

        for field in required_fields:
            if field not in analysis:
                raise ValueError(f"Missing required field: {field}")

        # Validate scores are in range
        if not (0 <= analysis["overall_score"] <= 10):
            raise ValueError(f"Overall score out of range: {analysis['overall_score']}")

        for cat_name, cat_data in analysis["category_scores"].items():
            score = cat_data.get("score", -1)
            if not (0 <= score <= 10):
                raise ValueError(f"Category {cat_name} score out of range: {score}")

        return True
