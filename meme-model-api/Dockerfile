FROM python:3.8
WORKDIR /modergator
COPY requirements.txt requirements.txt
COPY meme-model-api/ meme-model-api/
COPY data/ data/
RUN apt-get update && apt-get install -y net-tools
RUN pip3 install -r requirements.txt
RUN pip3 install -r meme-model-api/requirements.txt
RUN pip3 install -r meme-model-api/requirements_git.txt
WORKDIR /modergator/meme-model-api/vilio/py-bottom-up-attention
RUN python3 setup.py build develop
WORKDIR /modergator
CMD ["python3", "meme-model-api/main.py"]
