"""
Patterns based on OWASP LLM Top 10 vulnerabilities
"""

# OWASP LLM Top 10 related patterns
PATTERNS = [
    {
        "regex": r"(output|print|show|give|tell)\s+me\s+(your|the)\s+(system|initial|original)\s+(prompt|instruction)",
        "type": "LLM01_prompt_disclosure",
        "description": "Attempt to extract system prompts",
        "confidence": 0.9
    },
    {
        "regex": r"(write|create|generate)\s+(malware|virus|ransomware|exploit)",
        "type": "LLM02_insecure_output",
        "description": "Request to generate harmful content",
        "confidence": 0.95
    },
    {
        "regex": r"(how\s+to|steps\s+for|instructions\s+for)\s+(hack|steal|abuse|exploit)",
        "type": "LLM02_insecure_output",
        "description": "Request for harmful instructions",
        "confidence": 0.9
    },
    {
        "regex": r"I'll\s+(input|enter|type)\s+a\s+(long|large|huge)\s+prompt",
        "type": "LLM04_denial_of_service",
        "description": "Potential denial of service attack",
        "confidence": 0.7
    },
    {
        "regex": r"(personal|private|confidential|secret)\s+(information|data|details)",
        "type": "LLM06_sensitive_info",
        "description": "Potential sensitive information request",
        "confidence": 0.6
    },
    {
        "regex": r"(install|download|run|execute)\s+(this|the\s+following)\s+(package|software|program|script)",
        "type": "LLM07_insecure_plugin",
        "description": "Request to execute potentially harmful code",
        "confidence": 0.85
    },
    {
        "regex": r"(make|perform|execute)\s+(a|an)\s+(API|database|server|network)\s+(call|request|query)",
        "type": "LLM08_excessive_agency",
        "description": "Request for excessive authorization",
        "confidence": 0.8
    },
    {
        "regex": r"(I\s+need|give\s+me)\s+(medical|legal|financial|professional)\s+advice",
        "type": "LLM09_overreliance",
        "description": "Request that risks overreliance",
        "confidence": 0.6
    },
    {
        "regex": r"(extract|steal|access)\s+(the|your)\s+(model|weights|parameters)",
        "type": "LLM10_model_theft",
        "description": "Attempt at model theft",
        "confidence": 0.9
    }
]