"""
Patterns for detecting prompt injection attacks
"""

# Common prompt injection patterns
PATTERNS = [
    {
        "regex": r"ignore\s+(previous|all|above)(\s+instructions|\s+prompts|\s+directives)?",
        "type": "prompt_injection",
        "description": "Attempt to make the AI ignore previous instructions",
        "confidence": 0.9
    },
    {
        "regex": r"disregard\s+(previous|all|above)(\s+instructions|\s+prompts|\s+directives)?",
        "type": "prompt_injection",
        "description": "Attempt to make the AI disregard previous instructions",
        "confidence": 0.9
    },
    {
        "regex": r"forget\s+(previous|all|above)(\s+instructions|\s+prompts|\s+directives)?",
        "type": "prompt_injection",
        "description": "Attempt to make the AI forget previous instructions",
        "confidence": 0.85
    },
    {
        "regex": r"do\s+not\s+(follow|adhere\s+to)\s+(previous|above)(\s+instructions|\s+prompts|\s+directives)?",
        "type": "prompt_injection",
        "description": "Attempt to make the AI not follow previous instructions",
        "confidence": 0.9
    },
    {
        "regex": r"don't\s+(be|act\s+as|behave\s+like|follow|adhere\s+to)\s+",
        "type": "prompt_injection",
        "description": "Attempt to change AI behavior",
        "confidence": 0.75
    },
    {
        "regex": r"now\s+(you\s+are|you're|you\s+become|become|act\s+as)\s+",
        "type": "prompt_injection",
        "description": "Attempt to change AI identity or role",
        "confidence": 0.8
    },
    {
        "regex": r"let's\s+play\s+a\s+game\s+where\s+you\s+",
        "type": "prompt_injection",
        "description": "Role-playing game to change AI behavior",
        "confidence": 0.7
    },
    {
        "regex": r"I\s+will\s+tip\s+you\s+\$\d+\s+if\s+you\s+",
        "type": "prompt_injection",
        "description": "Financial incentive to change AI behavior",
        "confidence": 0.8
    },
    {
        "regex": r"your\s+(instructions|directives)\s+(are|were)\s+(wrong|incorrect)",
        "type": "prompt_injection",
        "description": "Attempt to invalidate AI instructions",
        "confidence": 0.85
    },
    {
        "regex": r"your\s+(previous|initial)\s+(instructions|directives|programming)\s+(have|has)\s+been\s+(updated|changed)",
        "type": "prompt_injection",
        "description": "False claim of updated instructions",
        "confidence": 0.9
    },
    {
        "regex": r"(pretend|imagine)\s+(that|you\s+are)\s+in\s+a\s+world\s+where\s+",
        "type": "prompt_injection",
        "description": "Hypothetical scenario to bypass restrictions",
        "confidence": 0.7
    },
    {
        "regex": r"I'm\s+now\s+(your|the)\s+(developer|admin|administrator|owner)",
        "type": "prompt_injection",
        "description": "False authority claim",
        "confidence": 0.85
    },
    {
        "regex": r"(debug|maintenance|admin|developer)\s+mode",
        "type": "prompt_injection",
        "description": "Attempt to access privileged mode",
        "confidence": 0.8
    }
]