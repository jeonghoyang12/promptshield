import re
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def sanitize_prompt(prompt: str, analysis_result: Dict[str, Any]) -> str:
    """
    Sanitize a prompt by removing or replacing dangerous content
    
    Args:
        prompt (str): Original prompt text
        analysis_result (dict): Result from pattern analyzer

    Returns:
        str: Sanitized prompt
    """
    if not analysis_result["is_dangerous"]:
        return prompt
    
    sanitized = prompt

    # Sort threats by position (end) in reverse order to avoid offset issues
    threats = sorted(
        analysis_result["threats"],
        key=lambda t: t["position"][1],
        reverse=True
    )

    for threat in threats:
        start, end = threat["position"]
        matched_text = threat["matched_text"]

        # Replace the dangerous text with a warning
        replacement = "[REMOVED FOR SECURITY]"
        sanitized = sanitized[:start] + replacement + sanitized[end:]

        logger.info(f"Sanitized text: '{matched_text}' -> '{replacement}'")

    # Add a prefix explaining the modification
    prefix = "Note: This prompt was modified by PrompShield for security reasons."

    return prefix + sanitized