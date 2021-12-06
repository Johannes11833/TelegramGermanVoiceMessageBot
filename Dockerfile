FROM python:3

WORKDIR /usr/src/app

# install dependencies
RUN apt update
RUN apt install -y ffmpeg
RUN apt install -y git
RUN git clone https://github.com/Uberi/speech_recognition

# install speech_recognition via pip
WORKDIR /usr/src/app/speech_recognition
RUN pip install -e .

# copy the content of the local src directory to the working directory
WORKDIR /usr/src/app/telegram_bot
COPY . .

# install requirements
RUN pip install --no-cache-dir -r requirements.txt


EXPOSE 80


CMD [ "python", "./main.py" ]