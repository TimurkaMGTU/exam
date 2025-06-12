# coding: utf-8
# license: GPLv3

from solar_objects import Star, Planet


def read_space_objects_data_from_file(input_filename):
    objects = []
    current_star = None

    with open("C:/Users/timkaMGTU/OneDrive/Рабочий стол/two_stars_system.txt") as input_file:
        for line in input_file:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            parts = line.split()
            obj_type = parts[0].lower()

            if obj_type == "star":
                star = Star()
                parse_star_parameters(line, star)
                objects.append(star)
                current_star = star

            elif obj_type == "planet" and current_star:
                planet = Planet()
                parse_planet_parameters(line, planet)
                planet.parent_star = current_star  # Жесткая привязка к текущей звезде
                objects.append(planet)

    return objects



def parse_star_parameters(line, star):
    """Считывает данные о звезде из строки.
    Входная строка должна иметь следующий формат:
    Star <радиус в пикселах> <цвет> <масса> <x> <y> <Vx> <Vy>

    Здесь (x, y) — координаты звезды, (Vx, Vy) — скорость.
    Пример строки:
    Star 10 red 1000 1 2 3 4

    Параметры:

    **line** — строка с описанием звезды.
    **star** — объект звезды.
    """
    match = line.split()

    match[1], match[3], match[4], match[5], match[6], match[7] = int(match[1]), float(match[3]), float(
        match[4]), float(
        match[5]), float(match[6]), float(match[7])

    star.r = match[1]
    star.color = match[2]
    star.m = match[3]
    star.x = match[4]
    star.y = match[5]
    star.Vx = match[6]
    star.Vy = match[7]


def parse_planet_parameters(line, planet):
    parts = line.split()
    planet.R = int(parts[1])
    planet.color = parts[2]
    planet.m = float(parts[3])

    # Правильное начальное расположение относительно звезды
    planet.x = float(parts[4])
    planet.y = float(parts[5])

    # Начальные скорости должны быть перпендикулярны радиус-вектору
    planet.Vx = float(parts[6])
    planet.Vy = float(parts[7])


def write_space_objects_data_to_file(output_filename, space_objects):
    """Сохраняет данные о космических объектах в файл.
    Строки должны иметь следующий формат:
    Star <радиус в пикселах> <цвет> <масса> <x> <y> <Vx> <Vy>
    Planet <радиус в пикселах> <цвет> <масса> <x> <y> <Vx> <Vy>

    Параметры:

    **output_filename** — имя входного файла
    **space_objects** — список объектов планет и звёзд
    """
    with open(output_filename, 'w') as out_file:
        for obj in space_objects:
            print(out_file, "%s %d %s %f" % ('1', 2, '3', 4.5))
            # FIXME: should store real values

# FIXME: хорошо бы ещё сделать функцию, сохранающую статистику в заданный файл...

if __name__ == "__main__":
    print("This module is not for direct call!")
