"""
MCP Filesystem Server - Python Implementation
Secure filesystem access server with 14 tools for file operations.
Based on the official TypeScript implementation from modelcontextprotocol/servers.
"""

import sys
import os
import base64
import json
from pathlib import Path
from typing import Optional, List, Dict, Any

from mcp.server.fastmcp import FastMCP

from path_utils import normalize_path, expand_home
from roots_utils import get_valid_root_directories
from lib import (
    set_allowed_directories,
    get_allowed_directories,
    validate_path,
    read_file_content,
    write_file_content,
    get_file_stats,
    apply_file_edits,
    tail_file,
    head_file,
    search_files_with_validation,
    format_size,
)


# Parse command line arguments
args = sys.argv[1:]
if len(args) == 0:
    print("Usage: python server.py [allowed-directory] [additional-directories...]", file=sys.stderr)
    print("Note: Allowed directories can be provided via:", file=sys.stderr)
    print("  1. Command-line arguments (shown above)", file=sys.stderr)
    print("  2. MCP roots protocol (if client supports it)", file=sys.stderr)
    print("At least one directory must be provided by EITHER method for the server to operate.", file=sys.stderr)


# Initialize allowed directories
async def initialize_allowed_directories(dirs: List[str]) -> List[str]:
    """Initialize and validate allowed directories."""
    validated_dirs = []
    for dir_path in dirs:
        expanded = expand_home(dir_path)
        absolute = os.path.abspath(expanded)
        try:
            # Resolve symlinks for security
            resolved = str(Path(absolute).resolve())
            normalized = normalize_path(resolved)
            validated_dirs.append(normalized)
        except Exception:
            # If can't resolve, use normalized absolute path
            validated_dirs.append(normalize_path(absolute))
    
    # Validate that all directories exist and are accessible
    for dir_path in validated_dirs:
        if not os.path.exists(dir_path):
            print(f"Error: {dir_path} does not exist", file=sys.stderr)
            sys.exit(1)
        if not os.path.isdir(dir_path):
            print(f"Error: {dir_path} is not a directory", file=sys.stderr)
            sys.exit(1)
    
    return validated_dirs


# Initialize FastMCP server
mcp = FastMCP("mcp-filesystem-server")


