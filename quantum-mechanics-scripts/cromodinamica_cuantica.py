"""Color and flavor: an animated tour of quarks, gluons and the weak interaction.

Run: python cromodinamica_cuantica.py
Preview: python cromodinamica_cuantica.py --scene colors --time 2 --save qcd.png
Requires numpy and matplotlib. Educational illustration, not a numerical QCD calculation.
Sources and scope: LEEME_cromodinamica_cuantica.md in this folder.
"""
import argparse
from math import pi
from time import perf_counter

import numpy as np


BG = '#0b1220'
PANEL = '#121f31'
INK = '#edf4ff'
MUTED = '#9aacbf'
ACCENT = '#67e8d3'
GOLD = '#ffda85'
COLORS = ('#ff667f', '#5adea0', '#63adff')
COLOR_NAMES = ('red', 'green', 'blue')
COLOR_CODES = ('R', 'G', 'B')
FLAVORS = (
    ('u', 'up', 1, '+2/3', 'Together with down, forms the\nvalence quarks of protons\nand neutrons.'),
    ('d', 'down', 1, '−1/3', 'Can change into up in\nneutron beta decay.'),
    ('c', 'charm', 2, '+2/3', 'Found in D mesons and\ncharmonium (charm–anticharm).'),
    ('s', 'strange', 2, '−1/3', 'Found in kaons and baryons\nsuch as the lambda (uds).'),
    ('t', 'top', 3, '+2/3', 'Decays before forming hadrons.\nIts main decay is t → W⁺ + b.'),
    ('b', 'bottom', 3, '−1/3', 'Bottom hadrons let us study\nflavor mixing and CP violation.'),
)
SCENE_NAMES = ('colors', 'flavors', 'weak')
SCENE_ALIASES = dict(zip(('colores', 'sabores', 'debil'), SCENE_NAMES))
SCENE_DURATIONS = (30., 24., 16.)


def smooth(value):
    value = np.clip(value, 0., 1.)
    return value*value*(3-2*value)


def exchange_cases():
    """Six exchanges: each case starts where the previous one ended."""
    colors = [0, 1, 2]
    cases = []
    for source, target in [(0, 1), (1, 2), (2, 0)]*2:
        before = tuple(colors)
        colors[source], colors[target] = colors[target], colors[source]
        cases.append((source, target, before, tuple(colors)))
    return tuple(cases)


EXCHANGES = exchange_cases()


def color_exchange(seconds):
    """Color flow in a basis: g carries A anti-B, with formal charge e_A-e_B."""
    position = (seconds % SCENE_DURATIONS[0])/5.
    index = int(position)
    phase = position-index
    source, target, before, after = EXCHANGES[index]
    colors = list(before)
    if phase >= .18:
        colors[source] = before[target]
    if phase >= .72:
        colors[target] = before[source]
    return dict(index=index, phase=phase, source=source, target=target,
                before=before, after=after, colors=tuple(colors),
                flying=.18 <= phase < .72,
                travel=float(smooth((phase-.18)/.54)))


def beta_state(seconds):
    phase = (seconds % SCENE_DURATIONS[2])/SCENE_DURATIONS[2]
    # Electric charges in units of e; the virtual W carries -1 before the leptons.
    changed = phase >= .23
    return dict(phase=phase, changed=changed, w_visible=.23 <= phase < .57,
                leptons_visible=phase >= .57, hadron_charge=int(changed),
                w_charge=-int(.23 <= phase < .57), electron_charge=-int(phase >= .57))


class Scene:
    """Fixed artists are updated in place so a frame never rebuilds the figure."""

    def __init__(self, ax):
        self.ax = ax
        self.items = []
        self.moving = []
        self.revision = None

    def text(self, x, y, text, size=12, color=INK, **kwargs):
        item = self.ax.text(x, y, text, fontsize=size, color=color, **kwargs)
        self.items.append(item)
        return item

    def patch(self, item):
        self.ax.add_patch(item)
        self.items.append(item)
        return item

    def line(self, x, y, **kwargs):
        item, = self.ax.plot(x, y, **kwargs)
        self.items.append(item)
        return item

    def show(self, visible):
        for item in self.items:
            item.set_visible(visible)


