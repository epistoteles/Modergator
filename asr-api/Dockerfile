FROM python:3.8
WORKDIR /modergator
COPY requirements.txt requirements.txt
COPY asr-api/ asr-api/
COPY data/ data/
RUN apt-get update && apt-get install -y net-tools ffmpeg
RUN pip3 install -r requirements.txt
RUN pip3 install -r asr-api/requirements.txt
EXPOSE 80
CMD ["python3", "asr-api/main.py"]
