from PIL import Image, ImageOps

from particle import Particle
from spring import Spring
from settings import SimulatorSettings
from geometry import Point, Line, distance, segments_intersect
from math import sqrt
from collections import deque
from itertools import combinations
from functools import cmp_to_key

def _particle_bfs(start, min_depth, max_depth, neighbourhood):
    bfs_queue = deque([start])
    depth = {start: 0}

    while bfs_queue:
        current = bfs_queue.popleft()
        if min_depth <= depth[current] <= max_depth:
            neighbourhood.add(current)
        if depth[current] > max_depth:
            break

        for spring in current.springs:
            following = spring.other_end(current)
            if not following in depth:
                bfs_queue.append(following)
                depth[following] = depth[current] + 1

# check if removal of the spring will create a long cycle (potential void)
# return value is (can_be_removed, if_yes_is_cycle_fixable_by_a_new_spring)
def _spring_can_be_removed(spring, min_cycle_length, max_cycle_length, cycle):
    forbidden_springs = {spring}
    bfs_queue = deque([spring.particle1])
    link_to_previous = {spring.particle1: None}
    depth = {spring.particle1: 0}

    while bfs_queue:
        current = bfs_queue.popleft()
        for adjacent_spring in current.springs:
            following = adjacent_spring.other_end(current)
            if not following in depth:
                bfs_queue.append(following)
                link_to_previous[following] = adjacent_spring
                depth[following] = depth[current] + 1

                if following == spring.particle2 or \
                    depth[following] > max_cycle_length / 2:
                    bfs_queue.clear()
                    break

    if not spring.particle2 in depth:
        # particles became disjointed or too long cycle forms,
        # so removal of the spring is not possible
        return (False, False) 

    current = spring.particle2
    while current != spring.particle1:
        cycle.append(current)
        forbidden_springs.add(link_to_previous[current])
        current = link_to_previous[current].other_end(current)

    cycle.reverse()
    half_cycle_size = depth[spring.particle2]

    bfs_queue.append(spring.particle1)
    link_to_previous = {spring.particle1: None}
    depth = {spring.particle1: 0}

    while bfs_queue:
        current = bfs_queue.popleft()
        for adjacent_spring in current.springs:
            if not adjacent_spring in forbidden_springs:
                following = adjacent_spring.other_end(current)
                if not following in depth:
                    bfs_queue.append(following)
                    link_to_previous[following] = adjacent_spring
                    depth[following] = depth[current] + 1
                    if following == spring.particle2 or \
                        depth[following] + half_cycle_size > \
                        max_cycle_length:
                        bfs_queue.clear()
                        break

    if not spring.particle2 in depth:
        # only one path between the ends of the spring, no cycle formed
        # or (very unlikely) the second path is too long ("a crack forms")
        if half_cycle_size <= max_cycle_length / 2 and \
            spring.elongation > 1.6:
            return (True, False)
        else:
            return (False, False)

    # otherwise we have found a long cycle! but is it minimal?
    current = spring.particle2
    while current != spring.particle1:
        forbidden_springs.add(link_to_previous[current])
        current = link_to_previous[current].other_end(current)
        cycle.append(current)

    # try to shrink the found cycle - there can be at most one edge between
    # two "sides" of the cycle, according to our design where
    # we add 1 edge that might intersect spring

    for i in range(half_cycle_size - 1):
        for j in range(half_cycle_size, len(cycle) - 1):
            for cycle_spring in cycle[i].spring:
                if cycle_spring.other_end(cycle[i]) == cycle[j]:
                    # we can split the cycle
                    sub_cycle_size1 = j - i + 1
                    sub_cycle_size2 = len(cycle) - sub_cycle_size1 + 2
                    if sub_cycle_size1 < min_cycle_length and \
                        sub_cycle_size2 < min_cycle_length:
                        return (True, True)

    if depth[spring.particle2] + half_cycle_size < min_cycle_length:
        return (True, True)
    else:
        return (False, True)

