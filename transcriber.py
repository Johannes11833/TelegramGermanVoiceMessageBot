import os
import time
from pathlib import Path

from telegram import Update
from telegram.ext import CallbackContext


def transcribe(update: Update, context: CallbackContext):
    output_path = './downloads'
    filename = __download_file(update, context, output_path)

    update.message.reply_text('Wird bearbeitet...')

    filename_no_ext = Path(filename).stem

    # TODO: add api call here
    time.sleep(5)

    print(filename_no_ext)
    __cleanup(filename_no_ext, output_path)

    update.message.reply_text('Wurde bearbeitet...')


def __download_file(update: Update, context: CallbackContext, folder_path: str) -> str:
    # Download the file
    file = context.bot.getFile(update.message.voice.file_id)
    filename = f'./{folder_path}/voice_{update.update_id}.ogg'
    file.download(filename)

    return filename


def __cleanup(filename_prefix: str, path: str):
    """
    Removes all files starting with 'filename_prefix' in 'path'
    """
    file_list = [fn for fn in os.listdir(path) if fn.startswith(filename_prefix)]

    print(file_list)

    for fn in file_list:
        os.remove(os.path.join(path, fn))
