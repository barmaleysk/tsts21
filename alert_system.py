import telebot
import texts

token = ''
bot = telebot.TeleBot(token)


def alert(user, bot_name):
    bot.send_message(chat_id=user, text=texts.alert_message.format(bot_name))
