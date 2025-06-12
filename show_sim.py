import tkinter
import tkinter as tk
from tkinter.filedialog import *

import space_objects
from space_objects import *
from parse_data import *

class Window:
    def __init__(self, window_width=800, window_height=800):
        self.space_objects = []
        self.physical_time = 0
        self.perform_execution = False
        self.displayed_time = None
        self.time_step = None
        self.statistics_history = []
        self.frame_counter = 0
        self.space = None
        self.window_width = window_width
        self.window_height = window_height
        self.camera_x = 0
        self.camera_y = 0
        self.scale_factor = 1.0
        self.default_scale_factor = 1.0
        self.time_speed = None
        self.start_button = None
        self.parser = Parser()

    def scale_x(self, x):
        return int((x - self.camera_x) * self.scale_factor) + self.window_width // 2

    def scale_y(self, y):
        return self.window_height // 2 - int((y - self.camera_y) * self.scale_factor)

    def zoom_in(self, event=None):  # Добавили event=None, чтобы можно было вызывать с кнопки
        """Приближает вид."""
        self.scale_factor *= 1.5

    def zoom_out(self, event=None):
        """Отдаляет вид."""
        self.scale_factor /= 1.5

    def move_camera(self, direction):
        """Перемещает камеру с помощью стрелок."""
        # Смещение будет зависеть от масштаба, чтобы движение было комфортным
        pan_step = min(self.window_width, self.window_height) / self.scale_factor / 10  # 1/10 ширины экрана

        if direction == "up":
            self.camera_y += pan_step
        elif direction == "down":
            self.camera_y -= pan_step
        elif direction == "left":
            self.camera_x -= pan_step
        elif direction == "right":
            self.camera_x += pan_step

    def reset_view(self, event=None):
        """Сбрасывает вид к начальному состоянию."""
        self.camera_x = 0.0
        self.camera_y = 0.0
        self.scale_factor = self.default_scale_factor
        print("View has been reset.")

    def calculate_scale_factor(self, max_distance):
        """Вычисляет значение глобальной переменной **scale_factor** по данной характерной длине"""
        initial_scale = 0.4 * min(self.window_height, self.window_width) / max_distance
        self.scale_factor = initial_scale
        self.default_scale_factor = initial_scale
        print('Scale factor:', self.scale_factor)

    def execution(self):
        for obj in self.space_objects:
            obj.calculate_force(self.space_objects)

        for obj in self.space_objects:
            obj.move_space_object(self.time_step.get())

        if self.frame_counter % 10 == 0:  # Сбор статистики каждый 10 кадр для оптимизации
            ke, pe, te = calculate_system_energy(self.space_objects)
            stats_point = {
                "time": self.physical_time,
                "ke": ke,
                "pe": pe,
                "te": te
            }
            self.statistics_history.append(stats_point)
        self.frame_counter += 1

        for body in self.space_objects:
            body.update_object_position(self.space, self.window_width, self.window_height, self.scale_x(body.x), self.scale_y(body.y))
        self.physical_time += self.time_step.get()
        self.displayed_time.set("%.1f" % self.physical_time + " seconds gone")

        if self.perform_execution:
            self.space.after(101 - int(self.time_speed.get()), self.execution)

    def start_execution(self):
        """Обработчик события нажатия на кнопку Start.
        Запускает циклическое исполнение функции execution.
        """
        self.perform_execution = True
        self.start_button['text'] = "Pause"
        self.start_button['command'] = self.stop_execution  #FIXME

        self.execution()
        print('Started execution...')

    def stop_execution(self):
        """Обработчик события нажатия на кнопку Start.
        Останавливает циклическое исполнение функции execution.
        """
        self.perform_execution = False
        self.start_button['text'] = "Start"
        self.start_button['command'] = self.start_execution #FIXME
        print('Paused execution.')

    def open_file_dialog(self):
        """Открывает диалоговое окно выбора имени файла и вызывает
        функцию считывания параметров системы небесных тел из данного файла.
        Считанные объекты сохраняются в глобальный список space_objects
        """
        self.statistics_history.clear()
        self.frame_counter = 0
        self.perform_execution = False
        for obj in self.space_objects:
            self.space.delete(obj.image)  # удаление старых изображений планет
        in_filename = askopenfilename(filetypes=(("Text file", ".txt"),))
        self.space_objects = self.parser.read_space_objects_data_from_file(in_filename)
        max_distance = max([max(abs(obj.x), abs(obj.y)) for obj in self.space_objects])
        self.calculate_scale_factor(max_distance)

        for obj in self.space_objects:
            obj.create_object_image(self.space, self.scale_x(obj.x), self.scale_y(obj.y))

    def save_stats_dialog(self):
        """Открывает диалог сохранения файла и записывает статистику."""
        if not self.statistics_history:
            print("No statistics to save yet.")
            return

        out_filename = asksaveasfilename(filetypes=(("CSV file", ".csv"),))
        if out_filename:
            self.parser.write_statistics_to_file(out_filename, self.statistics_history)
            print(f"Statistics saved to {out_filename}")

    def save_file_dialog(self):
        """Открывает диалоговое окно выбора имени файла и вызывает
        функцию считывания параметров системы небесных тел из данного файла.
        Считанные объекты сохраняются в глобальный список space_objects
        """
        out_filename = asksaveasfilename(filetypes=(("Text file", ".txt"),))
        self.parser.write_space_objects_data_to_file(out_filename, self.space_objects)

