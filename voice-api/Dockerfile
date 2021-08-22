FROM python:3.8
WORKDIR /voice-api
COPY . .
RUN pip3 install -r base-requirements.txt
RUN pip3 install -r requirements.txt
CMD ["python3", "main.py"]
