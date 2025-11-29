"""
Core file operations library for MCP filesystem server.
Provides secure file I/O, editing, and search functionality.
"""

import os
import secrets
import difflib
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from fnmatch import fnmatch

from path_utils import normalize_path, expand_home
from path_validation import is_path_within_allowed_directories


# Global allowed directories - set by the main module
_allowed_directories: List[str] = []


def set_allowed_directories(directories: List[str]) -> None:
    """Set allowed directories from the main module."""
    global _allowed_directories
    _allowed_directories = directories.copy()


def get_allowed_directories() -> List[str]:
    """Get current allowed directories."""
    return _allowed_directories.copy()


# Utility Functions

def format_size(bytes_size: int) -> str:
    """
    Format bytes as human-readable size.
    
    Args:
        bytes_size: Size in bytes
        
    Returns:
        Formatted size string (e.g., "1.5 MB")
    """
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    if bytes_size == 0:
        return '0 B'
    
    i = 0
    size = float(bytes_size)
    while size >= 1024 and i < len(units) - 1:
        size /= 1024
        i += 1
    
    if i == 0:
        return f"{int(size)} {units[i]}"
    return f"{size:.2f} {units[i]}"


def normalize_line_endings(text: str) -> str:
    """Normalize line endings to \\n."""
    return text.replace('\r\n', '\n')


def create_unified_diff(original_content: str, new_content: str, filepath: str = 'file') -> str:
    """
    Create a unified diff between two text contents.
    
    Args:
        original_content: Original file content
        new_content: Modified file content
        filepath: File path for diff header
        
    Returns:
        Unified diff string
    """
    # Ensure consistent line endings for diff
    normalized_original = normalize_line_endings(original_content)
    normalized_new = normalize_line_endings(new_content)
    
    original_lines = normalized_original.splitlines(keepends=True)
    new_lines = normalized_new.splitlines(keepends=True)
    
    diff = difflib.unified_diff(
        original_lines,
        new_lines,
        fromfile=f"{filepath} (original)",
        tofile=f"{filepath} (modified)",
        lineterm=''
    )
    
    return '\n'.join(diff)


# Security & Validation Functions

async def validate_path(requested_path: str) -> str:
    """
    Validate and resolve a path, ensuring it's within allowed directories.
    
    Args:
        requested_path: Path to validate
        
    Returns:
        Validated absolute path
        
    Raises:
        PermissionError: If path is outside allowed directories
        FileNotFoundError: If parent directory doesn't exist for new files
    """
    expanded_path = expand_home(requested_path)
    absolute = os.path.abspath(expanded_path)
    normalized_requested = normalize_path(absolute)
    
    # Security: Check if path is within allowed directories before any file operations
    is_allowed = is_path_within_allowed_directories(normalized_requested, _allowed_directories)
    if not is_allowed:
        raise PermissionError(
            f"Access denied - path outside allowed directories: {absolute} not in {', '.join(_allowed_directories)}"
        )
    
    # Security: Handle symlinks by checking their real path to prevent symlink attacks
    try:
        real_path = str(Path(absolute).resolve())
        normalized_real = normalize_path(real_path)
        if not is_path_within_allowed_directories(normalized_real, _allowed_directories):
            raise PermissionError(
                f"Access denied - symlink target outside allowed directories: {real_path} not in {', '.join(_allowed_directories)}"
            )
        return real_path
    except FileNotFoundError:
        # Security: For new files that don't exist yet, verify parent directory
        parent_dir = os.path.dirname(absolute)
        try:
            real_parent_path = str(Path(parent_dir).resolve())
            normalized_parent = normalize_path(real_parent_path)
            if not is_path_within_allowed_directories(normalized_parent, _allowed_directories):
                raise PermissionError(
                    f"Access denied - parent directory outside allowed directories: {real_parent_path} not in {', '.join(_allowed_directories)}"
                )
            return absolute
        except FileNotFoundError:
            raise FileNotFoundError(f"Parent directory does not exist: {parent_dir}")


# File Operations

async def get_file_stats(file_path: str) -> Dict[str, any]:
    """
    Get detailed file statistics.
    
    Args:
        file_path: Path to file
        
    Returns:
        Dictionary with file metadata
    """
    stats = os.stat(file_path)
    return {
        'size': format_size(stats.st_size),
        'created': stats.st_ctime,
        'modified': stats.st_mtime,
        'accessed': stats.st_atime,
        'isDirectory': os.path.isdir(file_path),
        'isFile': os.path.isfile(file_path),
        'permissions': oct(stats.st_mode)[-3:],
    }


async def read_file_content(file_path: str, encoding: str = 'utf-8') -> str:
    """
    Read file content as text.
    
    Args:
        file_path: Path to file
        encoding: Text encoding (default: utf-8)
        
    Returns:
        File content as string
    """
    with open(file_path, 'r', encoding=encoding) as f:
        return f.read()


async def write_file_content(file_path: str, content: str) -> None:
    """
    Write content to file with atomic operation.
    
    Args:
        file_path: Path to file
        content: Content to write
    """
    # Security: Use atomic write to prevent race conditions
    temp_path = f"{file_path}.{secrets.token_hex(16)}.tmp"
    try:
        with open(temp_path, 'w', encoding='utf-8') as f:
            f.write(content)
        # Atomic rename
        os.replace(temp_path, file_path)
    except Exception as e:
        # Clean up temp file on error
        if os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except:
                pass
        raise e