class Particle:
    def __init__(self, scene, position, symbol, color, radius=.43):
        from matplotlib.patches import Circle
        self.radius = radius
        self.glows = [scene.patch(Circle(position, radius*factor, facecolor=color,
                                        edgecolor='none', alpha=alpha, zorder=4))
                      for factor, alpha in [(1.6, .045), (1.28, .09)]]
        self.disk = scene.patch(Circle(position, radius, facecolor=PANEL,
                                       edgecolor=color, linewidth=3, zorder=5))
        self.symbol = scene.text(*position, symbol, 25, color, ha='center', va='center',
                                  fontweight='bold', zorder=6)
        self.caption = scene.text(position[0], position[1]-radius-.24, '', 11,
                                   ha='center', va='top', zorder=6)
        self.set(position, symbol, color)

    def set(self, position, symbol, color, caption='', pulse=0.):
        for i, glow in enumerate(self.glows):
            glow.center = position
            glow.set_facecolor(color)
            glow.set_alpha((.045, .09)[i]*(1+.4*pulse))
        self.disk.center = position
        self.disk.set_edgecolor(color)
        self.symbol.set_position(position)
        self.symbol.set_text(symbol)
        self.symbol.set_color(color)
        self.caption.set_position((position[0], position[1]-self.radius-.24))
        self.caption.set_text(caption)

    def visible(self, value):
        for item in self.artists():
            item.set_visible(value)

    def artists(self):
        return [*self.glows, self.disk, self.symbol, self.caption]


class ColorScene(Scene):
    def __init__(self, ax):
        super().__init__(ax)
        from matplotlib.patches import Ellipse, Wedge
        self.text(5, 6.85, 'PROTON  ·  VALENCE QUARKS uud', 15,
                  ha='center', fontweight='bold')
        self.patch(Ellipse((5, 3.72), 8.9, 5.1, facecolor=PANEL,
                           edgecolor='#28415b', linewidth=1.4, linestyle='--'))
        self.positions = np.array([[2.25, 4.65], [7.75, 4.65], [5., 2.1]])
        for p in self.positions:
            self.line([5, p[0]], [3.6, p[1]], color='#2a415c', linewidth=2)
        self.particles = [Particle(self, p, symbol, COLORS[i])
                          for i, (p, symbol) in enumerate(zip(self.positions, ('u', 'u', 'd')))]
        self.wave1 = self.line([], [], color=COLORS[0], lw=2, alpha=.85, zorder=3)
        self.wave2 = self.line([], [], color=COLORS[1], lw=2, alpha=.55, zorder=3)
        self.gluon_halves = [self.patch(Wedge((5, 5), .23, 90, 270, zorder=7)),
                             self.patch(Wedge((5, 5), .23, -90, 90, zorder=7))]
        self.gluon_text = self.text(5, 5.5, '', 12, GOLD, ha='center', zorder=8)
        self.step = self.text(5, .75, '', 13, ACCENT, ha='center')
        self.text(5, .23, 'Color ≠ flavor ≠ electric charge', 12, MUTED, ha='center')
        self.moving = [self.wave1, self.wave2, *self.gluon_halves, self.gluon_text,
                       *(a for particle in self.particles for a in particle.artists())]

    def render(self, seconds):
        state = color_exchange(seconds)
        source, target = state['source'], state['target']
        old, new = state['before'][source], state['before'][target]
        a, b = self.positions[source], self.positions[target]
        direction = b-a
        normal = np.array([-direction[1], direction[0]])/np.linalg.norm(direction)
        t = np.linspace(0., 1., 160)
        arch = a+t[:, None]*direction+.50*np.sin(pi*t)[:, None]*normal
        wave = .055*np.sin(18*pi*t-seconds*5)*np.sin(pi*t)
        for line, sign, color in [(self.wave1, 1, old), (self.wave2, -1, new)]:
            points = arch+sign*wave[:, None]*normal
            line.set_data(points[:, 0], points[:, 1])
            line.set_color(COLORS[color])
            line.set_visible(state['flying'])
        travel = state['travel']
        location = a+travel*direction+.50*np.sin(pi*travel)*normal
        for half, color in zip(self.gluon_halves, (old, new)):
            half.set_center(location)
            half.set_facecolor(COLORS[color])
            half.set_visible(state['flying'])
        self.gluon_text.set_position((location[0], location[1]+.52))
        self.gluon_text.set_text(f'g: {COLOR_CODES[old]} + anti-{COLOR_CODES[new]}')
        self.gluon_text.set_visible(state['flying'])
        for i, (particle, color) in enumerate(zip(self.particles, state['colors'])):
            particle.set(self.positions[i], ('u', 'u', 'd')[i], COLORS[color],
                         f'{COLOR_NAMES[color]} · {("+2/3", "+2/3", "−1/3")[i]} e',
                         .5+.5*np.sin(seconds*3))
        if state['phase'] < .18:
            step = '01  /  Before the exchange'
            explanation = 'Quarks have color, flavor\nand electric charge.\nHere the flavors are u, u, d.'
        elif state['flying']:
            step = '02  /  Emission: the gluon carries color'
            explanation = (f'The emitter changes from {COLOR_NAMES[old]}\nto {COLOR_NAMES[new]}. The gluon carries\n'
                           f'{COLOR_NAMES[old]} and anti-{COLOR_NAMES[new]}.')
        else:
            step = '03  /  Absorption: the colors have been exchanged'
            explanation = (f'The receiver changes from {COLOR_NAMES[new]}\nto {COLOR_NAMES[old]}. Flavors and\n'
                           'electric charges stay the same.')
        self.step.set_text(step)
        self.revision = (state['index'], 0 if state['phase'] < .18 else 1 if state['flying'] else 2)
        return dict(kicker='01 / STRONG INTERACTION', title='Exchanging color',
                    body=explanation,
                    equation=(f'q({COLOR_CODES[old]}) → q({COLOR_CODES[new]}) + g\n'
                              f'g = {COLOR_CODES[old]} anti-{COLOR_CODES[new]}\n'
                              f'q({COLOR_CODES[new]}) + g → q({COLOR_CODES[old]})'),
                    detail='8 gluon color states in QCD:\n6 off-diagonal color pairs\nand 2 diagonal combinations.\n\nGluons also interact with\neach other: they carry color.',
                    takeaway='Color changes.\nFlavor is preserved.',
                    note='A color-flow illustration: the true singlet is a superposition. The exchanged gluon also carries color.')


