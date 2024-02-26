import pygame, sys
from pygame.locals import *
import Puzzle
from components.Button import Button
from os import listdir
from os.path import isfile, join

maps = [f for f in listdir("assets/maps") if isfile(join("assets/maps", f)) and f.endswith(".txt")]
map = ""

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480

pygame.font.init()
pygame.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Sokoban Game")
bg = pygame.image.load("assets/images/background.png")

button_surface = pygame.image.load("assets/images/button.png")
button_font = pygame.font.SysFont(None, 30)
button_surface = pygame.transform.scale(button_surface, (204, 42))


def generated_buttons_levels():
    levels = []
    y = 220
    zone = 0
    count = 0

    for i in range(len(maps)):
        if zone == 0:
            levels.append(Button(screen, button_surface, 144, y, maps[i].replace(".txt", ""), button_font))
        else:
            levels.append(Button(screen, button_surface, 496, y, maps[i].replace(".txt", ""), button_font))

        y = 220 if y == 344 else y + 62
        count += 1

        if count % 3 == 0:
            zone = 1 - zone  # Alternates between 0 and 1 for each row

    return levels


levels = generated_buttons_levels()

next = Button(screen, button_surface, 480, 440, "next", button_font)
previous = Button(screen, button_surface, 160, 440, "previous", button_font)

level_init = 0

while map == "":
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            for i in range(level_init, min(level_init + 6, len(levels))):
                if levels[i].checkForInput(pygame.mouse.get_pos()):
                    map = levels[i].getText() + ".txt"

            if next.checkForInput(pygame.mouse.get_pos()) and next.isEnable():
                level_init += 6
            elif previous.checkForInput(pygame.mouse.get_pos()) and previous.isEnable():
                level_init -= 6

    screen.blit(bg, (0, 0))

    for i in range(level_init, min(level_init + 6, len(levels))):
        levels[i].update()
        levels[i].changeColor(pygame.mouse.get_pos())

    if len(levels) > 6 and len(levels) - level_init > 6:
        next.setEnable()
        next.update()
        next.changeColor(pygame.mouse.get_pos())
    else:
        next.setDisable()

    if level_init > 0:
        previous.setEnable()
        previous.update()
        previous.changeColor(pygame.mouse.get_pos())
    else:
        previous.setDisable()

    pygame.display.update()

Puzzle.run("assets/maps/" + map)
