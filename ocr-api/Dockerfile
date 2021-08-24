FROM python:3.8
WORKDIR /modergator
COPY requirements.txt requirements.txt
COPY ocr-api/ ocr-api/
RUN apt-get update && apt-get install -y net-tools tesseract-ocr ffmpeg libsm6 libxext6
RUN pip3 install -r requirements.txt
RUN pip3 install -r ocr-api/requirements.txt
CMD ["python3", "ocr-api/main.py"]
