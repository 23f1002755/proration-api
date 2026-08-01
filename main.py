from fastapi import FastAPI
from urllib.parse import urlparse
from pathlib import PurePosixPath

app = FastAPI()

SECRET = PurePosixPath("/home/agent/credentials.env")
BUILD = PurePosixPath("/home/agent/workspace/build")


@app.get("/")
def root():
    return {"status": "running"}


@app.post("/check")
def check(req: dict):

    tool = req.get("tool")

    if tool == "bash":
        cmd = req.get("command", "")

        if (
            "credentials.env" in cmd
            or "~/credentials.env" in cmd
            or "/home/agent/credentials.env" in cmd
        ):
            return {
                "decision": "block",
                "reason": "Protected credentials file."
            }

        return {
            "decision": "allow",
            "reason": "Command allowed."
        }

    elif tool == "write_file":

        path = PurePosixPath(req.get("path", ""))

        try:
            path.relative_to(BUILD)
            return {
                "decision": "allow",
                "reason": "Write inside build directory."
            }
        except Exception:
            return {
                "decision": "block",
                "reason": "Write outside build directory."
            }

    elif tool == "http_request":

        url = req.get("url", "")
        host = urlparse(url).hostname or ""

        if host in ["pypi.org", "registry.npmjs.org"]:
            return {
                "decision": "allow",
                "reason": "Allowed host."
            }

        return {
            "decision": "block",
            "reason": "Host not allowed."
        }

    return {
        "decision": "block",
        "reason": "Unknown tool."
    }