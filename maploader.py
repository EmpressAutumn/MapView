import copy
import imageio.v3 as iio
import numpy as np
from shapely.geometry.polygon import Polygon
from shapely.ops import unary_union


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
        self.consts = []
        self.coords = []

    def add_const(self, constituency):
        self.consts.append(constituency)

    def add_coord(self, coordinate):
        self.coords.append(coordinate)


def remove_by_index(list_i, x, y):
    list_i[y] = list_i[y][0: x - 1] + list_i[y][x: len(list_i[y])]
    if not list_i[y]:
        list_i = list_i[0: y - 1] + list_i[y: len(list_i)]
    return list_i


def merge_provinces(prov_list):
    done = False
    md = []
    while not done:
        done = True
        color_list = [prov_list[0][0]]
        prov_list = remove_by_index(prov_list, 0, 0)
        for y in range(len(prov_list)):
            for x in range(len(prov_list[y])):
                old_length = len(prov_list)
                if prov_list[y][x].color == color_list[0].color:
                    done = False
                    color_list.append(prov_list[y][x])
                    prov_list = remove_by_index(prov_list, x, y)
                    x -= 1
                    if len(prov_list) == old_length:
                        y -= 1


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
                "consts": [(x, y), (x + 1, y), (x + 1, y + 1), (x, y + 1)]
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
    merge_provinces(prov_list)

    return md


if __name__ == "__main__":
    map_data = maploader_handler()
