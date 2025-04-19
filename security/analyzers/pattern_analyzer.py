import re
import logging
import importlib
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class PatternAnalyzer:
    """Analyze prompts using regex patterns."""

    def __init__(self, pattern_modules=None):
        """
        Initialize the pattern analyzer
        
        Args:
            pattern_modules (list, optional): List of pattern module names to load
        """
        self.patterns = []

        # Default pattern modules
        if pattern_modules is None:
            pattern_modules = [
                "security.patterns.injection_patterns",
                "security.patterns.owasp_patterns",
            ]

        # Load pattern from modules
        for module_name in pattern_modules:
            try:
                module = importlib.import_module(module_name)
                if hasattr(module, "PATTERNS"):
                    self.patterns.extend(
                        {"pattern": pattern, "source": module_name}
                        for pattern in module.PATTERNS
                    )
            except ImportError as e:
                logger.error(f"Failed to load pattern module {module_name}: {str(e)}")

    def analyze(self, prompt: str) -> Dict[str, Any]:
        """
        Analyze the prompt for security threats

        Args:
            prompt (str): The prompt to analyze

        Returns:
            dict: Analysis results
        """
        result = {
            "is_dangerous": False,
            "threats": [],
            "confidence": 0.0,
            "matched_patterns": [],
        }

        # Check against each pattern
        for pattern_info in self.patterns:
            pattern = pattern_info["pattern"]

            # If pattern is a dict with regex and metadata
            if isinstance(pattern, dict):
                regex = pattern.get("regex", "")
                threat_type = pattern.get("type", "unknown")
                description = pattern.get("description", "")
                confidence = pattern.get("confidence", 0.8)
            else:
                # Simple string pattern
                regex = pattern
                threat_type = "prompt_injection"
                description = "Potential prompt injection detected"
                confidence = 0.8

             # Check for matches
            try:
                matches = list(re.finditer(regex, prompt, re.IGNORECASE))

                if matches:
                    result["is_dangerous"] = True
                    result["confidence"] = max(result["confidence"], confidence)
                    
                    # Add details for each match
                    for match in matches:
                        threat = {
                            "type": threat_type,
                            "description": description,
                            "confidence": confidence,
                            "matched_text": match.group(0),
                            "position": (match.start(), match.end()),
                        }
                        result["threats"].append(threat)
                        result["matched_patterns"].append(pattern_info)
            except re.error as e:
                logger.error(f"Invalid regex pattern: {regex}, error: {str(e)}")
    
        return result