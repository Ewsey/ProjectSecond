import os
import telebot
from telebot.types import InputFile
import pickle
from game import Game, Alph, Nums

# init bot
token = '5866341366:AAF7gOQ30992B2zgP38ZYk1Vod-EM3i0XTA'
bot = telebot.TeleBot(token)

DBD = './'
Matches = []
Games = {}
HelloText = 'Привет! Это бот для игры в шахматы с друзьями. Ты только что зарегистрировался'
HelpText = '''Чтобы играть с другом напиши его никнейм.
Если он запускал этот бот я отправлю ему запрос
Если ты уже играешь партию то нужно отправить свой ход в формате е2е4
Для досрочного окончания партии напиши /end'''
TryingConnectText = 'Отправляю запрос на подключение...'
UserNotInBaseText = 'К сожалению такого пользователя нет в базе'
NotValidMove = 'Такой ход невозможен'
WaitOpponentsMove = 'Нужно подождать ход соперника'
NotYourMove = 'Сейчас ходите не Вы, дождитесь хода соперника'
GameInstruction = '''Игра началась
Чтобы ходить напиши свой ход в формате e2e4'''
YouAlreadyPlaying = 'Нельзя начать новую игру до завершения старой'
UserAlreadyPlaying = 'Пользователь уже начал игру с другим человеком'
GameIsOver = ['Вы победили!', 'Вы проиграли...']
NowYourMove = 'Соперник сделал ход'
YouNotInGame = 'Невозможно закончить игру: Вас нет в списке активных игр'

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
    print('starting game with', u1, 'and', u2)
    # Связываем игроков с конкретной игрой
    game = Game(u1, u2, i1, i2)
    Games[u1] = game
    Games[u2] = game
    bot.send_message(i1, GameInstruction)
    bot.send_message(i2, GameInstruction)
    send_field(i1, game)
    send_field(i2, game)


def end_game(game, user=False):
    if user: # Проигрывает сдавшийся
        if user == game.u1:
            win1 = True
            win2 = False
        else:
            win1 = False
            win2 = True
    else:
        win1 = 1 == game.winner
        win2 = 0 == game.winner
    send_field(game.i1, game)
    bot.send_message(game.i1, GameIsOver[win1])
    send_field(game.i2, game)
    bot.send_message(game.i2, GameIsOver[win2])
    Games.pop(game.u1)
    if game.u1 != game.u2:
        Games.pop(game.u2)


def send_field(id, game):
    if not os.path.isdir('temp'):
        os.mkdir('temp')
    path = game.to_image()
    image = InputFile(path)
    bot.send_photo(id, image)



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


@bot.message_handler(commands=['end'])
def end_game_handler(message):
    user = message.from_user.username.lower()
    id = message.chat.id
    if user not in Games:
        bot.send_message(id, YouNotInGame)
        return
    game = Games[user]
    end_game(game, user)



@bot.message_handler(func=lambda message: message.text[0] == '@')
def create_game(message):
    global users, Matches
    username1 = message.from_user.username.lower()
    id1 = message.chat.id
    username2 = message.text[1:].lower()

    if username2 in Games:
        bot.send_message(message.chat.id, UserAlreadyPlaying)
        return
    if username1 in Games:
        bot.send_message(message.chat.id, YouAlreadyPlaying)
        return

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
    else:
        bot.send_message(id1, UserNotInBaseText)


def is_move(message):
    text = message.text.lower()
    if len(text) != 4:
        return
    if text[0] in Alph and text[2] in Alph and text[1] in Nums and text[3] in Nums:
        return True


@bot.message_handler(func=is_move)
def handle_move(message):
    username = message.from_user.username.lower()
    game = Games[username]
    move = message.text
    valid_move = game.process_move(move, username)
    if not valid_move:
        # нельзя так ходить
        bot.send_message(message.chat.id, NotValidMove)
    elif valid_move == 2:
        # нужно подождать ход соперника
        bot.send_message(message.chat.id, NotYourMove)
    elif valid_move == 3:
        # конец игры
        end_game(game)
    else:
        # корректный ход
        bot.send_message(message.chat.id, WaitOpponentsMove)
        send_field(message.chat.id, game)
        opponentid = game.i2 if game.move%2 else game.i1
        bot.send_message(opponentid, NowYourMove)
        send_field(opponentid, game)


users = load_users()
print(users)
bot.infinity_polling()
