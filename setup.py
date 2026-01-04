#!/usr/bin/env python3
"""Setup script for stock-eda environment using uv."""

import subprocess
import sys
import os

def run_command(cmd, description):
    """Run a shell command and handle errors."""
    print(f"\n{'='*60}")
    print(f"{description}")
    print(f"{'='*60}")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        if e.stderr:
            print(e.stderr)
        return False

def get_uv_path():
    """Find uv executable path."""
    # Check common locations
    possible_paths = [
        "uv",  # In PATH
        os.path.expanduser("~/.local/bin/uv"),  # Linux/Mac default
        os.path.expanduser("~/.cargo/bin/uv"),  # Alternative location
        os.path.expanduser("~\\AppData\\Roaming\\uv\\uv.exe"),  # Windows default
        os.path.expanduser("~\\.cargo\\bin\\uv.exe"),  # Windows cargo
    ]
    
    for path in possible_paths:
        try:
            subprocess.run([path, "--version"], check=True, capture_output=True)
            return path
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue
    
    return None

def main():
    """Set up the development environment."""
    print("Stock EDA Environment Setup")
    print("="*60)
    
    # Find uv
    uv_cmd = get_uv_path()
    
    if uv_cmd is None:
        print("uv not found. Installing uv...")
        
        # Platform-specific installation
        if sys.platform == "win32":
            install_cmd = 'powershell -c "irm https://astral.sh/uv/install.ps1 | iex"'
        else:
            install_cmd = "curl -LsSf https://astral.sh/uv/install.sh | sh"
        
        result = subprocess.run(install_cmd, shell=True, capture_output=True, text=True)
        
        # Try to find uv again after installation
        uv_cmd = get_uv_path()
        
        if uv_cmd is None:
            print("\n⚠️  uv installation had issues. Falling back to pip + venv...")
            # Fallback to standard Python approach
            python_cmd = "python" if sys.platform == "win32" else "python3"
            if not run_command(f"{python_cmd} -m venv .venv", "Creating virtual environment"):
                return False
            
            # Determine pip path
            if sys.platform == "win32":
                pip_path = os.path.join(".venv", "Scripts", "pip.exe")
            else:
                pip_path = os.path.join(".venv", "bin", "pip")
            
            if not run_command(f"{pip_path} install -e .", "Installing dependencies"):
                return False
        else:
            print(f"✓ Found uv at: {uv_cmd}")
            # Create virtual environment
            if not run_command(f"{uv_cmd} venv", "Creating virtual environment"):
                return False
            # Install dependencies
            if not run_command(f"{uv_cmd} pip install -e .", "Installing dependencies"):
                return False
    else:
        print(f"✓ Found uv at: {uv_cmd}")
        # Create virtual environment
        if not run_command(f"{uv_cmd} venv", "Creating virtual environment"):
            return False
        # Install dependencies
        if not run_command(f"{uv_cmd} pip install -e .", "Installing dependencies"):
            return False
    
    # Setup Jupyter kernel - determine correct Python path
    if sys.platform == "win32":
        venv_python = os.path.join(".venv", "Scripts", "python.exe")
    else:
        venv_python = os.path.join(".venv", "bin", "python")
    
    if not os.path.exists(venv_python):
        print(f"Warning: Could not find Python at {venv_python}")
        return False
    
    if not run_command(f'"{venv_python}" -m ipykernel install --user --name=stock-eda', 
                      "Setting up Jupyter kernel"):
        return False
    
    # Enable Jupyter widgets (for classic Jupyter Notebook, not needed for VS Code)
    print("\n" + "="*60)
    print("Configuring Jupyter widgets")
    print("="*60)
    try:
        # This enables widgets in classic Jupyter Notebook
        result = subprocess.run(
            f'"{venv_python}" -m jupyter nbextension enable --py widgetsnbextension --sys-prefix',
            shell=True, capture_output=True, text=True
        )
        if result.returncode == 0:
            print("✓ Jupyter widgets configured for classic Jupyter Notebook")
        else:
            print("ℹ️  Jupyter widgets auto-configuration skipped (VS Code users don't need this)")
    except Exception as e:
        print("ℹ️  Widget configuration skipped (not required for VS Code)")
    
    print("\n" + "="*60)
    print("Setup completed successfully!")
    print("="*60)
    print("\nTo activate the environment:")
    if sys.platform == "win32":
        print("  .venv\\Scripts\\activate     (PowerShell)")
        print("  .venv\\Scripts\\activate.bat (Command Prompt)")
    else:
        print("  source .venv/bin/activate")
    print("\nTo start Jupyter:")
    print("  jupyter notebook")
    print("\nOpen 'stock_analysis.ipynb' and select 'stock-eda' kernel")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
