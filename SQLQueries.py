CREATE_NEW_USER = "CREATE TABLE user{}(bot_name text NOT NULL, " \
                  "greeting text NOT NULL, " \
                  "delay text NOT NULL, " \
                  "active text NOT NULL," \
                  "second_greeting text NOT NULL," \
                  "token text NOT NULL," \
                  "users text NOT NULL," \
                  "banned_users text NOT NULL," \
                  "user_id text NOT NULL," \
                  "ad bigint NOT NULL default 1," \
                  "second_greeting_active bigint NOT NULL default 0);"
CREATE_USERS_TABLE = "CREATE TABLE user{}users(user_id text NOT NULL," \
                     "user_name text NOT NULL);"
CREATE_COMMANDS_TABLE = "CREATE TABLE user{}commands(command_name text NOT NULL," \
                        "value text NOT NULL," \
                        "image text NOT NULL);"
CREATE_BANNED_USERS_TABLE = "CREATE TABLE banned{}(user_id text NOT NULL);"
INSERT_NEW_BOT = "INSERT INTO user{}(bot_name, " \
                 "greeting, " \
                 "second_greeting, " \
                 "delay, " \
                 "active," \
                 "token," \
                 "user_id," \
                 "banned_users," \
                 "users," \
                 "second_greeting_active) VALUES('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', {})"
SELECT_ALL_USER_BOTS = "SELECT bot_name FROM user{}"
GET_ALL_TABLES = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
SELECT_GREETING = "SELECT greeting FROM user{} WHERE bot_name = '{}'"
DELETE_COMMAND = "DELETE FROM user{}commands WHERE command_name = '{}';"
ADD_COMMAND = "INSERT INTO user{}commands(command_name, value, image) VALUES('{}', '{}', '{}')"
UPDATE_COMMAND = "UPDATE user{}commands SET value = '{}' WHERE command_name = '{}';"
GET_COMMAND = "SELECT command_name FROM user{}commands"
GET_COMMAND_VALUE = "SELECT value FROM user{}commands WHERE command_name = '{}'"
DELETE_BOT = "DELETE FROM user{} WHERE bot_name = '{}';"
SELECT_DELAY = "SELECT delay FROM user{} WHERE bot_name = '{}'"
RESET_GREETING = "UPDATE user{} SET active = '{}' WHERE bot_name = '{}';"
GET_GREETING_STATUS = "SELECT active FROM user{} WHERE bot_name = '{}';"
SET_GREETING_STATUS_FOR_ALL = "UPDATE user{} SET active = '{}';"
SET_GREETING_DELAY = "UPDATE user{} SET delay = '{}' WHERE bot_name = '{}';"
SET_GREETING_DELAY_FOR_ALL = "UPDATE user{} SET active = '{}';"
RESET_GREETING_MESSAGE = "UPDATE user{} SET greeting = '{}' WHERE bot_name = '{}';"
RESET_GREETING_MESSAGE_FOR_ALL = "UPDATE user{} SET greeting = '{}';"
SELECT_ALL_TOKENS = "SELECT token, user_id FROM {}"
DELETE_INVALID_TOKEN = "DELETE FROM user{} WHERE token = '{}'"
SET_SECOND_GREETING = "UPDATE user{} SET second_greeting = '{}' WHERE bot_name = '{}';"
SET_SECOND_GREETING_FOR_ALL = "UPDATE user{} SET second_greeting = '{}';"
SELECT_SECOND_GREETING = "SELECT second_greeting FROM user{} WHERE bot_name = '{}'"
ADD_USER = "UPDATE user{} SET users = '{}' WHERE bot_name = '{}';"
GET_ALL_USERS = "SELECT users FROM user{} WHERE bot_name = '{}';"
GET_USERS_DUMP = "SELECT user_id FROM user{}users"
INSERT_USER_INTO_DUMP = "INSERT INTO user{}users(user_id, user_name) VALUES('{}', '{}')"
SELECT_ONE_TIME_TOKEN = "SELECT token FROM user{} WHERE bot_name = '{}';"
DELETE_ALL_BOTS = "DELETE FROM user{}"
SELECT_INFO_FOR_ALL_DISPATCH = "SELECT token, users FROM user{}"
GET_BANNED_USERS_FOR_ONE_BOT = "SELECT banned_users FROM user{} WHERE bot_name = '{}';"
ADD_NEW_BANNED_USER = "UPDATE user{} SET banned_users = '{}' WHERE bot_name = '{}';"
SELECT_AD_STATUS = "SELECT ad FROM user{} WHERE bot_name = '{}'"
SELECT_AD_STATUS_FOR_ALL = "SELECT ad FROM user{}"
SET_AD = "UPDATE user{} SET ad = {} WHERE bot_name = '{}'"
SET_AD_FOR_ALL = "UPDATE user{} SET ad = {}"
GET_SECOND_GREETING_STATUS = "SELECT second_greeting_active FROM user{} WHERE bot_name = '{}'"
GET_ALL_SECOND_GREETING_STATUS = "SELECT second_greeting_active FROM user{}"
UPDATE_SECOND_GREETING_ACTIVE = "UPDATE user{} SET second_greeting_active = {} WHERE bot_name = '{}'"
UPDATE_SECOND_GREETING_ACTIVE_ALL = "UPDATE user{} SET second_greeting_active = {}"
CREATE_BUTTONS_TABLE = "CREATE TABLE user{}buttons(name text NOT NULL," \
                       "bot text NOT NULL," \
                       "value text NOT NULL," \
                       "active text NOT NULL);"
ADD_BUTTON = "INSERT INTO user{}buttons(name, bot, value, active) VALUES('{}', '{}', '{}', '1')"
GET_BUTTONS = "SELECT name FROM user{}buttons WHERE bot = '{}'"
GET_BUTTON_VAL = "SELECT value FROM user{}buttons WHERE name = '{}' and bot = '{}'"
