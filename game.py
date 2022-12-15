import pygame
import random
pygame.font.init()
font = pygame.font.SysFont('Europe Book', 20)

BCC = (50, 50, 50)  # Black cell color
WCC = (180, 180, 180)  # White cell color

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
        for i in range(8):
            wpawn = Pawn(Alph[i], '2', True)
            bpawn = Pawn(Alph[i], '7', False)
            self.figures += [wpawn, bpawn]
        # Создаём ладьи, коней и слонов
        for i, f in enumerate([Rook, Knight, Bishop]):
            f1 = f(Alph[i], '8', False)
            f2 = f(Alph[7-i], '8', False)
            f3 = f(Alph[i], '1', True)
            f4 = f(Alph[7-i], '1', True)
            self.figures += [f1, f2, f3, f4]
        # Создаём королей и королев
        K1 = King('e', '1', True)
        K2 = King('e', '8', False)
        Q1 = Queen('d', '1', True)
        Q2 = Queen('d', '8', False)
        self.figures += (K1, K2, Q1, Q2)


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


    def to_image(self, path=f'temp/{random.randint(1, 10**10)}.png'):
        """ Создаёт с помощью pygame изображение игрового поля и сохраняет в path, возвращает path
        """
        size = (520, 520)
        image = pygame.Surface(size)
        # Рисуем фон
        image.fill(BCC)
        for i in range(8):
            for j in range(8):
                if (i+j) % 2 == 0:
                    x = i*60 + 20
                    y = j*60 + 20
                    pygame.draw.rect(image, WCC, (x, y, 60, 60))
        # Пишем буквы и цифры
        for i in range(8):
            char = font.render(Alph[i], True, WCC)
            x = i*60 + 50 - char.get_width()//2
            uy = 10 - char.get_height()//2
            by = 510 - char.get_height()//2
            image.blit(char, (x, uy))
            image.blit(char, (x, by))
            num = font.render(Nums[7-i], True, WCC)
            lx = 10 - char.get_width()//2
            rx = 510 - char.get_width()//2
            y = i*60 + 50 - char.get_height()//2
            image.blit(num, (lx, y))
            image.blit(num, (rx, y))
        # Добавляем фигуры
        for fig in self.figures:
            i = Alph.index(fig.ch)
            j = 7-Nums.index(fig.num)
            x = i*60 + 20
            y = j*60 + 20
            image.blit(fig.sprite, (x, y))
        # Сохраняем картинку
        pygame.image.save(image, path)
        return path


class Figure:
    def __init__(self, ch, num, white):
        self.ch = ch
        self.num = num
        self.white = white
        if self.white:
            self.sprite = pygame.image.load(self.wimage)
        else:
            self.sprite = pygame.image.load(self.bimage)

    def check_move(self, *args):
        return True


class Pawn(Figure):
    wimage = 'images/white pawn.png'
    bimage = 'images/black pawn.png'


class Bishop(Figure):
    wimage = 'images/white bishop.png'
    bimage = 'images/black bishop.png'


class King(Figure):
    wimage = 'images/white king.png'
    bimage = 'images/black king.png'


class Knight(Figure):
    wimage = 'images/white knight.png'
    bimage = 'images/black knight.png'


class Queen(Figure):
    wimage = 'images/white queen.png'
    bimage = 'images/black queen.png'


class Rook(Figure):
    wimage = 'images/white rook.png'
    bimage = 'images/black rook.png'
