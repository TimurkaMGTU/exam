# coding: utf-8
# license: GPLv3

"""Модуль визуализации.
Нигде, кроме этого модуля, не используются экранные координаты объектов.
Функции, создающие графические объекты и перемещающие их на экране, принимают физические координаты
"""
from math import sqrt

star_orbits = {}  # {star_id: [orbit1, orbit2, ...]}


header_font = "Arial-16"
"""Шрифт в заголовке"""

window_width = 800
"""Ширина окна"""

window_height = 800
"""Высота окна"""

scale_factor = None
"""Масштабирование экранных координат по отношению к физическим.
Тип: float
Мера: количество пикселей на один метр."""


def calculate_scale_factor(max_distance):
    """Вычисляет значение глобальной переменной **scale_factor** по данной характерной длине"""
    global scale_factor
    scale_factor = 0.4*min(window_height, window_width)/max_distance
    print('Scale factor:', scale_factor)


def scale_x(x):
    """Возвращает экранную **x** координату по **x** координате модели.
    Принимает вещественное число, возвращает целое число.
    В случае выхода **x** координаты за пределы экрана возвращает
    координату, лежащую за пределами холста.

    Параметры:

    **x** — x-координата модели.
    """

    return int(x*scale_factor) + window_width//2


def scale_y(y):
    """Возвращает экранную **y** координату по **y** координате модели.
    Принимает вещественное число, возвращает целое число.
    В случае выхода **y** координаты за пределы экрана возвращает
    координату, лежащую за пределами холста.
    Направление оси развёрнуто, чтобы у модели ось **y** смотрела вверх.

    Параметры:

    **y** — y-координата модели.
    """

    return window_height//2 - int(y*scale_factor)  #FIXME: not done yet


def create_star_image(space, star):
    """Создаёт отображаемый объект звезды.

    Параметры:

    **space** — холст для рисования.
    **star** — объект звезды.
    """

    x = scale_x(star.x)
    y = scale_y(star.y)
    r = star.R
    star.image = space.create_oval([x - r, y - r], [x + r, y + r], fill=star.color)




def create_satellite_image(space, satellite):
    """Создаёт отображаемый объект планеты.

        Параметры:

        **space** — холст для рисования.
        **satellite** — объект планеты.
    """
    x = scale_x(satellite.x)
    y = scale_y(satellite.y)
    r = satellite.R
    satellite.image = space.create_oval([x - r, y - r], [x + r, y + r], fill=satellite.color)

def update_system_name(space, system_name):
    """Создаёт на холсте текст с названием системы небесных тел.
    Если текст уже был, обновляет его содержание.

    Параметры:

    **space** — холст для рисования.
    **system_name** — название системы тел.
    """
    space.create_text(30, 80, tag="header", text=system_name, font=header_font)


# Добавляем в начало файла
orbit_dict = {}  # Словарь для хранения орбит: {planet_id: orbit_id}


def draw_orbit(space, star, planet):
    """Рисует идеально круглую орбиту и сохраняет её в словарь star_orbits"""
    a = ((planet.x - star.x) ** 2 + (planet.y - star.y) ** 2) ** 0.5
    orbit = space.create_oval(
        scale_x(star.x - a), scale_y(star.y - a),
        scale_x(star.x + a), scale_y(star.y + a),
        outline="gray", dash=(2, 2), width=1, tags=("orbit", f"star_{id(star)}")
    )

    # Сохраняем орбиту в словарь star_orbits
    if id(star) not in star_orbits:
        star_orbits[id(star)] = []
    star_orbits[id(star)].append(orbit)

    return orbit

def clear_star_orbits(space, star):
    """Удаляет все орбиты, связанные с конкретной звездой"""
    if id(star) in star_orbits:
        for orbit in star_orbits[id(star)]:
            space.delete(orbit)
        star_orbits[id(star)] = []

def update_orbital_position(body, dt):
    """Гарантирует идеальное круговое движение"""
    if hasattr(body, 'parent_star'):
        star = body.parent_star
        r = ((body.x-star.x)**2 + (body.y-star.y)**2)**0.5
        if r > 0:
            # Вычисляем угловую скорость
            omega = (gravitational_constant * star.m / r**3)**0.5
            # Обновляем позицию по кругу
            angle = atan2(body.y-star.y, body.x-star.x) + omega * dt
            body.x = star.x + r * cos(angle)
            body.y = star.y + r * sin(angle)
            # Корректируем скорость для идеальной орбиты
            body.Vx = -r * omega * sin(angle)
            body.Vy = r * omega * cos(angle)


def clear_all_orbits(space):
    """Удаляет все орбиты"""
    for orbit_id in orbit_dict.values():
        space.delete(orbit_id)
    orbit_dict.clear()


# Обновляем функции создания и обновления объектов
def create_planet_image(space, planet):
    x = scale_x(planet.x)
    y = scale_y(planet.y)
    r = planet.R
    planet.image = space.create_oval([x - r, y - r], [x + r, y + r], fill=planet.color)

    if hasattr(planet, 'parent_star'):
        draw_orbit(space, planet.parent_star, planet)


def update_object_position(space, body):
    """Гарантирует точное положение на орбите"""
    if hasattr(body, 'parent_star'):
        star = body.parent_star
        # Пересчитываем расстояние для идеальной орбиты
        dx = body.x - star.x
        dy = body.y - star.y
        distance = (dx ** 2 + dy ** 2) ** 0.5
        body.x = star.x + dx / distance * ((star.x - body.x) ** 2 + (star.y - body.y) ** 2) ** 0.5
        body.y = star.y + dy / distance * ((star.x - body.x) ** 2 + (star.y - body.y) ** 2) ** 0.5

    # Стандартное обновление позиции
    x = scale_x(body.x)
    y = scale_y(body.y)
    r = body.R
    space.coords(body.image, x - r, y - r, x + r, y + r)

    # Обновляем орбиту
    if hasattr(body, 'orbit') and hasattr(body, 'parent_star'):
        update_orbit(space, body.parent_star, body)
