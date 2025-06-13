# coding: utf-8
# license: GPLv3

import tkinter
from tkinter.filedialog import *
from solar_vis import *
from solar_model import *
from solar_input import *



global perform_execution, simulation_paused


from math import atan2, cos, sin
global show_orbits, orbit_button
show_orbits = True
orbit_button = None
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

    if not perform_execution:
        return

    dt = float(time_step.get()) if time_step.get() else 1.0

    # Вращение планет с учетом четности орбит
    for body in space_objects:
        if getattr(body, 'type', None) == 'planet' and hasattr(body, 'parent_star'):
            star = body.parent_star
            dx = body.x - star.x
            dy = body.y - star.y
            r = sqrt(dx ** 2 + dy ** 2)

            if r > 0:
                # Определяем направление вращения
                direction = -1 if body.orbit_number % 2 else 1  # -1 для нечетных (CCW), 1 для четных (CW)
                angular_speed = 0.05 * direction

                # Обновляем угол
                if not hasattr(body, 'orbit_angle'):
                    body.orbit_angle = atan2(dy, dx)
                body.orbit_angle += angular_speed * dt

                # Обновляем позицию
                body.x = star.x + r * cos(body.orbit_angle)
                body.y = star.y + r * sin(body.orbit_angle)

                # Обновляем на экране
                update_planet_position(space, body)

    physical_time += dt
    displayed_time.set(f"Время: {physical_time:.1f} сек")

    if perform_execution:
        space.after(50, execution)


def start_execution():
    global perform_execution, physical_time

    if not perform_execution:
        perform_execution = True
        physical_time = 0
        start_button['text'] = "Pause"

        # Инициализация орбит
        for star in [obj for obj in space_objects if obj.type == 'star']:
            planets = [p for p in space_objects if getattr(p, 'parent_star', None) == star]
            planets.sort(key=lambda p: sqrt((p.x - star.x) ** 2 + (p.y - star.y) ** 2))

            for i, planet in enumerate(planets, 1):
                planet.orbit_number = i  # Нумерация от 1
                print(f"Планета {planet.color}: орбита {i} ({'CW' if i % 2 == 0 else 'CCW'})")

        execution()
    else:
        perform_execution = False
        start_button['text'] = "Start"




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
    global physical_time, displayed_time, time_step, time_speed, space, start_button, frame, orbit_button
    global perform_execution, simulation_paused
    perform_execution = False
    simulation_paused = False
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

    stop_button = tkinter.Button(frame, text="Stop", command=stop_execution, width=6)
    stop_button.pack(side=tkinter.LEFT)


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
    orbit_button = tkinter.Button(frame, text="Hide Orbits", command=toggle_orbits)
    orbit_button.pack(side=tkinter.LEFT)

    root.mainloop()
    print('Modelling finished!')


def toggle_orbits():
    global show_orbits, space, orbit_button

    show_orbits = not show_orbits

    # Переключаем видимость орбит
    if show_orbits:
        space.itemconfigure("orbit", state="normal")
        orbit_button.config(text="Hide Orbits")
    else:
        space.itemconfigure("orbit", state="hidden")
        orbit_button.config(text="Show Orbits")
def toggle_pause():
    from solar_model import sim
    is_paused = sim.toggle_pause()
    pause_button['text'] = "Resume" if is_paused else "Pause"

if __name__ == "__main__":
    main()