class FlavorScene(Scene):
    def __init__(self, ax):
        super().__init__(ax)
        from matplotlib.patches import FancyBboxPatch, Circle
        self.text(5, 6.85, 'EXPLORING THE SIX FLAVORS', 15, ha='center', fontweight='bold')
        self.cards, self.dots = [], []
        for generation in range(3):
            self.text(1.7+generation*3.3, 6.22, f'GENERATION {generation+1}', 11,
                      MUTED, ha='center')
        for i, (symbol, name, generation, charge, _) in enumerate(FLAVORS):
            x, y = .3+(generation-1)*3.3, (3.72 if i % 2 == 0 else .97)
            self.cards.append(self.patch(FancyBboxPatch((x, y), 2.8, 2.25,
                               boxstyle='round,pad=0.02,rounding_size=0.16',
                               facecolor=PANEL, edgecolor='#2b4159', lw=1.5)))
            self.text(x+.35, y+1.50, symbol, 34, fontweight='bold')
            self.text(x+1.35, y+1.70, name, 14)
            self.text(x+1.35, y+1.24, f'{charge} e', 12, MUTED)
            dots = []
            for c in range(3):
                dots.append(self.patch(Circle((x+.5+c*.88, y+.52), .15,
                                               facecolor=COLORS[c], edgecolor=COLORS[c], lw=1)))
                self.text(x+.5+c*.88, y+.14, COLOR_CODES[c], 9, MUTED, ha='center')
            self.dots.append(dots)
        self.text(5, .35, 'Every flavor can carry red, green or blue.', 13, ACCENT, ha='center')
        self.moving = [dot for dots in self.dots for dot in dots]

    def render(self, seconds):
        index = int(seconds/4) % 6
        self.revision = index
        symbol, name, generation, charge, description = FLAVORS[index]
        for i, card in enumerate(self.cards):
            card.set_edgecolor(ACCENT if i == index else '#2b4159')
            card.set_linewidth(2.8 if i == index else 1.3)
            card.set_facecolor('#193344' if i == index else PANEL)
            for c, dot in enumerate(self.dots[i]):
                dot.set_radius(.15+(.035*(.5+.5*np.sin(seconds*3-c*2)) if i == index else 0))
        return dict(kicker=f'02 / FLAVORS · GENERATION {generation}',
                    title=f'{symbol}  /  {name}', body=description,
                    equation=f'Electric charge: {charge} e\nPossible colors: R, G, B\nFlavor: {name}',
                    detail='Color and flavor are distinct.\nEach flavor has three colors.\nAntiquarks: opposite electric\ncharge and anticolors.\nThe weak interaction mixes\nflavors (the CKM matrix).',
                    takeaway='A gluon does not turn\nan up into a down.',
                    note='The highlighted cards explore quark types; they do not depict spontaneous changes of flavor.')


