# syntax=docker/dockerfile:1
FROM python:3.8-alpine
WORKDIR /LT-demo-bot
COPY .. .
RUN pip3 install -r requirements.txt
CMD ["python3", "main.py"]
