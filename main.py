import telebot
import pickle

DBD = './'
Matches = []
HelloText = 'Привет! Это бот для игры в шахматы с друзьями. Ты только что зарегистрировался'
HelpText = 'Чтобы играть с другом напиши его никнейм. Если он запускал этот бот я отправлю ему запрос'
TryingConnectText = 'Отправляю запрос на подключение...'

def load_users():
    try:
        with open(DBD + 'Users.pickle', 'rb') as file:
            users = pickle.load(file)
    except FileNotFoundError:
        users = {}
        with open(DBD + 'Users.pickle', 'wb') as file:
            pickle.dump(users, file)
    return users


def start_game(u1, u2, i1, i2):
    print('starting game with', u1, u2)


token = '5866341366:AAF7gOQ30992B2zgP38ZYk1Vod-EM3i0XTA'
bot = telebot.TeleBot(token)


@bot.message_handler(commands=['start'])
def start(message):
    """ При подключении нового аккаунта добавляем его в users и приветствуем
    """
    global users
    username = message.from_user.username.lower()
    userid = message.chat.id
    print(f'New user: {username} id: {userid}')
    if username not in users:
        bot.send_message(userid, HelloText)
        bot.send_message(userid, HelpText)
        users[username] = message.chat.id
        with open(DBD + 'Users.pickle', 'wb') as file:
            pickle.dump(users, file)


@bot.message_handler(commands=['help'])
def help_handler(message):
    bot.send_message(message.chat.id, HelpText)


@bot.message_handler(func=lambda message: message.text[0] == '@')
def create_game(message):
    global users, Matches
    username1 = message.from_user.username.lower()
    id1 = message.chat.id
    username2 = message.text[1:].lower()
    if (username2, username1) in Matches:
        id2 = users[username2]
        Matches.remove((username2, username1))
        start_game(username1, username2, id1, id2)
        return
    if username2 in users.keys():
        bot.send_message(id1, TryingConnectText)
        id2 = users[username2]
        bot.send_message(id2, f'К тебе пытается подключиться @{username1}\nОтправь его никнейм для старта игры с ним')
        Matches.append((username1, username2))


users = load_users()
print(users)
bot.infinity_polling()
