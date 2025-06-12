# coding: utf-8
# license: GPLv3
gravitational_constant = 6.67408E-11
"""Гравитационная постоянная Ньютона G"""


def calculate_force(body, space_objects):
    """Вычисляет силу, действующую на тело"""
    body.Fx = body.Fy = 0

    # Для планет считаем только силу от их звезды
    if hasattr(body, 'parent_star'):
        star = body.parent_star
        r = ((body.x - star.x) ** 2 + (body.y - star.y) ** 2) ** 0.5
        if r > 0:  # Избегаем деления на ноль
            force = gravitational_constant * star.m * body.m / (r ** 2)
            r_x = star.x - body.x
            r_y = star.y - body.y
            body.Fx += force * r_x / r
            body.Fy += force * r_y / r
    # Для звезд считаем все силы
    else:
        for obj in space_objects:
            if body == obj:
                continue
            r = ((body.x - obj.x) ** 2 + (body.y - obj.y) ** 2) ** 0.5
            if r > 0:
                force = gravitational_constant * obj.m * body.m / (r ** 2)
                r_x = obj.x - body.x
                r_y = obj.y - body.y
                body.Fx += force * r_x / r
                body.Fy += force * r_y / r


def move_space_object(body, dt):
    """Движение по идеальной орбите с коррекцией"""
    if hasattr(body, 'parent_star'):
        update_orbital_position(body, dt)
    else:
        # Стандартное движение для звезд
        ax = body.Fx / body.m
        ay = body.Fy / body.m
        body.Vx += ax * dt
        body.Vy += ay * dt
        body.x += body.Vx * dt
        body.y += body.Vy * dt

def recalculate_space_objects_positions(space_objects, dt):
    """Пересчитывает координаты объектов.

    Параметры:

    **space_objects** — список объектов, для которых нужно пересчитать координаты.
    **dt** — шаг по времени
    """

    for body in space_objects:
        calculate_force(body, space_objects)
    for body in space_objects:
        move_space_object(body, dt)


if __name__ == "__main__":
    print("This module is not for direct call!")
