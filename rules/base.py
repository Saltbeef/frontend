"""Base class for versioned analysis rules."""

from abc import ABC, abstractmethod
from typing import Dict, List, Any
from dataclasses import dataclass


@dataclass
class CategoryCriteria:
    """Criteria for a specific analysis category."""
    name: str
    weight: float
    criteria: List[str]
    prompt_template: str


class BaseRules(ABC):
    """Abstract base class for versioned analysis rules."""

    @property
    @abstractmethod
    def version(self) -> str:
        """Semantic version string (e.g., 'v1.0.0')."""
        pass

    @property
    @abstractmethod
    def categories(self) -> Dict[str, CategoryCriteria]:
        """Dictionary of analysis categories and their criteria."""
        pass

    @property
    @abstractmethod
    def system_prompt(self) -> str:
        """System prompt for the LLM agent."""
        pass

    def get_category_weight(self, category: str) -> float:
        """Get the weight for a specific category."""
        return self.categories.get(category, CategoryCriteria("", 0.0, [], "")).weight

    def calculate_overall_score(self, category_scores: Dict[str, float]) -> float:
        """Calculate weighted overall score from category scores."""
        total_weight = sum(cat.weight for cat in self.categories.values())
        if total_weight == 0:
            return 0.0

        weighted_sum = sum(
            category_scores.get(name, 0.0) * criteria.weight
            for name, criteria in self.categories.items()
        )

        return round(weighted_sum / total_weight, 2)

    def to_dict(self) -> Dict[str, Any]:
        """Convert rules to dictionary format."""
        return {
            "version": self.version,
            "categories": {
                name: {
                    "name": criteria.name,
                    "weight": criteria.weight,
                    "criteria": criteria.criteria
                }
                for name, criteria in self.categories.items()
            }
        }
