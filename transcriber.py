import pathlib
from pathlib import Path

from telegram import Update
from telegram.ext import CallbackContext

from RecognitionTargets import Google, Azure, APIProviders


def transcribe(update: Update, context: CallbackContext):
    output_path = pathlib.Path('./downloads')
    output_path.mkdir(exist_ok=True)
    filename = __download_file(update, context, output_path)

    msg_processing = update.message.reply_text('Wird bearbeitet...')
    try:
        filename_no_ext = Path(filename).stem

        # get the preferred api provider
        provider = context.user_data.get('api_provider', APIProviders.azure.value)
        reco_target = None
        if provider == APIProviders.google.value:
            reco_target = Google()
        elif provider == APIProviders.azure.value:
            reco_target = Azure()

        files = reco_target.convert(in_file=filename)
        for file in files:
            text = reco_target.recognize_speech(file)
            update.message.reply_text(text, reply_to_message_id=update.message.message_id)
    except Exception as e:
        update.message.reply_text("❌ An Error occured ❌", reply_to_message_id=update.message.message_id)
        pass

    # delete the processing message
    msg_processing.delete()

    __cleanup(filename_no_ext, output_path)

    # increase the message count
    context.user_data['message_count'] = context.user_data.get('message_count', 0) + 1


def __download_file(update: Update, context: CallbackContext, folder_path: pathlib.Path) -> pathlib.Path:
    # Download the file
    if update.message.audio is not None:
        file_id = update.message.audio.file_id
        duration = update.message.audio.duration
    elif update.message.voice is not None:
        file_id = update.message.voice.file_id
        duration = update.message.voice.duration
    else:
        raise RuntimeError("No supported message type found")

    # download the voice message
    file = context.bot.getFile(file_id)
    filename = folder_path / f'voice_{update.update_id}{pathlib.Path(file["file_path"]).suffix}'
    file.download(filename)

    # save the length of the voice message
    if duration > context.user_data.get('max_message_length', 0):
        context.user_data['max_message_length'] = duration

    return pathlib.Path(filename)


def __cleanup(filename_prefix: str, path: pathlib.Path):
    """
    Removes all files starting with 'filename_prefix' in 'path'
    """
    file_list = [fn for fn in path.glob(f'*')]

    for fn in file_list:
        fn.unlink()
