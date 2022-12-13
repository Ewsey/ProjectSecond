Alph = 'abcdefgh'
Nums = '12345678'

class Game:
    winner = 1
    def __init__(self, u1, u2, i1, i2):
        self.u1 = u1
        self.u2 = u2
        self.i1 = i1
        self.i2 = i2
        self.move = 1
        self.figures = []
        # Создаём пешки
        for i in range(2):
            wpawn = Pawn(Alph[i], '2', True)
            bpawn = Pawn(Alph[i], '7', False)
            self.figures += [wpawn, bpawn]

    def process_move(self, move, u):
        """ Обрабатывыает ход сделанный игроком.
            Если ход отправил игрок который должен ожидать ход соперника возвращает 2
            Если такой ход возможен то возвращает 1, иначе 0
        """
        if self.u1 != self.u2:
            if u == self.u1 and self.move%2 == 1:
                return 2
            if u == self.u2 and self.move%2 == 2:
                return 2

        ch1, num1, ch2, num2 = move
        figure = False
        for fig in self.figures:
            if fig.ch == ch1 and fig.num == num1 and fig.white == self.move%2:
                figure = fig
        if not figure:
            return 0
        if not figure.check_move(ch2, num2):
            return 0

        # Проверяем съедение другуой фигуры
        for fig in self.figures:
            if fig.ch == ch2 and fig.num == num2:
                self.figures.remove(fig)
        # Двигаем фигуру
        figure.ch = ch2
        figure.num = num2
        self.move += 1

        # Проверяем закончена ли игра
        is_end = self.is_game_end()
        if is_end:
            self.winner = self.move%2
            return 3


        return 1


    def is_game_end(self):
        wexist = False
        bexist = False
        for fig in self.figures:
            if fig.white:
                wexist = True
            else:
                bexist = True
        if wexist and bexist:
            return False
        return True


    def to_text_message(self):
        text = [['□']*8 for _ in range(8)]
        for fig in self.figures:
            m = 7-Nums.index(fig.num)
            n = Alph.index(fig.ch)
            text[m][n] = fig.wletter if fig.white else fig.bletter
        for i in range(8):
            for j in range(8):
                text[i][j] = f'{text[i][j]: ^11}'
            text[i] = ''.join(text[i])
        text = '\n\n'.join(text)
        return text



class Figure:
    def __init__(self, ch, num, white):
        self.ch = ch
        self.num = num
        self.white = white


class Pawn(Figure):
    wletter = '♙'
    bletter = '♟'
    def __init__(self, ch, num, white):
        super().__init__(ch, num, white)

    def check_move(self, *args):
        return True
