import pygame
pygame.font.init()
intr_font = pygame.font.SysFont('Arial', 100)

W_WIDTH = 800
W_HEIGHT = 600

screen = pygame.display.set_mode((W_WIDTH, W_HEIGHT))
pygame.display.set_caption('Chess')

# Вывод приветствия
intr = intr_font.render('Chess', True, (180, 180, 180))
draw_x = W_WIDTH//2 - intr.get_width()//2
draw_y = W_HEIGHT//2 - intr.get_height()//2 - 10
screen.blit(intr, (draw_x, draw_y))
pygame.display.update()

while 1:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            exit()

    pygame.display.update()