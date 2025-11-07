"""Registry for managing versioned analysis rules."""

from typing import Dict, Type, Optional
from .base import BaseRules
from .v1_0_0 import RulesV1_0_0


class RulesRegistry:
    """Central registry for all rule versions."""

    _rules: Dict[str, Type[BaseRules]] = {
        "v1.0.0": RulesV1_0_0,
    }

    @classmethod
    def get_rules(cls, version: str = "latest") -> BaseRules:
        """
        Get rules instance for a specific version.

        Args:
            version: Version string (e.g., 'v1.0.0') or 'latest' for most recent

        Returns:
            Instance of the requested rules version

        Raises:
            ValueError: If version not found
        """
        if version == "latest":
            # Get the latest version (highest semantic version)
            version = cls.get_latest_version()

        rules_class = cls._rules.get(version)
        if not rules_class:
            available = ", ".join(cls._rules.keys())
            raise ValueError(
                f"Rules version '{version}' not found. "
                f"Available versions: {available}"
            )

        return rules_class()

    @classmethod
    def get_latest_version(cls) -> str:
        """Get the latest (most recent) rules version."""
        if not cls._rules:
            raise ValueError("No rules registered")

        # Sort versions semantically
        versions = sorted(
            cls._rules.keys(),
            key=lambda v: [int(x) for x in v.lstrip('v').split('.')],
            reverse=True
        )
        return versions[0]

    @classmethod
    def list_versions(cls) -> list[str]:
        """List all available rule versions."""
        return sorted(
            cls._rules.keys(),
            key=lambda v: [int(x) for x in v.lstrip('v').split('.')],
            reverse=True
        )

    @classmethod
    def register(cls, rules_class: Type[BaseRules]) -> None:
        """
        Register a new rules version.

        Args:
            rules_class: Rules class to register
        """
        instance = rules_class()
        version = instance.version
        if version in cls._rules:
            raise ValueError(f"Rules version '{version}' already registered")
        cls._rules[version] = rules_class


# Convenience function
def get_rules(version: str = "latest") -> BaseRules:
    """Get rules instance for a specific version."""
    return RulesRegistry.get_rules(version)
