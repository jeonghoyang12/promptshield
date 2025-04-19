import os
import sys
import argparse
import logging
import time
import signal
import threading
from core.app_service import AISecurityProxyService
from config.settings import load_config
from utils.logging_utils import setup_logging

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="AI Security Proxy")
    parser.add_argument("--config", help="Path to the configuration file")
    parser.add_argument("--uninstall", action="store_true", help="Uninstall the proxy")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    return parser.parse_args()

def main():
    """Main entry point"""
    args = parse_args()

    # Setup logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    setup_logging(log_level)
    logger = logging.getLogger(__name__)
    
    # Load configuration
    config_path = args.config
    config = load_config(config_path)
    
    # Create service instance
    service = AISecurityProxyService(
        proxy_host=config.get("proxy_host", "127.0.0.1"),
        proxy_port=config.get("proxy_port", 8080),
        api_port=config.get("api_port", 3001),
        config=config
    )
    
    # Handle uninstall
    if args.uninstall:
        logger.info("Uninstalling PromptShield...")
        return service.uninstall()
    
    # Setup signal handlers for graceful shutdown
    def signal_handler(sig, frame):
        logger.info("Received shutdown signal, stopping services...")
        service.stop()
        sys.exit(0)
        
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start the service
    try:
        if service.start():
            logger.info(f"PromptShield is running on {config.get('proxy_host', '127.0.0.1')}:{config.get('proxy_port', 8080)}")
            logger.info(f"API server is running on {config.get('proxy_host', '127.0.0.1')}:{config.get('api_port', 3001)}")
            logger.info("Press Ctrl+C to stop the service.")
            
            # Keep main thread alive
            while True:
                time.sleep(1)
        else:
            logger.error("Failed to start the service.")
            return 1
    except KeyboardInterrupt:
        logger.info("Shutting down PromptShield...")
    finally:
        service.stop()
        
    return 0

if __name__ == "__main__":
    sys.exit(main())