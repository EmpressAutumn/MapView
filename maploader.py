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
        self.coords = country_data["coords"]

    def add_const(self, constituency):
        self.consts.append(constituency)

    def add_coord(self, coordinate):
        self.coords.append(coordinate)


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
    md = merge_provinces(prov_list)

    return md


if __name__ == "__main__":
    map_data = maploader_handler()
