# coding: utf8
import telebot
import func
import connector
from multiprocessing import Process
from message_templates import *
import re
import imgur

commands_validate_pattern = re.compile(r'/[A-Za-z_]+')
processes = {}
token = '655728040:AAFnhcwYKbkBUoWhDJLxaaR3aG4-NY9bQWE'
bot = telebot.TeleBot(token)
client_status = {}


def dispatch(user_id, text, _bot=None, for_all=False):
    if not for_all:
        users = DB.get_all_users(user_id=user_id, bot=_bot)
        bot_token = DB.get_one_time_token(user_id=user_id, bot_name=_bot)[0][0]
        __bot = telebot.TeleBot(bot_token)
        for user in users[0][0].split():
            print('Sending to user {}, message: {}'.format(user, text))
            __bot.send_message(chat_id=user, text=text)
    else:
        data = DB.select_info_for_all_dispatch(user_id=user_id)
        for _token in data:
            __bot = telebot.TeleBot(_token)
            for user in data[_token]:
                __bot.send_message(chat_id=user, text=text)


def get_bot_name(_token):
    return telebot.TeleBot(_token).get_me().username


def check_token(_token):
    driver = telebot.TeleBot(_token)
    try:
        driver.get_me()
        return True
    except:
        return False


@bot.message_handler(commands=['start', 'run'])
def greeting(message):
    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=False, resize_keyboard=True)
    markup.row('Добавить бота', 'Мои боты')
    markup.row('Как это работает?', 'Поддержка')
    bot.send_message(message.chat.id,
                     text=how,
                     reply_markup=markup,
                     parse_mode='Markdown')


@bot.message_handler(content_types=["text", 'photo'])
def add_bot(message):
    if message.text == 'Добавить бота':
        reset_option(message)
        markup = telebot.types.InlineKeyboardMarkup()
        cancel_button = telebot.types.InlineKeyboardButton(text='Отмена', callback_data='Отмена')
        markup.add(cancel_button)
        bot.send_message(message.chat.id, text='Отправьте токен, или перешлите сообщение с токеном от @BotFather.',
                         reply_markup=markup)
        client_status[message.from_user.id] = {'token': 'wait'}
    elif message.text == 'Мои боты':
        reset_option(message)
        bot_settings(msg=message)
    elif message.text == 'Как это работает?':
        reset_option(message)
        bot.send_message(message.chat.id, text=how,
                         parse_mode='Markdown')
    elif message.text == 'Поддержка':
        reset_option(message)
        keyboard = telebot.types.InlineKeyboardMarkup()
        donate = telebot.types.InlineKeyboardButton(text='Донат', callback_data='donate')
        keyboard.add(donate)
        bot.send_message(message.chat.id, text=support, reply_markup=keyboard)
    elif message.from_user.id in client_status and 'token' in client_status[message.from_user.id]:
        add_new_bot(message)
    elif message.from_user.id in client_status and 'option' in client_status[message.from_user.id]:
        bot_name = client_status[message.from_user.id]['bot_name']
        main_bots_settings(message=message, user_id=message.from_user.id,
                           option=client_status[message.from_user.id]['option'],
                           value=message.text,
                           bot_name=bot_name if bot_name != 'all' else False)


def add_new_bot(message):
    if client_status[message.from_user.id]['token'] == 'wait':
        if len(message.text.split()) == 1:
            _token = message.text
        else:
            try:
                _token = message.text.split('\n\n')[1].split('API:\n')[1]
            except IndexError:
                return bot.send_message(chat_id=message.from_user.id, text='Токен необнаружен. Попробуйте снова.')
        client_status[message.from_user.id]['token'] = _token
        try:
            if client_status[message.from_user.id]['token'] not in DB.get_all_tokens(extend=True):
                if check_token(client_status[message.from_user.id]['token']):
                    process = Process(target=func.main, args=(_token, message.from_user.id))
                    name = get_bot_name(_token)
                    if str(message.from_user.id) not in processes:
                        processes[str(message.from_user.id)] = {name: process}
                    else:
                        processes[str(message.from_user.id)].update({name: process})
                    process.start()
                    DB.insert_new_bot(user=str(message.from_user.id),
                                      bot_name=get_bot_name(client_status[message.from_user.id]['token']),
                                      token=client_status[message.from_user.id]['token'])
                    bot.send_message(message.chat.id, text='*Бот создан.*', parse_mode='Markdown')
                    bot_settings(message)
                else:
                    bot.send_message(message.chat.id, text='Токен невалидный. Попробуйте снова.')
                    client_status[message.from_user.id]['token'] = 'wait'
            else:
                client_status[message.from_user.id]['token'] = 'wait'
                bot.send_message(message.chat.id, text='Бот с таким токеном уже существует. Попробуйте снова.')
        except Exception as bot_create_error:
            bot.send_message(message.chat.id, bot_create_error)


