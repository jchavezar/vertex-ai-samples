#!/bin/bash
# Clean shutdown for Weil Legal-Tech Innovation Showcase
echo "🛑 Shutting down Weil Legal-Tech Showcase services (ports 8000, 5173)..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:5173 | xargs kill -9 2>/dev/null || true
echo "✅ Shutdown complete. Ports 8000 and 5173 are clean."