class WeakScene(Scene):
    def __init__(self, ax):
        super().__init__(ax)
        from matplotlib.patches import Ellipse
        self.text(5, 6.85, 'FLAVOR CHANGE  ·  BETA DECAY', 15,
                  ha='center', fontweight='bold')
        self.patch(Ellipse((2.15, 4.0), 3.65, 3.75, facecolor=PANEL,
                           edgecolor='#2b4159', linewidth=1.5, linestyle='--'))
        self.positions = [(1.35, 4.55), (2.85, 4.8), (2.7, 3.22)]
        self.quarks = [Particle(self, p, s, COLORS[i], .36)
                       for i, (p, s) in enumerate(zip(self.positions, ('u', 'd', 'd')))]
        self.hadron = self.text(2.15, 1.64, '', 15, ha='center', fontweight='bold')
        self.link = self.line([3.16, 5.6], [3.22, 3.6], color=GOLD, lw=1.6, linestyle='--')
        self.w = Particle(self, (4.5, 3.4), r'$W^-$', GOLD, .32)
        self.electron = Particle(self, (7.5, 4.8), r'$e^-$', '#e5b9ff', .31)
        self.neutrino = Particle(self, (7.5, 2.2), r'$\bar{\nu}_e$', '#b8c9dc', .31)
        self.lepton_lines = [self.line([], [], color=c, lw=1.4, alpha=.55)
                             for c in ('#e5b9ff', '#b8c9dc')]
        self.caption = self.text(5, .72, '', 13, ACCENT, ha='center')
        self.text(5, .20, r'$n\,(udd)\ \longrightarrow\ p\,(uud) + e^- + \bar{\nu}_e$',
                  16, ha='center')
        self.moving = [self.link, *self.w.artists(), *self.electron.artists(),
                       *self.neutrino.artists(), *self.lepton_lines,
                       *(a for particle in self.quarks for a in particle.artists())]

    def render(self, seconds):
        state = beta_state(seconds)
        phase = state['phase']
        self.revision = (phase >= .08, phase >= .23, phase >= .57)
        for i, q in enumerate(self.quarks):
            symbol = ('u', 'd', 'u' if state['changed'] else 'd')[i]
            q.set(self.positions[i], symbol, COLORS[i], COLOR_NAMES[i], .5+.5*np.sin(seconds*3))
        self.hadron.set_text('Proton · uud · +1 e' if state['changed'] else 'Neutron · udd · 0 e')
        travel = float(smooth((phase-.23)/.34))
        location = np.array([3.12, 3.22])+travel*np.array([2.48, .38])
        self.w.set(location, r'$W^-$', GOLD, 'virtual')
        self.w.visible(state['w_visible'])
        self.link.set_visible(state['w_visible'])
        decay = float(smooth((phase-.57)/.28))
        start = np.array([5.6, 3.6])
        for particle, path, end, symbol, color, caption in [
            (self.electron, self.lepton_lines[0], np.array([8.15, 5.15]), r'$e^-$', '#e5b9ff', 'electron · −1 e'),
            (self.neutrino, self.lepton_lines[1], np.array([8.15, 2.25]), r'$\bar{\nu}_e$', '#b8c9dc', 'antineutrino · 0 e')]:
            position = start+decay*(end-start)
            particle.set(position, symbol, color, caption)
            particle.visible(state['leptons_visible'])
            # Delay the labels until the outgoing legs separate enough to read them.
            particle.caption.set_visible(state['leptons_visible'] and decay > .35)
            path.set_data([start[0], position[0]], [start[1], position[1]])
            path.set_visible(state['leptons_visible'])
        if not state['changed']:
            self.caption.set_text('Example start / replay: neutron (udd).' if phase < .08
                                  else 'A down quark in the neutron will change into up.')
            body = 'A down changes into up through\nthe weak interaction. Its color\nstays blue in this example.'
        elif state['w_visible']:
            self.caption.set_text('d → u: same color, different flavor and electric charge.')
            body = 'A virtual W⁻ represents\nthe exchange, rather than\na gluon or a free, real W.'
        else:
            self.caption.set_text('Result: proton + electron + electron antineutrino.')
            body = 'An electron and an electron\nantineutrino are produced.\nElectric charge is conserved.'
        return dict(kicker='03 / WEAK INTERACTION', title='Flavor can change',
                    body=body,
                    equation=r'$d \to u + W^-$'+'\n'+r'$W^- \to e^- + \bar{\nu}_e$'+'\n(virtual W in the full process)',
                    detail='Charge: −1/3 = +2/3 − 1\nFull process:\n0 = +1 − 1 + 0\n\nW, electron and antineutrino\ncarry no color charge.',
                    takeaway='Flavor changes.\nColor is preserved.',
                    note='The full process takes place in a neutron, not in a free down quark. The W is virtual; the timing is illustrative.')