def reset_option(message):
    if message.from_user.id in client_status:
        user = client_status[message.from_user.id]
        if 'option' in user:
            del client_status[message.from_user.id]['option']
        if 'token' in user:
            del client_status[message.from_user.id]['token']


def validate_commands(commands):
    result = commands_validate_pattern.findall(commands)
    if result:
        return len(result) > 1, result


def add_more_commands(commands, message):
    commands_set = []
    for command in commands:
        if command not in [x[0] for x in DB.get_commands(_all=True, user_id=message.from_user.id)]:
            print(command)
            DB.add_command(user_id=message.from_user.id, command=command, msg='empty')
        else:
            commands_set.append(command)
    if commands_set:
        message_text = '('+', '.join(commands_set).strip(', ')+')'
        bot.send_message(chat_id=message.from_user.id,
                         text='Некоторые из команд у Вас уже есть. {}\nОни небыли добавлены.'.format(message_text))
    else:
        bot.send_message(chat_id=message.from_user.id, text='Команды добавлены.')
        return True
    return False


def main_bots_settings(message, user_id, option, bot_name=False, value=False):
    if bot_name:
        if option == 'first':
            DB.reset_greeting(user_id=user_id, bot_name=client_status[user_id]['bot_name'],
                              new_greeting=value)
            del client_status[user_id]['option']
            return set_greetings(chat_id=user_id)
        elif option == 'delay':
            if value.isdigit():
                DB.set_greeting_delay(user_id=user_id, value=value,
                                      bot_name=client_status[user_id]['bot_name'])
                del client_status[user_id]['option']
                bot.send_message(user_id, text='Готово.')
            else:
                bot.send_message(message.from_user.id, text='Введите задержку в секундах, например: *18*',
                                 parse_mode='Markdown')
                return
        elif option == 'second':
            DB.reset_greeting(second=True, user_id=user_id, new_greeting=value, bot_name=bot_name)
            bot.send_message(user_id, text='Готово.')
            del client_status[user_id]['option']
            return set_greetings(chat_id=user_id)
        elif option == 'dispatch':
            dispatch(_bot=bot_name, user_id=user_id, text=message.text)
            bot.send_message(message.chat.id, text='Рассылка окончена.')
    else:
        if option in ['first', 'delay', 'second']:
            if option == 'first':
                DB.reset_greeting(user_id=user_id, new_greeting=value)
                bot.send_message(user_id, text='Готово.')
                del client_status[user_id]['option']
                return set_greetings(chat_id=user_id, _all=True)
            elif option == 'delay':
                if value.isdigit():
                    DB.set_greeting_delay(user_id=user_id, value=value, for_all=True)
                else:
                    bot.send_message(user_id, text='Введите задержку в секундах, например: *18*',
                                     parse_mode='Markdown')
                    return
            elif option == 'second':
                DB.reset_greeting(second=True, user_id=user_id, new_greeting=value)
                bot.send_message(user_id, text='Готово.')
                del client_status[user_id]['option']
                return set_greetings(chat_id=user_id, _all=True)
        elif option == 'dispatch':
            dispatch(for_all=True, user_id=user_id, text=message.text)
            bot.send_message(message.chat.id, text='Рассылка окончена.')
        elif option == 'add':
            validate = validate_commands(message.text)
            if not validate[0]:
                keyboard = telebot.types.InlineKeyboardMarkup()
                cancel = telebot.types.InlineKeyboardButton(text='Отмена', callback_data='cancel')
                keyboard.add(cancel)
                if message.text not in [x[0] for x in DB.get_commands(_all=True, user_id=message.from_user.id)]:
                    if message.text.startswith('/'):
                        client_status[user_id]['command'] = validate[1][0]
                        client_status[user_id]['option'] = 'set_value'
                        bot.send_message(chat_id=user_id, text='Укажите значение для команды *(только текст или смайлы)*',
                                         parse_mode='Markdown', reply_markup=keyboard)
                    else:
                        bot.send_message(user_id, text='Ошибочный формат команды. Попробуйте снова.',
                                         reply_markup=keyboard)
                    return
                return bot.send_message(message.chat.id, text='У Вас уже есть такая команда. Укажите другое имя.',
                                        reply_markup=keyboard)
            else:
                add_more_commands(validate[1], message)
        elif option == 'set_value':
            keyboard = telebot.types.InlineKeyboardMarkup()
            next_step = telebot.types.InlineKeyboardButton(text='Завершить', callback_data='next')
            keyboard.add(next_step)
            client_status[user_id]['value'] = message.text
            client_status[user_id]['option'] = 'set_image'
            bot.send_message(chat_id=user_id, text='Отправьте фото. (нажмите завершить чтобы пропустить этот шаг)',
                             reply_markup=keyboard)
            return
        elif option == 'set_image':
            command = client_status[user_id]['command']
            value = client_status[user_id]['value']
            _file_id = bot.get_file(message.photo[-1].file_id)
            path = _file_id.file_path
            image_url = str(imgur.upload_image(path))
            DB.add_command(user_id=user_id, command=command, msg=value, image=image_url)
        elif option == 'edit':
            msg = message.text
            DB.update_command(user_id=user_id, command=client_status[user_id]['command'], value=msg)
            bot.send_message(user_id, text='Готово.')
            commands_settings(chat_id=user_id, user_id=user_id, get=True)
            del client_status[user_id]['option']
            return
        del client_status[user_id]['option']
        bot.send_message(user_id, text='Готово.')
    get_two_level_settings(send=True, message=message, bot_name=client_status[message.from_user.id]['bot_name'])


