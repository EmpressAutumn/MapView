import json
import imageio.v3 as iio
import numpy as np


def map_to_json(provinces):
    md = {}
    return md


def load_map():
    provinces = iio.imread("assets/textures/map/earth.png").tolist()
    for y in range(len(provinces)):
        for x in range(len(provinces[y])):
            provinces[y][x] = tuple(provinces[y][x])
    return provinces


if __name__ == "__main__":
    prov = load_map()
    map_data = map_to_json(prov)
