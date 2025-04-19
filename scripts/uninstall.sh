#!/usr/bin/env bash
# Uninstallation script for PromptShield

echo "Uninstalling PromptShield..."

# Run the uninstall command
if command -v promptshield &> /dev/null; then
    promptshield --uninstall
fi

echo "Uninstallation complete!"