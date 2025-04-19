import os
import sys
import argparse
import logging

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

    # Set up logging
    log_level = logging.DEBUG if args.debug else logging.INFO