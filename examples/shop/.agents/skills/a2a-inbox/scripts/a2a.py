#!/usr/bin/env python3
"""A minimal A2A 1.0 endpoint and client for coding agents. See ../SKILL.md.

  a2a.py serve <name> "<what you're working on>"   start your endpoint; run it in the background
  a2a.py agents                                    list the agents in this project
  a2a.py send <from> <to> "<message>"
  a2a.py inbox <name> [after]                      messages sent to you, numbered
  a2a.py wait <name> <after> [secs]                return when a message newer than <after> arrives
  a2a.py stop <name>
"""
import json
import os
import re
import signal
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib import error, request

A2A_VERSION = "1.0"
VERSION_NOT_SUPPORTED = -32009


def channels_dir():
    # Use the main checkout's .agents/channels, so agents in worktrees share it.
    if os.environ.get("A2A_CHANNELS_DIR"):
        return Path(os.environ["A2A_CHANNELS_DIR"])
    try:
        common = subprocess.run(
            ["git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
        return Path(common).parent / ".agents" / "channels"
    except (subprocess.CalledProcessError, FileNotFoundError):
        return Path.cwd() / ".agents" / "channels"


DIR = channels_dir()
AGENTS = DIR / "agents"
INBOX = DIR / "inbox"


def fail(message, code=1):
    print(f"a2a.py: {message}", file=sys.stderr)
    sys.exit(code)


def usage():
    print("\n".join(line.strip() for line in __doc__.splitlines() if line.startswith("  a2a.py")), file=sys.stderr)
    sys.exit(2)


def check_name(name):
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", name):
        fail(f"'{name}' isn't a valid name: use lowercase letters, digits and dashes")
    return name


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def alive(pid):
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def entry(name):
    path = AGENTS / f"{name}.json"
    return json.loads(path.read_text()) if path.exists() else None


def read_inbox(name):
    path = INBOX / f"{name}.jsonl"
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def rpc_error(rid, code, message):
    return {"jsonrpc": "2.0", "id": rid, "error": {"code": code, "message": message}}


def serve(name, description):
    current = entry(name)
    if current and alive(current["pid"]):
        fail(f"{name} is already serving at {current['url']}")
    AGENTS.mkdir(parents=True, exist_ok=True)
    INBOX.mkdir(parents=True, exist_ok=True)
    inbox = INBOX / f"{name}.jsonl"

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def reply(self, status, body):
            data = json.dumps(body).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            if self.path == "/.well-known/agent-card.json":
                self.reply(200, card)
            else:
                self.reply(404, {"error": "not found"})

        def do_POST(self):
            try:
                req = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))))
            except ValueError:
                return self.reply(200, rpc_error(None, -32700, "Parse error"))
            rid = req.get("id")
            version = self.headers.get("A2A-Version", "0.3")
            if version.split(".")[0] != "1":
                return self.reply(200, rpc_error(rid, VERSION_NOT_SUPPORTED, f"A2A-Version {version} isn't supported; use {A2A_VERSION}"))
            if req.get("method") != "SendMessage":
                return self.reply(200, rpc_error(rid, -32601, "Method not found"))
            message = (req.get("params") or {}).get("message") or {}
            text = "".join(part.get("text", "") for part in message.get("parts", []))
            if not message.get("messageId") or not text:
                return self.reply(200, rpc_error(rid, -32602, "Invalid params: the message needs a messageId and a text part"))
            # HTTPServer handles one request at a time, so appends never interleave.
            seq = len(read_inbox(name)) + 1
            sender = (message.get("metadata") or {}).get("from", "unknown")
            with inbox.open("a") as f:
                f.write(json.dumps({"seq": seq, "received": now(), "from": sender, "messageId": message["messageId"], "text": text}) + "\n")
            self.reply(200, {"jsonrpc": "2.0", "id": rid, "result": {"message": {
                "messageId": str(uuid.uuid4()),
                "contextId": message.get("contextId") or str(uuid.uuid4()),
                "role": "ROLE_AGENT",
                "parts": [{"text": f"Delivered to {name}'s inbox as message {seq}."}],
            }}})

    server = HTTPServer(("127.0.0.1", 0), Handler)
    url = f"http://127.0.0.1:{server.server_port}/"
    card = {
        "name": name,
        "description": description,
        "supportedInterfaces": [{"url": url, "protocolBinding": "JSONRPC", "protocolVersion": A2A_VERSION}],
        "version": "1.0.0",
        "capabilities": {"streaming": False, "pushNotifications": False},
        "defaultInputModes": ["text/plain"],
        "defaultOutputModes": ["text/plain"],
        "skills": [{
            "id": "coordinate",
            "name": "Coordinate",
            "description": "Receives messages from the other coding agents in this project.",
            "tags": ["coordination"],
        }],
    }
    path = AGENTS / f"{name}.json"
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps({"name": name, "url": url, "pid": os.getpid()}) + "\n")
    tmp.replace(path)

    def shutdown(*_):
        current = entry(name)
        if current and current["pid"] == os.getpid():
            path.unlink()
        sys.exit(0)

    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)
    print(f"{name} is serving at {url}", flush=True)
    server.serve_forever()


