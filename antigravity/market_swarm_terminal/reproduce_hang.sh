#!/bin/bash

echo ">>> 1. WARMUP: Simple Time Check"
curl -s -X POST http://localhost:8001/chat \
-H "Content-Type: application/json" \
-d '{"message": "What time is it?", "session_id": "repro_hang", "model": "gemini-2.5-flash"}' > /dev/null
echo -e "\n[Done]"

echo ">>> 2. COMPLEX: Compare Amazon and Google"
# We expect this to trigger the parallel workflow
curl -s -N -X POST http://localhost:8001/chat \
-H "Content-Type: application/json" \
-d '{"message": "Compare Amazon (AMZN) and Google (GOOGL) revenue", "session_id": "repro_hang", "model": "gemini-2.5-flash"}' > complex_out.txt
echo -e "\n[Done Complex]"

echo ">>> 3. SIMPLE: Price of MSFT (The Hang Candidate)"
# This is where it reportedly hangs
curl -v -N -X POST http://localhost:8001/chat \
-H "Content-Type: application/json" \
-d '{"message": "what was the stock price for MSFT YSTD?", "session_id": "repro_hang", "model": "gemini-2.5-flash"}'
