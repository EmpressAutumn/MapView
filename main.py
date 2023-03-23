import argparse
import json
import numpy as np
import pygame


class MapData:
    def __init__(self):
        self.countries = []

    def add_country(self, country):
        self.countries.append(country)


class Region:
    def __init__(self, name, prefix="", suffix="", color="", government="", leader=""):
        self.name = name
        if prefix is not None:
            self.prefix = prefix
        if suffix is not None:
            self.suffix = suffix
        if color is None:
            self.color = list(np.random.choice(range(256), size=3))  # Generates a random color value, may be changed later
        if government is not None:
            self.government = government
        if leader is not None:
            self.leader = leader
        self.consts = []
        self.coords = []

    def add_const(self, constituency):
        self.consts.append(constituency)

    def add_coord(self, coordinate):
        self.coords.append(coordinate)


parser = argparse.ArgumentParser()
parser.add_argument("-f", "--filename", type=str)


BACKGROUND = (0, 0, 0)


def coords_alterer(coords, o_x, o_y):
    for i in range(len(coords)):
        coords[i] += (o_x, o_y)
    return coords


def draw_map(screen, md, o_x, o_y):
    for i in range(0, len(md.countries) - 1):
        color = md.countries[i].color
        pygame.draw.polygon(screen, color, coords_alterer(md.countries[i].coords, o_x, o_y))


def map_handler(md):
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption(f"MapView {json.load(open('properties.json'))['version']}")

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
        draw_map(screen, md, o_x, o_y)
        pygame.display.update()


def country_read_handler(raw_data):
    base_level = True
    for key, value in raw_data.items():
        if key == "constituencies":
            base_level = False


def read_map(fn):
    if fn is None:
        fn = input("File to be opened: ")
    file = json.load(open("map/" + fn))
    md = MapData()
    for key, value in file.items():
        if key == "structure":
            print(fn + " using file structure " + str(value))
        else:
            country_read_handler(value)
            md.add_country("")
    return md


if __name__ == "__main__":
    args = parser.parse_args()
    file_name = args.filename

    map_data = read_map(file_name)
    map_handler(map_data)
