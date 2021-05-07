from geometry import distance

class Spring:
    def __init__(self, p1, p2, length, settings):
        self._p1 = p1
        self._p2 = p2
        self._length = length
        self._settings = settings

        self._p1.springs.append(self)
        self._p2.springs.append(self)

        self._force = 0

    @property
    def particle1(self):
        return self._p1

    @property
    def particle2(self):
        return self._p2

    @property
    def settings(self):
        return self._settings

    @settings.setter
    def settings(self, new_settings):
        self._settings = new_settings

    @property
    def length(self):
        return self._length

    @property
    def actual_length(self):
        return distance(self._p1, self._p2) - self._p1.radius - self._p2.radius

    @property
    def elongation(self):
        return self.actual_length / self.length

    @property
    def force(self):
        return self._force

    def update_force(self):
        if self.actual_length < self.length:
            self._force = (1 / self.actual_length - 1 / self.length) * \
                          self._settings.spring_default_stiffness * \
                          self.length * self.length / 2
        else:
            self._force = self._settings.spring_default_stiffness * \
                          (self.length - self.actual_length)

    def other_end(self, particle):
        if self._p1 == particle:
            return self._p2
        elif self._p2 == particle:
            return self._p1
        else:
            return None

