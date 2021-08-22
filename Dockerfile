FROM python:3.8
WORKDIR /modergator
COPY . .
RUN apt-get clean -y
RUN apt-get update -y && apt-get upgrade -y
RUN apt-get clean -y
RUN apt-get -y install screen net-tools tesseract-ocr virtualenv
RUN chmod +x install.sh
RUN chmod +x run.sh
RUN ./install.sh
CMD ["bash", "run.sh"]