# Helper function to read media files
async def read_file_as_base64(file_path: str) -> str:
    """Read a file and encode as base64."""
    with open(file_path, 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')


# Tool: read_text_file
@mcp.tool()
async def read_text_file(path: str, tail: Optional[int] = None, head: Optional[int] = None) -> str:
    """
    Read the complete contents of a file as text.
    
    Args:
        path: Path to the file
        tail: If provided, returns only the last N lines
        head: If provided, returns only the first N lines
    
    Returns:
        File content as string
    """
    valid_path = await validate_path(path)
    
    if head is not None and tail is not None:
        raise ValueError("Cannot specify both head and tail parameters simultaneously")
    
    if tail is not None:
        content = await tail_file(valid_path, tail)
    elif head is not None:
        content = await head_file(valid_path, head)
    else:
        content = await read_file_content(valid_path)
    
    return content


# Tool: read_multiple_files
@mcp.tool()
async def read_multiple_files(paths: List[str]) -> str:
    """
    Read multiple files simultaneously.
    
    Args:
        paths: Array of file paths to read
    
    Returns:
        Combined file contents separated by ---
    """
    results = []
    for file_path in paths:
        try:
            valid_path = await validate_path(file_path)
            content = await read_file_content(valid_path)
            results.append(f"{file_path}:\n{content}\n")
        except Exception as error:
            results.append(f"{file_path}: Error - {str(error)}")
    
    return "\n---\n".join(results)


# Tool: write_file
@mcp.tool()
async def write_file(path: str, content: str) -> str:
    """
    Create a new file or overwrite an existing file.
    
    Args:
        path: Path to the file
        content: Content to write
    
    Returns:
        Success message
    """
    valid_path = await validate_path(path)
    await write_file_content(valid_path, content)
    return f"Successfully wrote to {path}"


# Tool: edit_file
@mcp.tool()
async def edit_file(path: str, edits: List[Dict[str, str]], dryRun: bool = False) -> str:
    """
    Make line-based edits to a text file.
    
    Args:
        path: Path to the file
        edits: List of edit operations with 'oldText' and 'newText'
        dryRun: Preview changes without applying
    
    Returns:
        Diff showing the changes
    """
    valid_path = await validate_path(path)
    result = await apply_file_edits(valid_path, edits, dryRun)
    return result


# Tool: create_directory
@mcp.tool()
async def create_directory(path: str) -> str:
    """
    Create a new directory or ensure it exists.
    
    Args:
        path: Path to the directory
    
    Returns:
        Success message
    """
    valid_path = await validate_path(path)
    os.makedirs(valid_path, exist_ok=True)
    return f"Successfully created directory {path}"


# Tool: list_directory
@mcp.tool()
async def list_directory(path: str) -> str:
    """
    List contents of a directory.
    
    Args:
        path: Path to the directory
    
    Returns:
        Directory listing with [FILE] and [DIR] prefixes
    """
    valid_path = await validate_path(path)
    entries = os.listdir(valid_path)
    
    formatted = []
    for entry in sorted(entries):
        entry_path = os.path.join(valid_path, entry)
        prefix = "[DIR]" if os.path.isdir(entry_path) else "[FILE]"
        formatted.append(f"{prefix} {entry}")
    
    return "\n".join(formatted)


# Tool: list_directory_with_sizes
@mcp.tool()
async def list_directory_with_sizes(path: str, sortBy: str = "name") -> str:
    """
    List directory contents with file sizes.
    
    Args:
        path: Path to the directory
        sortBy: Sort by 'name' or 'size'
    
    Returns:
        Detailed directory listing with sizes and summary
    """
    valid_path = await validate_path(path)
    entries = os.listdir(valid_path)
    
    detailed_entries = []
    for entry in entries:
        entry_path = os.path.join(valid_path, entry)
        try:
            stats = os.stat(entry_path)
            detailed_entries.append({
                'name': entry,
                'isDirectory': os.path.isdir(entry_path),
                'size': stats.st_size,
                'mtime': stats.st_mtime
            })
        except Exception:
            detailed_entries.append({
                'name': entry,
                'isDirectory': os.path.isdir(entry_path),
                'size': 0,
                'mtime': 0
            })
    
    # Sort entries
    if sortBy == 'size':
        detailed_entries.sort(key=lambda x: x['size'], reverse=True)
    else:
        detailed_entries.sort(key=lambda x: x['name'])
    
    # Format output
    formatted = []
    for entry in detailed_entries:
        prefix = "[DIR]" if entry['isDirectory'] else "[FILE]"
        size_str = "" if entry['isDirectory'] else format_size(entry['size']).rjust(10)
        formatted.append(f"{prefix} {entry['name'].ljust(30)} {size_str}")
    
    # Add summary
    total_files = sum(1 for e in detailed_entries if not e['isDirectory'])
    total_dirs = sum(1 for e in detailed_entries if e['isDirectory'])
    total_size = sum(e['size'] for e in detailed_entries if not e['isDirectory'])
    
    formatted.append("")
    formatted.append(f"Total: {total_files} files, {total_dirs} directories")
    formatted.append(f"Combined size: {format_size(total_size)}")
    
    return "\n".join(formatted)


# Tool: directory_tree
@mcp.tool()
async def directory_tree(path: str, excludePatterns: Optional[List[str]] = None) -> str:
    """
    Get recursive tree structure of directory.
    
    Args:
        path: Path to the directory
        excludePatterns: Patterns to exclude
    
    Returns:
        JSON tree structure
    """
    if excludePatterns is None:
        excludePatterns = []
    
    async def build_tree(current_path: str, root_path: str) -> List[Dict]:
        valid_path = await validate_path(current_path)
        entries = os.listdir(valid_path)
        result = []
        
        for entry in sorted(entries):
            entry_path = os.path.join(current_path, entry)
            relative_path = os.path.relpath(entry_path, root_path)
            
            # Check exclude patterns
            from fnmatch import fnmatch
            should_exclude = any(fnmatch(relative_path, pattern) for pattern in excludePatterns)
            if should_exclude:
                continue
            
            entry_data = {
                'name': entry,
                'type': 'directory' if os.path.isdir(entry_path) else 'file'
            }
            
            if os.path.isdir(entry_path):
                try:
                    entry_data['children'] = await build_tree(entry_path, root_path)
                except Exception:
                    entry_data['children'] = []
            
            result.append(entry_data)
        
        return result
    
    valid_path = await validate_path(path)
    tree_data = await build_tree(valid_path, valid_path)
    return json.dumps(tree_data, indent=2)


# Tool: move_file
@mcp.tool()
async def move_file(source: str, destination: str) -> str:
    """
    Move or rename a file or directory.
    
    Args:
        source: Source path
        destination: Destination path
    
    Returns:
        Success message
    """
    valid_source = await validate_path(source)
    valid_dest = await validate_path(destination)
    
    os.rename(valid_source, valid_dest)
    return f"Successfully moved {source} to {destination}"


# Tool: search_files
@mcp.tool()
async def search_files(path: str, pattern: str, excludePatterns: Optional[List[str]] = None) -> str:
    """
    Recursively search for files matching a pattern.
    
    Args:
        path: Starting directory
        pattern: Search pattern (glob-style)
        excludePatterns: Patterns to exclude
    
    Returns:
        List of matching file paths
    """
    if excludePatterns is None:
        excludePatterns = []
    
    valid_path = await validate_path(path)
    allowed_dirs = get_allowed_directories()
    results = await search_files_with_validation(valid_path, pattern, allowed_dirs, excludePatterns)
    
    return "\n".join(results) if results else "No matches found"


# Tool: get_file_info
@mcp.tool()
async def get_file_info(path: str) -> str:
    """
    Get detailed metadata about a file or directory.
    
    Args:
        path: Path to the file or directory
    
    Returns:
        File metadata as formatted text
    """
    valid_path = await validate_path(path)
    info = await get_file_stats(valid_path)
    
    return "\n".join(f"{key}: {value}" for key, value in info.items())


# Tool: list_allowed_directories
@mcp.tool()
async def list_allowed_directories() -> str:
    """
    List all directories the server is allowed to access.
    
    Returns:
        List of allowed directories
    """
    allowed_dirs = get_allowed_directories()
    return f"Allowed directories:\n" + "\n".join(allowed_dirs)


# Main entry point
if __name__ == "__main__":
    # Initialize allowed directories from command line args
    import asyncio
    
    async def setup():
        if args:
            allowed_dirs = await initialize_allowed_directories(args)
            set_allowed_directories(allowed_dirs)
            print(f"Initialized with allowed directories: {allowed_dirs}", file=sys.stderr)
        else:
            print("Started without allowed directories - waiting for client to provide roots via MCP protocol", file=sys.stderr)
            set_allowed_directories([])
    
    # Run setup
    asyncio.run(setup())
    
    # Run the server
    mcp.run()