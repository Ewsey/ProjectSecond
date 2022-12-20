import pygame
pygame.font.init()
font = pygame.font.SysFont('Europe Book', 20)

BCC = (60, 60, 60)  # Black cell color
WCC = (190, 190, 190)  # White cell color

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
            wpawn = Pawn(self, Alph[i], '2', True)
            bpawn = Pawn(self, Alph[i], '7', False)
            self.figures += [wpawn, bpawn]
        # Создаём ладьи, коней и слонов
        for i, f in enumerate([Rook, Knight, Bishop]):
            f1 = f(self, Alph[i], '8', False)
            f2 = f(self, Alph[7-i], '8', False)
            f3 = f(self, Alph[i], '1', True)
            f4 = f(self, Alph[7-i], '1', True)
            self.figures += [f1, f2, f3, f4]
        # Создаём королей и королев
        K1 = King(self, 'e', '1', True)
        K2 = King(self, 'e', '8', False)
        Q1 = Queen(self, 'd', '1', True)
        Q2 = Queen(self, 'd', '8', False)
        self.figures += (K1, K2, Q1, Q2)
        self.w_king = K1
        self.b_king = K2

    def process_move(self, move, u):
        """ Обрабатывыает ход сделанный игроком.
            Если ход отправил игрок который должен ожидать ход соперника возвращает 2
            Если такой ход возможен то возвращает 1, иначе 0
        """
        self.field_of_figures()
        # Этот ли игрок должен ходить?
        if self.u1 != self.u2:
            if u == self.u1 and self.move%2 == 0:
                return 2
            if u == self.u2 and self.move%2 == 1:
                return 2

        # Не рокировка ли это? (обрабатываем отдельно)
        castling = self.process_castling(move)
        if type(castling) == str:
            return 4
        if castling is True:
            return 1

        ch1, num1, ch2, num2 = move
        # Есть ли на выбранной клетке фигура?
        figure = False
        for fig in self.figures:
            if fig.ch == ch1 and fig.num == num1 and fig.white == self.move%2:
                figure = fig
        if not figure:
            return 0
        # Может ли фигура так ходить?
        if figure.check_move(ch2, num2) != True:
            return 0

        # Проверяем съедение другой фигуры
        for fig in self.figures:
            if fig.ch == ch2 and fig.num == num2:
                # Случай когда был атакован король и игра заканчивается
                if type(fig) == King:
                    self.winner = not bool(self.move % 2)
                    return 3
                self.figures.remove(fig)
        # Двигаем фигуру
        figure.ch = ch2
        figure.num = num2
        self.move += 1

        return 1

    def comment_to_move(self, move):
        comment = self.process_castling(move)
        if comment:
            return comment
        ch1, num1, ch2, num2 = move
        figure = False
        for fig in self.figures:
            if fig.ch == ch1 and fig.num == num1 and fig.white == self.move % 2:
                figure = fig
        if not figure:
            return 'на выбранной клетке нет фигур'
        if type(figure) != King:
            return figure.check_move(ch2, num2)
        return figure.check_move(ch2, num2, True)

    def process_castling(self, move):
        ch1, num1, ch2, num2 = move
        if not (move in ['e1h1', 'e1a1'] and self.move%2==1) and not (move in ['e8a8', 'e8a1'] and self.move%2==0):
            return

        king = False
        rook = False
        for fig in self.figures:
            if fig.white == self.move%2:
                if type(fig) == King and fig.ch == ch1 and fig.num == num1:
                    king = fig
                if type(fig) == Rook and fig.ch == ch2 and fig.num == num2:
                    rook = fig
        if not king:
            return 'на этой позиции нет короля'
        if not rook:
            return 'на этой позиции нет ладьи'
        if not king.can_castling:
            return 'король не может сделать рокировку'
        if not rook.can_castling:
            return 'ладья не может сделать рокировку'

        field = self.field_of_figures()
        if move == 'e1h1':
            white_space = field[0][5:7]
            king_pos = 'g1'
            rook_pos = 'f1'
        if move == 'e1a1':
            white_space = field[0][1:4]
            king_pos = 'c1'
            rook_pos = 'd1'
        if move == 'e8a8':
            white_space = field[7][5:7]
            king_pos = 'g8'
            rook_pos = 'f8'
        if move == 'e8a8':
            white_space = field[7][1:4]
            king_pos = 'c8'
            rook_pos = 'd8'
        if set(white_space) != {0}:
            return 'между королём и ладьёй лишние фигуры'

        king.ch = king_pos[0]
        king.num = king_pos[1]
        rook.ch = rook_pos[0]
        rook.num = rook_pos[1]
        king.can_castling = False
        rook.can_castling = False
        return True

    def field_of_figures(self):
        field = [[0] * 8 for _ in range(8)]
        for fig in self.figures:
            m = Nums.index(fig.num)
            n = Alph.index(fig.ch)
            field[m][n] = 'w' if fig.white else 'b'
        return field


    def to_image(self, white, path):
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
            x = i*60 if white else (7-i) * 60
            x += 50 - char.get_width()//2
            uy = 10 - char.get_height()//2
            by = 510 - char.get_height()//2
            image.blit(char, (x, uy))
            image.blit(char, (x, by))
            num = font.render(Nums[7-i], True, WCC)
            lx = 10 - char.get_width()//2
            rx = 510 - char.get_width()//2
            y = i*60 if white else (7-i) * 60
            y += 50 - char.get_height()//2
            image.blit(num, (lx, y))
            image.blit(num, (rx, y))
        # Добавляем фигуры
        for fig in self.figures:
            i = Alph.index(fig.ch)
            j = Nums.index(fig.num)
            if white:
                j = 7-j
            else:
                i = 7-i
            x = i*60 + 20
            y = j*60 + 20
            image.blit(fig.sprite, (x, y))
        # Сохраняем картинку
        pygame.image.save(image, path)
        return path


