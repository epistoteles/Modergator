FROM python:3.8
WORKDIR /modergator
COPY requirements.txt requirements.txt
COPY text-api/ text-api/
RUN pip3 install -r requirements.txt
RUN pip3 install -r text-api/requirements.txt
EXPOSE 80
CMD ["python3", "text-api/main.py"]
