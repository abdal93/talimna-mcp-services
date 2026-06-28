# TALIMNA MCP Services — BRICS+ Commerce Infrastructure

Multi-Agent Swarm (MAS) commerce infrastructure for BRICS+ trade corridors.

## Services

| Service | Port | Description |
|---------|:----:|-------------|
| Trade Translation MCP | 8001 | 34 BRICS+ languages, trade doc field extraction |
| Sharia Compliance MCP | 8002 | Transaction screening, zakat, riba detection |

## Architecture

Each service is a standalone FastAPI server exposing MCP JSON-RPC 2.0 endpoints.
A2A agent-to-agent protocol for autonomous inter-service communication.