def bot_settings(msg, edit=False):
    if msg.from_user.id in client_status:
        del client_status[msg.from_user.id]
    keyboard = telebot.types.InlineKeyboardMarkup()
    bots = DB.get_bots(user_id=str(msg.from_user.id))
    if bots:
        for i in bots:
            url_button = telebot.types.InlineKeyboardButton(text=i[0], callback_data=i[0])
            keyboard.add(url_button)
        change_all_greetings = telebot.types.InlineKeyboardButton(text='Все боты',
                                                                  callback_data='all')
        keyboard.add(change_all_greetings)
        if not edit:
            bot.send_message(msg.chat.id, 'Настройка ботов.', reply_markup=keyboard)
        else:
            bot.edit_message_text(chat_id=msg.message.chat.id,
                                  message_id=msg.message.message_id, text="Настройка ботов.",
                                  reply_markup=keyboard)
    else:
        bot.send_message(msg.chat.id, text='У Вас нет ботов.')


def get_two_level_settings(message, bot_name, send=False):
    client_status[message.from_user.id] = {'bot_name': bot_name}
    keyboard = telebot.types.InlineKeyboardMarkup()
    if bot_name != 'all':
        ad = DB.manage_ad(get=True, bot_name=bot_name, user_id=message.from_user.id)[0][0]
        second_status = DB.get_second_greeting_status(user_id=message.from_user.id,
                                                      bot_name=client_status[message.from_user.id]['bot_name'])[0][0]
        ad_status = ('✖️ Реклама', 'on_ad') if not ad else ('️✔ Реклама', 'off_ad')
        bot_status = ('✖️ Приветствие', 'on') if DB.off_greeting(get_status=True,
                                                                 user_id=message.from_user.id,
                                                                 bot_name=client_status[message.from_user.id]['bot_name']) == '0' else ('️✔ Приветствие', 'off')
        second_greeting = ('✖️ Второе приветствие', 'on_second') if not second_status else ('✔️ Второе приветствие',
                                                                                            'off_second')
    else:
        second_greeting = ('✖️ Второе приветствие', 'on_second')
        bot_status = ('✖ Приветствие', 'on')
        ad_status = ('✖️ Реклама', 'on_ad')
        for i in DB.get_bots(user_id=message.from_user.id):
            if DB.off_greeting(get_status=True, user_id=message.from_user.id, bot_name=i[0]) == '1':
                bot_status = ('✔️ Приветствие', 'off')
                break
        for i in DB.get_bots(user_id=message.from_user.id):
            ad = DB.manage_ad(get=True, bot_name=i[0], user_id=message.from_user.id)[0][0]
            if ad:
                ad_status = ('️✔ Реклама', 'off_ad')
                break
        for i in DB.get_second_greeting_status(for_all=True, user_id=message.from_user.id):
            if i[0] == 1:
                second_greeting = ('✔️️ Второе приветствие', 'off_second')
                break
    text = 'Настройка всех ботов' if bot_name == 'all' else 'Настройка бота @{}'.format(bot_name)
    set_ad = telebot.types.InlineKeyboardButton(text=ad_status[0], callback_data=ad_status[1])
    set_greeting_button = telebot.types.InlineKeyboardButton(text='Настройка приветствий', callback_data='greeting')
    set_delay_button = telebot.types.InlineKeyboardButton(text='Установить задержку', callback_data='delay')
    on_greeting_button = telebot.types.InlineKeyboardButton(text=bot_status[0], callback_data=bot_status[1])
    back_button = telebot.types.InlineKeyboardButton(text='Назад', callback_data='back')
    users = telebot.types.InlineKeyboardButton(text='Пользователи', callback_data='users')
    spam_list = telebot.types.InlineKeyboardButton(text='Чёрный список', callback_data='spam')
    delete_bot = telebot.types.InlineKeyboardButton(text='Удалить бота' if bot_name != 'all' else 'Удалить ботов',
                                                    callback_data='delB')
    second_greeting_active = telebot.types.InlineKeyboardButton(text=second_greeting[0],
                                                                callback_data=second_greeting[1])
    my_buttons = telebot.types.InlineKeyboardButton(text='Мои кнопки', callback_data='m_buttons')
    add_button = telebot.types.InlineKeyboardButton(text='Добавить кнопку', callback_data='a_button')
    keyboard.add(on_greeting_button, second_greeting_active)
    if bot_name == 'all':
        commands_button = telebot.types.InlineKeyboardButton(text='Мои команды', callback_data='get_commands_list')
        add_command_button = telebot.types.InlineKeyboardButton(text='Добавить команду', callback_data='add_command')
        keyboard.add(set_ad, commands_button)
        keyboard.add(add_command_button, set_delay_button)
        keyboard.add(set_greeting_button, delete_bot)
        keyboard.add(my_buttons, add_button)
        keyboard.add(back_button, users)
    if bot_name != 'all':
        keyboard.add(set_ad, set_delay_button)
        keyboard.add(set_greeting_button, spam_list)
        keyboard.add(users, delete_bot)
        keyboard.add(my_buttons, add_button)
        keyboard.add(back_button)
    if not send:
        bot.edit_message_text(chat_id=message.message.chat.id, message_id=message.message.message_id,
                              text=text,
                              reply_markup=keyboard)
    else:
        bot.send_message(message.from_user.id, text=text, reply_markup=keyboard)


