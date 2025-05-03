# fastapi_app/Dockerfile
FROM python:3.10-slim

RUN apt-get update && apt-get install -y libgomp1 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY fastapi_app/requirements-fastapi.txt .
RUN pip install --no-cache-dir -r requirements-fastapi.txt

COPY fastapi_app/app.py .
COPY src ./src

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
