import json
import pygame
import sys


BACKGROUND = (0, 0, 0)


def draw_map(screen, map_data, o_x, o_y):
    pass


def map_handler(map_data):
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption(f"MapView {json.load(open('properties.json'))['version']} by Pale Champion Atom596")

    running = True
    panning = False
    o_x, o_tx, o_y, o_ty = 0, 0, 0, 0
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 2:  # Middle Click
                panning = True
                o_tx, o_ty = event.pos

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 2:
                panning = False

            elif event.type == pygame.MOUSEMOTION and panning:
                o_x += (event.pos[0] - o_tx)
                o_y += (event.pos[1] - o_ty)
                o_tx, o_ty = event.pos

        screen.fill(BACKGROUND)
        draw_map(screen, map_data, o_x, o_y)
        pygame.display.update()


def read_map(file_name):
    print("reading", file_name)  # Will combine JSON reader from other code
    return [[0, 0], [0, 1], [1, 1], [1, 0]]


if __name__ == "__main__":
    file_name = None
    for place in range(1, len(sys.argv), 2):
        if sys.argv[place] in ["-f"]:
            try:
                if sys.argv[place] == "-f":
                    file = sys.argv[place + 1]
            except IndexError:
                raise ValueError(f"{sys.argv[place]} has no argument")
        else:
            raise ValueError(f"{sys.argv[place]} is not a valid argument option")

    map_data = read_map(file_name)
    map_handler(map_data)