def add_button_callback(call):
    pass


def commands_settings(chat_id, user_id, msg_id='', get=False):
    keyboard = telebot.types.InlineKeyboardMarkup()
    delete_button = telebot.types.InlineKeyboardButton(text='Удалить', callback_data='delete_command')
    edit_button = telebot.types.InlineKeyboardButton(text='Изменить значение', callback_data='edit_command')
    show_message_button = telebot.types.InlineKeyboardButton(text='Показать значение',
                                                             callback_data='show_command')
    back_btn = telebot.types.InlineKeyboardButton(text='Назад', callback_data='get_commands_list')
    keyboard.add(edit_button, show_message_button)
    keyboard.add(back_btn, delete_button)
    if not get:
        bot.edit_message_text(chat_id=chat_id, message_id=msg_id,
                              text='Настройка команды {}'.format(client_status[user_id]['command']),
                              reply_markup=keyboard)
    else:
        bot.send_message(chat_id=chat_id, text='Настройка команды {}'.format(client_status[user_id]['command']),
                         reply_markup=keyboard)


def get_commands_list(call):
    commands = DB.get_commands(_all=True, user_id=call.from_user.id)
    if commands:
        keyboard = telebot.types.InlineKeyboardMarkup()
        for i in commands:
            command_btn = telebot.types.InlineKeyboardButton(text=i[0], callback_data=i[0])
            keyboard.add(command_btn)
        cancel = telebot.types.InlineKeyboardButton(text='Назад', callback_data='cancel')
        keyboard.add(cancel)
        return bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                     text='Список Ваших команд', reply_markup=keyboard)
    bot.send_message(call.from_user.id, text='У Вас нет команд')


