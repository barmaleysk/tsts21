import telebot
import message_templates

token = ''
bot = telebot.TeleBot(token)


def alert(user, bot_name):
    bot.send_message(
        chat_id=user,
        text=message_templates.alert_message.format(bot_name),
    )
