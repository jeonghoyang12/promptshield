#!/usr/bin/env bash
# Installation script for PromptShield

# Function to detect OS
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    elif [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        echo "windows"
    else
        echo "unknown"
    fi
}

# Function to check for Python
check_python() {
    if command -v python3 &> /dev/null; then
        python_cmd="python3"
    elif command -v python &> /dev/null; then
        python_version=$(python --version 2>&1 | cut -d " " -f 2 | cut -d "." -f 1)
        if [[ "$python_version" -ge 3 ]]; then
            python_cmd="python"
        else
            echo "Error: Python 3.8+ is required"
            exit 1
        fi
    else
        echo "Error: Python not found. Please install Python 3.8+"
        exit 1
    fi
    
    echo "Using $python_cmd"
}

# Function to create virtual environment
create_venv() {
    echo "Creating virtual environment..."
    $python_cmd -m venv venv
    
    if [[ "$os" == "windows" ]]; then
        source venv/Scripts/activate
    else
        source venv/bin/activate
    fi
}

# Function to install dependencies
install_deps() {
    echo "Installing dependencies..."
    pip install -r requirements.txt
}

# Function to run setup
run_setup() {
    echo "Running setup..."
    pip install -e .
}

# Function to create necessary directories
create_dirs() {
    echo "Creating directories..."
    mkdir -p data/logs
    mkdir -p data/stats
    mkdir -p data/certs
}

# Main installation process
main() {
    echo "Installing PromptShield..."
    
    os=$(detect_os)
    echo "Detected OS: $os"
    
    check_python
    create_venv
    install_deps
    run_setup
    create_dirs
    
    echo "Installation complete!"
    echo "To start PromptShield, run: promptshield"
}

# Run the installation
main