def user_commands_callback(call):
    if call.from_user.id in client_status:
        client_status[call.from_user.id]['command'] = call.data
        commands_settings(chat_id=call.message.chat.id, user_id=call.from_user.id, msg_id=call.message.message_id)


def cancel_callback(call):
    if call.from_user.id in client_status:
        if 'bot_name' in client_status[call.from_user.id]:
            get_two_level_settings(call, client_status[call.from_user.id]['bot_name'])
            if 'option' in client_status[call.from_user.id]:
                del client_status[call.from_user.id]['option']


def second_greeting_callback(call):
    keyboard = telebot.types.InlineKeyboardMarkup()
    back_button = telebot.types.InlineKeyboardButton(text='Назад', callback_data='greeting')
    keyboard.add(back_button)
    try:
        client_status[call.from_user.id]['option'] = call.data
    except KeyError:
        pass
    if call.from_user.id in client_status and client_status[call.from_user.id]['bot_name'] == 'all':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Установить второе приветствие для всех ботов.',
                              reply_markup=keyboard)
    else:
        if call.from_user.id in client_status and 'bot_name' in client_status[call.from_user.id]:
            _bot = client_status[call.from_user.id]['bot_name']
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text='Установить второе приветствие для: @{}'.format(_bot),
                                  reply_markup=keyboard)


def on_first_greeting_callback(call):
    if call.from_user.id in client_status and 'bot_name' in client_status[call.from_user.id]:
        bot_name = client_status[call.from_user.id]['bot_name']
        if bot_name != 'all':
            DB.off_greeting(user_id=call.from_user.id, bot_name=client_status[call.from_user.id]['bot_name'],
                            value='1')
        else:
            for i in DB.get_bots(user_id=call.from_user.id):
                DB.off_greeting(user_id=call.from_user.id, bot_name=i[0],
                                value='1')
        get_two_level_settings(call, client_status[call.from_user.id]['bot_name'])


def off_first_greeting_callback(call):
    if call.from_user.id in client_status and 'bot_name' in client_status[call.from_user.id]:
        bot_name = client_status[call.from_user.id]['bot_name']
        if bot_name != 'all':
            DB.off_greeting(user_id=call.from_user.id, bot_name=client_status[call.from_user.id]['bot_name'],
                            value='0')
        else:
            for i in DB.get_bots(user_id=call.from_user.id):
                DB.off_greeting(user_id=call.from_user.id, bot_name=i[0],
                                value='0')
        get_two_level_settings(call, client_status[call.from_user.id]['bot_name'])


def set_option_callback(call):
    if call.from_user.id in client_status and 'bot_name' in client_status[call.from_user.id]:
        keyboard = telebot.types.InlineKeyboardMarkup()
        back_button = telebot.types.InlineKeyboardButton(text='Назад', callback_data='cancel')
        keyboard.add(back_button)
        client_status[call.from_user.id]['option'] = call.data
        if client_status[call.from_user.id]['bot_name'] == 'all':
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text=option_text['for_all'][call.data],
                                  reply_markup=keyboard)
        else:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text=option_text['for_one'][call.data].format(
                                      '@' + client_status[call.from_user.id]['bot_name']),
                                  reply_markup=keyboard)


def add_command_callback(call):
    if call.from_user.id in client_status:
        keyboard = telebot.types.InlineKeyboardMarkup()
        cancel = telebot.types.InlineKeyboardButton(text='Назад', callback_data='cancel')
        keyboard.add(cancel)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Укажите название команды.\nНапример:\n/price\n/my_shop\n/pay',
                              reply_markup=keyboard)
        client_status[call.from_user.id]['option'] = 'add'


