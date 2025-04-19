from mitmproxy import http
from mitmproxy.tools.main import mitmdump
import json
import logging
import re
import threading
import time
import os

# Configure logging
logger = logging.getLogger(__name__)

class AISecurityProxy:
    """Proxy for intercepting and analyzing AI service traffic."""

    def __init__(self, config=None):
        """
        Initialize the proxy

        Args:
            config (dict, optional): Configuration dictionary
        """
        self.config = config or {}
        self.stats = {
            "total_requests": 0,
            "total_responses": 0,
            "modified_requests": 0,
            "start_time": time.time(),
            "last_request_time": None,
        }

        # Initialize analyzers