class Figure:
    moves = [(Alph[n%8], Nums[n//8]) for n in range(64)]
    interfering_figures = []

    def set_possible_moves(self):
        pass

    def __init__(self, game, ch, num, white):
        self.game = game
        self.ch = ch
        self.num = num
        self.white = white
        if self.white:
            sprite = pygame.image.load(self.wimage)
        else:
            sprite = pygame.image.load(self.bimage)
        # Центрируем спрайт
        self.sprite = pygame.Surface((60, 60), pygame.SRCALPHA)
        x = 30 - sprite.get_width()//2
        y = 30 - sprite.get_height()//2
        self.sprite.blit(sprite, (x, y))

    def check_move(self, ch, num):
        self.set_possible_moves()
        #print(type(self), self.moves)
        if (ch, num) not in self.moves:
            if (ch, num) in self.interfering_figures:
                return 'мешают другие фигуры'
            return 'невозможный ход'
        if type(self) == Rook:
            self.can_castling = False
        return True


class Pawn(Figure):
    wimage = 'images/white pawn.png'
    bimage = 'images/black pawn.png'

    def set_possible_moves(self):
        field = self.game.field_of_figures()
        moves = []
        interfering_figures = []
        m = Nums.index(self.num)  # string
        n = Alph.index(self.ch)  # column
        # Для белых пешек
        if self.white and m < 7:
            # Простой шаг вперёд
            if not field[m+1][n]:
                moves.append((Alph[n], Nums[m+1]))
            else:
                interfering_figures.append((Alph[n], Nums[m+1]))
            # Первый ход на 2 шага сразу
            if m == 1 and (not field[m+2][n]):
                moves.append((Alph[n], Nums[m+2]))
            elif m == 1:
                interfering_figures.append((Alph[n], Nums[m+2]))
            # Поедание другой фигуры пешкой
            if n < 7 and field[m+1][n+1] == 'b':
                moves.append((Alph[n+1], Nums[m+1]))
            if n > 0 and field[m+1][n-1] == 'b':
                moves.append((Alph[n-1], Nums[m+1]))
        # Для чёрных пешек
        elif m > 0:
            # Простой шаг вперёд
            if not field[m-1][n]:
                moves.append((Alph[n], Nums[m-1]))
            else:
                interfering_figures.append((Alph[n], Nums[m-1]))
            # Первый ход на 2 шага сразу
            if m == 6 and (not field[m-2][n]):
                moves.append((Alph[n], Nums[m-2]))
            elif m == 6:
                interfering_figures.append((Alph[n], Nums[m-2]))
            # Поедание другой фигуры пешкой
            if n < 7 and field[m-1][n+1] == 'w':
                moves.append((Alph[n+1], Nums[m-1]))
            if n > 0 and field[m-1][n-1] == 'w':
                moves.append((Alph[n-1], Nums[m-1]))
        self.moves = moves
        self.interfering_figures = interfering_figures

    @property
    def king_banned_moves(self):
        moves = []
        m = Nums.index(self.num)  # string
        n = Alph.index(self.ch)  # column
        if self.white and m < 7:
            if n < 7:
                moves.append((Alph[n+1], Nums[m+1]))
            if n > 0:
                moves.append((Alph[n-1], Nums[m+1]))
        elif m > 0:
            if n < 7:
                moves.append((Alph[n+1], Nums[m-1]))
            if n > 0:
                moves.append((Alph[n-1], Nums[m-1]))
        return moves


class Rook(Figure):
    wimage = 'images/white rook.png'
    bimage = 'images/black rook.png'

    def __init__(self, *args):
        super().__init__(*args)
        self.can_castling = True

    def set_possible_moves(self):
        field = self.game.field_of_figures()
        moves = []
        int_fig = []
        n = Nums.index(self.num)  # string
        m = Alph.index(self.ch)  # column

        # + по цифрам
        interfering = False
        for i in range(n+1, 8):
            move = (Alph[m], Nums[i])
            if not interfering:
                moves.append(move)
            else:
                int_fig.append(move)
            if field[i][m]:
                if field[i][m] == ('w' if self.white else 'b') and not interfering:
                    moves.remove(move)
                interfering = True

        # - по цифрам
        interfering = False
        for i in range(n-1, -1, -1):
            move = (Alph[m], Nums[i])
            if not interfering:
                moves.append(move)
            else:
                int_fig.append(move)
            if field[i][m]:
                if field[i][m] == ('w' if self.white else 'b') and not interfering:
                    moves.remove(move)
                interfering = True

        # + по буквам
        interfering = False
        for i in range(m+1, 8):
            move = (Alph[i], Nums[n])
            if not interfering:
                moves.append(move)
            else:
                int_fig.append(move)
            if field[n][i]:
                if field[n][i] == ('w' if self.white else 'b') and not interfering:
                    moves.remove(move)
                interfering = True

        # - по буквам
        interfering = False
        for i in range(m-1, -1, -1):
            move = (Alph[i], Nums[n])
            if not interfering:
                moves.append(move)
            else:
                int_fig.append(move)
            if field[n][i]:
                if field[n][i] == ('w' if self.white else 'b') and not interfering:
                    moves.remove(move)
                interfering = True

        self.moves = moves
        self.interfering_figures = int_fig


class Bishop(Figure):
    wimage = 'images/white bishop.png'
    bimage = 'images/black bishop.png'

    def set_possible_moves(self):
        field = self.game.field_of_figures()
        moves = []
        int_fig = []
        n = Nums.index(self.num)  # string
        m = Alph.index(self.ch)  # column

        # + по буквам + по цифрам
        interfering = False
        for i in range(1, min(8-m, 8-n)):
            move = (Alph[m+i], Nums[n+i])
            if not interfering:
                moves.append(move)
            else:
                int_fig.append(move)
            if field[n+i][m+i] and not interfering:
                interfering = True
                if field[n+i][m+i] == ('w' if self.white else 'b'):
                    moves.remove(move)

        # - по буквам - по цифрам
        interfering = False
        for i in range(1, min(m, n)+1):
            move = (Alph[m-i], Nums[n-i])
            if not interfering:
                moves.append(move)
            else:
                int_fig.append(move)
            if field[n-i][m-i] and not interfering:
                interfering = True
                if field[n-i][m-i] == ('w' if self.white else 'b'):
                    moves.remove(move)

        # + по буквам - по цифрам
        interfering = False
        for i in range(1, min(7-m, n)+1):
            move = (Alph[m+i], Nums[n-i])
            if not interfering:
                moves.append(move)
            else:
                int_fig.append(move)
            if field[n-i][m+i] and not interfering:
                interfering = True
                if field[n-i][m+i] == ('w' if self.white else 'b'):
                    moves.remove(move)

        # - по буквам + по цифрам
        interfering = False
        for i in range(1, min(m, 7-n)+1):
            move = (Alph[m-i], Nums[n+i])
            if not interfering:
                moves.append(move)
            else:
                int_fig.append(move)
            if field[n+i][m-i] and not interfering:
                interfering = True
                if field[n+i][m-i] == ('b' if self.white else 'w'):
                    moves.remove(move)

        self.moves = moves
        self.interfering_figures = int_fig


class Queen(Figure):
    wimage = 'images/white queen.png'
    bimage = 'images/black queen.png'

    def set_possible_moves(self):
        """ Берём все ходы от ладьи и слона
        """
        Bishop.set_possible_moves(self)
        bish_moves = self.moves
        bish_inter = self.interfering_figures
        Rook.set_possible_moves(self)
        self.moves += bish_moves
        self.interfering_figures += bish_inter


class Knight(Figure):
    wimage = 'images/white knight.png'
    bimage = 'images/black knight.png'

    def set_possible_moves(self):
        field = self.game.field_of_figures()
        moves = []
        int_fig = []
        n = Nums.index(self.num)  # string
        m = Alph.index(self.ch)  # column

        movesij = []
        # + по цифрам
        movesij.append((n-2, m-1))
        movesij.append((n-2, m+1))
        # - по цифрам
        movesij.append((n+2, m-1))
        movesij.append((n+2, m+1))
        # + по буквам
        movesij.append((n-1, m+2))
        movesij.append((n+1, m+2))
        # - по буквам
        movesij.append((n-1, m-2))
        movesij.append((n+1, m-2))
        for ijmove in movesij:
            if 0 <= ijmove[0] <= 7 and 0 <= ijmove[1] <= 7:
                move = (Alph[ijmove[1]], Nums[ijmove[0]])
                if field[ijmove[0]][ijmove[1]] != ('w' if self.white else 'b'):
                    moves.append(move)
                else:
                    int_fig.append(move)

        self.moves = moves
        self.interfering_figures = int_fig


class King(Figure):
    wimage = 'images/white king.png'
    bimage = 'images/black king.png'

    def __init__(self, *args):
        super().__init__(*args)
        self.can_castling = True

    def all_moves(self):
        n = Nums.index(self.num)  # string
        m = Alph.index(self.ch)  # column
        movesij = []
        moves = []
        # верхний ряд (+ по цифрам)
        movesij.append((n + 1, m + 1))
        movesij.append((n + 1, m))
        movesij.append((n + 1, m - 1))
        # средний ряд
        movesij.append((n, m + 1))
        movesij.append((n, m))
        movesij.append((n, m - 1))
        # нижний ряд (- по цифрам)
        movesij.append((n - 1, m + 1))
        movesij.append((n - 1, m))
        movesij.append((n - 1, m - 1))

        for ijmove in movesij:
            if 0 <= ijmove[0] <= 7 and 0 <= ijmove[1] <= 7:
                move = (Alph[ijmove[1]], Nums[ijmove[0]])
                moves.append(move)
        return moves

    def banned_moves(self, recursion=False):
        moves = []
        for fig in self.game.figures:
            if fig.white != self.white:
                if type(fig) == Pawn:
                    moves += fig.king_banned_moves
                elif type(fig) == King and not recursion:
                    fig.set_possible_moves(recursion=True)
                    moves += fig.moves
                elif type(fig) == King and recursion:
                    king_moves = fig.all_moves()
                    moves += king_moves
                else:
                    fig.set_possible_moves()
                    moves += fig.moves
        return sorted(list(set(moves)))

    def is_shah(self):
        return (self.ch, self.num) in self.banned_moves()

    def set_possible_moves(self, recursion=False):
        field = self.game.field_of_figures()
        moves = []
        int_fig = []

        kmoves = self.all_moves()

        if not recursion:
            banned = self.banned_moves()
        else:
            banned = self.banned_moves(recursion=True)
        #print('white' if self.white else 'black', 'banned', banned)
        for move in kmoves:
            if move in banned:
                continue
            n = Nums.index(move[1])
            m = Alph.index(move[0])
            if field[n][m] != ('w' if self.white else 'b'):
                moves.append(move)
            else:
                int_fig.append(move)

        self.moves = moves
        self.interfering_figures = int_fig
        self.banned = banned

    def check_move(self, ch, num, for_comment=False):
        if not for_comment:
            self.set_possible_moves()
            #print(type(self), self.moves)
        if (ch, num) in self.banned:
            return 'вражеские фигуры смогут атаковать короля'
        if (ch, num) not in self.moves:
            if (ch, num) in self.interfering_figures:
                return 'мешают другие фигуры'
            return 'невозможный ход'
        self.can_castling = False
        return True