class Simulator:
    def __init__(self, animate=True, scene='colors', seconds=0.):
        import matplotlib.pyplot as plt
        from matplotlib.animation import FuncAnimation
        from matplotlib.widgets import Button, Slider
        from matplotlib.patches import FancyBboxPatch, Rectangle

        self.plt = plt
        self.scene_index = SCENE_NAMES.index(SCENE_ALIASES.get(scene, scene))
        self.seconds = seconds % SCENE_DURATIONS[self.scene_index]
        self.running, self.automatic = True, True
        self.last_time = perf_counter()
        self._visible_scene = None
        self._static_revision = None
        self._layout_key = None
        self.animation = None
        plt.rcParams.update({'font.family': 'DejaVu Sans', 'text.color': INK,
                             'axes.labelcolor': INK, 'xtick.color': MUTED,
                             'ytick.color': MUTED, 'font.size': 11})
        self.fig = plt.figure(figsize=(15, 9), facecolor=BG)
        self.fig.canvas.manager.set_window_title('Color and flavor · quantum chromodynamics')
        self.fig.text(.055, .905, 'Quarks: color and flavor', fontsize=28, fontweight='bold')
        self.fig.text(.055, .868, 'Three color charges · six flavors · two interactions',
                       color=MUTED, fontsize=12)
        self.ax = self.fig.add_axes([.035, .235, .615, .615])
        self.ax.set(xlim=(0, 10), ylim=(0, 7.3), aspect='equal')
        self.ax.set_axis_off()
        self.sidebar = self.fig.add_axes([.67, .255, .295, .575])
        self.sidebar.set_axis_off()
        self.sidebar.add_patch(FancyBboxPatch((.0, .0), 1, 1,
                                 boxstyle='round,pad=0,rounding_size=.035',
                                 transform=self.sidebar.transAxes, facecolor=PANEL, edgecolor='#24364d'))
        self.kicker = self.sidebar.text(.06, .93, '', fontsize=10, color=ACCENT, va='top')
        self.title = self.sidebar.text(.06, .855, '', fontsize=16, fontweight='bold', va='top')
        self.body = self.sidebar.text(.06, .77, '', fontsize=12, va='top', linespacing=1.5)
        self.equation = self.sidebar.text(.06, .575, '', fontsize=13, color=GOLD,
                                          va='top', linespacing=1.6)
        self.detail = self.sidebar.text(.06, .365, '', fontsize=11, color=MUTED,
                                        va='top', linespacing=1.35)
        self.takeaway = self.sidebar.text(.06, .070, '', fontsize=14, color=ACCENT,
                                          va='top', linespacing=1.3, fontweight='bold')
        self.note_ax = self.fig.add_axes([.055, .19, .91, .037])
        self.note_ax.set_axis_off()
        self.note = self.note_ax.text(0, .8, '', fontsize=9, color=MUTED, va='top')
        self.progress_ax = self.fig.add_axes([.055, .171, .91, .006])
        self.progress_ax.set_axis_off()
        self.progress_ax.add_patch(Rectangle((0, 0), 1, 1, facecolor='#203047'))
        self.progress = self.progress_ax.add_patch(Rectangle((0, 0), 0, 1, facecolor=ACCENT))

        self.scenes = [ColorScene(self.ax), FlavorScene(self.ax), WeakScene(self.ax)]
        self.controls = []
        for i, label in enumerate(('01  Colors', '02  Flavors', '03  Weak')):
            button = Button(self.fig.add_axes([.055+i*.139, .103, .129, .048]), label,
                             color=PANEL, hovercolor='#28425b')
            button.label.set_color(INK)
            button.on_clicked(lambda _, index=i: self.select_scene(index))
            self.controls.append(button)
        self.pause_button = Button(self.fig.add_axes([.49, .103, .105, .048]), 'Pause',
                                   color='#234548', hovercolor='#326362')
        self.restart_button = Button(self.fig.add_axes([.607, .103, .105, .048]), 'Restart',
                                     color=PANEL, hovercolor='#28425b')
        self.auto_button = Button(self.fig.add_axes([.725, .103, .24, .048]), 'Automatic tour: ON',
                                  color=PANEL, hovercolor='#28425b')
        self.speed = Slider(self.fig.add_axes([.15, .060, .28, .018]), 'Speed',
                            .25, 2, valinit=1., valfmt='%1.2f×', color=ACCENT,
                            track_color='#203047')
        self.fig.text(.49, .060, 'Space: pause    R: restart    A: auto tour    1–3: chapter',
                       fontsize=9, color=MUTED)
        self.fig.text(.055, .022,
            'Conceptual animation: sizes, paths and times are not to scale. '
            'Color labels name charges, not visible colors.', fontsize=9, color=MUTED)
        self.pause_button.on_clicked(self.toggle)
        self.restart_button.on_clicked(self.restart)
        self.auto_button.on_clicked(self.toggle_auto)
        self.fig.canvas.mpl_connect('key_press_event', self.keypress)
        self.fig.canvas.mpl_connect('resize_event', self.on_resize)
        from matplotlib.text import Text
        self._font_sizes = {text: text.get_fontsize() for text in self.fig.findobj(Text)}
        self.shared_artists = (self.progress,)
        # Only moving elements animate. Text and diagrams are cached until a stage changes.
        self.use_blit = animate and self.fig.canvas.supports_blit
        for artist in [*self.shared_artists, *(a for s in self.scenes for a in s.moving)]:
            artist.set_animated(self.use_blit)
        self.render()
        self.animation = (FuncAnimation(self.fig, self.tick, init_func=self.artists,
                          interval=1000/60, blit=self.use_blit, cache_frame_data=False)
                          if animate else None)
        self.last_time = perf_counter()

    def artists(self):
        return (*self.scenes[self.scene_index].moving, *self.shared_artists)

    def fit_layout(self, revision):
        """Measure actual text, stack it with gaps, and adapt to window size/DPI."""
        key = (*self.fig.get_size_inches(), self.fig.dpi, revision)
        if self._layout_key == key:
            return False
        self._layout_key = key
        scale = min(self.fig.get_figwidth()/15., self.fig.get_figheight()/9.)
        for text, size in self._font_sizes.items():
            text.set_fontsize(size*scale)

        renderer = self.fig.canvas.get_renderer()
        width, height = self.sidebar.get_window_extent(renderer).size
        labels = (self.kicker, self.title, self.body, self.equation, self.detail, self.takeaway)
        gap = height*.027
        usable_width, usable_height = width*.88, height*.88
        # The final callout has its own measured space; it never shares a fixed
        # vertical position with the preceding paragraph, even on smaller windows.
        for _ in range(4):
            boxes = [label.get_window_extent(renderer) for label in labels]
            factor = min(1., usable_width/max(box.width for box in boxes),
                         (usable_height-gap*(len(labels)-1))/sum(box.height for box in boxes))
            if factor >= .999:
                break
            for label in labels:
                label.set_fontsize(label.get_fontsize()*factor*.99)
        boxes = [label.get_window_extent(renderer) for label in labels]
        cursor = .94
        for label, box in zip(labels, boxes):
            label.set_position((.06, cursor))
            cursor -= (box.height+gap)/height
        return True

    def on_resize(self, _=None):
        self._layout_key = None
        self.render()
        self.fig.canvas.draw_idle()

    def render(self):
        if self._visible_scene != self.scene_index:
            for i, scene in enumerate(self.scenes):
                scene.show(i == self.scene_index)
            self._visible_scene = self.scene_index
        values = self.scenes[self.scene_index].render(self.seconds)
        for name, value in values.items():
            label = getattr(self, name)
            if label.get_text() != value:
                label.set_text(value)
        self.progress.set_width(self.seconds/SCENE_DURATIONS[self.scene_index])
        revision = (self.scene_index, self.scenes[self.scene_index].revision)
        layout_changed = self.fit_layout(revision)
        if self._static_revision != revision or layout_changed:
            self._static_revision = revision
            if self.animation is not None and self.use_blit:
                self.fig.canvas.draw()
                # FuncAnimation keys backgrounds by limits, which stay fixed across chapters.
                # Invalidate them explicitly when the static teaching content changes.
                self.animation._blit_cache.clear()
        return self.artists()

    def advance(self, dt):
        if not np.isfinite(dt) or dt < 0:
            raise ValueError('The time step must be finite and nonnegative.')
        self.seconds += dt
        if self.automatic:
            self.seconds %= sum(SCENE_DURATIONS)
            while self.seconds >= SCENE_DURATIONS[self.scene_index]:
                self.seconds -= SCENE_DURATIONS[self.scene_index]
                self.scene_index = (self.scene_index+1) % len(self.scenes)
        else:
            self.seconds %= SCENE_DURATIONS[self.scene_index]
        return self.render()

    def tick(self, _=None):
        now = perf_counter()
        dt = min(max(now-self.last_time, 0.), .1)*self.speed.val
        self.last_time = now
        return self.advance(dt) if self.running else self.artists()

    def refresh(self):
        self.render()
        # Also show a selected chapter immediately while paused, using public canvas APIs.
        if self.use_blit:
            self.fig.canvas.draw()
            for artist in sorted(self.artists(), key=lambda item: item.get_zorder()):
                artist.axes.draw_artist(artist)
            self.fig.canvas.blit(self.fig.bbox)
        else:
            self.fig.canvas.draw_idle()

    def select_scene(self, index):
        self.scene_index, self.seconds = index, 0.
        self.last_time = perf_counter()
        self.refresh()

    def toggle(self, _=None):
        self.running = not self.running
        self.last_time = perf_counter()
        self.pause_button.label.set_text('Pause' if self.running else 'Resume')
        self.refresh()

    def restart(self, _=None):
        self.select_scene(0)

    def toggle_auto(self, _=None):
        self.automatic = not self.automatic
        self.auto_button.label.set_text('Automatic tour: ' + ('ON' if self.automatic else 'OFF'))
        self.refresh()

    def keypress(self, event):
        if event.key == ' ':
            self.toggle()
        elif event.key in ('r', 'R'):
            self.restart()
        elif event.key in ('a', 'A'):
            self.toggle_auto()
        elif event.key in ('1', '2', '3'):
            self.select_scene(int(event.key)-1)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--save', '--guardar', dest='save', metavar='IMAGE.png',
                        help='Save a preview without opening a window.')
    parser.add_argument('--scene', '--escena', dest='scene',
                        type=lambda value: SCENE_ALIASES.get(value, value),
                        choices=SCENE_NAMES, default='colors', help='Choose the starting chapter.')
    parser.add_argument('--time', '--tiempo', dest='time', type=float, default=0.,
                        help='Illustrative seconds within the selected chapter.')
    args = parser.parse_args()
    if not np.isfinite(args.time) or args.time < 0:
        parser.error('--time must be finite and nonnegative.')
    if args.save:
        import matplotlib
        matplotlib.use('Agg')
    sim = Simulator(animate=not bool(args.save), scene=args.scene, seconds=args.time)
    if args.save:
        sim.fig.savefig(args.save, dpi=140, facecolor=BG)
        sim.plt.close(sim.fig)
    else:
        sim.plt.show()


if __name__ == '__main__':
    main()
