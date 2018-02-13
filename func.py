# coding: utf8
import telebot
import connector
from time import sleep
import sys
from alert_system import alert


def main(token, user_id):
    client_id = False
    bot = telebot.TeleBot(token)
    _bot = bot.get_me().username

    @bot.message_handler(commands=['ban'])
    def ban_user(message):
        db = connector.DataBaseConnect()
        if message.reply_to_message is not None:
            if message.reply_to_message.forward_from.id != user_id:
                db.ban_user(user_id=user_id, bot_name=_bot, banned_user=str(message.reply_to_message.forward_from.id))
                bot.send_message(user_id, text='Пользователь успешно заблокирован.')
            else:
                bot.send_message(user_id, text='Вы неможете заблокировать себя.')
        else:
            bot.send_message(user_id, text='Пользователь невыбран.')

    @bot.message_handler(commands=['start'])
    def run(message):
        global flag
        flag = True
        db = connector.DataBaseConnect()
        if int(message.chat.id) != int(user_id) and str(message.chat.id) not in db.get_banned_users(user_id=user_id,
                                                                                                    bot_name=_bot):
            bot.forward_message(user_id, message_id=message.message_id, from_chat_id=message.chat.id)
        db.add_user(user_id=user_id, user=message, _bot=_bot)
        if str(message.chat.id) not in db.get_banned_users(user_id=user_id, bot_name=_bot):
            if db.off_greeting(get_status=True, user_id=user_id, bot_name=bot.get_me().username) == '1':
                delay = db.get_delay(user_id=user_id, bot_name=bot.get_me().username)
                sleep(int(delay[0]))
                greeting = db.get_greeting(user_id=str(user_id), bot_name=bot.get_me().username)[0]
                if db.manage_ad(get=True, user_id=user_id, bot_name=_bot)[0][0]:
                    greeting += '\n\nБот создан с помощью @FoqBot.'
                bot.send_message(message.chat.id, text=greeting)

    @bot.message_handler(content_types=["text", "sticker", "photo", "audio", 'document', 'voice'])
    def driver(message):
        nonlocal client_id
        global flag
        db = connector.DataBaseConnect()
        if str(message.chat.id) not in db.get_banned_users(user_id=user_id, bot_name=_bot):
            if int(message.from_user.id) != int(user_id):
                bot.forward_message(user_id, message_id=message.message_id, from_chat_id=message.chat.id)
                if message.text in [x[0] for x in db.get_commands(user_id=user_id, _all=True)] and message.text != 'empty':
                    command_message = db.get_commands(user_id=user_id, command=message.text)
                    bot.send_message(message.from_user.id, text=command_message)
                    bot.send_message(user_id, text=command_message)
                try:
                    if flag:
                        status = db.get_second_greeting_status(user_id=user_id, bot_name=_bot)[0][0]
                        if status:
                            second_greeting = db.get_greeting(second=True, user_id=user_id, bot_name=_bot)
                            if second_greeting[0] != 'empty':
                                bot.send_message(message.from_user.id, text=second_greeting[0])
                            flag = False
                except NameError:
                    pass
            else:
                try:
                    if message.reply_to_message is not None:
                        bot.send_message(message.reply_to_message.forward_from.id, text=message.text)
                        client_id = message.reply_to_message.forward_from.id
                        if message.text in [x[0] for x in db.get_commands(user_id=user_id, _all=True)] and message.text != 'empty':
                            command_message = db.get_commands(user_id=user_id, command=message.text)
                            bot.send_message(client_id, text=command_message)
                            bot.send_message(user_id, text=command_message)
                    else:
                        if client_id:
                            flag = False
                            if message.text in [x[0] for x in db.get_commands(user_id=user_id, _all=True)]:
                                command_message = db.get_commands(user_id=user_id, command=message.text)
                                bot.send_message(client_id, message.text)
                                bot.send_message(client_id, text=command_message)
                                bot.send_message(user_id, text=command_message)
                            else:
                                bot.send_message(client_id, text=message.text)
                        else:
                            bot.send_message(message.chat.id, 'Вы не выбрали получателя.')
                except Exception as Error:
                    print(Error)
    while True:
        try:
            bot.get_updates()
            bot.polling(none_stop=True, timeout=100)
        except Exception as ApiError:
            if '409' in str(ApiError):
                print('Conflict was occurred in bot: {}. Holder: {}'.format(_bot, user_id))
                sys.exit()
            else:
                print('Error at bot: {}. Body: {}'.format(_bot, ApiError))
