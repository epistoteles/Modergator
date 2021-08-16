# syntax=docker/dockerfile:1
FROM python:3.8-alpine
WORKDIR /hatefulmemes-text-api
COPY . .
RUN pip3 install -r requirements.txt
CMD ["python3", "main.py"]
