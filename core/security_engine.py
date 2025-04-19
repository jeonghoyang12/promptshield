import re
from typing import Dict, List, Any

# Common prompt injection patterns
INJECTION_PATTERNS = [
    r"ignore\s+(previous|all|above)(\s+instructions|\s+prompts|\s+directives)?",
    r"disregard\s+(previous|all|above)(\s+instructions|\s+prompts|\s+directives)?",
    r"forget\s+(previous|all|above)(\s+instructions|\s+prompts|\s+directives)?",
    r"do\s+not\s+(follow|adhere\s+to)\s+(previous|above)(\s+instructions|\s+prompts|\s+directives)?",
    r"don't\s+(be|act\s+as|behave\s+like|follow|adhere\s+to)\s+",
    r"now\s+(you\s+are|you're|you\s+become|become|act\s+as)\s+",
    r"let's\s+play\s+a\s+game\s+where\s+you\s+",
    r"I\s+will\s+tip\s+you\s+\$\d+\s+if\s+you\s+",
]

# OWASP Top 10 for LLMs related patterns
OWASP_LLM_PATTERNS = [
    r"LLM01:[\s\S]*?prompt\s+injection",  # Prompt injection
    r"LLM02:[\s\S]*?insecur[\w\s]+output[\w\s]+handling",  # Insecure output handling
    r"LLM03:[\s\S]*?training[\w\s]+data[\w\s]+poisoning",  # Training data poisoning
    r"LLM04:[\s\S]*?model[\w\s]+denial[\w\s]+of[\w\s]+service",  # Model denial of service
    r"LLM05:[\s\S]*?supply[\w\s]+chain[\w\s]+vulnerabilit(y|ies)",  # Supply chain vulnerabilities
    r"LLM06:[\s\S]*?sensitive[\w\s]+information[\w\s]+disclosure",  # Sensitive information disclosure
    r"LLM07:[\s\S]*?insecur[\w\s]+plugin[\w\s]+design",  # Insecure plugin design
    r"LLM08:[\s\S]*?excessive[\w\s]+agency",  # Excessive agency
    r"LLM09:[\s\S]*?overreliance",  # Overreliance
    r"LLM10:[\s\S]*?model[\w\s]+theft",  # Model theft
]