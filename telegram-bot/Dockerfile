FROM python:3.8
WORKDIR /modergator
COPY requirements.txt requirements.txt
COPY telegram-bot/ telegram-bot/
COPY optoutlist.pickle optoutlist.pickle
COPY data/ data/
RUN apt-get update && apt-get install -y net-tools
RUN pip3 install -r requirements.txt
RUN pip3 install -r telegram-bot/requirements.txt
CMD ["python3", "telegram-bot/main.py"]
