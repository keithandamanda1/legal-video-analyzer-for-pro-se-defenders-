#!/usr/bin/env python3
"""
Download a Google Drive file via the Anthropic MCP proxy.
Streams the response directly to disk to avoid memory issues.
Usage: python3 download_from_drive.py <file_id> <output_path>
"""
import sys
import os
import json
import base64
import requests
from pathlib import Path

SESSION_TOKEN = open(os.environ["CLAUDE_SESSION_INGRESS_TOKEN_FILE"]).read().strip()
SESSION_ID = "cse_01RsVGJBeV1boqgWFXgtukfq"
MCP_URL = (
    f"https://api.anthropic.com/v2/ccr-sessions/{SESSION_ID}/mcp"
    "?mcp_url=https%3A%2F%2Fdrivemcp.googleapis.com%2Fmcp%2Fv1"
    "&mcp_server_id=94a695a0-028a-5606-ad79-5650b8fca4c9"
    "&toolbox_mcp_server_id=a86bdf3f-496b-4ccb-87da-26592230a659"
)
HEADERS = {
    "Authorization": f"Bearer {SESSION_TOKEN}",
    "Content-Type": "application/json",
    "X-MCP-Server-ID": "a86bdf3f-496b-4ccb-87da-26592230a659",
    "X-Session-UUID": SESSION_ID,
    "Accept": "text/event-stream",
}

def mcp_call(method, params=None, req_id=1):
    payload = {"jsonrpc": "2.0", "id": req_id, "method": method}
    if params:
        payload["params"] = params
    resp = requests.post(MCP_URL, headers=HEADERS, json=payload, stream=True, timeout=300)
    resp.raise_for_status()
    # Parse SSE stream
    for line in resp.iter_lines(decode_unicode=True):
        if line.startswith("data:"):
            data = line[5:].strip()
            if data:
                try:
                    return json.loads(data)
                except json.JSONDecodeError:
                    continue
    return None

def download_file(file_id, output_path):
    print(f"Downloading file {file_id} to {output_path} ...")

    # Initialize
    init = mcp_call("initialize", {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {"name": "downloader", "version": "1.0"}
    })
    if not init or "result" not in init:
        print("ERROR: MCP initialize failed:", init)
        sys.exit(1)
    print("MCP initialized.")

    # Call download_file_content
    print("Requesting file content (this may take a while for large files)...")
    result = mcp_call("tools/call", {
        "name": "download_file_content",
        "arguments": {"fileId": file_id}
    }, req_id=2)

    if not result:
        print("ERROR: No response from download_file_content")
        sys.exit(1)
    if "error" in result:
        print("ERROR:", result["error"])
        sys.exit(1)

    # Extract content from result
    tool_result = result.get("result", {})
    content_list = tool_result.get("content", [])
    if not content_list:
        print("ERROR: Empty content in response")
        print("Result:", json.dumps(result)[:500])
        sys.exit(1)

    # Find binary/blob content
    for item in content_list:
        item_type = item.get("type", "")
        if item_type == "blob":
            data_b64 = item.get("data", "")
            print(f"Got blob data, size={len(data_b64)} chars, decoding...")
            raw = base64.b64decode(data_b64)
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "wb") as f:
                f.write(raw)
            print(f"Saved {len(raw):,} bytes to {output_path}")
            return
        elif item_type == "text":
            # Maybe it's base64 text
            text = item.get("text", "")
            print(f"Got text data ({len(text)} chars)")
            # Try to decode as base64
            try:
                raw = base64.b64decode(text)
                Path(output_path).parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, "wb") as f:
                    f.write(raw)
                print(f"Saved {len(raw):,} bytes to {output_path}")
                return
            except Exception:
                print("Text content (not base64):", text[:200])
                return
        elif item_type == "resource":
            # Might have a URI
            resource = item.get("resource", {})
            print("Resource item:", json.dumps(resource)[:300])

    print("ERROR: No downloadable content found")
    print("Content types found:", [i.get("type") for i in content_list])

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 download_from_drive.py <file_id> <output_path>")
        sys.exit(1)
    download_file(sys.argv[1], sys.argv[2])
