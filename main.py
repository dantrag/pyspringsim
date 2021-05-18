#!/usr/bin/python

import sys
import argparse

from geometry import Point
from settings import SimulatorSettings
from simulator import SpringSimulator

from PIL import Image

parser = argparse.ArgumentParser(description = 'Simulator control script',
             formatter_class = argparse.RawDescriptionHelpFormatter,
             epilog = '''\
Example usage:
  python main.py -c init -i mask.png -o initialized.xml
  python main.py -c pass -i state.xml -p 0 0 50 50 100 40 -o newstate.xml
  python main.py -c predict -i mask.png -t target.txt -o moves.txt''')

parser.add_argument('-c', dest = 'command',
                    choices = ['init', 'pass', 'predict'],
                    help = 'command to run')
parser.add_argument('-i', dest = 'input', help = 'input file (PNG or XML)')
parser.add_argument('-p', dest = 'params', help = 'laser pass coordinates',
                    nargs = '+', type = int)
parser.add_argument('-t', dest = 'target',
                    help = 'target file (shape outline XY coordinates)')
parser.add_argument('-s', dest = 'settings', help = 'settings file')
parser.add_argument('-o', dest = 'output',
                    help = 'output file (moves for predict, XML for pass)')

args = parser.parse_args(sys.argv[1:])

if args.command:
    if args.settings:
        settings = SimulatorSettings(args.settings)
        sim = SpringSimulator(settings)
    else:
        sim = SpringSimulator()
        print("Warning: no settings file provided, using default (use -s)")

    if args.input:
        try:
            image = Image.open(args.input)
            pixels = image.load()
            sim.initialize_from_image(image)
        except:
            print("Error: failed reading input file")
            sys.exit()
    else:
        print("Error: no input file provided to initialize from")
        sys.exit()
    
    if args.command == 'pass':
        if args.params:
            count = len(args.params)
            if count < 4:
                print("Error: too few coordinates provided (at least 2 points)")
                sys.exit()
            if count & 1:
                print("Error: odd number of coordinates provided (2 per point)")
                sys.exit()
            points = [Point(x, y) for x, y in zip(args.params[::2],
                                                  args.params[1::2])]
            sim.run_linear_passes(points)
        else:
            print("Error: no coordinates of laser pass provided (use -p)")
            sys.exit()

    if args.output:
        if args.command in ('pass', 'init'):
            # todo: output xml
            pass
        elif args.command == 'predict':
            # todo: output moves
            pass
    if not args.output:
        print("Warning: no output file provided (use -o)")

else:
    print("No command provided (use -c)")
