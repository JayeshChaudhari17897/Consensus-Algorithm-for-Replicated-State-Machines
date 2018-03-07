# coding=utf-8
# -*- coding: utf-8 -*-


from random import shuffle
import sys
from base64 import b64encode
from time import localtime, strftime, sleep

from bokeh.io import curdoc
from bokeh.layouts import layout, widgetbox, row
from bokeh.plotting import figure
import bokeh.palettes
from bokeh.models import (
    FixedTicker, Button, ColumnDataSource, PanTool, Scroll,
    RadioButtonGroup, RadioGroup, Arrow, NormalHead, HoverTool, Dimensions)
from pro650_nacl.signing import SigningKey
from bokeh.palettes import plasma, small_palettes
from bfs import bfs
from dfs import dfs
from random_generator import  randrange
import Node


R_COLORS = small_palettes['Greens'][9]
shuffle(R_COLORS)
def round_color(r):
    return R_COLORS[r % 9]

I_COLORS = plasma(256)
def idx_color(r):
    return I_COLORS[r % 256]


class App:
    def __init__(self, no_of_nodes):
        self.i = 0
        signing_keys = [SigningKey.generate() for _ in range(no_of_nodes)]
        stake_of_this_node = {signing_key.verify_key: 1 for signing_key in signing_keys}

        network = {}
        self.nodes = [Node.Node(signing_key, network, no_of_nodes, stake_of_this_node) for signing_key in signing_keys]
        for n in self.nodes:
            network[n.id] = n.ask_sync
        self.ids = {signing_key.verify_key: i for i, signing_key in enumerate(signing_keys)}

        self.main_its = [n.main() for n in self.nodes]
        for m in self.main_its:
            next(m)

        def toggle():
            if play.label == '► Play':
                play.label = '❚❚ Pause'
                curdoc().add_periodic_callback(self.animate, 50)
            else:
                play.label = '► Play'
                curdoc().remove_periodic_callback(self.animate)

        play = Button(label='► Play', width=60)
        play.on_click(toggle)

        def sel_node(new):
            self.active = new
            node = self.nodes[new]
            self.rounds_to_be_decided = {}
            self.tr_src.data, self.links_src.data = self.extract_data(
                    node, bfs((node.head,), lambda u: node.hashgraph[u].parents), 0)
            for u, j in tuple(self.rounds_to_be_decided.items()):
                self.tr_src.data['line_alpha'][j] = 1 if node.famous.get(u) else 0
                if u in node.idx:
                    self.tr_src.data['round_color'][j] = idx_color(node.idx[u])
                self.tr_src.data['idx'][j] = node.idx.get(u)
                if u in node.idx and u in node.famous:
                    del self.rounds_to_be_decided[u]
                    print('updated')
            self.tr_src.trigger('data', None, self.tr_src.data)

        selector = RadioButtonGroup(
                labels=['Node %i' % i for i in range(no_of_nodes)], active=0,
                name='Node to inspect')
        selector.on_click(sel_node)

        plot = figure(
                plot_height=700, plot_width=900, y_range=(0, 30),
                tools=[PanTool(dimensions=Dimensions.height),
                       HoverTool(tooltips=[
                           ('round_nos_of_all_events', '@round_nos_of_all_events'), ('hash', '@hash'),
                           ('timestamp', '@time'), ('payload', '@payload'),
                           ('number', '@idx')])])
        plot.xgrid.grid_line_color = None
        plot.xaxis.minor_tick_line_color = None
        plot.ygrid.grid_line_color = None
        plot.yaxis.minor_tick_line_color = None

        self.links_src = ColumnDataSource(data={'x0': [], 'y0': [], 'x1': [],
                                                'y1': [], 'width': []})
        #self.links_rend = plot.add_layout(
        #        Arrow(end=NormalHead(fill_color='black'), x_start='x0', y_start='y0', x_end='x1',
        #        y_end='y1', source=self.links_src))
        self.links_rend = plot.segment(color='#777777',
                x0='x0', y0='y0', x1='x1',
                y1='y1', source=self.links_src, line_width='width')

        self.tr_src = ColumnDataSource(
                data={'x': [], 'y': [], 'round_color': [], 'idx': [],
                    'line_alpha': [], 'round_nos_of_all_events': [], 'hash': [], 'payload': [],
                    'time': []})

        self.tr_rend = plot.circle(x='x', y='y', size=20, color='round_color',
                                   line_alpha='line_alpha', source=self.tr_src, line_width=5)

        sel_node(0)
        curdoc().add_root(row([widgetbox(play, selector, width=300), plot], sizing_mode='fixed'))

    def extract_data(self, node, trs, i):
        tr_data = {'x': [], 'y': [], 'round_color': [], 'idx': [],
                'line_alpha': [], 'round_nos_of_all_events': [], 'hash': [], 'payload': [],
                'time': []}
        links_data = {'x0': [], 'y0': [], 'x1': [], 'y1': [], 'width': []}
        for j, u in enumerate(trs):
            self.rounds_to_be_decided[u] = i + j
            ev = node.hashgraph[u]
            x = self.ids[ev.verify_key]
            y = node.height[u]
            tr_data['x'].append(x)
            tr_data['y'].append(y)
            tr_data['round_color'].append(round_color(node.round_nos_of_all_events[u]))
            tr_data['round_nos_of_all_events'].append(node.round_nos_of_all_events[u])
            tr_data['hash'].append(b64encode(u).decode('utf8'))
            tr_data['payload'].append(ev.d)
            tr_data['time'].append(str(ev.t))  # ev.t.strftime("%Y-%m-%d %H:%M:%S"))

            tr_data['idx'].append(None)
            tr_data['line_alpha'].append(None)

            if ev.parents:
                links_data['x0'].extend((x, x))
                links_data['y0'].extend((y, y))
                links_data['x1'].append(self.ids[node.hashgraph[ev.parents[0]].verify_key])
                links_data['x1'].append(self.ids[node.hashgraph[ev.parents[1]].verify_key])
                links_data['y1'].append(node.height[ev.parents[0]])
                links_data['y1'].append(node.height[ev.parents[1]])
                links_data['width'].extend((3, 1))

        return tr_data, links_data

    def animate(self):
        r = randrange(len(self.main_its))
        print('working node: %i, event number: %i' % (r, self.i))
        self.i += 1
        new = next(self.main_its[r])
        if r == self.active:
            tr, links = self.extract_data(self.nodes[r], new, len(self.tr_src.data['x']))
            self.tr_src.stream(tr)
            self.links_src.stream(links)
            for u, j in tuple(self.rounds_to_be_decided.items()):
                self.tr_src.data['line_alpha'][j] = 1 if self.nodes[r].famous.get(u) else 0
                if u in self.nodes[r].idx:
                    self.tr_src.data['round_color'][j] = idx_color(self.nodes[r].idx[u])
                self.tr_src.data['idx'][j] = self.nodes[r].idx.get(u)
                if u in self.nodes[r].idx and u in self.nodes[r].famous:
                    del self.rounds_to_be_decided[u]
                    print('updated')
            self.tr_src.trigger('data', None, self.tr_src.data)


App(int(sys.argv[1]))