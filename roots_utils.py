"""
MCP roots protocol utilities.
Handles parsing and validation of root directories from MCP client.
"""

import os
from pathlib import Path
from typing import List, Optional
from path_utils import normalize_path


async def parse_root_uri(root_uri: str) -> Optional[str]:
    """
    Converts a root URI to a normalized directory path with basic security validation.
    
    Args:
        root_uri: File URI (file://...) or plain directory path
        
    Returns:
        Validated path or None if invalid
    """
    try:
        # Remove file:// prefix if present
        raw_path = root_uri[7:] if root_uri.startswith('file://') else root_uri
        
        # Expand home directory
        if raw_path.startswith('~/') or raw_path == '~':
            expanded_path = os.path.join(os.path.expanduser('~'), raw_path[1:].lstrip('/'))
        else:
            expanded_path = raw_path
        
        # Resolve to absolute path
        absolute_path = str(Path(expanded_path).resolve())
        
        # Resolve symlinks
        resolved_path = str(Path(absolute_path).resolve())
        
        return normalize_path(resolved_path)
    except Exception:
        return None  # Path doesn't exist or other error


def format_directory_error(dir_path: str, error: Optional[Exception] = None, reason: Optional[str] = None) -> str:
    """
    Formats error message for directory validation failures.
    
    Args:
        dir_path: Directory path that failed validation
        error: Error that occurred during validation
        reason: Specific reason for failure
        
    Returns:
        Formatted error message
    """
    if reason:
        return f"Skipping {reason}: {dir_path}"
    
    message = str(error) if error else "unknown error"
    return f"Skipping invalid directory: {dir_path} due to error: {message}"


async def get_valid_root_directories(requested_roots: List[dict]) -> List[str]:
    """
    Resolves requested root directories from MCP root specifications.
    
    Converts root URI specifications (file:// URIs or plain paths) into normalized
    directory paths, validating that each path exists and is a directory.
    Includes symlink resolution for security.
    
    Args:
        requested_roots: Array of root specifications with 'uri' and optional 'name'
        
    Returns:
        Array of validated directory paths
    """
    validated_directories: List[str] = []
    
    for requested_root in requested_roots:
        root_uri = requested_root.get('uri', '')
        resolved_path = await parse_root_uri(root_uri)
        
        if not resolved_path:
            print(format_directory_error(root_uri, reason='invalid path or inaccessible'), 
                  file=__import__('sys').stderr)
            continue
        
        try:
            path_obj = Path(resolved_path)
            if path_obj.is_dir():
                validated_directories.append(resolved_path)
            else:
                print(format_directory_error(resolved_path, reason='non-directory root'), 
                      file=__import__('sys').stderr)
        except Exception as error:
            print(format_directory_error(resolved_path, error=error), 
                  file=__import__('sys').stderr)
    
    return validated_directories