def ad_trigger_callback(call):
    if call.from_user.id in client_status and 'bot_name' in client_status[call.from_user.id]:
        bot_name = client_status[call.from_user.id]['bot_name']
        if call.data == 'off_ad':
            if bot_name != 'all':
                DB.manage_ad(bot_name=bot_name, user_id=call.from_user.id,
                             ad_status=0)
            else:
                DB.manage_ad(for_all=True, user_id=call.from_user.id, ad_status=0)
        elif call.data == 'on_ad':
            if bot_name != 'all':
                DB.manage_ad(bot_name=bot_name, user_id=call.from_user.id,
                             ad_status=1)
            else:
                DB.manage_ad(for_all=True, user_id=call.from_user.id, ad_status=1)
        get_two_level_settings(call, bot_name)


def delete_command_callback(call):
    if call.from_user.id in client_status and 'command' in client_status[call.from_user.id]:
        DB.delete_command(user_id=call.from_user.id, command=client_status[call.from_user.id]['command'])
        get_commands_list(call)


def show_command_value_callback(call):
    if call.from_user.id in client_status and 'command' in client_status[call.from_user.id]:
        info = DB.get_commands(user_id=call.from_user.id, command=client_status[call.from_user.id]['command'])
        bot.send_message(call.from_user.id, text=info)


def edit_command_callback(call):
    if call.from_user.id in client_status:
        keyboard = telebot.types.InlineKeyboardMarkup()
        cancel = telebot.types.InlineKeyboardButton(text='Назад', callback_data='back_cm')
        keyboard.add(cancel)
        client_status[call.from_user.id]['option'] = 'edit'
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Укажите новое значение для команды.', reply_markup=keyboard)


def dispatch_callback(call):
    if call.from_user.id in client_status:
        client_status[call.from_user.id]['option'] = 'dispatch'
        keyboard = telebot.types.InlineKeyboardMarkup()
        cancel = telebot.types.InlineKeyboardButton(text='Назад', callback_data='cancel')
        keyboard.add(cancel)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Введите сообщение. *(только текст и/или смайлы)*',
                              parse_mode='Markdown',
                              reply_markup=keyboard)


def users_callback(call):
    if call.from_user.id in client_status and 'bot_name' in client_status[call.from_user.id]:
        bot_name = client_status[call.from_user.id]['bot_name']
        if bot_name == 'all':
            msg = 'Вы можете отправить сообщение пользователям всех Ваших ботов'
        else:
            msg = 'Вы можете отослать сообщение всем пользователям бота @{}'.format(bot_name)
        keyboard = telebot.types.InlineKeyboardMarkup()
        dispatch_button = telebot.types.InlineKeyboardButton(text='Рассылка', callback_data='dispatch')
        cancel = telebot.types.InlineKeyboardButton(text='Назад', callback_data='cancel')
        keyboard.add(dispatch_button)
        keyboard.add(cancel)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=msg,
                              reply_markup=keyboard)


def delete_bot_menu_callback(call):
    if call.from_user.id in client_status and 'bot_name' in client_status[call.from_user.id]:
        _bot_name = client_status[call.from_user.id]['bot_name']
        keyboard = telebot.types.InlineKeyboardMarkup()
        yes = telebot.types.InlineKeyboardButton(text='Да', callback_data='delete_bot')
        no = telebot.types.InlineKeyboardButton(text='Нет', callback_data='cancel')
        keyboard.add(yes)
        keyboard.add(no)
        if _bot_name != 'all':
            msg = 'Вы уверены что хотите удалить бота @{}?'.format(_bot_name)
        else:
            msg = 'Вы уверены что хотите удалить всех ботов?'
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text=msg,
                              reply_markup=keyboard)


