import argparse
import copy
import imageio.v3 as iio
import json
import numpy as np
import pygame
import pygame_gui
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
from shapely.ops import unary_union


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
            self.color = list(np.random.choice(range(256), size=3))  # Generates a random color value, will change later
        self.government = country_data["government"]
        self.leader = country_data["leader"]
        self.consts = ["consts"]
        self.coords = country_data["coords"]

    def add_const(self, constituency):
        self.consts.append(constituency)

    def add_coord(self, coordinate):
        self.coords.append(coordinate)


BACKGROUND = (31, 128, 128)
BLANKED = (186, 178, 159)


def coords_alterer(coords, o_x, o_y, zoom):
    for i in range(len(coords)):
        coords[i] = (coords[i][0] * 10 * zoom + o_x, coords[i][1] * 10 * zoom + o_y)
    return coords


def get_coords(country):
    if len(country.coords) > 1:
        return tuple([[copy.deepcopy(country.coords)], False])
    else:
        polygons = []
        for const in country.consts:
            polygons.append(Polygon(get_coords(const)[0][0]))
        x, y = unary_union(polygons).exterior.coords.xy

        coords = []
        for i in range(len(x)):
            coords.append((x[i], y[i]))

        return tuple([[coords], True])


def draw_map(clicked, screen, countries, o_x, o_y, zoom, blank=False):
    if len(clicked) > 1:
        country = countries
        for index in clicked[1: len(clicked) - 1]:
            country = country[index].consts
        clicked_index = clicked[len(clicked) - 1]
        if not get_coords(country[clicked_index]):
            draw_map(clicked[1: len(clicked)], screen, countries[clicked_index], o_x, o_y, zoom)
        else:
            try:
                draw_map(clicked[1: len(clicked)], screen, countries[clicked_index].consts, o_x, o_y, zoom)
            except IndexError:
                pass
    else:
        for i in range(0, len(countries)):
            coord_set = get_coords(countries[i])[0]
            color = countries[i].color
            if blank:
                color = BLANKED
            for coords in coord_set:
                pygame.draw.polygon(screen, color, coords_alterer(coords, o_x, o_y, zoom))
                if not blank:
                    pygame.draw.polygon(screen, (0, 0, 0), coords, zoom)


def country_clicked_getter(countries, x, y, o_x, o_y, zoom, clicked_list):
    while len(clicked_list) > 1:
        clicked_list = clicked_list[1: len(clicked_list)]
        countries = countries[clicked_list[0]].consts
    for i in range(0, len(countries)):
        for coords in get_coords(countries[i])[0]:
            if Polygon(coords_alterer(coords, o_x, o_y, zoom)).contains(Point(x, y)):
                return i
    return -1


def init_gui(manager):
    gui_dict = {"quit": pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((700, 550), (100, 50)),
        text="Quit",
        manager=manager)
    }
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
    clicked_list = [-1]
    zoom = 2
    while running:
        time_delta = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == gui_dict["quit"]:
                running = False

            elif event.type == pygame.QUIT:
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

            elif event.type == pygame.MOUSEWHEEL:  # Mouse Wheel
                zoom += event.y * 2
                if zoom <= 2:
                    zoom = 2

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left Click
                clicked = country_clicked_getter(md.countries, event.pos[0], event.pos[1], o_x, o_y, zoom, clicked_list)
                print("Clicked")
                if clicked != -1:
                    clicked_list.append(clicked)
                    clicked_on = md.countries
                    for i in range(1, len(clicked_list)):
                        if i != 1:
                            clicked_on = clicked_on.consts
                        clicked_on = clicked_on[clicked_list[i]]
                    full_name = clicked_on.name
                    if clicked_on.prefix is not None:
                        full_name = clicked_on.prefix + full_name
                    if clicked_on.suffix is not None:
                        full_name += clicked_on.suffix
                    print("Name:", full_name)
                else:
                    clicked_list = [-1]

            elif event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == gui_dict["hello_button"]:
                    pass

            manager.process_events(event)

        manager.update(time_delta)

        screen.fill(BACKGROUND)
        draw_map(clicked_list, screen, md.countries, o_x, o_y, zoom)
        manager.draw_ui(screen)
        pygame.display.update()


def merge_provinces(prov_list):
    done = False
    md = []
    done_colors = []
    while not done:
        color_list = []
        current_color = None
        for y in range(len(prov_list)):
            for x in range(len(prov_list[y])):
                if prov_list[y][x].color not in done_colors and not None:
                    current_color = prov_list[y][x].color
                    color_list.append(prov_list[y][x])
                    prov_list[y][x].color = None
        if current_color is not None:
            done_colors.append(current_color)
            polygons = []
            for country in color_list:
                polygons.append(Polygon(country.coords))
            x, y = unary_union(polygons).exterior.coords.xy
            coords = []
            for i in range(len(x)):
                coords.append((x[i], y[i]))
            color_list[0].coords = coords
            md.append(color_list[0])
        else:
            done = True
    return md


def map_to_json(provinces):
    prov_list = []
    for y in range(len(provinces)):
        row = []
        for x in range(len(provinces[y])):
            row.append(Region({
                "name": f"{x}, {y}",
                "prefix": None,
                "suffix": None,
                "color": provinces[y][x],
                "government": None,
                "leader": None,
                "coords": [(x, y), (x + 1, y), (x + 1, y + 1), (x, y + 1)]
            }))
        prov_list.append(row)
    return prov_list


def load_map():
    provinces = iio.imread("assets/textures/map/earth.png").tolist()
    for y in range(len(provinces)):
        for x in range(len(provinces[y])):
            provinces[y][x] = tuple(provinces[y][x])
    return provinces


def maploader_handler():
    provinces = load_map()
    prov_list = map_to_json(provinces)
    md = MapData()
    for province in merge_provinces(prov_list):
        md.add_country(province)
    return md


def read_country(count):
    count_data = {"name": None, "prefix": None, "suffix": None, "color": None, "government": None, "leader": None}
    for key, value in count.items():
        try:
            count_data[key] = count[key]
        except KeyError:
            pass
    count_data["coords"] = []
    count_data["consts"] = []
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
    file = json.load(open("data/map/" + fn))
    if file["structure"] != -1:
        md = MapData()
        for count in file["map_data"]:
            md.add_country(read_country(count))
        return md
    else:
        return maploader_handler()


parser = argparse.ArgumentParser()
parser.add_argument("-f", "--filename", type=str)


if __name__ == "__main__":
    args = parser.parse_args()
    file_name = args.filename

    map_data = read_map(file_name)
    map_handler(map_data)

    pygame.quit()
