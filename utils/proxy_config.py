import subprocess
import platform
import logging
import os
import sys

logger = logging.getLogger(__name__)

class SystemProxyConfig:
    """Configure system proxy settings"""
    
    def __init__(self, proxy_host="127.0.0.1", proxy_port=8080):
        """
        Initialize the proxy configuration
        
        Args:
            proxy_host (str): Proxy server hostname
            proxy_port (int): Proxy server port
        """
        self.proxy_host = proxy_host
        self.proxy_port = proxy_port
        self.proxy_url = f"{proxy_host}:{proxy_port}"
        self.system = platform.system()
        self.original_settings = self._get_current_settings()
    
    def _get_current_settings(self):
        """
        Get the current proxy settings to restore later
        
        Returns:
            dict: Current proxy settings
        """
        settings = {"enabled": False, "server": "", "bypass": ""}
        
        try:
            if self.system == "Windows":
                # Windows registry approach
                try:
                    import winreg
                    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                       r"Software\Microsoft\Windows\CurrentVersion\Internet Settings", 
                                       0, winreg.KEY_READ) as key:
                        settings["enabled"] = winreg.QueryValueEx(key, "ProxyEnable")[0]
                        settings["server"] = winreg.QueryValueEx(key, "ProxyServer")[0]
                        try:
                            settings["bypass"] = winreg.QueryValueEx(key, "ProxyOverride")[0]
                        except:
                            settings["bypass"] = ""
                except ImportError:
                    logger.error("Failed to import winreg module")
                except Exception as e:
                    logger.error(f"Failed to read Windows registry: {str(e)}")
                    
            elif self.system == "Darwin":
                # macOS
                try:
                    # Get list of network services, skip the first line which is a header
                    network_output = subprocess.check_output(["networksetup", "-listallnetworkservices"]).decode().split('\n')
                    networks = []
                    for line in network_output[1:]:  # Skip the first line
                        if line and not line.startswith('*'):  # Skip empty lines and disabled services
                            networks.append(line)
                    
                    settings["networks"] = []
                    
                    for network in networks:
                        try:
                            # Check if the network is active
                            proxy_state = subprocess.check_output(
                                ["networksetup", "-getwebproxystate", network]).decode().strip()
                            proxy_server = subprocess.check_output(
                                ["networksetup", "-getwebproxy", network]).decode().strip()
                            
                            enabled = "Enabled: Yes" in proxy_state
                            server = ""
                            port = ""
                            
                            for line in proxy_server.split('\n'):
                                if "Server:" in line:
                                    server = line.split(': ')[1]
                                if "Port:" in line:
                                    port = line.split(': ')[1]
                            
                            if server and port:
                                server_with_port = f"{server}:{port}"
                            else:
                                server_with_port = ""
                            
                            settings["networks"].append({
                                "name": network,
                                "enabled": enabled,
                                "server": server_with_port
                            })
                        except subprocess.CalledProcessError:
                            logger.warning(f"Could not get proxy settings for network {network}, skipping")
                            continue
                        except Exception as e:
                            logger.error(f"Error getting proxy settings for network {network}: {str(e)}")
                except Exception as e:
                    logger.error(f"Failed to get macOS proxy settings: {str(e)}")
                    
            elif self.system == "Linux":
                # Linux - check environment variables
                settings["http_proxy"] = os.environ.get("http_proxy", "")
                settings["https_proxy"] = os.environ.get("https_proxy", "")
                
                # Check GNOME settings if available
                try:
                    mode = subprocess.check_output(
                        ["gsettings", "get", "org.gnome.system.proxy", "mode"]).decode().strip()
                    settings["gnome_mode"] = mode
                    
                    if mode == "'manual'":
                        host = subprocess.check_output(
                            ["gsettings", "get", "org.gnome.system.proxy.http", "host"]).decode().strip()
                        port = subprocess.check_output(
                            ["gsettings", "get", "org.gnome.system.proxy.http", "port"]).decode().strip()
                        settings["gnome_http_host"] = host
                        settings["gnome_http_port"] = port
                except:
                    pass
        except Exception as e:
            logger.error(f"Failed to get current proxy settings: {str(e)}")
        
        return settings
    
    def enable_proxy(self):
        """
        Enable the proxy for system traffic
        
        Returns:
            bool: Success or failure
        """
        try:
            # Define bypass domains - only intercept AI domains, bypass everything else
            # This is a CRITICAL fix to maintain normal internet access
            bypass_list = [
                "localhost",
                "127.0.0.1",
                "*.local",
                "10.*",
                "192.168.*",
                "172.16.*",
                "172.17.*",
                "172.18.*",
                "172.19.*",
                "172.2*.*",
                "172.30.*",
                "172.31.*",
                "<local>"
            ]
            
            # Only intercept traffic to AI domains
            # By creating a bypass for everything except these domains, the proxy is
            # effectively selective and will only process traffic to AI services
            ai_domains = [
                "claude.ai",
                "chat.openai.com",
                "api.openai.com",
                "api.anthropic.com", 
                "bard.google.com"
            ]
            
            if self.system == "Windows":
                try:
                    import ctypes
                    import winreg
                    
                    # Set Windows proxy settings
                    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                       r"Software\Microsoft\Windows\CurrentVersion\Internet Settings", 
                                       0, winreg.KEY_WRITE) as key:
                        winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, 1)
                        winreg.SetValueEx(key, "ProxyServer", 0, winreg.REG_SZ, self.proxy_url)
                        
                        # Use the correct bypass list
                        bypass = ";".join(bypass_list)
                        winreg.SetValueEx(key, "ProxyOverride", 0, winreg.REG_SZ, bypass)
                    
                    # Notify system of the change
                    try:
                        subprocess.call(["netsh", "winhttp", "import", "proxy", "source=ie"])
                    except:
                        pass
                    
                    # Refresh Internet Explorer settings
                    try:
                        INTERNET_OPTION_REFRESH = 37
                        INTERNET_OPTION_SETTINGS_CHANGED = 39
                        ctypes.windll.Wininet.InternetSetOptionW(0, INTERNET_OPTION_SETTINGS_CHANGED, 0, 0)
                        ctypes.windll.Wininet.InternetSetOptionW(0, INTERNET_OPTION_REFRESH, 0, 0)
                    except:
                        pass
                    
                    logger.info("Enabled proxy on Windows")
                    return True
                except ImportError:
                    logger.error("Failed to import required modules for Windows proxy configuration")
                    return False
                except Exception as e:
                    logger.error(f"Failed to set Windows proxy: {str(e)}")
                    return False
                
            elif self.system == "Darwin":
                # macOS
                success = True
                try:
                    networks = []
                    network_output = subprocess.check_output(["networksetup", "-listallnetworkservices"]).decode().split('\n')
                    for line in network_output[1:]:  # Skip the first line
                        if line and not line.startswith('*'):  # Skip empty lines and disabled services
                            networks.append(line)
                    
                    for network in networks:
                        try:
                            # Get the current bypass domains
                            bypass_domains = subprocess.check_output(
                                ["networksetup", "-getproxybypassdomains", network]).decode().strip()
                            
                            # If no bypass domains are set, bypass_domains will be "There aren't any bypass domains set on xxxx."
                            # So we need to initialize an empty list in that case
                            bypass_domains_list = []
                            if not bypass_domains.startswith("There aren't any bypass domains"):
                                bypass_domains_list = bypass_domains.split("\n")
                            
                            # Add all our bypass domains
                            bypass_domains_list.extend(bypass_list)
                            
                            # Enable proxy for HTTP
                            subprocess.run(["networksetup", "-setwebproxy", 
                                           network, self.proxy_host, str(self.proxy_port)])
                            
                            # Enable proxy for HTTPS
                            subprocess.run(["networksetup", "-setsecurewebproxy", 
                                           network, self.proxy_host, str(self.proxy_port)])
                            
                            # Set bypass domains
                            subprocess.run(["networksetup", "-setproxybypassdomains", 
                                          network] + bypass_domains_list)
                            
                            # Turn on proxies
                            subprocess.run(["networksetup", "-setwebproxystate", network, "on"])
                            subprocess.run(["networksetup", "-setsecurewebproxystate", network, "on"])
                            
                            logger.info(f"Configured proxy for network {network}")
                        except Exception as e:
                            logger.error(f"Failed to set proxy for network {network}: {str(e)}")
                            success = False
                    
                    if success:
                        logger.info(f"Enabled proxy on macOS for networks: {', '.join(networks)}")
                    return success
                except Exception as e:
                    logger.error(f"Failed to set macOS proxy: {str(e)}")
                    return False
                
            elif self.system == "Linux":
                # Linux - set environment variables
                try:
                    # Set environment variables for the current process
                    os.environ["http_proxy"] = f"http://{self.proxy_url}"
                    os.environ["https_proxy"] = f"http://{self.proxy_url}"
                    os.environ["no_proxy"] = ",".join(bypass_list)
                    
                    # Write to a shell script that can be sourced
                    with open(os.path.expanduser("~/.promptshield-proxy"), "w") as f:
                        f.write(f"export http_proxy=http://{self.proxy_url}\n")
                        f.write(f"export https_proxy=http://{self.proxy_url}\n")
                        f.write(f"export no_proxy={','.join(bypass_list)}\n")
                    
                    # Try to set GNOME settings if available
                    try:
                        subprocess.run(["gsettings", "set", "org.gnome.system.proxy", "mode", "manual"])
                        subprocess.run(["gsettings", "set", "org.gnome.system.proxy.http", "host", self.proxy_host])
                        subprocess.run(["gsettings", "set", "org.gnome.system.proxy.http", "port", str(self.proxy_port)])
                        subprocess.run(["gsettings", "set", "org.gnome.system.proxy.https", "host", self.proxy_host])
                        subprocess.run(["gsettings", "set", "org.gnome.system.proxy.https", "port", str(self.proxy_port)])
                        
                        # Set bypass domains
                        subprocess.run(["gsettings", "set", "org.gnome.system.proxy", "ignore-hosts", 
                                      str(bypass_list)])
                        
                        logger.info("Enabled proxy on Linux (GNOME)")
                    except:
                        logger.warning("Failed to set GNOME proxy settings. Environment variables set.")
                    
                    logger.info("Proxy environment variables set for Linux")
                    return True
                except Exception as e:
                    logger.error(f"Failed to set Linux proxy: {str(e)}")
                    return False
            
            # Unsupported OS
            logger.warning(f"Unsupported operating system: {self.system}")
            return False
            
        except Exception as e:
            logger.error(f"Failed to enable proxy: {str(e)}")
            return False
    
    def disable_proxy(self):
        """
        Disable the proxy and restore original settings
        
        Returns:
            bool: Success or failure
        """
        try:
            if self.system == "Windows":
                try:
                    import winreg
                    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                       r"Software\Microsoft\Windows\CurrentVersion\Internet Settings", 
                                       0, winreg.KEY_WRITE) as key:
                        winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, 
                                         self.original_settings["enabled"])
                        if self.original_settings["server"]:
                            winreg.SetValueEx(key, "ProxyServer", 0, winreg.REG_SZ, 
                                             self.original_settings["server"])
                        if self.original_settings["bypass"]:
                            winreg.SetValueEx(key, "ProxyOverride", 0, winreg.REG_SZ, 
                                             self.original_settings["bypass"])
                    
                    # Notify system of the change
                    try:
                        subprocess.call(["netsh", "winhttp", "import", "proxy", "source=ie"])
                    except:
                        pass
                    
                    # Refresh Internet Explorer settings
                    try:
                        import ctypes
                        INTERNET_OPTION_REFRESH = 37
                        INTERNET_OPTION_SETTINGS_CHANGED = 39
                        ctypes.windll.Wininet.InternetSetOptionW(0, INTERNET_OPTION_SETTINGS_CHANGED, 0, 0)
                        ctypes.windll.Wininet.InternetSetOptionW(0, INTERNET_OPTION_REFRESH, 0, 0)
                    except:
                        pass
                    
                    logger.info("Restored original proxy settings on Windows")
                    return True
                except ImportError:
                    logger.error("Failed to import required modules for Windows proxy configuration")
                except Exception as e:
                    logger.error(f"Failed to restore Windows proxy: {str(e)}")
                    return False
                
            elif self.system == "Darwin":
                # macOS
                success = True
                try:
                    if "networks" in self.original_settings:
                        for network_config in self.original_settings["networks"]:
                            try:
                                network = network_config["name"]
                                if network_config["enabled"]:
                                    if ":" in network_config["server"]:
                                        server, port = network_config["server"].split(':')
                                        subprocess.run(["networksetup", "-setwebproxy", 
                                                      network, server, port])
                                        subprocess.run(["networksetup", "-setsecurewebproxy", 
                                                      network, server, port])
                                else:
                                    subprocess.run(["networksetup", "-setwebproxystate", 
                                                  network, "off"])
                                    subprocess.run(["networksetup", "-setsecurewebproxystate", 
                                                  network, "off"])
                            except Exception as e:
                                logger.error(f"Failed to restore proxy for network {network}: {str(e)}")
                                success = False
                        
                        if success:
                            logger.info("Restored original proxy settings on macOS")
                        return success
                    else:
                        # If no original settings, just disable proxies on all networks
                        networks = []
                        network_output = subprocess.check_output(["networksetup", "-listallnetworkservices"]).decode().split('\n')
                        for line in network_output[1:]:  # Skip the first line
                            if line and not line.startswith('*'):
                                networks.append(line)
                        
                        for network in networks:
                            try:
                                subprocess.run(["networksetup", "-setwebproxystate", network, "off"])
                                subprocess.run(["networksetup", "-setsecurewebproxystate", network, "off"])
                            except:
                                pass
                        
                        logger.info("Disabled all proxy settings on macOS")
                        return True
                except Exception as e:
                    logger.error(f"Failed to restore macOS proxy: {str(e)}")
                    return False
                
            elif self.system == "Linux":
                # Linux
                try:
                    if self.original_settings.get("http_proxy"):
                        os.environ["http_proxy"] = self.original_settings["http_proxy"]
                    else:
                        os.environ.pop("http_proxy", None)
                    
                    if self.original_settings.get("https_proxy"):
                        os.environ["https_proxy"] = self.original_settings["https_proxy"]
                    else:
                        os.environ.pop("https_proxy", None)
                    
                    # Remove the proxy environment file
                    proxy_file = os.path.expanduser("~/.promptshield-proxy")
                    if os.path.exists(proxy_file):
                        os.remove(proxy_file)
                    
                    # GNOME settings
                    if "gnome_mode" in self.original_settings:
                        try:
                            mode = self.original_settings["gnome_mode"]
                            subprocess.run(["gsettings", "set", "org.gnome.system.proxy", "mode", mode])
                            
                            if mode == "'manual'" and "gnome_http_host" in self.original_settings:
                                host = self.original_settings["gnome_http_host"]
                                port = self.original_settings["gnome_http_port"]
                                subprocess.run(["gsettings", "set", "org.gnome.system.proxy.http", "host", host])
                                subprocess.run(["gsettings", "set", "org.gnome.system.proxy.http", "port", port])
                        except Exception as e:
                            logger.error(f"Failed to restore GNOME proxy settings: {str(e)}")
                    
                    logger.info("Restored original proxy settings on Linux")
                    return True
                except Exception as e:
                    logger.error(f"Failed to restore Linux proxy: {str(e)}")
                    return False
            
            # Unsupported OS
            logger.warning(f"Unsupported operating system: {self.system}")
            return False
            
        except Exception as e:
            logger.error(f"Failed to disable proxy: {str(e)}")
            return False