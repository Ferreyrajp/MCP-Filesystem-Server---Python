"""
Simple test script to verify MCP filesystem server functionality.
"""

import asyncio
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lib import (
    set_allowed_directories,
    validate_path,
    read_file_content,
    write_file_content,
    format_size,
)
from path_utils import normalize_path
from path_validation import is_path_within_allowed_directories


async def test_basic_operations():
    """Test basic file operations."""
    print("=== Testing MCP Filesystem Server ===\n")
    
    # Setup
    test_dir = os.path.dirname(os.path.abspath(__file__))
    set_allowed_directories([test_dir])
    print(f"✓ Allowed directory: {test_dir}\n")
    
    # Test 1: Path validation
    print("Test 1: Path Validation")
    try:
        test_path = os.path.join(test_dir, "README.md")
        is_valid = is_path_within_allowed_directories(test_path, [test_dir])
        print(f"  ✓ Path validation works: {is_valid}")
    except Exception as e:
        print(f"  ✗ Path validation failed: {e}")
    
    # Test 2: Path normalization
    print("\nTest 2: Path Normalization")
    try:
        normalized = normalize_path(test_dir)
        print(f"  ✓ Normalized path: {normalized}")
    except Exception as e:
        print(f"  ✗ Normalization failed: {e}")
    
    # Test 3: Read file
    print("\nTest 3: Read File")
    try:
        readme_path = os.path.join(test_dir, "README.md")
        if os.path.exists(readme_path):
            valid_path = await validate_path(readme_path)
            content = await read_file_content(valid_path)
            print(f"  ✓ Read README.md ({len(content)} characters)")
            print(f"  First 100 chars: {content[:100]}...")
        else:
            print("  ⚠ README.md not found, skipping")
    except Exception as e:
        print(f"  ✗ Read failed: {e}")
    
    # Test 4: Write and read file
    print("\nTest 4: Write and Read File")
    try:
        test_file = os.path.join(test_dir, "test_output.txt")
        test_content = "Hello from MCP Filesystem Server!\nThis is a test file."
        
        await write_file_content(test_file, test_content)
        print(f"  ✓ Wrote test file")
        
        read_content = await read_file_content(test_file)
        if read_content == test_content:
            print(f"  ✓ Read test file successfully")
        else:
            print(f"  ✗ Content mismatch")
        
        # Cleanup
        os.remove(test_file)
        print(f"  ✓ Cleaned up test file")
    except Exception as e:
        print(f"  ✗ Write/Read failed: {e}")
    
    # Test 5: Format size
    print("\nTest 5: Format Size")
    try:
        sizes = [0, 1024, 1024*1024, 1024*1024*1024]
        for size in sizes:
            formatted = format_size(size)
            print(f"  ✓ {size} bytes = {formatted}")
    except Exception as e:
        print(f"  ✗ Format size failed: {e}")
    
    # Test 6: Security - attempt to access outside allowed directory
    print("\nTest 6: Security Test (should fail)")
    try:
        outside_path = "C:\\Windows\\System32\\config" if os.name == 'nt' else "/etc/passwd"
        valid_path = await validate_path(outside_path)
        print(f"  ✗ Security breach! Accessed: {valid_path}")
    except PermissionError as e:
        print(f"  ✓ Security working: {str(e)[:80]}...")
    except Exception as e:
        print(f"  ✓ Security working (different error): {str(e)[:80]}...")
    
    print("\n=== All tests completed ===")


if __name__ == "__main__":
    asyncio.run(test_basic_operations())
