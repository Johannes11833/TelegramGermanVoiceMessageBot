import json
import logging

from telegram import Update, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Enable logging
from RecognitionTargets import APIProviders
from transcriber import transcribe

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    update.message.reply_text('Moin Meister! Schick mir deine tollsten Sprachnachrichten.')


def help(update, context):
    update.message.reply_text(
        '<p><strong>Funktionsweise</strong>:</p><p>Schicke mir hier einfach deine Voice Message und ich werde sie f&uuml;r dich transkribieren.</p><p><strong>Befehle</strong>:</p><p>/api</p>',
        parse_mode=ParseMode.HTML)


def voice(update: Update, context: CallbackContext):
    transcribe(update, context)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def set_api_provider(update: Update, context):
    import re
    provider = [*re.findall(r'\/api ([\w]+)', update.message.text), None][0]

    supported_providers = [p.value for p in APIProviders]
    if provider in supported_providers:
        context.user_data['api_provider'] = provider
        update.message.reply_text(f'Der API Provider wurde geupdatet auf {provider}')
    elif provider is None:
        update.message.reply_text(
            f"Aktueller API Provider ist: {context.user_data.get('api_provider', APIProviders.azure.value)}")
    else:
        update.message.reply_text(
            f'{provider} ist kein unterstützter Provider! Erlaubt sind: {str(supported_providers)[1:-1]}')


def main():
    # get the token
    with open('config.json') as json_file:
        telegram_token = json.load(json_file)['telegram_token']

    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(telegram_token, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("api", set_api_provider))

    # add handlers for voice-messages and audio files.
    dp.add_handler(MessageHandler(Filters.voice, voice))
    dp.add_handler(MessageHandler(Filters.audio, voice))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
