# coding: utf-8
# license: GPLv3

import tkinter
from tkinter.filedialog import *
from solar_vis import *
from solar_model import *
from solar_input import *

perform_execution = False
"""Флаг цикличности выполнения расчёта"""

physical_time = 0
"""Физическое время от начала расчёта.
Тип: float"""

displayed_time = None
"""Отображаемое на экране время.
Тип: переменная tkinter"""

time_step = None
"""Шаг по времени при моделировании.
Тип: float"""

space_objects = []
"""Список космических объектов."""


def execution():
    global physical_time

    # Физические расчеты
    recalculate_space_objects_positions(space_objects, time_step.get())
    physical_time += time_step.get()
    displayed_time.set(f"{physical_time:.1f} seconds gone")



    if perform_execution:
        space.after(101 - int(time_speed.get()), execution)


def start_execution():
    """Обработчик события нажатия на кнопку Start.
    Запускает циклическое исполнение функции execution.
    """
    global perform_execution
    perform_execution = True
    start_button['text'] = "Pause"
    start_button['command'] = stop_execution

    execution()
    print('Started execution...')


def stop_execution():
    """Обработчик события нажатия на кнопку Start.
    Останавливает циклическое исполнение функции execution.
    """
    global perform_execution
    perform_execution = False
    start_button['text'] = "Start"
    start_button['command'] = start_execution
    print('Paused execution.')


def open_file_dialog():
    global space_objects
    perform_execution = False

    # Полная очистка предыдущего состояния
    for obj in space_objects:
        space.delete(obj.image)
    clear_all_orbits(space)  # Используем функцию очистки орбит

    in_filename = askopenfilename(filetypes=(("Text file", ".txt"),))
    if not in_filename:  # Если пользователь отменил выбор
        return

    space_objects = read_space_objects_data_from_file(in_filename)

    try:
        max_distance = max(max(abs(obj.x), abs(obj.y)) for obj in space_objects)
        calculate_scale_factor(max_distance)

        # Сначала создаем все звезды
        stars = [obj for obj in space_objects if obj.type == 'star']
        for star in stars:
            create_star_image(space, star)

        # Затем планеты с привязкой к своим звездам
        current_star = None
        for obj in space_objects:
            if obj.type == 'star':
                current_star = obj
            elif obj.type == 'planet' and current_star:
                obj.parent_star = current_star
                create_planet_image(space, obj)
    except Exception as e:
        print(f"Ошибка при загрузке файла: {e}")


def draw_system():
    # Очищаем предыдущее
    space.delete("all")

    # Рисуем звезды
    stars = [obj for obj in space_objects if obj.type == 'star']
    for star in stars:
        create_star_image(space, star)

        # Рисуем орбиты для каждой звезды
        planets = [obj for obj in space_objects
                   if getattr(obj, 'parent_star', None) == star]
        for planet in planets:
            planet.orbit = draw_orbit(space, star, planet)
            create_planet_image(space, planet)

def save_file_dialog():
    """Открывает диалоговое окно выбора имени файла и вызывает
    функцию считывания параметров системы небесных тел из данного файла.
    Считанные объекты сохраняются в глобальный список space_objects
    """
    out_filename = asksaveasfilename(filetypes=(("Text file", ".txt"),))
    write_space_objects_data_to_file(out_filename, space_objects)


def main():
    """Главная функция главного модуля.
    Создаёт объекты графического дизайна библиотеки tkinter: окно, холст, фрейм с кнопками, кнопки.
    """
    global physical_time
    global displayed_time
    global time_step
    global time_speed
    global space
    global start_button

    print('Modelling started!')
    physical_time = 0

    root = tkinter.Tk()
    # космическое пространство отображается на холсте типа Canvas
    space = tkinter.Canvas(root, width=window_width, height=window_height, bg="black")
    space.pack(side=tkinter.TOP)
    # нижняя панель с кнопками
    frame = tkinter.Frame(root)
    frame.pack(side=tkinter.BOTTOM)

    start_button = tkinter.Button(frame, text="Start", command=start_execution, width=6)
    start_button.pack(side=tkinter.LEFT)

    time_step = tkinter.DoubleVar()
    time_step.set(1)
    time_step_entry = tkinter.Entry(frame, textvariable=time_step)
    time_step_entry.pack(side=tkinter.LEFT)

    time_speed = tkinter.DoubleVar()
    scale = tkinter.Scale(frame, variable=time_speed, orient=tkinter.HORIZONTAL)
    scale.pack(side=tkinter.LEFT)

    load_file_button = tkinter.Button(frame, text="Open file...", command=open_file_dialog)
    load_file_button.pack(side=tkinter.LEFT)
    save_file_button = tkinter.Button(frame, text="Save to file...", command=save_file_dialog)
    save_file_button.pack(side=tkinter.LEFT)

    displayed_time = tkinter.StringVar()
    displayed_time.set(str(physical_time) + " seconds gone")
    time_label = tkinter.Label(frame, textvariable=displayed_time, width=30)
    time_label.pack(side=tkinter.RIGHT)

    root.mainloop()
    print('Modelling finished!')

if __name__ == "__main__":
    main()
