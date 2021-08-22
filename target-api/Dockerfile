FROM python:3.8
WORKDIR /target-api
COPY . .
RUN pip3 install -r base-requirements.txt
RUN pip3 install -r requirements.txt
EXPOSE 80
CMD ["python3", "./main.py"]
