#!/bin/bash
# Run HarmonyForge unified API (from project root)
cd "$(dirname "$0")"
pip install -q -r requirements.txt 2>/dev/null || true
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
