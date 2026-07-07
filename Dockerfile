FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir -e .

# Copy server code
COPY server.py .

# Run the MCP server
CMD ["python", "server.py"]
