import os
import subprocess
import platform
import logging
import shutil

logger = logging.getLogger(__name__)

class CertificateManager:
    """Manage SSL certificates for HTTPS interception"""
    
    def __init__(self, cert_dir="./certs"):
        """
        Initialize the certificate manager
        
        Args:
            cert_dir (str): Directory to store certificates
        """
        self.cert_dir = cert_dir
        self.ca_cert_path = os.path.join(cert_dir, "mitmproxy-ca.pem")
        self.ca_cert_crt_path = os.path.join(cert_dir, "mitmproxy-ca-cert.crt")
        
        # Create cert directory if it doesn't exist
        if not os.path.exists(cert_dir):
            os.makedirs(cert_dir)
    
    def generate_certificates(self):
        """
        Generate a new certificate authority
        
        Returns:
            bool: Success or failure
        """
        try:
            # Check if mitmproxy certificates already exist
            mitmproxy_dir = os.path.expanduser("~/.mitmproxy")
            
            if not os.path.exists(mitmproxy_dir):
                os.makedirs(mitmproxy_dir, exist_ok=True)
                
                # Run mitmproxy once to generate certificates
                logger.info("Generating new mitmproxy certificates...")
                subprocess.run(["mitmdump", "--quiet", "-n"], capture_output=True, check=True)
            
            if os.path.exists(os.path.join(mitmproxy_dir, "mitmproxy-ca.pem")):
                # Copy existing certificates
                shutil.copy(os.path.join(mitmproxy_dir, "mitmproxy-ca.pem"), self.ca_cert_path)
                
                # Convert to .crt format for Windows
                self._convert_to_crt()
                return True
            else:
                logger.error("Certificates not found after generation attempt")
                return False
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to generate certificates: {e.stderr.decode() if e.stderr else str(e)}")
            return False
        except Exception as e:
            logger.error(f"Failed to generate certificates: {str(e)}")
            return False
    
    def _convert_to_crt(self):
        """
        Convert PEM to CRT format for Windows systems
        
        Returns:
            bool: Success or failure
        """
        try:
            subprocess.run(
                ["openssl", "x509", "-in", self.ca_cert_path, "-inform", "PEM", 
                "-out", self.ca_cert_crt_path],
                capture_output=True, check=True
            )
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to convert certificate to CRT: {e.stderr.decode() if e.stderr else str(e)}")
            return False
        except Exception as e:
            logger.error(f"Failed to convert certificate to CRT: {str(e)}")
            return False
    
    def install_certificate(self):
        """
        Install the certificate to the system trust store
        
        Returns:
            bool: Success or failure
        """
        system = platform.system()
        
        try:
            if system == "Windows":
                # Windows - uses certutil
                subprocess.run(
                    ["certutil", "-addstore", "ROOT", self.ca_cert_crt_path],
                    capture_output=True, check=True
                )
                logger.info("Certificate installed to Windows trust store")
            elif system == "Darwin":
                # macOS - uses security
                subprocess.run(
                    ["security", "add-trusted-cert", "-d", "-r", "trustRoot", 
                    "-k", "/Library/Keychains/System.keychain", self.ca_cert_path],
                    capture_output=True, check=True
                )
                logger.info("Certificate installed to macOS trust store")
            elif system == "Linux":
                # Linux - varies by distribution
                # This covers Ubuntu/Debian
                debian_path = "/usr/local/share/ca-certificates/mitmproxy-ca.crt"
                subprocess.run(["sudo", "cp", self.ca_cert_path, debian_path], 
                              capture_output=True, check=True)
                subprocess.run(["sudo", "update-ca-certificates"],
                              capture_output=True, check=True)
                logger.info("Certificate installed to Linux trust store")
            
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install certificate: {e.stderr.decode() if e.stderr else str(e)}")
            return False
        except Exception as e:
            logger.error(f"Failed to install certificate: {str(e)}")
            return False
    
    def uninstall_certificate(self):
        """
        Remove the certificate from the system trust store
        
        Returns:
            bool: Success or failure
        """
        system = platform.system()
        
        try:
            if system == "Windows":
                # Windows
                subprocess.run(
                    ["certutil", "-delstore", "ROOT", "mitmproxy"],
                    capture_output=True, check=True
                )
                logger.info("Certificate removed from Windows trust store")
            elif system == "Darwin":
                # macOS
                subprocess.run(
                    ["security", "remove-trusted-cert", "-d", self.ca_cert_path],
                    capture_output=True, check=True
                )
                logger.info("Certificate removed from macOS trust store")
            elif system == "Linux":
                # Linux (Ubuntu/Debian)
                debian_path = "/usr/local/share/ca-certificates/mitmproxy-ca.crt"
                if os.path.exists(debian_path):
                    subprocess.run(["sudo", "rm", debian_path],
                                  capture_output=True, check=True)
                    subprocess.run(["sudo", "update-ca-certificates", "--fresh"],
                                  capture_output=True, check=True)
                logger.info("Certificate removed from Linux trust store")
            
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to uninstall certificate: {e.stderr.decode() if e.stderr else str(e)}")
            return False
        except Exception as e:
            logger.error(f"Failed to uninstall certificate: {str(e)}")
            return False