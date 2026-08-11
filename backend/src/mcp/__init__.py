"""MCP tool server definitions (plan Section 8).

The Worker discovers and calls tools through a bounded, permissioned interface.
Standalone processes under mcp-servers/ provide the deployed tool servers; the
registry here exposes the contracts. The concrete MCP transport wiring is a
deployment concern completed in Polish (T059).
"""
