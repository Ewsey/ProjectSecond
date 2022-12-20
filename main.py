import os
import pickle
import random
import telebot
from telebot.types import InputFile
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
Для окончания партии матом нужно атаковать короля оппонента
Для досрочного окончания партии напиши /end
Если Вам не пришло сообщение после отправки хода получите игровое поле с помощью /field
Во время партии Вы можете отправить сообщение оппоненту с помощью команды /chat ...'''
TryingConnectText = 'Отправляю запрос на подключение...'
UserNotInBaseText = 'К сожалению такого пользователя нет в базе'
NotValidMove = 'Такой ход невозможен: '
WaitOpponentsMove = 'Ждем ход соперника'
NotYourMove = 'Сейчас ходите не Вы, дождитесь хода соперника'
GameInstruction2 = '''Игра началась
Вы играете за белых
Чтобы ходить напишите свой ход в формате e2e4'''
GameInstruction1 = '''Игра началась
Вы играете за черных, подождите ход соперника
Чтобы ходить напишите свой ход в формате e2e4'''
YouAlreadyPlaying = 'Нельзя начать новую игру до завершения старой'
UserAlreadyPlaying = 'Пользователь уже начал игру с другим человеком'
YouLose = 'Вы проиграли...'
YouWin = 'Вы победили!'
GameIsOver = [YouWin, YouLose]
WinCheckmate = '(вы поставили мат)'
LoseCheckmate = '(вам поставили мат)'
Checkmate = [WinCheckmate, LoseCheckmate]
NowYourMove = 'Соперник сделал ход: '
YourKingInDanger = ' и поставил Вам шах'
YouNotInGame = 'Вас нет в списке активных игр'
YouTakeAMessage = 'Вы получили сообщение от оппонента:'
PlayerGiveUp = ' (один из игроков сдался)'

def load_users():
    """ Загружаем список пользователей уже запускавших бот
    """
    try:
        with open(DBD + 'Users.pickle', 'rb') as file:
            users = pickle.load(file)
    except FileNotFoundError:
        users = {}
        with open(DBD + 'Users.pickle', 'wb') as file:
            pickle.dump(users, file)
    return users


def start_game(u1, u2, i1, i2):
    """ Создаём игру, добавляем её в Games, шлем сообщения о старте игры
    """
    print('starting game with', u1, 'and', u2)
    # Связываем игроков с конкретной игрой
    game = Game(u1, u2, i1, i2)
    Games[u1] = game
    Games[u2] = game
    bot.send_message(i1, GameInstruction1)
    bot.send_message(i2, GameInstruction2)
    send_field(game, i1, i2)


def end_game(game, user=False):
    """ Заканчиваем игру
        Если кто-то сдался с помощью /end он проигрывает
        Игра удаляется из Games, игрокам шлются сообщения об окончании игры
    """
    if user: # Проигрывает сдавшийся
        if user == game.u1:
            win1 = False
            win2 = True
        else:
            win1 = True
            win2 = False
    else:
        win1 = 0 == game.winner
        win2 = 1 == game.winner
    if game.move % 2 == 1:  # Опытным путём
        send_field(game, game.i1, game.i2)
    else:
        send_field(game, game.i2, game.i1)
    bot.send_message(game.i1, GameIsOver[win1] + (PlayerGiveUp if user else Checkmate[win1]))
    bot.send_message(game.i2, GameIsOver[win2] + (PlayerGiveUp if user else Checkmate[win2]))
    Games.pop(game.u1)
    if game.u1 != game.u2:
        Games.pop(game.u2)


def send_field(game, id1=False, id2=False):
    """ Отправляет текущее игровое поле game игрокам, чьи id указаны
        При этом у белого игрока снизу белые фигуры, у чёрного черные
    """
    if not os.path.isdir('temp'):
        os.mkdir('temp')
    b_move = game.move % 2 == 0  # Опытным путём
    wpath = game.to_image(True, f'temp/{random.randint(1, 10**10)}.png')
    bpath = game.to_image(False, f'temp/{random.randint(1, 10**10)}.png')
    image1 = InputFile(wpath)
    image2 = InputFile(bpath)
    if id1:
        bot.send_photo(id1, image1 if b_move else image2)
    if id2:
        bot.send_photo(id2, image2 if b_move else image1)


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
    """ Отправляем инструкцию к игре по комманде /help
    """
    bot.send_message(message.chat.id, HelpText)


@bot.message_handler(commands=['end'])
def end_game_handler(message):
    """ Случай когда один из игрок сдался и закончил игру с помощью /end
    """
    user = message.from_user.username.lower()
    id = message.chat.id
    if user not in Games:
        bot.send_message(id, YouNotInGame)
        return
    game = Games[user]
    end_game(game, user)


@bot.message_handler(commands=['field'])
def field_sender(message):
    """ В случае когда после хода не отобразилось поле пользователь может написать /field и бот пошлёт текущее поле
    """
    user = message.from_user.username.lower()
    id = message.chat.id
    if user not in Games:
        bot.send_message(id, YouNotInGame)
        return
    game = Games[user]
    if id == game.i1 and game.move % 2 == 1 or id == game.i2 and game.move % 2 == 0:
        send_field(game, id)
    else:
        send_field(game, False, id)


@bot.message_handler(commands=['chat'])
def chat_with_opponent(message):
    user = message.from_user.username.lower()
    id = message.chat.id
    if user not in Games:
        bot.send_message(id, YouNotInGame)
        return
    game = Games[user]
    text = message.text[5:]
    opponentid = game.i1 if id == game.i2 else game.i2
    bot.send_message(opponentid, YouTakeAMessage)
    bot.send_message(opponentid, text)



@bot.message_handler(func=lambda message: message.text[0] == '@')
def create_game(message):
    """ Пользователь отправляет тег другого пользоваетеля
        Если этот тег есть в базе по ему отправляется запрос на начало игры
        Если этот тег есть в списке пользователей уже запросивших у отправителя игру то запускается игра
        Если этого не нашлось об этом сообщается отправителю
        Если игрок уже играет об этом сообщается отправителю
    """
    global users, Matches
    username1 = message.from_user.username.lower()
    id1 = message.chat.id
    username2 = message.text[1:].lower()

    # Один из пользователей уже играет
    if username2 in Games:
        bot.send_message(message.chat.id, UserAlreadyPlaying)
        return
    if username1 in Games:
        bot.send_message(message.chat.id, YouAlreadyPlaying)
        return

    # Случай ответа на запрос и старта игры
    if (username2, username1) in Matches:
        id2 = users[username2]
        Matches.remove((username2, username1))
        start_game(username2, username1, id1, id2)
        return
    # Запрос игры
    if username2 in users.keys():
        bot.send_message(id1, TryingConnectText)
        id2 = users[username2]
        bot.send_message(id2, f'К Вам пытается подключиться @{username1}\nОтправьте его никнейм для старта игры с ним')
        Matches.append((username1, username2))
    else:
        bot.send_message(id1, UserNotInBaseText) # Искомый пользователь не запускал бот


def is_move(message):
    """ Проверяем соответствует ли message шахматному ходу. Примеры ходов: e2e4 E2e4 G7G8 a1a1
    """
    text = message.text.lower()
    if len(text) != 4:
        return
    if text[0] in Alph and text[2] in Alph and text[1] in Nums and text[3] in Nums and text[:2] != text[2:]:
        return True


@bot.message_handler(func=is_move)
def handle_move(message):
    username = message.from_user.username.lower()
    game = Games[username]
    move = message.text.lower()
    valid_move = game.process_move(move, username)
    if not valid_move:
        # нельзя так ходить
        comment = game.comment_to_move(move)
        bot.send_message(message.chat.id, NotValidMove + comment)
    elif valid_move == 2:
        # нужно подождать ход соперника
        bot.send_message(message.chat.id, NotYourMove)
    elif valid_move == 3:
        # конец игры
        end_game(game)
    elif valid_move == 4:
        # неверная рокировка
        comment = game.comment_to_move(move)
        bot.send_message(message.chat.id, NotValidMove + comment)
    else:
        # корректный ход
        opponentid = game.i2 if game.move%2 else game.i1  # Опытным путём
        opponentking = game.w_king if game.move%2 else game.b_king
        send_field(game, message.chat.id, opponentid)
        bot.send_message(message.chat.id, WaitOpponentsMove)
        if opponentking.is_shah():
            bot.send_message(opponentid, NowYourMove + move + YourKingInDanger)
        else:
            bot.send_message(opponentid, NowYourMove + move)


users = load_users()
print(users)
bot.infinity_polling(timeout=2000, long_polling_timeout=2000)