def main():
    window = Window()
    print('Modelling started!')
    window.physical_time = 0

    root = tkinter.Tk()
    window.space = tkinter.Canvas(root, width=window.window_width, height=window.window_height, bg="black")

    window.space.pack(side=tkinter.TOP)

    frame = tkinter.Frame(root)
    frame.pack(side=tkinter.BOTTOM)

    window.space.focus_set()

    window.space.bind("<MouseWheel>", lambda event: window.zoom_in() if event.delta > 0 else window.zoom_out())

    # Привязываем клавиши со стрелками
    window.space.bind("<Up>", lambda event: window.move_camera("up"))
    window.space.bind("<Down>", lambda event: window.move_camera("down"))
    window.space.bind("<Left>", lambda event: window.move_camera("left"))
    window.space.bind("<Right>", lambda event: window.move_camera("right"))

    reset_view_button = tkinter.Button(frame, text="Reset View", command=window.reset_view)
    reset_view_button.pack(side=tkinter.LEFT)

    zoom_in_button = tkinter.Button(frame, text="+", command=window.zoom_in)
    zoom_in_button.pack(side=tkinter.LEFT)
    zoom_out_button = tkinter.Button(frame, text="-", command=window.zoom_out)
    zoom_out_button.pack(side=tkinter.LEFT)

    window.start_button = tkinter.Button(frame, text="Start", command=window.start_execution, width=6)
    window.start_button.pack(side=tkinter.LEFT)

    window.time_step = tkinter.DoubleVar()
    window.time_step.set(1)
    time_step_entry = tkinter.Entry(frame, textvariable=window.time_step)
    time_step_entry.pack(side=tkinter.LEFT)
    time_step_entry.bind("<Return>", lambda event: window.space.focus_set())

    window.time_speed = tkinter.DoubleVar()
    scale = tkinter.Scale(frame, variable=window.time_speed, orient=tkinter.HORIZONTAL)
    scale.pack(side=tkinter.LEFT)

    load_file_button = tkinter.Button(frame, text="Open file...", command=window.open_file_dialog)
    load_file_button.pack(side=tkinter.LEFT)
    save_stats_button = tkinter.Button(frame, text="Save Stats...", command=window.save_stats_dialog)
    save_stats_button.pack(side=tkinter.LEFT)
    save_file_button = tkinter.Button(frame, text="Save to file...", command=window.save_file_dialog)
    save_file_button.pack(side=tkinter.LEFT)

    window.displayed_time = tkinter.StringVar()
    window.displayed_time.set(str(window.physical_time) + " seconds gone")
    time_label = tkinter.Label(frame, textvariable=window.displayed_time, width=30)
    time_label.pack(side=tkinter.RIGHT)

    root.mainloop()
    print('Modelling finished!')


if __name__ == "__main__":
    main()