class SpringSimulator:
    def __init__(self, settings = None):
        if settings:
            self._settings = settings
        else:
            self._settings = SimulatorSettings()

        self._time = 0
        self._particles = []
        self._recently_added_springs = set()
        self._recently_removed_springs = set()

    @property
    def settings(self):
        return self._settings

    @settings.setter
    def settings(self, new_settings):
        self._settings = new_settings

    @property
    def time(self):
        return self._time

    def increment_time(self):
        self._time += 1

    @property
    def particles(self):
        return self._particles

    @property
    def recently_added_springs(self):
        return self._recently_added_springs

    @property
    def recently_removed_springs(self):
        return self._recently_removed_springs

    def clear(self):
        pass

    def debug(self):
        for particle in self._particles:
            print("%.3f %.3f" % (particle.x, particle.y))
        print("================")


    def clear_recent(self):
        self._recently_added_springs.clear()
        self._recently_removed_springs.clear()

    def _add_spring(self, p1, p2):
        if p1 and p2:
            for spring in p1.springs:
                if spring.other_end(p1) == p2:
                    return None
            return Spring(p1, p2,
                          self._settings.spring_default_length, self._settings)
        else:
            return None

    def _default_interval(self):
        return self._settings.particle_default_radius * 2 + \
               self._settings.spring_default_length

    def _initialize_field(self, centre, width, height, interval, include_point):
        self.clear()

        x_interval = interval
        y_interval = interval * sqrt(3) / 2
        
        size_x = int((width / 2 - x_interval / 2) / x_interval)
        size_y = int((height / 2 - x_interval / 2) / y_interval)
        if size_x <= 0 or size_y <= 0:
            return False

        grid = [[None] * (2 * size_x + 1) for _ in range(2 * size_y + 1)]

        for i in range(-size_y, size_y + 1):
            for j in range(-size_x, size_x + 1):
                x = centre.x + j * x_interval
                if i & 1:
                    x -= x_interval / 2
                y = centre.y + i * y_interval 
                if include_point(x, y):
                    grid[i + size_y][j + size_x] = Particle(self._settings,
                                                            x, y)

        for i in range(2 * size_y + 1):
            for j in range(2 * size_x + 1):
                if grid[i][j]:
                    if j > 0:
                        self._add_spring(grid[i][j], grid[i][j - 1])
                    if i > 0:
                        self._add_spring(grid[i][j], grid[i - 1][j])
                        if (i - size_y) & 1:
                            if j > 0:
                                self._add_spring(grid[i][j], grid[i - 1][j - 1])
                        else:
                            if j < 2 * size_x:
                                self._add_spring(grid[i][j], grid[i - 1][j + 1])
                    self._particles.append(grid[i][j])

    def initialize_circle(self, centre, radius):
        interval = self._default_interval()
        self._initialize_field(
            centre, radius * 2, radius * 2, interval, lambda x, y:
            distance(Point(x, y), centre) + interval / 2 <= radius + 1e-5)
        self.debug()

    def initialize_from_image(self, image, scale = 1.0):
        image = image.convert("L")
        interval = self._default_interval()
        width = image.width * scale
        height = image.height * scale
        pixels = image.load()
        if pixels[0,0]:
            image = ImageOps.invert(image)
            pixels = image.load()

        self._initialize_field(Point(width * scale / 2, height * scale / 2),
                               width * scale, height * scale, interval,
                               lambda x, y : pixels[x, y])
        self.debug()

    def run_pass(self, start, finish):
        length = distance(start, finish)
        ticks = int(length / self._settings.heater_speed) + 1
        speed = self._settings.heater_speed
        size = self._settings.heater_size
        cooldown_time = self._settings.molten_particle_cooldown_time
        for i in range(ticks):
            x = start.x + (finish.x - start.x) / length * speed * i
            y = start.y + (finish.y - start.y) / length * speed * i
            heater_position = Point(x, y)

            # cool timed out particles
            for particle in self._particles:
                if 0 < particle.melting_timeout <= self._time:
                    particle.molten = False
                    particle.movable = True

            # heat around x, y
            for particle in self._particles:
                if distance(heater_position, particle.point) <= size:
                    particle.molten = True
                    particle.melting_timeout = self._time + cooldown_time
                    particle.movable = True

            for particle in self._particles:
                for spring in particle.springs:
                    spring.update_force()

            self.relax_heat()

            for particle in self._particles:
                if not particle.molten:
                    particle.movable = False

            self.increment_time()

    def run_linear_passes(self, points):
        for start, finish in zip(points, points[1:]):
            self.run_pass(start, finish)

        # after-pass cooldown
        for particle in self._particles:
            if particle.molten:
                particle.molten = False
                particle.movable = True

        for particle in self._particles:
            for spring in particle.springs:
                spring.update_force()

        self.relax_heat()
        self.debug()

    def relax_heat(self):
        iteration_count = 0

        movable_particles = []
        for particle in self._particles:
            if particle.movable:
                movable_particles.append(particle)

        #print("%d movable" % len(movable_particles))
        while iteration_count < self._settings.relaxation_iteration_limit:
            max_displacement = 0
            for particle in movable_particles:
                x_displacement = 0
                y_displacement = 0
                max_allowable_move = self._settings.spring_default_length / 4
                neighbours = set()

                for spring in particle.springs:
                    delta_x = spring.other_end(particle).x - particle.x
                    delta_y = spring.other_end(particle).y - particle.y
                    if spring.force > 0:
                        delta_x = -delta_x
                        delta_y = -delta_y
                    delta_length = sqrt(delta_x * delta_x + delta_y * delta_y)
                    # make sure not to divide by a zero value
                    if delta_length < 1e-5:
                        continue
                    delta_x /= delta_length
                    delta_y /= delta_length
                    delta_x *= abs(spring.force)
                    delta_y *= abs(spring.force)
                    x_displacement += delta_x
                    y_displacement += delta_y

                    max_allowable_move = min(max_allowable_move,
                                             spring.actual_length / 4)
                    neighbours.add(spring.other_end(particle))

                checked_neighbours = set()
                for neighbour in neighbours:
                    checked_neighbours.add(neighbour)
                    for neighbour_spring in neighbour.springs:
                        neighbour2 = neighbour_spring.other_end(neighbour)
                        if neighbour2 in neighbours and \
                           not neighbour2 in checked_neighbours:
                            separation = particle.point.distance_to_line(
                                Line(neighbour, neighbour2))
                            max_allowable_move = min(max_allowable_move,
                                                     separation / 2)

                particle_move = sqrt(x_displacement * x_displacement +
                                     y_displacement * y_displacement)
                if particle_move > max_allowable_move:
                    scale_factor = particle_move / max_allowable_move
                    x_displacement /= scale_factor
                    y_displacement /= scale_factor
                    particle_move = sqrt(x_displacement * x_displacement +
                                         y_displacement * y_displacement)
                max_displacement = max(max_displacement, particle_move)
                particle.displacement = Point(x_displacement, y_displacement)

            for particle in movable_particles:
                particle.apply_displacement()

            min_cycle_length = 4
            max_cycle_length = 4

            # delete too long springs
            if iteration_count % 50 == 0:
                springs = [s for s in particle.springs
                             for particle in movable_particles
                             if s.elongation >
                                self._settings.spring_disconnection_threshold]

                #for particle in movable_particles:
                #    for spring in particle.springs:
                #        if spring.elongation >
                #           self._settings.spring_disconnection_threshold:
                #            springs.append(spring)

                def compare_spring_elongation(spring1, spring2):
                    return spring1.elongation > spring2.elongation

                springs.sort(key = cmp_to_key(compare_spring_elongation))

                for spring in springs:
                    # check if spring removal creates any leaves/isolated nodes
                    if len(spring.particle1.springs) <= 2 or \
                       len(spring.particle2.springs) <= 2:
                        continue

                    # check if spring removal creates any long cycles (voids)
                    cycle = []
                    can_remove, can_fix = _spring_can_be_removed(
                        spring, min_cycle_length, max_cycle_length, cycle)
                    if (not can_remove and can_fix):
                        # if a long cycle is created, can it be fixed
                        # with a shorter spring?
                        new_spring = None
                        for p1, p2 in combinations(cycle, 2):
                            if {p1, p2} == {spring.particle1, spring.particle2}:
                                continue
                            new_spring = self._add_spring(p1, p2)
                            if not new_spring:
                                continue

                            if new_spring.elongation < spring.elongation and \
                               _spring_can_be_removed(spring, min_cycle_length,
                                                      max_cycle_length, []):
                                # can eliminate the formed long cycle with
                                # a shorter spring, keep it
                                self._recently_added_springs.add(new_spring)
                                break
                            else:
                                p1.springs.remove(new_spring)
                                p2.springs.remove(new_spring)

                        if new_spring:
                            can_remove = True

                    if can_remove:
                        spring.particle1.springs.remove(spring)
                        spring.particle2.springs.remove(spring)
                        if spring in self._recently_added_springs:
                            self._recently_added_springs.remove(spring)
                        else:
                            self._recently_removed_springs.add(spring)

            # create new springs between close particles, but make sure
            # there are no overlaps
            if iteration_count % 50 == 0:
                for particle in movable_particles:
                    new_partners = set()
                    _particle_bfs(particle, 2, max_cycle_length, new_partners)
                    neighbourhood = new_partners.copy()
                    _particle_bfs(particle, 1, 1, neighbourhood)

                    for partner in new_partners:
                        if distance(particle.point, partner.point) - \
                           particle.radius - partner.radius < \
                           self._settings.spring_default_length * \
                           self._settings.spring_connection_threshold:
                            # check if new spring will intersect with some other
                            intersect = False
                            for other_particle in neighbourhood:
                                if other_particle == partner:
                                    continue
                                for spring in other_particle.springs:
                                    if spring.other_end(other_particle) in \
                                       {particle, partner}:
                                       continue

                                    # check intersection
                                    if segments_intersect(
                                        particle.point, partner.point,
                                        other_particle.point,
                                        spring.other_end(other_particle).point):
                                            intersect = True
                                            break

                                if intersect:
                                    break

                            if not intersect:
                                spring = self._add_spring(particle, partner)
                                if spring:
                                    self._recently_added_springs.add(spring)

            for particle in movable_particles:
                for spring in particle.springs:
                    spring.update_force()

            iteration_count += 1

            if max_displacement < self._settings.relaxation_convergence_limit:
                break

        for particle in movable_particles:
            if not particle.molten:
                particle.movable = False

        #print("%d steps" % iteration_count)

    def to_shape(self):
        # return shape
        pass