def delete_bot_callback(call):
    if call.from_user.id in client_status and 'bot_name' in client_status[call.from_user.id] and str(
            call.from_user.id) in processes:
        _bot_name = client_status[call.from_user.id]['bot_name']
        if _bot_name != 'all':
            DB.delete_bot(user_id=call.from_user.id, bot_name=_bot_name)
            bot_process = processes[str(call.from_user.id)][_bot_name]
            if bot_process.is_alive():
                bot_process.terminate()
            del processes[str(call.from_user.id)][_bot_name]
            bot.answer_callback_query(text='Бот отключён и удалён', callback_query_id=call.id, show_alert=True)
            print('BOT {} was deleted.'.format(_bot_name))
        else:
            DB.delete_all_bots(user_id=call.from_user.id)
            for i in processes[str(call.from_user.id)].values():
                if i.is_alive():
                    i.terminate()
            del processes[str(call.from_user.id)]
            bot.answer_callback_query(text='Боты отключёны и удалёны', callback_query_id=call.id,
                                      show_alert=True)
            print('All user {} bots was deleted.'.format(call.from_user.id))
        bots = DB.get_bots(user_id=call.from_user.id)
        if not bots:
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  text='У Вас нет ботов.')
        else:
            bot_settings(msg=call, edit=True)


def set_greetings_callback(call):
    if call.from_user.id in client_status and 'bot_name' in client_status[call.from_user.id]:
        pointer = True if client_status[call.from_user.id]['bot_name'] == 'all' else False
        set_greetings(call.message.chat.id, call.message.message_id, edit=True, _all=pointer)


def second_greeting_activate_callback(call):
    bot_name = client_status[call.from_user.id]['bot_name']
    if bot_name != 'all':
        DB.activate_second_greeting(user_id=call.from_user.id, bot_name=bot_name)
    else:
        if call.data == 'off_second':
            value = 0
        else:
            value = 1
        DB.activate_second_greeting(user_id=call.from_user.id, for_all=True, value=value)
    get_two_level_settings(call, bot_name)


def donate_callback(call):
    bot.send_message(chat_id=call.message.chat.id,
                     text='📥 Вы можете поддержать нас отправив Bitcoin\n\n`Средства поступят через 1 подтверждение сети.`',
                     parse_mode='Markdown')
    bot.send_message(chat_id=call.message.chat.id,
                     text='*17xDn9FC5BRHSPPEvP6bFT6znVBJLm5msX*',
                     parse_mode='Markdown')
    bot.send_photo(call.message.chat.id, open(r"QR.jpg", 'rb').read())


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.message:
        if call.data == 'cancel':
            cancel_callback(call)
        elif call.data == 'second':
            second_greeting_callback(call)
        elif call.data in ['off_second', 'on_second']:
            second_greeting_activate_callback(call)
        elif call.data == 'next':
            command = client_status[call.from_user.id]['command']
            value = client_status[call.from_user.id]['value']
            DB.add_command(user_id=call.from_user.id, command=command, msg=value)
            del client_status[call.from_user.id]['option']
            bot.send_message(call.from_user.id, text='Готово.')
            get_two_level_settings(send=True, message=call, bot_name=client_status[call.from_user.id]['bot_name'])
        elif call.data == 'on':
            on_first_greeting_callback(call)
        elif call.data == 'off':
            off_first_greeting_callback(call)
        elif call.data in ['on_ad', 'off_ad']:
            ad_trigger_callback(call)
        elif call.data in ['first', 'delay']:
            set_option_callback(call)
        elif call.data == 'back':
            bot_settings(call, edit=True)
        elif call.data == 'Отмена':
            if call.from_user.id in client_status:
                del client_status[call.from_user.id]
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text='Отменено')
        elif call.data == 'Назад':
            if call.from_user.id in client_status:
                del client_status[call.from_user.id]
            bot_settings(msg=call, edit=True)
        elif call.data == 'get_commands_list':
            get_commands_list(call)
        elif call.data == 'add_command':
            add_command_callback(call)
        elif call.data == 'delete_command':
            delete_command_callback(call)
        elif call.data == 'donate':
            donate_callback(call)
        elif call.data == 'show_command':
            show_command_value_callback(call)
        elif call.data == 'edit_command':
            edit_command_callback(call)
        elif call.data == 'back_cm':
            reset_option(call)
            commands_settings(chat_id=call.message.chat.id, user_id=call.from_user.id, msg_id=call.message.message_id)
        elif call.data == 'dispatch':
            dispatch_callback(call)
        elif call.data == 'users':
            users_callback(call)
        elif call.data == 'spam':
            get_spam_list(call)
        elif call.data == 'delB':
            delete_bot_menu_callback(call)
        elif call.data == 'delete_bot':
            delete_bot_callback(call)
        elif call.data == 'a_button':
            pass
        elif call.data == 'm_buttons':
            pass
        elif call.data == 'greeting':
            set_greetings_callback(call)
        else:
            try:
                user_commands = [x[0] for x in DB.get_commands(_all=True, user_id=call.from_user.id)]
            except TypeError:
                user_commands = []
            if call.data in user_commands:
                user_commands_callback(call)
            elif call.from_user.id in client_status:
                if 'bot_name' in client_status[call.from_user.id]:
                    if call.data in DB.get_banned_users(user_id=call.from_user.id,
                                                        bot_name=client_status[call.from_user.id]['bot_name']).split():
                        DB.clear_ban_user(user_id=call.from_user.id, banned_user=call.data,
                                          bot_name=client_status[call.from_user.id]['bot_name'])
                        bot.answer_callback_query(text='Пользователь разблокирован', callback_query_id=call.id)
                        get_two_level_settings(call, client_status[call.from_user.id]['bot_name'])
            elif call.data == 'all':
                get_two_level_settings(call, 'all')
            else:
                get_two_level_settings(call, call.data)


