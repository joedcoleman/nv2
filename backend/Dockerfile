# Use an official Python runtime as the base image
FROM python:3.10

WORKDIR /app

COPY settings.toml .

RUN mkdir /app/backend

COPY backend/requirements.txt /app/backend/

WORKDIR /app/backend

RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]