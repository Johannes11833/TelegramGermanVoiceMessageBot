FROM python:3-slim-buster

WORKDIR /usr/src/app

# install dependencies
RUN apt update
RUN apt install -y ffmpeg

# copy the content of the local src directory to the working directory
WORKDIR /usr/src/app/telegram_bot
COPY . .

# install requirements
RUN pip install --no-cache-dir -r requirements.txt


EXPOSE 80


CMD [ "python", "./main.py" ]