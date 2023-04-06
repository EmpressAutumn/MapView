import argparse
import copy
import json
import numpy as np
import pygame
import pygame_gui
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon


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
            self.color = list(np.random.choice(range(256), size=3))  # Generates a random color value, will be changed later
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


def coords_alterer(coords, o_x, o_y, zoom):
    for i in range(len(coords)):
        coords[i] = (coords[i][0] * zoom + o_x, coords[i][1] * zoom + o_y)
    return coords


def get_coords(country):
    if len(country.coords) > 1:
        return country.coords
    else:
        coords = []
        for ct in country.consts:
            for cd in get_coords(ct):
                coords.append(cd)
        return coords


def draw_map(screen, md, o_x, o_y, zoom):
    for i in range(0, len(md.countries)):
        coords = get_coords(md.countries[i])
        color = md.countries[i].color
        pygame.draw.polygon(screen, color, coords_alterer(copy.deepcopy(coords), o_x, o_y, zoom))


def country_clicked_getter(md, x, y, o_x, o_y, zoom):
    for i in range(0, len(md.countries)):
        if Polygon(coords_alterer(copy.deepcopy(get_coords(md.countries[i])), o_x, o_y, zoom)).contains(Point(x, y)):
            return i
    return 0


def init_gui(manager):
    gui_dict = {"quit": pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((700, 550), (100, 50)),
        text="Quit",
        manager=manager
    )}
    return gui_dict


def map_handler(md):
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption(f"MapView {json.load(open('properties.json'))['version']}")

    manager = pygame_gui.UIManager((800, 600))
    gui_dict = init_gui(manager)

    clock = pygame.time.Clock()
    running = True
    panning = False
    o_x, o_tx, o_y, o_ty = 0, 0, 0, 0
    zoom = 20
    while running:
        time_delta = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == gui_dict["quit"]:
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

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left Click
                clicked = country_clicked_getter(md, event.pos[0], event.pos[1], o_x, o_y, zoom)
                if clicked != 0:
                    print("Clicked on country", clicked)
                else:
                    print("Clicked on nothing")

            elif event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == gui_dict["hello_button"]:
                    print('Hello World!')

            manager.process_events(event)

        manager.update(time_delta)

        screen.fill(BACKGROUND)
        draw_map(screen, md, o_x, o_y, zoom)
        manager.draw_ui(screen)
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

    pygame.quit()
