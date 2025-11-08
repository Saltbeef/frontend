"""Markdown report generator for analysis results."""

import json
from pathlib import Path
from typing import Dict, Any


class MarkdownGenerator:
    """Generate Markdown reports from analysis results."""

    def generate(self, analysis: Dict[str, Any]) -> str:
        """
        Generate Markdown report from analysis result.

        Args:
            analysis: Analysis result dictionary

        Returns:
            Markdown report string
        """
        lines = []

        # Header
        lines.append(f"# 🏠 Analyse Rapport: {analysis.get('house_id', 'Unknown')}")
        lines.append("")
        lines.append(f"**Geanalyseerd op:** {analysis.get('analyzed_at', '')}")
        lines.append(f"**Rules Versie:** {analysis.get('rules_version', '')}")
        lines.append("")

        # Overall Score
        score = analysis.get('overall_score', 0)
        lines.append("## 📊 Overall Score")
        lines.append("")
        lines.append(f"### {score:.2f} / 10")
        lines.append("")

        # Investment Recommendation
        recommendation = analysis.get('investment_recommendation', '')
        rec_emoji = self._get_recommendation_emoji(recommendation)
        lines.append(f"**{rec_emoji} Aanbeveling:** {recommendation}")
        lines.append("")

        # Red Flags (v2.0.0+)
        if analysis.get('category_scores'):
            all_red_flags = []
            for cat_name, cat_data in analysis.get('category_scores', {}).items():
                if isinstance(cat_data, dict) and cat_data.get('red_flags'):
                    all_red_flags.extend(cat_data['red_flags'])

            if all_red_flags:
                lines.append("## 🚨 Red Flags")
                lines.append("")
                for flag in all_red_flags:
                    lines.append(f"- ⚠️ {flag}")
                lines.append("")

        # Financial Breakdown (v2.0.0+)
        financial_cat = None
        if analysis.get('category_scores'):
            financial_cat = analysis.get('category_scores', {}).get('financial')

        if financial_cat and financial_cat.get('calculations'):
            calc = financial_cat['calculations']
            lines.append("## 💰 Financiële Berekening")
            lines.append("")
            lines.append("| Item | Bedrag |")
            lines.append("|------|--------|")

            if calc.get('purchase_price'):
                lines.append(f"| Aankoopprijs | €{calc['purchase_price']:,.0f} |")
            if calc.get('total_investment'):
                lines.append(f"| Totale investering | €{calc['total_investment']:,.0f} |")
            if calc.get('estimated_annual_revenue'):
                lines.append(f"| Geschatte jaaromzet | €{calc['estimated_annual_revenue']:,.0f} |")
            if calc.get('estimated_annual_costs'):
                lines.append(f"| Geschatte jaarkosten | €{calc['estimated_annual_costs']:,.0f} |")
            if calc.get('net_annual_income'):
                lines.append(f"| **Netto jaarinkomen** | **€{calc['net_annual_income']:,.0f}** |")
            if calc.get('cash_on_cash_return'):
                coc = calc['cash_on_cash_return']
                emoji = "🟢" if coc >= 15 else "🔵" if coc >= 10 else "🟠"
                lines.append(f"| **Cash-on-Cash Return** | **{emoji} {coc:.1f}%** |")
            if calc.get('breakeven_years'):
                lines.append(f"| Break-even periode | {calc['breakeven_years']:.1f} jaar |")

            lines.append("")

        # Category Scores
        lines.append("## 📋 Categorie Scores")
        lines.append("")

        for cat_name, cat_data in analysis.get('category_scores', {}).items():
            if isinstance(cat_data, dict):
                cat_score = cat_data.get('score', 0)
                cat_display_name = cat_data.get('name', cat_name)

                # Score bar (0-10 scale)
                bar_length = int(cat_score)
                bar = "█" * bar_length + "░" * (10 - bar_length)

                lines.append(f"### {cat_display_name}")
                lines.append(f"**Score:** {cat_score:.1f}/10 `{bar}`")
                lines.append("")

                # Reasoning
                if cat_data.get('reasoning'):
                    lines.append(f"**Redenering:**")
                    lines.append(cat_data['reasoning'])
                    lines.append("")

                # Red flags for this category
                if cat_data.get('red_flags'):
                    lines.append("**Rode vlaggen:**")
                    for flag in cat_data['red_flags']:
                        lines.append(f"- ⚠️ {flag}")
                    lines.append("")

                # Recommendations
                if cat_data.get('recommendations'):
                    lines.append("**Aanbevelingen:**")
                    for rec in cat_data['recommendations']:
                        lines.append(f"- 💡 {rec}")
                    lines.append("")

        # Overall Assessment
        lines.append("## 📝 Overall Assessment")
        lines.append("")
        lines.append(analysis.get('overall_assessment', ''))
        lines.append("")

        # Strengths
        if analysis.get('top_strengths'):
            lines.append("## 💪 Sterke Punten")
            lines.append("")
            for strength in analysis['top_strengths']:
                lines.append(f"- ✅ {strength}")
            lines.append("")

        # Concerns
        if analysis.get('top_concerns'):
            lines.append("## ⚠️ Zorgen")
            lines.append("")
            for concern in analysis['top_concerns']:
                lines.append(f"- ⚠️ {concern}")
            lines.append("")

        # Action Plan (v2.0.0+)
        if analysis.get('action_plan'):
            lines.append("## 🎯 Actieplan")
            lines.append("")
            for i, action in enumerate(analysis['action_plan'], 1):
                lines.append(f"{i}. {action}")
            lines.append("")

        # Scale-up Potential (v2.0.0+)
        if analysis.get('scale_up_potential'):
            lines.append("## 📈 Scale-up Potentieel")
            lines.append("")
            lines.append(analysis['scale_up_potential'])
            lines.append("")

        # Metadata
        if analysis.get('metadata'):
            lines.append("---")
            lines.append("")
            lines.append("## 🔧 Metadata")
            lines.append("")
            metadata = analysis['metadata']
            lines.append(f"- **Apify Dataset ID:** {metadata.get('apify_dataset_id', 'N/A')}")
            lines.append(f"- **LLM Provider:** {metadata.get('llm_provider', 'N/A')}")
            lines.append(f"- **Processing Time:** {metadata.get('processing_time_seconds', 'N/A')}s")
            lines.append("")

        return "\n".join(lines)

    def _get_recommendation_emoji(self, recommendation: str) -> str:
        """Get emoji for investment recommendation."""
        rec_upper = recommendation.upper()
        if "KOPEN" in rec_upper or "BUY" in rec_upper:
            return "✅"
        elif "AFWIJZEN" in rec_upper or "PASS" in rec_upper:
            return "❌"
        elif "OVERWEGEN" in rec_upper or "CONSIDER" in rec_upper:
            return "⚠️"
        else:
            return "ℹ️"

    def save(self, analysis: Dict[str, Any], output_path: Path) -> None:
        """
        Generate and save Markdown report to file.

        Args:
            analysis: Analysis result dictionary
            output_path: Path to save the markdown file
        """
        markdown = self.generate(analysis)

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown)


def generate_markdown_report(analysis: Dict[str, Any], output_path: Path) -> None:
    """
    Convenience function to generate and save markdown report.

    Args:
        analysis: Analysis result dictionary
        output_path: Path to save the markdown file
    """
    generator = MarkdownGenerator()
    generator.save(analysis, output_path)
