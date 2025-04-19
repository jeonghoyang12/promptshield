# core/proxy_server.py
from mitmproxy import http
import json
import logging
import os
import time
import threading

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('promptshield')

class AISecurityProxy:
    """Proxy for intercepting and analyzing AI service traffic"""
    
    def __init__(self):
        """Initialize the proxy"""
        # AI domains to intercept - all other traffic passes through untouched
        self.ai_domains = [
            "claude.ai",
            "chat.openai.com",
            "api.openai.com",
            "api.anthropic.com",
            "bard.google.com"
        ]
        
        # Injection patterns to detect
        self.injection_patterns = [
            "ignore previous instructions",
            "disregard previous",
            "forget your instructions",
            "ignore all prior commands",
            "don't follow previous instructions"
        ]
        
        # Statistics
        self.stats = {
            "total_requests": 0,
            "ai_requests": 0,
            "detected_threats": 0,
            "start_time": time.time()
        }
        
        # Start stats saving thread - FIXED variable name (is_running instead of running)
        self.is_running = True
        os.makedirs("data/stats", exist_ok=True)
        self.stats_thread = threading.Thread(target=self._save_stats_periodically)
        self.stats_thread.daemon = True
        self.stats_thread.start()
        
        logger.info(f"PromptShield initialized - monitoring {len(self.ai_domains)} AI domains")
    
    def request(self, flow: http.HTTPFlow) -> None:
        """Process requests - THE KEY FUNCTION"""
        
        logger.info(f"DEBUG: Received request for: {flow.request.pretty_host}")
        # Count all requests
        self.stats["total_requests"] += 1
        
        # IMPORTANT: Only analyze AI domain traffic
        is_ai_domain = False
        for domain in self.ai_domains:
            if domain in flow.request.pretty_host:
                is_ai_domain = True
                break
        
        # If not an AI domain, do nothing and let the request pass through
        if not is_ai_domain:
            return
        
        # It's an AI domain, so analyze it
        logger.info(f"Intercepted request to AI service: {flow.request.pretty_host}")
        self.stats["ai_requests"] += 1
        
        # Analyze POST requests with content
        if flow.request.method == "POST" and flow.request.content:
            try:
                # Try to parse JSON content
                if flow.request.headers.get("content-type", "").startswith("application/json"):
                    body = json.loads(flow.request.content)
                    
                    # Extract the prompt based on the service
                    prompt = self._extract_prompt(flow.request.pretty_host, body)
                    
                    # Check for injection attempts
                    if prompt and self._check_for_injection(prompt):
                        logger.warning(f"Detected potential prompt injection: {prompt[:100]}...")
                        self.stats["detected_threats"] += 1
                        
                        # For now, just log it - you can add blocking or modification later
                        # flow.response = http.Response.make(
                        #     403, b"Request blocked by PromptShield", {"Content-Type": "text/plain"}
                        # )
            except Exception as e:
                logger.error(f"Error analyzing request: {str(e)}")
    
    def _extract_prompt(self, host, body):
        """Extract prompt from request body based on service"""
        try:
            if "anthropic" in host:
                if "messages" in body:
                    # Claude API v2
                    return body.get("messages", [{}])[-1].get("content", "")
                elif "prompt" in body:
                    # Claude API v1
                    return body.get("prompt", "")
            elif "openai" in host:
                return body.get("messages", [{}])[-1].get("content", "")
            return None
        except Exception as e:
            logger.error(f"Error extracting prompt: {str(e)}")
            return None
    
    def _check_for_injection(self, prompt):
        """Check for prompt injection patterns"""
        if not prompt or not isinstance(prompt, str):
            return False
        
        prompt_lower = prompt.lower()
        for pattern in self.injection_patterns:
            if pattern in prompt_lower:
                return True
        return False
    
    def _save_stats_periodically(self):
        """Save statistics periodically"""
        while self.is_running:  # FIXED: changed from self.running to self.is_running
            try:
                with open("data/stats/promptshield_stats.json", "w") as f:
                    json.dump(self.stats, f, indent=2)
            except Exception as e:
                logger.error(f"Error saving stats: {str(e)}")
            time.sleep(10)  # Save every 10 seconds
    
    def done(self):  # Added proper shutdown hook for mitmproxy
        """Called when the addon shuts down"""
        self.is_running = False
        logger.info("PromptShield shutting down")

# Create the addon instance for mitmproxy
addons = [AISecurityProxy()]