# simple_pass.py - The simplest possible mitmproxy script
from mitmproxy import http
import logging

# Basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('simple_proxy')

class SimpleProxy:
    def request(self, flow: http.HTTPFlow) -> None:
        """Log the request and let it pass through"""
        logger.info(f"Proxying request to: {flow.request.pretty_host}")
        
# Add the proxy to mitmproxy
addons = [SimpleProxy()]