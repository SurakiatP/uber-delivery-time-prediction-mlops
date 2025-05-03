FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN pip install kafka-python requests

CMD ["python", "stream_inference.py"]