def fetch_card(url):
    with request.urlopen(url + ".well-known/agent-card.json", timeout=3) as resp:
        return json.load(resp)


def agents():
    if not AGENTS.exists():
        return
    for path in sorted(AGENTS.glob("*.json")):
        info = json.loads(path.read_text())
        if not alive(info["pid"]):
            print(f"{info['name']}  (not running)")
            continue
        try:
            card = fetch_card(info["url"])
            print(f"{card['name']}  {card['description']}  {info['url']}")
        except (error.URLError, OSError, ValueError):
            print(f"{info['name']}  (not answering at {info['url']})")


def send(sender, to, text):
    if not entry(sender):
        fail(f"{sender} isn't serving; run `a2a.py serve {sender} ...` first")
    target = entry(to)
    if not target or not alive(target["pid"]):
        fail(f"no running agent named {to}; run `a2a.py agents`")
    try:
        card = fetch_card(target["url"])
    except (error.URLError, OSError, ValueError) as e:
        fail(f"couldn't read {to}'s agent card: {e}")
    interface = next((i for i in card.get("supportedInterfaces", []) if i.get("protocolBinding") == "JSONRPC"), None)
    if not interface:
        fail(f"{to} has no JSON-RPC interface")
    body = {"jsonrpc": "2.0", "id": str(uuid.uuid4()), "method": "SendMessage", "params": {"message": {
        "messageId": str(uuid.uuid4()),
        "role": "ROLE_USER",
        "parts": [{"text": text}],
        "metadata": {"from": sender},
    }}}
    req = request.Request(interface["url"], data=json.dumps(body).encode(), method="POST",
                          headers={"Content-Type": "application/json", "A2A-Version": A2A_VERSION})
    try:
        with request.urlopen(req, timeout=5) as resp:
            reply = json.load(resp)
    except (error.URLError, OSError, ValueError) as e:
        fail(f"couldn't reach {to}: {e}")
    if "error" in reply:
        fail(f"{to} refused the message: {reply['error']['message']}")
    print("".join(part.get("text", "") for part in reply["result"]["message"]["parts"]))


def show(messages):
    for m in messages:
        print(f"{m['seq']} {m['received']} {m['from']}: {' '.join(m['text'].splitlines())}")


def wait(name, after, secs):
    deadline = time.time() + secs
    while time.time() < deadline:
        new = [m for m in read_inbox(name) if m["seq"] > after]
        if new:
            return show(new)
        time.sleep(0.5)
    fail(f"no new messages for {name} in {secs}s")


def stop(name):
    info = entry(name)
    if not info:
        fail(f"{name} isn't serving")
    if alive(info["pid"]):
        os.kill(info["pid"], signal.SIGTERM)
        for _ in range(20):
            if not alive(info["pid"]):
                break
            time.sleep(0.1)
    (AGENTS / f"{name}.json").unlink(missing_ok=True)


def main(args):
    if not args:
        usage()
    cmd, rest = args[0], args[1:]
    if cmd == "serve" and len(rest) == 2:
        serve(check_name(rest[0]), rest[1])
    elif cmd == "agents" and not rest:
        agents()
    elif cmd == "send" and len(rest) == 3:
        send(check_name(rest[0]), check_name(rest[1]), rest[2])
    elif cmd == "inbox" and len(rest) in (1, 2):
        after = int(rest[1]) if len(rest) == 2 else 0
        show([m for m in read_inbox(check_name(rest[0])) if m["seq"] > after])
    elif cmd == "wait" and len(rest) in (2, 3):
        wait(check_name(rest[0]), int(rest[1]), int(rest[2]) if len(rest) == 3 else 600)
    elif cmd == "stop" and len(rest) == 1:
        stop(check_name(rest[0]))
    else:
        usage()


if __name__ == "__main__":
    main(sys.argv[1:])
