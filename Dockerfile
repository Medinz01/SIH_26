FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app /app

# The command to run our FastAPI app. We'll create main.py next.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]