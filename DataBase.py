import os
from urllib import parse
import psycopg2
import SQLQueries


class DataBaseConnect:
    # стандартное приветствие
    greeting = 'Привет!\nНапишите мне Ваш вопрос и я отвечу в ближайшее время'
    second_greeting = 'Приветствие неуказано'

    def __init__(self):
        self.parse_object = parse.uses_netloc.append("postgres")
        self.url = parse.urlparse(os.environ["DATABASE_URL"])
        self.connection = psycopg2.connect(
                            database=self.url.path[1:],
                            user=self.url.username,
                            password=self.url.password,
                            host=self.url.hostname,
                            port=self.url.port
                            )
        self.connection.autocommit = True
        self.cursor = self.connection.cursor()

    def update_command(self, user_id, command, value):
        # изменить значение команды
        self.cursor.execute(SQLQueries.UPDATE_COMMAND.format(user_id, value, command))

    def add_command(self, user_id, command, msg, image='Empty'):
        # добавить команду
        if 'user{}commands' not in self.get_all_tables():
            self.create_commands_table(user_id=user_id)
        self.cursor.execute(SQLQueries.ADD_COMMAND.format(user_id, command, msg, image))

    def get_commands(self, user_id, _all=False, command=''):
        # получить все команды, или значение конкретной команды
        self.create_commands_table(user_id=user_id)
        if _all:
            try:
                self.cursor.execute(SQLQueries.GET_COMMAND.format(user_id))
            except:
                return False
        else:
            self.cursor.execute(SQLQueries.GET_COMMAND_VALUE.format(user_id, command))
        return self.cursor.fetchall()

    def delete_command(self, user_id, command):
        # удалить команду
        self.cursor.execute(SQLQueries.DELETE_COMMAND.format(user_id, command))

    def create_commands_table(self, user_id):
        # создать таблицу с командами для юзера
        all_tables = self.get_all_tables()
        if all_tables and 'user{}commands'.format(user_id) not in all_tables:
            self.cursor.execute(SQLQueries.CREATE_COMMANDS_TABLE.format(user_id))

    def delete_bot(self, user_id, bot_name):
        # удалить бота
        self.cursor.execute(SQLQueries.DELETE_BOT.format(user_id, bot_name))

    def delete_all_bots(self, user_id):
        self.cursor.execute(SQLQueries.DELETE_ALL_BOTS.format(user_id))

    def get_delay(self, user_id, bot_name):
        # получить задержку
        self.cursor.execute(SQLQueries.SELECT_DELAY.format(user_id, bot_name))
        return self.cursor.fetchall()[0]

    def off_greeting(self, user_id, value=False, bot_name=None, for_all=False, get_status=False):
        # включить/отключить приветствие, при get_status == True, вернуть статус приветствия
        if not for_all and not get_status:
            self.cursor.execute(SQLQueries.RESET_GREETING.format(user_id, value, bot_name))
        elif get_status:
            self.cursor.execute(SQLQueries.GET_GREETING_STATUS.format(user_id, bot_name))
            status = self.cursor.fetchall()
            return status[0][0]
        elif for_all:
            self.cursor.execute(SQLQueries.SET_GREETING_STATUS_FOR_ALL.format(user_id, value))

    def set_greeting_delay(self, user_id, value, bot_name=None, for_all=False):
        # установить задержку
        if not for_all:
            self.cursor.execute(SQLQueries.SET_GREETING_DELAY.format(user_id, value, bot_name))
        else:
            self.cursor.execute(SQLQueries.SET_GREETING_DELAY_FOR_ALL.format(user_id, value))

    def reset_greeting(self, user_id, new_greeting, bot_name=False, second=False):
        # изменить приветствие всем/конкретному боту
        if bot_name:
            if not second:
                self.cursor.execute(SQLQueries.RESET_GREETING_MESSAGE.format(user_id, new_greeting, bot_name))
            else:
                self.cursor.execute(SQLQueries.SET_SECOND_GREETING.format(user_id, new_greeting, bot_name))
        else:
            if not second:
                self.cursor.execute(SQLQueries.RESET_GREETING_MESSAGE_FOR_ALL.format(user_id, new_greeting))
            else:
                self.cursor.execute(SQLQueries.SET_SECOND_GREETING_FOR_ALL.format(user_id, new_greeting))

    def get_greeting(self, bot_name, user_id, second=False):
        # получить приветствие
        if not second:
            self.cursor.execute(SQLQueries.SELECT_GREETING.format(user_id, bot_name))
        else:
            self.cursor.execute(SQLQueries.SELECT_SECOND_GREETING.format(user_id, bot_name))
        try:
            return self.cursor.fetchall()[0]
        except:
            pass

    def get_all_tables(self):
        # получить все таблицы
        self.cursor.execute(SQLQueries.GET_ALL_TABLES)
        try:
            result = [x[0] for x in self.cursor.fetchall()]
        except:
            result = False
        return result

    def create_new_user(self, user_id):
        # создать юзера
        self.cursor.execute(SQLQueries.CREATE_NEW_USER.format(user_id))

    def get_bots(self, user_id):
        # получить всех ботов юзера
        try:
            self.cursor.execute(SQLQueries.SELECT_ALL_USER_BOTS.format(user_id))
            result = self.cursor.fetchall()
            return [x for x in result]
        except:
            return False

    def insert_new_bot(self, user, bot_name, token):
        # добавить бота
        if 'user{}'.format(user) not in self.get_all_tables():
            self.create_new_user(user_id=user)
        self.cursor.execute(SQLQueries.INSERT_NEW_BOT.format(user, bot_name, DataBaseConnect.greeting,
                                                             DataBaseConnect.second_greeting, '0',
                                                             '1', token, user, '0', '0', 0))

    def get_all_tokens(self, extend=False):
        # получить токены
        tokens = []
        for table in self.get_all_tables():
            try:
                self.cursor.execute(SQLQueries.SELECT_ALL_TOKENS.format(table))
                for token in self.cursor.fetchall():
                    tokens.append(token)
            except:
                continue
        return tokens if not extend else [x[0] for x in tokens]

    def delete_items(self, token, user_id):
        # удалить невалидный токен
        self.cursor.execute(SQLQueries.DELETE_INVALID_TOKEN.format(user_id, token))

    def get_all_users(self, user_id=None, bot=None, extend=False):
        if not extend:
            self.cursor.execute(SQLQueries.GET_ALL_USERS.format(str(user_id), bot))
        else:
            self.cursor.execute(SQLQueries.GET_USERS_DUMP.format(str(user_id)))
        users = self.cursor.fetchall()
        return users

    def add_user(self, user_id, user, _bot):
        if 'user{}users'.format(user_id) not in self.get_all_tables():
            self.cursor.execute(SQLQueries.CREATE_USERS_TABLE.format(user_id))
        name = user.from_user.first_name
        identifer = str(user.from_user.id)
        users = self.get_all_users(bot=_bot, user_id=user_id)
        if users is not None:
            all_users = ' '.join([x[0] for x in users])
        else:
            all_users = ''
        if identifer not in all_users:
            all_users += f'{identifer} '
            self.cursor.execute(SQLQueries.ADD_USER.format(user_id, all_users, _bot))
        users = self.get_all_users(user_id=user_id, extend=True)
        if users is not None:
            all_users = ' '.join([x[0] for x in users])
        else:
            all_users = ''
        if identifer not in all_users:
            self.cursor.execute(SQLQueries.INSERT_USER_INTO_DUMP.format(user_id, identifer, name))

    def get_one_time_token(self, user_id, bot_name):
        self.cursor.execute(SQLQueries.SELECT_ONE_TIME_TOKEN.format(user_id, bot_name))
        return self.cursor.fetchall()

    def select_info_for_all_dispatch(self, user_id):
        finally_result = {}
        self.cursor.execute(SQLQueries.SELECT_INFO_FOR_ALL_DISPATCH.format(user_id))
        result = self.cursor.fetchall()
        for i in result:
            finally_result.update({i[0]: i[1].split()})
        return finally_result

    def get_banned_users(self, user_id, bot_name=None, for_all=False):
        if not for_all:
            self.cursor.execute(SQLQueries.GET_BANNED_USERS_FOR_ONE_BOT.format(user_id, bot_name))
        result = self.cursor.fetchall()
        if result is not None:
            return ' '.join([x[0] for x in result])
        return ''

    def ban_user(self, bot_name, user_id, banned_user, for_all=False):
        if not for_all:
            users = self.get_banned_users(user_id=user_id, bot_name=bot_name)
            if banned_user not in users:
                users += f'{banned_user} '
                self.cursor.execute(SQLQueries.ADD_NEW_BANNED_USER.format(user_id, users, bot_name))

    def clear_ban_user(self, banned_user, user_id, bot_name):
        banned_users = self.get_banned_users(user_id=user_id, bot_name=bot_name).split()
        banned_users.remove(banned_user)
        users = ' '.join(banned_users) + ' '
        self.cursor.execute(SQLQueries.ADD_NEW_BANNED_USER.format(user_id, users, bot_name))

    def manage_ad(self, user_id, bot_name='', ad_status='', get=False, for_all=False):
        if get:
            if not for_all:
                self.cursor.execute(SQLQueries.SELECT_AD_STATUS.format(user_id, bot_name))
            else:
                self.cursor.execute(SQLQueries.SELECT_AD_STATUS_FOR_ALL.format(user_id))
            return self.cursor.fetchall()
        else:
            if not for_all:
                self.cursor.execute(SQLQueries.SET_AD.format(user_id, ad_status, bot_name))
            else:
                self.cursor.execute(SQLQueries.SET_AD_FOR_ALL.format(user_id, ad_status))

    def get_second_greeting_status(self, user_id, bot_name='', for_all=False):
        if not for_all:
            self.cursor.execute(SQLQueries.GET_SECOND_GREETING_STATUS.format(user_id, bot_name))
        else:
            self.cursor.execute(SQLQueries.GET_ALL_SECOND_GREETING_STATUS.format(user_id))
        return self.cursor.fetchall()

    def activate_second_greeting(self, user_id, bot_name='', for_all=False, value=''):
        if not for_all:
            status = self.get_second_greeting_status(user_id=user_id, bot_name=bot_name)[0][0]
            _value = 1 if not status else 0
            self.cursor.execute(SQLQueries.UPDATE_SECOND_GREETING_ACTIVE.format(user_id, _value, bot_name))
        else:
            self.cursor.execute(SQLQueries.UPDATE_SECOND_GREETING_ACTIVE_ALL.format(user_id, value))

    def add_button(self, user, bot_name, name, value):
        if 'user{}buttons'.format(user) not in self.get_all_tables():
            self.cursor.execute(SQLQueries.CREATE_BUTTONS_TABLE.format(user))
        self.cursor.execute(SQLQueries.ADD_BUTTON.format(user, name, bot_name, value))

    def get_buttons(self, bot_name, user):
        self.cursor.execute(SQLQueries.GET_BUTTONS.format(user, bot_name))
        result = [x[0] for x in self.cursor.fetchall()]
        self.cursor.execute(SQLQueries.GET_BUTTONS.format(user, 'all'))
        all_buttons = self.cursor.fetchall()
        if all_buttons:
            result.extend([x[0] for x in all_buttons])
        return result

    def get_button_value(self, button, bot, user):
        self.cursor.execute(SQLQueries.GET_BUTTON_VAL.format(user, button, bot))
        return self.cursor.fetchall()