# docker/backend.dockerfile

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY smart_quiz_api/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend source
COPY smart_quiz_api/ .

# Expose FastAPI default port
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
