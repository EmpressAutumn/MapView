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
    def __init__(self, country_data):
        self.name = country_data["name"]
        self.prefix = country_data["prefix"]
        self.suffix = country_data["suffix"]
        if country_data["color"] is not None:
            self.color = country_data["color"]
        else:
            self.color = list(np.random.choice(range(256), size=3))  # Generates a random color value, may be changed later
        self.government = country_data["government"]
        self.leader = country_data["leader"]
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


def read_country(count):
    count_data = {"name": None, "prefix": None, "suffix": None, "color": None, "government": None, "leader": None}
    for key, value in count.items():
        try:
            count_data[key] = count[key]
        except KeyError:
            pass
    country = Region(count_data)
    try:
        for coords in count["coordinates"]:
            country.add_coord((coords[0], coords[1]))
    except KeyError:
        for ct in count["constituencies"]:
            country.add_const(read_country(ct))
    return country


def read_map(fn):
    if fn is None:
        fn = input("File to be opened: ")
    file = json.load(open("map/" + fn))
    md = MapData()
    for count in file["map_data"]:
        md.add_country(read_country(count))
    return md


if __name__ == "__main__":
    args = parser.parse_args()
    file_name = args.filename

    map_data = read_map(file_name)
    map_handler(map_data)
