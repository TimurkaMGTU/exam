# coding: utf-8
# license: GPLv3

import re

from space_objects import *

class Parser:
    def read_space_objects_data_from_file(self, input_filename):
        """Cчитывает данные о космических объектах из файла, создаёт сами объекты
        и вызывает создание их графических образов

        Параметры:

        **input_filename** — имя входного файла
        """

        objects = []
        with open(input_filename) as input_file:
            for line in input_file:
                if len(line.strip()) == 0 or line[0] == '#':
                    continue  # пустые строки и строки-комментарии пропускаем
                match = re.search(r"Star|Planet|Satellite", line)
                if match.group() == "Star":
                    star = Star()
                    self.parse_obj_parameters(line, star)
                    objects.append(star)
                elif match.group() == "Planet":
                    planet = Planet()
                    self.parse_obj_parameters(line, planet)
                    objects.append(planet)
                elif match.group() == "Satellite":
                    satellite = Satellite()
                    self.parse_obj_parameters(line, satellite, objects)
                    objects.append(satellite)
                else:
                    print("Unknown space object")
        return objects


    def parse_obj_parameters(self, line, obj, objects=None):
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

        obj.name = match[0]
        obj.r = match[1]
        obj.color = match[2]
        obj.m = match[3]
        obj.x = match[4]
        obj.y = match[5]
        obj.Vx = match[6]
        obj.Vy = match[7]
        if len(match) == 9:
            for i in objects:
                if i.name == match[8]:
                    obj.parentPlanet = i
                    break

    def write_space_objects_data_to_file(self, output_filename, space_objects):
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
                print(f"{obj.name} {obj.r} {obj.color} {obj.m} {obj.x} {obj.y} {obj.Vx} {obj.Vy}\n", file=out_file)


    def write_statistics_to_file(self, output_filename, stats_history):
        """Сохраняет собранную статистику (энергию, время) в CSV-файл.

        Параметры:

        **output_filename** — имя выходного файла.
        **stats_history** — список словарей со статистикой.
        """
        with open(output_filename, 'w') as out_file:
            # Записываем заголовок CSV-файла
            out_file.write("Time,KineticEnergy,PotentialEnergy,TotalEnergy\n")

            # Записываем каждую точку данных
            for stats_point in stats_history:
                time = stats_point["time"]
                ke = stats_point["ke"]
                pe = stats_point["pe"]
                te = stats_point["te"]
                # Форматируем строку и записываем. Используем научную нотацию (e) для больших чисел.
                out_file.write(f"{time:.4f},{ke:.4e},{pe:.4e},{te:.4e}\n")

if __name__ == "__main__":
    print("This module is not for direct call!")
