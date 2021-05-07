from geometry import Point

class Particle:
    def __init__(self, settings, x = 0, y = 0):
        self._x = x
        self._y = y
        self._settings = settings

        self._displacement = Point()
        self._molten = False
        self._melting_timeout = 0
        self._movable = False

        self._springs = []

    def __del__(self):
        for spring in self._springs:
            spring.other_end(self).springs.remove(spring)
            del spring
        self._springs.clear()

    @property
    def point(self):
        return Point(self._x, self._y)

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def radius(self):
        return (self._settings.molten_particle_default_radius if self.molten
                else self._settings.particle_default_radius)

    @property
    def displacement(self):
        return self._displacement

    @displacement.setter
    def displacement(self, vector):
        self._displacement = Point(vector.x, vector.y)

    def apply_displacement(self):
        self._x += self._displacement.x
        self._y += self._displacement.y

    # molten implies larger radius; mobility is set separately
    @property
    def molten(self):
        return self._molten

    @molten.setter
    def molten(self, is_molten):
        self._molten = is_molten
        if not is_molten:
            self.melting_timeout = -1

    @property
    def melting_timeout(self):
        return self._melting_timeout

    @melting_timeout.setter
    def melting_timeout(self, timeout):
        self._melting_timeout = timeout

    # mark that this particle is allowed to relax its new state (move)
    @property
    def movable(self):
        return self._movable

    @movable.setter
    def movable(self, is_movable):
        self._movable = is_movable

    @property
    def springs(self):
        return self._springs

    @property
    def settings(self):
        return self._settings

    @settings.setter
    def settings(self, new_settings):
        self._settings = new_settings

