FROM python:3.11-slim
WORKDIR /app
RUN pip install --no-cache-dir fastmcp plaid-python requests uvicorn
COPY . .
ENV PORT=8080
ENV MCP_TRANSPORT=streamable-http
EXPOSE 8080
CMD ["python", "server.py"]
