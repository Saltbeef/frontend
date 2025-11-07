"""HTML report generator for analysis results."""

import json
from pathlib import Path
from typing import Dict, Any


class ReportGenerator:
    """Generate HTML reports from analysis results."""

    def __init__(self, template_path: str = None):
        """
        Initialize report generator.

        Args:
            template_path: Path to HTML template file
        """
        if template_path is None:
            # Default to templates/report.html relative to this file
            base_dir = Path(__file__).parent.parent
            template_path = base_dir / "templates" / "report.html"

        self.template_path = Path(template_path)

        if not self.template_path.exists():
            raise FileNotFoundError(f"Template not found: {self.template_path}")

        with open(self.template_path, 'r') as f:
            self.template = f.read()

    def generate(self, analysis: Dict[str, Any]) -> str:
        """
        Generate HTML report from analysis result.

        Args:
            analysis: Analysis result dictionary

        Returns:
            HTML report string
        """
        # Prepare template variables
        context = {
            "house_id": analysis.get("house_id", "Unknown"),
            "analyzed_at": analysis.get("analyzed_at", ""),
            "rules_version": analysis.get("rules_version", ""),
            "overall_score": analysis.get("overall_score", 0),
            "category_scores": analysis.get("category_scores", {}),
            "overall_assessment": analysis.get("overall_assessment", ""),
            "top_strengths": analysis.get("top_strengths", []),
            "top_concerns": analysis.get("top_concerns", []),
            "investment_recommendation": analysis.get("investment_recommendation", ""),
            "metadata": analysis.get("metadata", {})
        }

        # Determine recommendation class for styling
        rec = context["investment_recommendation"].upper()
        if "BUY" in rec:
            context["recommendation_class"] = "buy"
        elif "PASS" in rec:
            context["recommendation_class"] = "pass"
        else:
            context["recommendation_class"] = "consider"

        # Simple template rendering (replace with Jinja2 for production)
        html = self._render_simple(self.template, context)

        return html

    def _render_simple(self, template: str, context: Dict[str, Any]) -> str:
        """
        Simple template rendering without external dependencies.

        For production, consider using Jinja2.

        Args:
            template: HTML template string
            context: Template variables

        Returns:
            Rendered HTML
        """
        html = template

        # Replace simple variables {{ var }}
        for key, value in context.items():
            if isinstance(value, (str, int, float)):
                html = html.replace(f"{{{{ {key} }}}}", str(value))

        # Handle category_scores loop {% for ... %}
        category_html = ""
        for cat_name, cat_data in context["category_scores"].items():
            category_block = f"""
            <div class="category">
                <h2>
                    <span>{cat_name.replace('_', ' ').title()}</span>
                    <span class="category-score">{cat_data.get('score', 0)}/10</span>
                </h2>

                <div class="reasoning">
                    {cat_data.get('reasoning', '')}
                </div>
            """

            # Red flags
            red_flags = cat_data.get('red_flags', [])
            if red_flags:
                category_block += """
                <div class="flags">
                    <h3>⚠️ Red Flags</h3>
                """
                for flag in red_flags:
                    category_block += f'<div class="flag-item">{flag}</div>'
                category_block += "</div>"

            # Recommendations
            recommendations = cat_data.get('recommendations', [])
            if recommendations:
                category_block += """
                <div class="recommendations">
                    <h3>💡 Recommendations</h3>
                """
                for rec in recommendations:
                    category_block += f'<div class="rec-item">{rec}</div>'
                category_block += "</div>"

            category_block += "</div>"
            category_html += category_block

        # Replace category loop
        html = html.split("{% for category_name, category_data in category_scores.items() %}")[0] + \
               category_html + \
               html.split("{% endfor %}")[1] if "{% for category_name" in html else html

        # Handle conditional blocks
        if context.get("overall_assessment"):
            html = html.replace("{% if overall_assessment %}", "")
            html = html.replace("{% endif %}", "")
        else:
            # Remove section if empty
            start = html.find("{% if overall_assessment %}")
            if start != -1:
                end = html.find("{% endif %}", start)
                if end != -1:
                    html = html[:start] + html[end + 11:]

        # Handle top_strengths list
        if context.get("top_strengths"):
            strengths_html = ""
            for strength in context["top_strengths"]:
                strengths_html += f"<li>{strength}</li>"
            html = html.replace("{% for strength in top_strengths %}", "")
            html = html.replace("{% endfor %}", "")
            html = html.replace("{{ strength }}", strengths_html)

        # Handle top_concerns list
        if context.get("top_concerns"):
            concerns_html = ""
            for concern in context["top_concerns"]:
                concerns_html += f"<li>{concern}</li>"
            html = html.replace("{% for concern in top_concerns %}", "")
            html = html.replace("{{ concern }}", concerns_html)

        # Handle metadata conditionals
        if context.get("metadata"):
            html = html.replace("{% if metadata %}", "")
            metadata = context["metadata"]
            html = html.replace("{{ metadata.llm_model }}", str(metadata.get("llm_model", "Unknown")))
            html = html.replace("{{ metadata.processing_time_seconds }}", str(metadata.get("processing_time_seconds", 0)))
        else:
            # Remove metadata section
            start = html.find("{% if metadata %}")
            if start != -1:
                end = html.find("{% endif %}", start)
                if end != -1:
                    html = html[:start] + html[end + 11:]

        # Clean up any remaining template tags
        html = html.replace("{% if top_strengths %}", "")
        html = html.replace("{% if top_concerns %}", "")
        html = html.replace("{% endif %}", "")

        return html

    def save(self, analysis: Dict[str, Any], output_path: str) -> None:
        """
        Generate and save HTML report to file.

        Args:
            analysis: Analysis result dictionary
            output_path: Path to save HTML file
        """
        html = self.generate(analysis)

        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w') as f:
            f.write(html)

        print(f"Report saved to: {output_file}")
