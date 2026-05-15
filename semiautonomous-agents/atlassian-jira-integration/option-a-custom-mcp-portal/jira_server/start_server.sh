#!/bin/bash
source ../jira/bin/activate

# Kill existing server on port 8080
pid=$(lsof -t -i:8080)
if [ -n "$pid" ]; then
  echo "Killing existing server on PID $pid"
  kill -9 $pid
fi

# Also kill by name just in case
pkill -f "python server.py"

echo "Starting server..."
# Use -u for unbuffered output
nohup python -u server.py > server.log 2>&1 &
pid=$!
echo "Server process started with PID $pid"

# Wait for port 8080 to be active
echo "Waiting for server to listen on port 8080..."
for i in {1..10}; do
    if lsof -i:8080 > /dev/null; then
        echo "Server is up!"
        exit 0
    fi
    sleep 1
done

echo "Server failed to start within 10 seconds. Checking logs:"
cat server.log
exit 1
