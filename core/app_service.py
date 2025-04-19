import os
import sys
import logging
import subprocess
import threading
import time
import json
import signal
import platform
from utils.cert_manager import CertificateManager
from utils.proxy_config import SystemProxyConfig

logger = logging.getLogger(__name__)

class AISecurityProxyService:
    """Main application service that manages the proxy and related components"""
    
    def __init__(self, proxy_host="127.0.0.1", proxy_port=8080, api_port=3001, config=None):
        """
        Initialize the service
        
        Args:
            proxy_host (str): Host to bind the proxy to
            proxy_port (int): Port for the proxy server
            api_port (int): Port for the API server
            config (dict, optional): Configuration dictionary
        """
        self.proxy_host = proxy_host
        self.proxy_port = proxy_port
        self.api_port = api_port
        self.config = config or {}
        
        # Initialize components
        cert_dir = self.config.get("cert_dir", "data/certs")
        self.cert_manager = CertificateManager(cert_dir=cert_dir)
        self.proxy_config = SystemProxyConfig(proxy_host, proxy_port)
        
        # Process handles
        self.proxy_process = None
        self.api_server_process = None
        self.running = False
    
    def start(self):
        """Start the proxy service"""
        if self.running:
            logger.warning("Service is already running")
            return False
        
        try:
            # Step 1: Ensure certificates are generated
            logger.info("Generating certificates...")
            if not self.cert_manager.generate_certificates():
                logger.error("Failed to generate certificates")
                return False
            
            # Step 2: Install certificate to system trust store
            logger.info("Installing certificate...")
            if not self.cert_manager.install_certificate():
                logger.warning("Failed to install certificate. User may need to install manually.")
            
            # Step 3: Configure system proxy
            logger.info("Configuring system proxy...")
            if not self.proxy_config.enable_proxy():
                logger.warning("Failed to configure system proxy. User may need to configure manually.")
            
            # Step 4: Start the proxy
            logger.info("Starting proxy server...")
            self._start_proxy_server()
            
            # Step 5: Start API server for the control panel
            logger.info("Starting API server...")
            self._start_api_server()
            
            self.running = True
            logger.info("AI Security Proxy Service started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start service: {str(e)}")
            self.stop()  # Clean up any partial setup
            return False
    
    def stop(self):
        """Stop the proxy service"""
        logger.info("Stopping AI Security Proxy Service...")
        self.running = False
        
        # Stop the proxy process
        if self.proxy_process:
            logger.info("Terminating proxy server...")
            try:
                if platform.system() == 'Windows':
                    self.proxy_process.send_signal(signal.CTRL_C_EVENT)
                else:
                    self.proxy_process.terminate()
                self.proxy_process.wait(timeout=5)
            except:
                self.proxy_process.kill()
            finally:
                self.proxy_process = None
        
        # Stop the API server
        if self.api_server_process:
            logger.info("Terminating API server...")
            try:
                if platform.system() == 'Windows':
                    self.api_server_process.send_signal(signal.CTRL_C_EVENT)
                else:
                    self.api_server_process.terminate()
                self.api_server_process.wait(timeout=5)
            except:
                self.api_server_process.kill()
            finally:
                self.api_server_process = None
        
        # Restore original proxy settings
        logger.info("Restoring system proxy settings...")
        self.proxy_config.disable_proxy()
        
        logger.info("AI Security Proxy Service stopped")
        return True
    
    def uninstall(self):
        """Uninstall the proxy and clean up"""
        logger.info("Uninstalling AI Security Proxy...")
        
        # Stop the service if it's running
        if self.running:
            self.stop()
        
        # Remove the certificate
        logger.info("Removing certificate...")
        self.cert_manager.uninstall_certificate()
        
        logger.info("Uninstallation complete")
        return True
    
    def _start_proxy_server(self):
        """Start the mitmproxy server"""
        # Create proxy server command
        cmd = [
            sys.executable,
            "-m", "mitmproxy.tools.main",
            "--listen-host", self.proxy_host,
            "--listen-port", str(self.proxy_port),
            "-s", os.path.join(os.path.dirname(__file__), "proxy_server.py")
        ]
        
        # Start the proxy as a subprocess
        self.proxy_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Give it a moment to start
        time.sleep(1)
        
        # Check if process is still running
        if self.proxy_process.poll() is not None:
            err = self.proxy_process.stderr.read().decode('utf-8')
            logger.error(f"Proxy server failed to start: {err}")
            self.proxy_process = None
            raise RuntimeError("Failed to start proxy server")
    
    def _start_api_server(self):
        """Start the API server for the control panel"""
        # Create API server command
        cmd = [
            sys.executable,
            os.path.join(os.path.dirname(os.path.dirname(__file__)), "api", "server.py"),
            "--host", self.proxy_host,
            "--port", str(self.api_port)
        ]
        
        # Start the API server as a subprocess
        self.api_server_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Give it a moment to start
        time.sleep(1)
        
        # Check if process is still running
        if self.api_server_process.poll() is not None:
            err = self.api_server_process.stderr.read().decode('utf-8')
            logger.error(f"API server failed to start: {err}")
            self.api_server_process = None
            raise RuntimeError("Failed to start API server")
    
    def run_forever(self):
        """Keep the service running until interrupted"""
        while self.running:
            # Check if processes are still running
            if self.proxy_process and self.proxy_process.poll() is not None:
                logger.error("Proxy server crashed, restarting...")
                self._start_proxy_server()
            
            if self.api_server_process and self.api_server_process.poll() is not None:
                logger.error("API server crashed, restarting...")
                self._start_api_server()
            
            time.sleep(5)