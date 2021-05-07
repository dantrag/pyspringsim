#!/usr/bin/python

from geometry import Point
from settings import SimulatorSettings
from simulator import SpringSimulator

s = SimulatorSettings('spring5.5_ticks20_spot20.cfg')
sim = SpringSimulator(s)
sim.initialize_circle(Point(0, 0), 50)
sim.run_linear_passes([Point(-60, 0), Point(60, 0)])
for particle in sim.particles:
    print("%.3f %.3f" % (particle.x, particle.y))
