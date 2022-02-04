import json
import pathlib
from enum import Enum
from typing import List

import speech_recognition as sr
import abc
from pydub import AudioSegment


class APIProviders(Enum):
    azure = "azure"
    google = "google"


class RecognitionTarget:
    def __init__(self):
        self.speech_eng = sr.Recognizer()
        self.lang = "de-DE"
        self.seg_len = 1e10  # infinity

    def convert(self, in_file) -> List[pathlib.Path]:
        sound = self._get_sound(in_file)
        files = []
        i = 0
        start = 0
        end = start + self.seg_len
        while start < sound.duration_seconds:
            files.append(in_file.with_suffix(f'.{i}.wav'))
            sound[start * 1000:min(end, sound.duration_seconds) * 1000].export(files[-1], format = "wav")
            start = end
            end += self.seg_len
            i += 1
        return files

    @abc.abstractmethod
    def recognize_speech(self, wav_file) -> str:
        pass

    def _get_data(self, wav_file: pathlib.Path):
        with sr.AudioFile(str(wav_file)) as f:
            data = self.speech_eng.record(f)
        return data

    @staticmethod
    def _get_sound(in_file: pathlib.Path):
        if in_file.suffix in [".ogg", ".oga"]:
            return AudioSegment.from_ogg(in_file)
        elif in_file.suffix == ".opus":
            return AudioSegment.from_file(in_file, codec = "opus")
        elif in_file.suffix == ".m4a":
            return AudioSegment.from_file(in_file)


class Google(RecognitionTarget):
    def __init__(self):
        super().__init__()
        self.seg_len = 180

    def recognize_speech(self, wav_file):
        return self.speech_eng.recognize_google(self._get_data(wav_file = wav_file), language = self.lang)


class Azure(RecognitionTarget):
    def __init__(self):
        super().__init__()
        self.seg_len = 60
        with open('data/config.json') as json_file:
            self.__API_KEY__ = json.load(json_file)['AZURE_key']
        self.service_loc = "westeurope"

    def recognize_speech(self, wav_file):
        return self.speech_eng.recognize_azure(self._get_data(wav_file), language = self.lang, key = self.__API_KEY__,
                                               location = self.service_loc)
