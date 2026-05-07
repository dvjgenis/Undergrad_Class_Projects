# HarmonyForge Makefile — The Commander
# Use these commands for cross-language tests and evaluation.
# See .cursorrules: AI should rely on Makefile to trigger tests.

.PHONY: dev dev-clean dev-backend dev-frontend install test-solver calc-her eval-telemetry health check-audiveris install-audiveris

# Install Python backend dependencies (use same python3 as make dev)
install:
	python3 -m pip install -r requirements.txt

# Kill processes on ports 8000, 3000, 3001 (run before dev if "Address already in use")
dev-clean:
	@lsof -ti:8000 -ti:3000 -ti:3001 2>/dev/null | xargs kill -9 2>/dev/null || true
	@echo "Ports 8000, 3000, 3001 cleared."

# Full stack (frontend + backend)
dev:
	npm run dev

# Backend only
dev-backend:
	npm run dev:backend

# Frontend only
dev-frontend:
	npm run dev:frontend

# Engine/solver tests (Python)
test-solver:
	@python -m pytest engine/ -v -x 2>/dev/null || echo "Run: pip install pytest && make test-solver"

# Harmonic Error Rate (music21)
calc-her:
	python eval/her_calculator.py

# Telemetry / Repair Efficiency analysis
eval-telemetry:
	@echo "Telemetry scripts: eval/telemetry/"
	@echo "Place survey data and timing logs there. Run custom analysis as needed."

# Health check (backend must be running)
health:
	curl -s http://localhost:8000/health || echo "Backend not running. Start with: make dev-backend"

# Check if Audiveris is installed (for PDF → MusicXML)
check-audiveris:
	./scripts/check-audiveris.sh

# Install Audiveris (macOS; run in Terminal if DMG mount fails)
install-audiveris:
	./scripts/install-audiveris.sh
