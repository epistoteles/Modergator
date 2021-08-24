FROM python:3.8
WORKDIR /modergator
COPY requirements.txt requirements.txt
COPY meme-detection-api/ meme-detection-api/
COPY ocr-api/ ocr-api/
COPY data/ data/
RUN apt-get update && apt-get install -y net-tools ffmpeg
RUN pip3 install -r requirements.txt
RUN pip3 install -r meme-detection-api/requirements.txt
CMD ["python3", "meme-detection-api/main.py"]

