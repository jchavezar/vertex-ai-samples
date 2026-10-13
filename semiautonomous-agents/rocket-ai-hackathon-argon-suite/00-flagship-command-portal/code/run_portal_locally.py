#!/usr/bin/env python3
"""Launch the Flagship Rocket AI Hackathon Command Hub locally on port 8080."""
import os
import sys
import uvicorn

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
os.environ.setdefault("SERVICE_MODE", "portal")
os.environ.setdefault("GCP_PROJECT", "vtxdemos")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get("PORT", "8080")), reload=True)
