#!/usr/bin/env python3
"""
Download a Google Drive file via the Anthropic MCP proxy.
Handles large files by accumulating the full SSE stream before parsing.
"""
import sys, os, json, base64, requests
from pathlib import Path

SESSION_TOKEN = open(os.environ["CLAUDE_SESSION_INGRESS_TOKEN_FILE"]).read().strip()
SESSION_ID    = "cse_01RsVGJBeV1boqgWFXgtukfq"
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
    payload = {"jsonrpc":"2.0","id":req_id,"method":method}
    if params:
        payload["params"] = params
    resp = requests.post(MCP_URL, headers=HEADERS, json=payload,
                         stream=True, timeout=3600)
    resp.raise_for_status()

    # Accumulate ALL data lines — large files come as one huge data: line
    buf = ""
    for chunk in resp.iter_content(chunk_size=65536, decode_unicode=True):
        buf += chunk

    # Find the last complete data: JSON block
    best = None
    pos = 0
    while True:
        idx = buf.find("data:", pos)
        if idx == -1:
            break
        end = buf.find("\n", idx)
        if end == -1:
            end = len(buf)
        data = buf[idx+5:end].strip()
        if data:
            try:
                best = json.loads(data)
            except json.JSONDecodeError:
                pass
        pos = end + 1
    return best

def download_file(file_id, output_path):
    print(f"Downloading {file_id} → {output_path}")

    init = mcp_call("initialize", {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {"name": "downloader", "version": "1.1"}
    })
    if not init or "result" not in init:
        print("ERROR: MCP initialize failed:", init); sys.exit(1)
    print("MCP initialized.")

    print("Requesting file content…")
    result = mcp_call("tools/call", {
        "name": "download_file_content",
        "arguments": {"fileId": file_id}
    }, req_id=2)

    if not result:
        print("ERROR: no response"); sys.exit(1)
    if "error" in result:
        print("ERROR:", result["error"]); sys.exit(1)

    content_list = result.get("result", {}).get("content", [])
    if not content_list:
        print("ERROR: empty content"); sys.exit(1)

    for item in content_list:
        t = item.get("type","")
        if t == "blob":
            raw = base64.b64decode(item["data"])
        elif t == "text":
            try:
                raw = base64.b64decode(item["text"])
            except Exception:
                print("text content not base64:", item["text"][:200])
                sys.exit(1)
        else:
            print("Unknown content type:", t)
            continue

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(raw)
        print(f"Saved {len(raw):,} bytes → {output_path}")

        # Fix junk-prefix header (39 bytes) like seg2 had
        with open(output_path, "rb") as f:
            head = f.read(100)
        idx = head.find(b"ftyp")
        if idx > 4:
            offset = idx - 4
            print(f"Stripping {offset} junk bytes from header…")
            with open(output_path, "rb") as f:
                f.seek(offset)
                clean = f.read()
            with open(output_path, "wb") as f:
                f.write(clean)
            print(f"Fixed. Final size: {len(clean):,} bytes")
        return

    print("ERROR: no downloadable content found")
    sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 download_from_drive.py <file_id> <output_path>")
        sys.exit(1)
    download_file(sys.argv[1], sys.argv[2])
