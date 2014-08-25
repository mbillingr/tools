#!/bin/env python3

import xml.etree.ElementTree as ET
import sys


target_opacities = {'alpha {}'.format(a): a for a in [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]}


target_gradients = {'white-black': {'type': 'axial', 'extend': 'yes', 'coords': [0, 0, 128, 0],
                                    'stops': [{'offset': 0, 'color': [1, 1, 1]},
                                              {'offset': 1, 'color': [0, 0, 0]}]},
                    'red-black':   {'type': 'axial', 'extend': 'yes', 'coords': [0, 0, 128, 0],
                                    'stops': [{'offset': 0, 'color': [1, 0, 0]},
                                              {'offset': 1, 'color': [0, 0, 0]}]},
                    'green-black': {'type': 'axial', 'extend': 'yes', 'coords': [0, 0, 128, 0],
                                    'stops': [{'offset': 0, 'color': [0, 1, 0]},
                                              {'offset': 1, 'color': [0, 0, 0]}]},
                    'blue-black':  {'type': 'axial', 'extend': 'yes', 'coords': [0, 0, 128, 0],
                                    'stops': [{'offset': 0, 'color': [0, 0, 1]},
                                              {'offset': 1, 'color': [0, 0, 0]}]},
                    'cyan-black':  {'type': 'axial', 'extend': 'yes', 'coords': [0, 0, 128, 0],
                                    'stops': [{'offset': 0, 'color': [0, 1, 1]},
                                              {'offset': 1, 'color': [0, 0, 0]}]},
                    'magent-black':{'type': 'axial', 'extend': 'yes', 'coords': [0, 0, 128, 0],
                                    'stops': [{'offset': 0, 'color': [1, 0, 1]},
                                              {'offset': 1, 'color': [0, 0, 0]}]},
                    'yellow-black':{'type': 'axial', 'extend': 'yes', 'coords': [0, 0, 128, 0],
                                    'stops': [{'offset': 0, 'color': [1, 1, 0]},
                                              {'offset': 1, 'color': [0, 0, 0]}]},
                    'red-white':   {'type': 'axial', 'extend': 'yes', 'coords': [0, 0, 128, 0],
                                    'stops': [{'offset': 0, 'color': [1, 0, 0]},
                                              {'offset': 1, 'color': [1, 1, 1]}]},
                    'green-white': {'type': 'axial', 'extend': 'yes', 'coords': [0, 0, 128, 0],
                                    'stops': [{'offset': 0, 'color': [0, 1, 0]},
                                              {'offset': 1, 'color': [1, 1, 1]}]},
                    'blue-white':  {'type': 'axial', 'extend': 'yes', 'coords': [0, 0, 128, 0],
                                    'stops': [{'offset': 0, 'color': [0, 0, 1]},
                                              {'offset': 1, 'color': [1, 1, 1]}]},
                    'cyan-white':  {'type': 'axial', 'extend': 'yes', 'coords': [0, 0, 128, 0],
                                    'stops': [{'offset': 0, 'color': [0, 1, 1]},
                                              {'offset': 1, 'color': [1, 1, 1]}]},
                    'magent-white':{'type': 'axial', 'extend': 'yes', 'coords': [0, 0, 128, 0],
                                    'stops': [{'offset': 0, 'color': [1, 0, 1]},
                                              {'offset': 1, 'color': [1, 1, 1]}]},
                    'yellow-white':{'type': 'axial', 'extend': 'yes', 'coords': [0, 0, 128, 0],
                                    'stops': [{'offset': 0, 'color': [1, 1, 0]},
                                              {'offset': 1, 'color': [1, 1, 1]}]}}


def str2list(s, type=int, sep=' '):
    return [type(i) for i in s.split(sep)]


def list2str(l, sep=' '):
    return sep.join([str(i) for i in l])


def parse_opacities(style):
    opacities = {}
    for o in style.findall('opacity'):
        opacities[o.attrib['name']] = float(o.attrib['value'])
    return opacities


def update_opacities(style, opacities):
    for o in style.findall('opacity'):
        if o.attrib['name'] in opacities:
            style.remove(o)
    for o, v in opacities.items():
        attrib = {'name': o, 'value': str(v)}
        new_el =ET.Element('opacity', attrib)
        style.append(new_el)


def parse_gradients(style):
    gradients = {}
    for g in style.findall('gradient'):

        stops = []
        for s in g.findall('stop'):
            stop = {'offset': float(s.attrib['offset']),
                    'color': str2list(s.attrib['color'], float)}
            stops.append(stop)

        gradients[g.attrib['name']] = {'type': g.attrib['type'],
                                       'coords': str2list(g.attrib['coords']),
                                       'stops': stops}
    return gradients


def update_gradients(style, gradients):
    for g in style.findall('gradient'):
        if g.attrib['name'] in gradients:
            style.remove(g)
    for g, v in gradients.items():
        attrib = {'name': g, 'type': v['type'], 'coords': list2str(v['coords'])}
        new_el =ET.Element('gradient', attrib)
        for s in v['stops']:
            new_el.append(ET.Element('stop', {'offset': str(s['offset']),
                                              'color': list2str(s['color'])}))
        style.append(new_el)


def update_dict(original, target, info=''):
    all_skipped = True
    for k, v in target.items():
        if k not in original:
            print('adding', info, k)
            original[k] = v
            all_skipped &= False
        elif overwrite:
            print('updating', info, k)
            original[k] = v
            all_skipped &= False
        else:
            print('skipping', info, k)
    return not all_skipped


if '--help' in sys.argv or not 2 <= len(sys.argv) <= 4:
    print('''Usage: ipe++ <inputfile> [outputfile] [options]

Options:
  --help        show this help
  --overwrite   overwrite existing tags

  If no outputfile is provided the input file will be overwritten!
''')
    exit()

overwrite = '--overwrite' in sys.argv

try:
    sys.argv.remove('--overwrite')
except ValueError:
    pass

infile = sys.argv[1]
outfile = sys.argv[2]

tree = ET.parse(infile)

ipe = tree.getroot()
style = ipe.findall('ipestyle')

if len(style) != 1:
    raise ValueError('Found {} <ipestyle> elements, but exepected exactly one.')
style = style[0]

ipe_gradients = parse_gradients(style)
ipe_opacities = parse_opacities(style)

op_changed = update_dict(ipe_opacities, target_opacities, 'opacity')
gr_changed = update_dict(ipe_gradients, target_gradients, 'gradient')

if not op_changed and not gr_changed:
    print('nothing to do')
    if outfile == infile:
        exit()
else:
    if op_changed:
        update_opacities(style, ipe_opacities)
    if gr_changed:
        update_gradients(style, ipe_gradients)

tree.write(outfile)