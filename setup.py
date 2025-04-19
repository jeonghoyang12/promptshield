from setuptools import setup, find_packages

setup(
    name="promptshield",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "flask>=2.3.0",
        "flask-cors>=4.0.0",
        "mitmproxy>=10.0.0",
        "psutil>=5.9.0",
        "requests>=2.31.0",
        "pyOpenSSL>=23.0.0"
    ],
    entry_points={
        "console_scripts": [
            "promptshield=main:main",
        ],
    },
    author="PromptShield Developer",
    author_email="developer@promptshield.example",
    description="Network-level proxy security solution for AI services",
    keywords="ai, security, proxy, prompt-injection",
    python_requires=">=3.8",
)