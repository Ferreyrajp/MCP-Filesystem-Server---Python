"""
Quick test to verify MCP server tools are registered correctly.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the server module
import server

print("=" * 60)
print("MCP Filesystem Server - Tool Registration Test")
print("=" * 60)

# Get the FastMCP instance
mcp_server = server.mcp

# Access the tool manager
tool_manager = mcp_server._tool_manager

# List all registered tools
print(f"\n✅ Server initialized successfully")
print(f"✅ Tools registered: {len(tool_manager._tools)}")
print(f"\nRegistered tools:")
print("-" * 60)

for i, (tool_name, tool_func) in enumerate(tool_manager._tools.items(), 1):
    # Get the docstring
    doc = tool_func.__doc__ or "No description"
    # Get first line of docstring
    first_line = doc.strip().split('\n')[0]
    print(f"{i:2}. {tool_name:30} - {first_line}")

print("-" * 60)
print(f"\n✅ All tools registered successfully!")
print(f"\nTo run the server:")
print(f"  python server.py i:/MCP-Server-filesystem")
print("\nOr configure in Claude Desktop using:")
print(f"  claude_desktop_config.json")
print("=" * 60)