# File Editing Functions

async def apply_file_edits(
    file_path: str,
    edits: List[Dict[str, str]],
    dry_run: bool = False
) -> str:
    """
    Apply line-based edits to a file.
    
    Args:
        file_path: Path to file
        edits: List of edit operations with 'oldText' and 'newText'
        dry_run: If True, only preview changes without applying
        
    Returns:
        Diff string showing changes
    """
    # Read file content and normalize line endings
    with open(file_path, 'r', encoding='utf-8') as f:
        content = normalize_line_endings(f.read())
    
    # Apply edits sequentially
    modified_content = content
    for edit in edits:
        old_text = normalize_line_endings(edit['oldText'])
        new_text = normalize_line_endings(edit['newText'])
        
        # If exact match exists, use it
        if old_text in modified_content:
            modified_content = modified_content.replace(old_text, new_text, 1)
            continue
        
        # Otherwise, try line-by-line matching with flexibility for whitespace
        old_lines = old_text.split('\n')
        content_lines = modified_content.split('\n')
        match_found = False
        
        for i in range(len(content_lines) - len(old_lines) + 1):
            potential_match = content_lines[i:i + len(old_lines)]
            
            # Compare lines with normalized whitespace
            is_match = all(
                old_line.strip() == content_line.strip()
                for old_line, content_line in zip(old_lines, potential_match)
            )
            
            if is_match:
                # Preserve original indentation of first line
                original_indent = content_lines[i][:len(content_lines[i]) - len(content_lines[i].lstrip())]
                new_lines = new_text.split('\n')
                new_lines_indented = [
                    original_indent + line.lstrip() if j == 0 else line
                    for j, line in enumerate(new_lines)
                ]
                
                content_lines[i:i + len(old_lines)] = new_lines_indented
                modified_content = '\n'.join(content_lines)
                match_found = True
                break
        
        if not match_found:
            raise ValueError(f"Could not find exact match for edit:\n{edit['oldText']}")
    
    # Create unified diff
    diff = create_unified_diff(content, modified_content, file_path)
    
    # Format diff with backticks
    num_backticks = 3
    while '`' * num_backticks in diff:
        num_backticks += 1
    formatted_diff = f"{'`' * num_backticks}diff\n{diff}\n{'`' * num_backticks}\n\n"
    
    if not dry_run:
        await write_file_content(file_path, modified_content)
    
    return formatted_diff


async def tail_file(file_path: str, num_lines: int) -> str:
    """
    Get the last N lines of a file efficiently.
    
    Args:
        file_path: Path to file
        num_lines: Number of lines to read
        
    Returns:
        Last N lines as string
    """
    CHUNK_SIZE = 1024
    
    with open(file_path, 'rb') as f:
        f.seek(0, os.SEEK_END)
        file_size = f.tell()
        
        if file_size == 0:
            return ''
        
        lines = []
        position = file_size
        remaining_text = ''
        
        while position > 0 and len(lines) < num_lines:
            size = min(CHUNK_SIZE, position)
            position -= size
            f.seek(position)
            chunk = f.read(size).decode('utf-8', errors='ignore')
            chunk_text = chunk + remaining_text
            chunk_lines = normalize_line_endings(chunk_text).split('\n')
            
            if position > 0:
                remaining_text = chunk_lines[0]
                chunk_lines = chunk_lines[1:]
            
            for line in reversed(chunk_lines):
                if len(lines) < num_lines:
                    lines.insert(0, line)
        
        return '\n'.join(lines)


async def head_file(file_path: str, num_lines: int) -> str:
    """
    Get the first N lines of a file efficiently.
    
    Args:
        file_path: Path to file
        num_lines: Number of lines to read
        
    Returns:
        First N lines as string
    """
    lines = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i >= num_lines:
                break
            lines.append(line.rstrip('\n\r'))
    
    return '\n'.join(lines)


async def search_files_with_validation(
    root_path: str,
    pattern: str,
    allowed_directories: List[str],
    exclude_patterns: Optional[List[str]] = None
) -> List[str]:
    """
    Recursively search for files matching a pattern.
    
    Args:
        root_path: Starting directory
        pattern: Glob-style search pattern
        allowed_directories: List of allowed directories
        exclude_patterns: Optional list of patterns to exclude
        
    Returns:
        List of matching file paths
    """
    if exclude_patterns is None:
        exclude_patterns = []
    
    results = []
    
    async def search(current_path: str):
        try:
            entries = os.listdir(current_path)
        except PermissionError:
            return
        
        for entry in entries:
            full_path = os.path.join(current_path, entry)
            
            try:
                await validate_path(full_path)
                
                relative_path = os.path.relpath(full_path, root_path)
                
                # Check exclude patterns
                should_exclude = any(
                    fnmatch(relative_path, exclude_pattern)
                    for exclude_pattern in exclude_patterns
                )
                
                if should_exclude:
                    continue
                
                # Check if matches search pattern
                if fnmatch(relative_path, pattern):
                    results.append(full_path)
                
                # Recurse into directories
                if os.path.isdir(full_path):
                    await search(full_path)
            except (PermissionError, FileNotFoundError):
                continue
    
    await search(root_path)
    return results
