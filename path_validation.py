"""
Path validation utilities for security checks.
Ensures filesystem operations only occur within allowed directories.
"""

import os
from pathlib import Path
from typing import List


def is_path_within_allowed_directories(absolute_path: str, allowed_directories: List[str]) -> bool:
    """
    Checks if an absolute path is within any of the allowed directories.
    
    Args:
        absolute_path: The absolute path to check
        allowed_directories: Array of absolute allowed directory paths
        
    Returns:
        True if the path is within an allowed directory, False otherwise
        
    Raises:
        ValueError: If given relative paths after normalization
    """
    # Type validation
    if not isinstance(absolute_path, str) or not isinstance(allowed_directories, list):
        return False
    
    # Reject empty inputs
    if not absolute_path or len(allowed_directories) == 0:
        return False
    
    # Reject null bytes (forbidden in paths)
    if '\x00' in absolute_path:
        return False
    
    # Normalize the input path
    try:
        normalized_path = str(Path(absolute_path).resolve())
    except Exception:
        return False
    
    # Verify it's absolute after normalization
    if not Path(normalized_path).is_absolute():
        raise ValueError('Path must be absolute after normalization')
    
    # Check against each allowed directory
    for dir_path in allowed_directories:
        if not isinstance(dir_path, str) or not dir_path:
            continue
        
        # Reject null bytes in allowed dirs
        if '\x00' in dir_path:
            continue
        
        # Normalize the allowed directory
        try:
            normalized_dir = str(Path(dir_path).resolve())
        except Exception:
            continue
        
        # Verify allowed directory is absolute after normalization
        if not Path(normalized_dir).is_absolute():
            raise ValueError('Allowed directories must be absolute paths after normalization')
        
        # Check if normalized_path is within normalized_dir
        # Path is inside if it's the same or a subdirectory
        if normalized_path == normalized_dir:
            return True
        
        # Check if path is a subdirectory
        try:
            # Use relative_to to check if path is within directory
            Path(normalized_path).relative_to(normalized_dir)
            return True
        except ValueError:
            # Not a subdirectory, continue checking other allowed directories
            continue
    
    return False
