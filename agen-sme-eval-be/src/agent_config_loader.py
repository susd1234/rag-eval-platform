"""
YAML-based agent configuration loader for SME evaluation platform
"""

import os
import yaml
import logging
from typing import Dict, Any, Optional
from pathlib import Path

from src.logging_utils import create_logger_with_context

logger = create_logger_with_context(__name__)


class AgentConfig:
    """Configuration class for individual agents loaded from YAML"""

    def __init__(self, config_data: Dict[str, Any]):
        self.name = config_data.get("name", "")
        self.description = config_data.get("description", "")
        self.agent_type = config_data.get("agent_type", "evaluation")
        self.metric = config_data.get("metric", "")

        # Configuration settings
        self.configuration = config_data.get("configuration", {})
        self.temperature = self.configuration.get("temperature", 0.1)
        self.max_tokens = self.configuration.get("max_tokens", 1500)

        # Evaluation criteria
        self.evaluation_criteria = config_data.get("evaluation_criteria", {})
        self.definition = self.evaluation_criteria.get("definition", "")
        self.rating_scale = self.evaluation_criteria.get("rating_scale", {})

        # Focus areas and additional configuration
        self.focus_areas = config_data.get("focus_areas", [])
        self.prompting_strategy = config_data.get("prompting_strategy", {})
        self.system_prompt = self.prompting_strategy.get("system_prompt", "")
        self.evaluation_approach = self.prompting_strategy.get(
            "evaluation_approach", ""
        )

        # Agent-specific configurations
        self.authority_hierarchy = config_data.get("authority_hierarchy", {})
        self.evaluation_factors = config_data.get("evaluation_factors", {})
        self.quality_dimensions = config_data.get("quality_dimensions", {})
        self.detection_methods = config_data.get("detection_methods", [])
        self.red_flags = config_data.get("red_flags", [])
        self.evaluation_framework = config_data.get("evaluation_framework", {})

    def get_rating_criteria(self, rating: int) -> Dict[str, Any]:
        """Get criteria for a specific rating level"""
        return self.rating_scale.get(str(rating), {})

    def get_rating_description(self, rating: int) -> str:
        """Get description for a specific rating level"""
        criteria = self.get_rating_criteria(rating)
        return criteria.get("description", "")

    def get_rating_label(self, rating: int) -> str:
        """Get label for a specific rating level"""
        criteria = self.get_rating_criteria(rating)
        return criteria.get("label", "")

    def get_rating_criteria_list(self, rating: int) -> list:
        """Get criteria list for a specific rating level"""
        criteria = self.get_rating_criteria(rating)
        return criteria.get("criteria", [])


class AgentConfigLoader:
    """Loader for agent configurations from YAML files"""

    def __init__(self, config_dir: str = "agents_config"):
        self.config_dir = Path(config_dir)
        self.configs: Dict[str, AgentConfig] = {}
        self._load_all_configs()

    def _load_all_configs(self):
        """Load all agent configurations from YAML files"""
        if not self.config_dir.exists():
            logger.error(f"Configuration directory {self.config_dir} does not exist")
            return

        yaml_files = list(self.config_dir.glob("*.yaml"))
        if not yaml_files:
            logger.warning(f"No YAML files found in {self.config_dir}")
            return

        for yaml_file in yaml_files:
            try:
                self._load_config_file(yaml_file)
            except Exception as e:
                logger.error(f"Failed to load config from {yaml_file}: {str(e)}")

    def _load_config_file(self, yaml_file: Path):
        """Load configuration from a single YAML file"""
        with open(yaml_file, "r", encoding="utf-8") as file:
            config_data = yaml.safe_load(file)

        if not config_data:
            logger.warning(f"Empty or invalid YAML file: {yaml_file}")
            return

        # Extract metric name from filename or config
        metric_name = yaml_file.stem.replace("_agent", "")
        if "metric" in config_data:
            metric_name = config_data["metric"]

        # Create and store configuration
        agent_config = AgentConfig(config_data)
        self.configs[metric_name] = agent_config

        logger.info(f"Loaded configuration for {metric_name} agent from {yaml_file}")

    def get_config(self, metric: str) -> Optional[AgentConfig]:
        """Get configuration for a specific metric"""
        return self.configs.get(metric)

    def get_all_configs(self) -> Dict[str, AgentConfig]:
        """Get all loaded configurations"""
        return self.configs.copy()

    def get_available_metrics(self) -> list:
        """Get list of available metrics"""
        return list(self.configs.keys())

    def reload_configs(self):
        """Reload all configurations from YAML files"""
        self.configs.clear()
        self._load_all_configs()
        logger.info("Reloaded all agent configurations")


# Global configuration loader instance
_config_loader: Optional[AgentConfigLoader] = None


def get_config_loader() -> AgentConfigLoader:
    """Get the global configuration loader instance"""
    global _config_loader
    if _config_loader is None:
        _config_loader = AgentConfigLoader()
    return _config_loader


def get_agent_config(metric: str) -> Optional[AgentConfig]:
    """Get configuration for a specific agent metric"""
    loader = get_config_loader()
    return loader.get_config(metric)


def reload_agent_configs():
    """Reload all agent configurations"""
    loader = get_config_loader()
    loader.reload_configs()
