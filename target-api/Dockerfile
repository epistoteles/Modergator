FROM python:3.8
WORKDIR /modergator
COPY requirements.txt requirements.txt
COPY target-api/ target-api/
RUN apt-get update && apt-get install -y net-tools
RUN pip3 install -r requirements.txt
RUN pip3 install -r target-api/requirements.txt
EXPOSE 80
CMD ["python3", "target-api/main.py"]
