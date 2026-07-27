FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy Python code
COPY app ./app

EXPOSE 8081

ENV PYTHONUNBUFFERED=1
ENV PORT=8081

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8081"]
