# TelegramGermanVoiceMessageBot
Telegram bot that can transcribe German voice messages.


## Info for using Docker
Map the path of the config on the host to /usr/src/app/telegram_bot/config.json on the container. The config is not included in the docker container.

### Example config file
The confg file should be place at `data/config.json`:

```
{
    "telegram_token": "<YOUR_TELEGRAM_TOKEN>",
    "AZURE_key": "<YOU_AZURE_KEY>"
}
```