def get_spam_list(call):
    if call.from_user.id in client_status and 'bot_name' in client_status[call.from_user.id]:
        keyboard = telebot.types.InlineKeyboardMarkup()
        spam = DB.get_banned_users(user_id=call.from_user.id, bot_name=client_status[call.from_user.id]['bot_name']).split()
        if spam:
            for i in spam:
                name = bot.get_chat_member(chat_id=int(i), user_id=int(i)).user.first_name
                user_button = telebot.types.InlineKeyboardButton(text=name, callback_data=i)
                keyboard.add(user_button)
            back = telebot.types.InlineKeyboardButton(text='Назад', callback_data='cancel')
            keyboard.add(back)
            bot.edit_message_text(chat_id=call.from_user.id,
                                  text='Заблокированные пользователи. Нажмите на пользователя для разблокировки.',
                                  reply_markup=keyboard,
                                  message_id=call.message.message_id)
        else:
            bot.answer_callback_query(text='Список пуст', callback_query_id=call.id)


def set_greetings(chat_id, message_id='', edit=False, _all=False):
    if not _all:
        current_first_greeting = DB.get_greeting(user_id=chat_id, bot_name=client_status[chat_id]['bot_name'])
        current_second_greeting = DB.get_greeting(second=True, user_id=chat_id,
                                                  bot_name=client_status[chat_id]['bot_name'])
        msg = 'Настройка приветствий бота: @{}\n' \
              'Текущее первое приветствие: {}\n' \
              'Текущее второе приветствие: {}'.format(client_status[chat_id]['bot_name'],
                                                      current_first_greeting[0] if current_first_greeting is not None else 'None',
                                                      current_second_greeting[0] if current_second_greeting is not None else 'None')
    else:
        msg = 'Настройка приветствий всех ботов.'
    keyboard = telebot.types.InlineKeyboardMarkup()
    first = telebot.types.InlineKeyboardButton(text='Первое приветствие', callback_data='first')
    second = telebot.types.InlineKeyboardButton(text='Второе приветствие', callback_data='second')
    cancel = telebot.types.InlineKeyboardButton(text='Назад', callback_data='cancel')
    keyboard.add(first)
    keyboard.add(second)
    keyboard.add(cancel)
    if not edit:
        bot.send_message(chat_id=chat_id, text=msg, reply_markup=keyboard)
    else:
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=msg, reply_markup=keyboard)


def run_bots():
    print('Запуск пользовательских ботов.')
    counter = 0
    for i in DB.get_all_tokens():
        if check_token(i[0]):
            counter += 1
            print('Запуск бота под номером: {}.'.format(counter))
            name = get_bot_name(i[0])
            process = Process(target=func.main, args=(i[0], i[1]))
            if i[1] not in processes:
                processes[i[1]] = {name: process}
            else:
                processes[i[1]].update({name: process})
            try:
                process.start()
            except RuntimeError:
                print('Can\'t start new process')
        else:
            print('Token {} was deleted'.format(i[0]))
            DB.delete_items(token=i[0], user_id=i[1])


def main():
    run_bots()
    print('Основной бот запущен.')
    bot.polling(none_stop=True)


if __name__ == '__main__':
    DB = connector.DataBaseConnect()
    main()
