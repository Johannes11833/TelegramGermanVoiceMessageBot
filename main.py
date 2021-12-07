import json
import logging
import pathlib

from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, PicklePersistence

# Enable logging
from RecognitionTargets import APIProviders
from transcriber import transcribe

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    update.message.reply_text(
        'Moin Meister! Schick mir deine tollsten Sprachnachrichten. \n\nGebe /help ein, um alle Befehle zu sehen.')


def help(update, context):
    update.message.reply_text(
        '<strong>Funktionsweise</strong>:\nSchicke mir hier einfach deine Voice Message und ich werde sie für dich '
        'transkribieren.'
        '\n\n<strong>Befehle</strong>:\n/api &lt;provider&gt; - Legt die zum Transkribieren zu verwendende API fest. '
        '\n/highscore Gibt die Länge deiner längsten Sprachnachricht aus.',
        parse_mode='HTML')


def voice(update: Update, context: CallbackContext):
    transcribe(update, context)


def highscore(update: Update, context: CallbackContext):
    max_length = context.user_data.get("max_message_length", None)

    if max_length is None:
        update.message.reply_text('Du hast mir noch keine Sprachnachricht geschickt')
    else:
        update.message.reply_text(
            f'Deine Längste Sprachnachricht: <strong>{max_length} Sekunden </strong>',
            parse_mode='HTML')


def message_count(update: Update, context: CallbackContext):
    update.message.reply_text(f'Bisher transkribierte Sprachnachrichten: '
                              f'<b>{context.user_data.get("message_count", 0)}</b>',parse_mode='HTML')


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def set_api_provider(update: Update, context):
    import re
    provider: str = [*re.findall(r'\/api ([\w]+)', update.message.text), ''][0].lower().strip()

    supported_providers = [p.value for p in APIProviders]
    if provider in supported_providers:
        context.user_data['api_provider'] = provider
        update.message.reply_text(f'Der API Provider wurde geupdatet auf {provider}')
    elif not provider:
        update.message.reply_text(
            f"Aktueller API Provider ist: {context.user_data.get('api_provider', APIProviders.azure.value)}")
    else:
        update.message.reply_text(
            f'{provider} ist kein unterstützter Provider! Erlaubt sind: {str(supported_providers)[1:-1]}')


def main():
    # create Data folder and initialize PicklePersistence
    pathlib.Path('./data').mkdir(exist_ok=True)
    persistence = PicklePersistence('./data/bot_data.pkl')

    # get the token
    with open('data/config.json') as json_file:
        telegram_token = json.load(json_file)['telegram_token']

    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(telegram_token, use_context=True, persistence=persistence)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("api", set_api_provider))
    dp.add_handler(CommandHandler("highscore", highscore))
    dp.add_handler(CommandHandler("count", message_count))

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
