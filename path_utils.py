"""
Path utilities for cross-platform path normalization and conversion.
Based on the MCP filesystem server TypeScript implementation.
"""

import os
import platform
from pathlib import Path


def convert_to_windows_path(p: str) -> str:
    """
    Converts WSL or Unix-style Windows paths to Windows format.
    
    Args:
        p: The path to convert
        
    Returns:
        Converted Windows path
    """
    # Handle WSL paths (/mnt/c/...)
    # NEVER convert WSL paths - they are valid Linux paths that work with Python in WSL
    if p.startswith('/mnt/'):
        return p  # Leave WSL paths unchanged
    
    # Handle Unix-style Windows paths (/c/...)
    # Only convert when running on Windows
    if p.startswith('/') and len(p) > 2 and p[1].isalpha() and p[2] == '/':
        if platform.system() == 'Windows':
            drive_letter = p[1].upper()
            path_part = p[2:].replace('/', '\\')
            return f"{drive_letter}:{path_part}"
    
    # Handle standard Windows paths, ensuring backslashes
    if len(p) > 1 and p[1] == ':':
        return p.replace('/', '\\')
    
    # Leave non-Windows paths unchanged
    return p


def normalize_path(p: str) -> str:
    """
    Normalizes path by standardizing format while preserving OS-specific behavior.
    
    Args:
        p: The path to normalize
        
    Returns:
        Normalized path
    """
    # Remove any surrounding quotes and whitespace
    p = p.strip().strip('"').strip("'")
    
    # Check if this is a Unix path that should not be converted
    is_unix_path = p.startswith('/') and (
        # Always preserve WSL paths (/mnt/c/, /mnt/d/, etc.)
        (p.startswith('/mnt/') and len(p) > 5 and p[5].isalpha() and p[6] == '/') or
        # On non-Windows platforms, treat all absolute paths as Unix paths
        (platform.system() != 'Windows') or
        # On Windows, preserve Unix paths that aren't Unix-style Windows paths
        (platform.system() == 'Windows' and not (len(p) > 2 and p[1].isalpha() and p[2] == '/'))
    )
    
    if is_unix_path:
        # For Unix paths, just normalize without converting to Windows format
        # Replace double slashes with single slashes and remove trailing slashes
        import re
        p = re.sub(r'/+', '/', p)
        p = p.rstrip('/')
        return p if p else '/'
    
    # Convert Unix-style Windows paths to Windows format if on Windows
    p = convert_to_windows_path(p)
    
    # Use pathlib for normalization
    normalized = str(Path(p).resolve())
    
    # On Windows, ensure drive letter is capitalized
    if platform.system() == 'Windows' and len(normalized) > 1 and normalized[1] == ':':
        normalized = normalized[0].upper() + normalized[1:]
    
    return normalized


def expand_home(filepath: str) -> str:
    """
    Expands home directory tildes in paths.
    
    Args:
        filepath: The path to expand
        
    Returns:
        Expanded path
    """
    if filepath.startswith('~/') or filepath == '~':
        return os.path.join(os.path.expanduser('~'), filepath[1:].lstrip('/'))
    return filepath
