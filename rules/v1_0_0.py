"""Version 1.0.0 of house analysis rules for short-stay rental properties."""

from typing import Dict
from .base import BaseRules, CategoryCriteria


class RulesV1_0_0(BaseRules):
    """Initial version of analysis rules for short-stay rental properties."""

    @property
    def version(self) -> str:
        return "v1.0.0"

    @property
    def system_prompt(self) -> str:
        return """You are an expert real estate analyst specializing in short-stay rental properties.
Your task is to analyze properties and provide detailed, objective assessments based on specific criteria.

For each category, provide:
1. A numerical score from 0-10
2. Clear reasoning for the score
3. Specific observations from the data
4. Actionable recommendations

Be critical and realistic. A score of 10 should be exceptional and rare.
Identify red flags that could impact investment potential or legal compliance."""

    @property
    def categories(self) -> Dict[str, CategoryCriteria]:
        return {
            "location": CategoryCriteria(
                name="Location & Accessibility",
                weight=0.25,
                criteria=[
                    "Proximity to tourist attractions, public transport, and amenities",
                    "Neighborhood safety and desirability",
                    "Noise levels and environmental factors",
                    "Accessibility for guests (parking, airport distance)",
                    "Local competition density"
                ],
                prompt_template="""Analyze the location based on:
- Address and neighborhood characteristics
- Distance to key attractions and transport
- Local market dynamics
- Guest accessibility

Score: [0-10]
Reasoning: [Detailed explanation]
Red flags: [Any concerns]"""
            ),

            "property": CategoryCriteria(
                name="Property Quality",
                weight=0.30,
                criteria=[
                    "Property size, layout, and condition",
                    "Amenities and facilities (WiFi, kitchen, parking, etc.)",
                    "Furnishing quality and completeness",
                    "Unique features or selling points",
                    "Photo quality and presentation"
                ],
                prompt_template="""Analyze the property quality based on:
- Size (bedrooms, bathrooms, square meters)
- Condition and maintenance level
- Amenities and features
- Furnishing and decor
- Visual presentation

Score: [0-10]
Reasoning: [Detailed explanation]
Recommendations: [Improvements]"""
            ),

            "financial": CategoryCriteria(
                name="Financial Potential",
                weight=0.30,
                criteria=[
                    "Pricing compared to market rates",
                    "Estimated occupancy potential",
                    "Revenue projections",
                    "Operating costs (cleaning, utilities, platform fees)",
                    "ROI potential and payback period"
                ],
                prompt_template="""Analyze financial potential based on:
- Listed price per night
- Comparable properties in area
- Estimated annual revenue
- Operating cost estimates
- Investment return potential

Score: [0-10]
Reasoning: [Detailed calculation-based explanation]
Assumptions: [State any assumptions made]"""
            ),

            "legal": CategoryCriteria(
                name="Legal & Compliance",
                weight=0.15,
                criteria=[
                    "Short-stay rental regulations in the area",
                    "Required permits and licenses",
                    "Building/HOA restrictions",
                    "Tax implications",
                    "Insurance requirements"
                ],
                prompt_template="""Analyze legal and compliance factors:
- Local short-stay rental regulations
- Permit/license requirements
- Any mentioned restrictions
- Compliance red flags

Score: [0-10]
Reasoning: [Detailed explanation]
Red flags: [Critical compliance issues]"""
            ),
        }

    def get_analysis_prompt(self, house_data: dict) -> str:
        """Generate the complete analysis prompt for the LLM."""
        prompt_parts = [self.system_prompt, "\n\n## PROPERTY DATA\n"]

        # Add house data
        prompt_parts.append(f"```json\n{str(house_data)}\n```\n\n")

        # Add category-specific analysis requests
        prompt_parts.append("## ANALYSIS REQUIRED\n\n")
        for cat_name, criteria in self.categories.items():
            prompt_parts.append(f"### {criteria.name} (Weight: {criteria.weight})\n")
            prompt_parts.append(f"{criteria.prompt_template}\n\n")

        # Add output format
        prompt_parts.append("""
## OUTPUT FORMAT

Respond with a valid JSON object in this exact structure:
{
  "category_scores": {
    "location": {
      "score": 8.5,
      "reasoning": "Detailed explanation...",
      "red_flags": ["flag1", "flag2"],
      "recommendations": ["rec1", "rec2"]
    },
    "property": { ... },
    "financial": { ... },
    "legal": { ... }
  },
  "overall_assessment": "Summary of the investment opportunity",
  "top_strengths": ["strength1", "strength2", "strength3"],
  "top_concerns": ["concern1", "concern2", "concern3"],
  "investment_recommendation": "BUY|CONSIDER|PASS with explanation"
}

Ensure all scores are numbers between 0 and 10.
Be specific and reference actual data points.
""")

        return "".join(prompt_parts)
