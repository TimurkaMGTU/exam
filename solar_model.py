from math import atan2, cos, sin, sqrt

gravitational_constant = 6.67408E-11


def calculate_force(body, space_objects):
    body.Fx = body.Fy = 0
    if body.type == 'star':
        for obj in space_objects:
            if obj.type == 'star' and obj != body:
                r = sqrt((body.x - obj.x) ** 2 + (body.y - obj.y) ** 2)
                if r > 0:
                    force = gravitational_constant * body.m * obj.m / r ** 2
                    body.Fx += force * (obj.x - body.x) / r
                    body.Fy += force * (obj.y - body.y) / r


def move_space_object(body, dt):
    if body.type == 'planet' and hasattr(body, 'parent_star'):
        star = body.parent_star
        dx = body.x - star.x
        dy = body.y - star.y
        r = sqrt(dx ** 2 + dy ** 2)

        if r > 0:
            # Определяем направление вращения по четности орбиты
            if body.orbit_number % 2 == 0:  # Четные орбиты
                direction = 1  # По часовой
            else:  # Нечетные орбиты
                direction = -1  # Против часовой

            # Угловая скорость
            omega = sqrt(gravitational_constant * star.m / r ** 3) * direction

            # Обновляем позицию
            angle = atan2(dy, dx) + omega * dt
            body.x = star.x + r * cos(angle)
            body.y = star.y + r * sin(angle)

            # Обновляем скорость
            body.Vx = -r * omega * sin(angle)
            body.Vy = r * omega * cos(angle)
    else:
        # Движение для звезд
        ax = body.Fx / body.m * dt
        ay = body.Fy / body.m * dt
        body.Vx += ax
        body.Vy += ay
        body.x += body.Vx * dt
        body.y += body.Vy * dt


def recalculate_space_objects_positions(space_objects, dt):
    for body in space_objects:
        calculate_force(body, space_objects)
    for body in space_objects:
        move_space_object(body, dt)