"""Quantum fields, made visible: an animated introduction in five chapters.

Run: python campos_cuanticos.py
Preview: python campos_cuanticos.py --scene packet --time 9 --save field.png
Requires numpy, matplotlib and campos_cuanticos_modelos.py in this folder.
Sources and model scope: LEEME_campos_cuanticos.md.
"""
import argparse
from functools import lru_cache
from time import perf_counter

import numpy as np

from campos_cuanticos_modelos import FreeScalarField, oscillator_density, mode_transfer


BG = '#0b1220'
PANEL = '#121f31'
INK = '#edf4ff'
MUTED = '#9aacbf'
ACCENT = '#67e8d3'
GOLD = '#ffda85'
PURPLE = '#bd9aff'
SCENE_NAMES = ('field', 'packet', 'quanta', 'vacuum', 'coupling')
SCENE_DURATIONS = (16., 18., 20., 18., 16.)


class Scene:
    def __init__(self, ax):
        self.ax = ax
        self.items, self.moving = [], []
        self.revision = 0

    def text(self, x, y, text, size=12, color=INK, **kwargs):
        item = self.ax.text(x, y, text, fontsize=size, color=color, **kwargs)
        self.items.append(item)
        return item

    def line(self, x, y, **kwargs):
        item, = self.ax.plot(x, y, **kwargs)
        self.items.append(item)
        return item

    def patch(self, item):
        self.ax.add_patch(item)
        self.items.append(item)
        return item

    def collection(self, item):
        self.ax.add_collection(item)
        self.items.append(item)
        return item

    def show(self, value):
        for item in self.items:
            item.set_visible(value)


class FieldSurface:
    """A fast projected mesh: height is a scalar value, not a material surface."""

    def __init__(self, scene, model, center=4.45, height=.58, limit=1.):
        from matplotlib.collections import PolyCollection, LineCollection
        from matplotlib.colors import LinearSegmentedColormap

        self.height, self.limit = height, limit
        self.indices = np.arange(0, model.size, 2)
        x = model.X[np.ix_(self.indices, self.indices)]/(model.length/2)
        y = model.Y[np.ix_(self.indices, self.indices)]/(model.length/2)
        self.base = np.stack([5+3.0*x+1.5*y, center-.32*x+.76*y], axis=-1)
        self.cmap = LinearSegmentedColormap.from_list('scalar_value',
                          [PURPLE, '#445678', '#172b3e', '#28756f', ACCENT])
        # Back rows are drawn first in the projected view.
        self.order = np.arange((len(self.indices)-1)**2).reshape(
                              len(self.indices)-1, -1)[::-1].ravel()
        self.faces = scene.collection(PolyCollection([], edgecolors='none', alpha=.93, zorder=2))
        self.mesh = scene.collection(LineCollection([], colors='#b1d9df',
                                      linewidths=.5, alpha=.32, zorder=3))
        self.mesh.set_clip_on(False)
        baseline = np.concatenate([self.base, self.base.transpose(1, 0, 2)])
        scene.collection(LineCollection(baseline, colors='#1c3045', linewidths=.55, zorder=1))
        scene.text(9.35, center+.36, 'x', 10, MUTED)
        scene.text(7.3, 6.08, 'y', 10, MUTED)
        scene.moving.extend([self.faces, self.mesh])

    def update(self, field):
        values = field[np.ix_(self.indices, self.indices)]
        points = self.base.copy()
        points[..., 1] += self.height*values
        faces = np.stack([points[:-1, :-1], points[:-1, 1:],
                          points[1:, 1:], points[1:, :-1]], axis=2).reshape(-1, 4, 2)
        means = (values[:-1, :-1]+values[1:, :-1]+values[:-1, 1:]+values[1:, 1:]).ravel()/4
        self.faces.set_verts(faces[self.order])
        self.faces.set_facecolors(self.cmap(np.clip(.5+.5*means[self.order]/self.limit, 0, 1)))
        self.mesh.set_segments(np.concatenate([points, points.transpose(1, 0, 2)]))


class FieldScene(Scene):
    def __init__(self, ax, model):
        super().__init__(ax)
        self.model = model
        self.text(5, 6.86, 'A VALUE AT EVERY POSITION', 16, ha='center', fontweight='bold')
        self.text(5, 6.35, 'A simple scalar field · one traveling mode', 12, MUTED, ha='center')
        self.surface = FieldSurface(self, model)
        self.text(.65, 2.48, 'SLICE THROUGH y = 0', 10, MUTED)
        self.line([.65, 9.35], [1.45, 1.45], color='#2a4059', lw=1)
        self.slice_x = np.linspace(.65, 9.35, model.size)
        self.slice = self.line([], [], color=ACCENT, lw=2.5)
        self.readout = self.text(5, .40, '', 12, ACCENT, ha='center')
        self.text(.65, .60, '−x', 10, MUTED)
        self.text(9.35, .60, '+x', 10, MUTED, ha='right')
        self.moving.extend([self.slice, self.readout])

    def render(self, seconds):
        field = self.model.mode(seconds)
        self.surface.update(field)
        row = field[self.model.size//2]
        self.slice.set_data(self.slice_x, 1.45+.62*row)
        self.readout.set_text(f'Field value at the center: {row[self.model.size//2]:+.2f}')
        return dict(kicker='01 / WHAT IS A FIELD?', title='A value across space',
            body='A field assigns something to\nevery position. This simple\nscalar field assigns one number.',
            equation=r'$\phi(x,y,t)$'+'\nHeight = field value\nTeal: positive · violet: negative',
            detail='The curve below is a slice\nthrough the same field.\n\nThe grid is a way to draw values,\nnot a material sheet. Quantum\ntheory comes in the next steps.',
            takeaway='The field extends\nthrough the whole region.',
            note='Classical scalar-field illustration. The height is a field value, not an extra spatial dimension or a literal fabric.')


class PacketScene(Scene):
    def __init__(self, ax, model):
        super().__init__(ax)
        self.model = model
        self.text(5, 6.86, 'MANY MODES, ONE MOVING PACKET', 16, ha='center', fontweight='bold')
        self.text(5, 6.35, 'Exact free-field propagation · no external force', 12, MUTED, ha='center')
        self.surface = FieldSurface(self, model, height=.95)
        self.text(.65, 2.48, 'FIELD SLICE · NOT A PROBABILITY', 10, MUTED)
        self.line([.65, 9.35], [1.40, 1.40], color='#2a4059', lw=1)
        self.slice_x = np.linspace(.65, 9.35, model.size)
        self.slice = self.line([], [], color=ACCENT, lw=2.5)
        self.energy0 = model.packet_energy(0.)
        self.text(5, .40, 'A localized disturbance propagates through the field.', 12, ACCENT, ha='center')
        self.moving.append(self.slice)

    def render(self, seconds):
        field = self.model.packet(.8*seconds)
        self.surface.update(field)
        self.slice.set_data(self.slice_x, 1.40+.83*field[self.model.size//2])
        return dict(kicker='02 / PROPAGATION', title='A wave packet travels',
            body='Many wavelengths combine\ninto a localized disturbance.\nEach mode has its own frequency.',
            equation=r'$\omega_k=\sqrt{k^2+m^2}$'+'\n'+r'$\partial_t^2\phi-\nabla^2\phi+m^2\phi=0$',
            detail='This is a classical field, or\nthe mean of a coherent state.\nIts height is not a one-particle\nprobability amplitude.\n\nTotal field energy is conserved.',
            takeaway='Modes combine.\nThe disturbance moves.',
            note='Free Klein–Gordon field, ℏ = c = 1. Finite periodic window; the chapter replays the same prepared wave packet.')


class QuantaScene(Scene):
    def __init__(self, ax, model):
        super().__init__(ax)
        from matplotlib.patches import FancyBboxPatch, Rectangle, Polygon
        self.text(5, 6.86, 'ONE MODE, DISCRETE ENERGY LEVELS', 16, ha='center', fontweight='bold')
        self.selection = self.text(5, 6.25, '', 12, ACCENT, ha='center')
        self.text(2.4, 5.66, 'ENERGY / ℏω', 11, MUTED, ha='center')
        self.text(7.7, 5.66, 'PROBABILITY DENSITY', 11, MUTED, ha='center')
        for n in range(5):
            y = 1.15+.91*n
            self.line([.75, 4.15], [y, y], color='#2b425d', lw=1.5)
            self.text(.82, y+.15, f'n = {n}', 11, MUTED)
            self.text(4.12, y+.15, f'{n+.5:.1f}', 11, MUTED, ha='right')
        self.highlight = self.patch(Rectangle((.75, 1.11), 3.4, .08,
                                    facecolor=GOLD, edgecolor='none', zorder=3))
        self.patch(FancyBboxPatch((5.65, 1.05), 3.95, 4.25,
                   boxstyle='round,pad=0.0,rounding_size=.12', facecolor=PANEL, edgecolor='#273a51'))
        self.q = np.linspace(-4.5, 4.5, 500)
        self.qx = 5.8+(self.q+4.5)/9*3.65
        self.fill = self.patch(Polygon([[5.8, 1.25]], facecolor=ACCENT, alpha=.14, edgecolor='none'))
        self.density = self.line([], [], color=ACCENT, lw=2.5, zorder=4)
        self.line([5.8, 9.45], [1.25, 1.25], color='#3b516b', lw=1)
        for value in (-4, 0, 4):
            self.text(5.8+(value+4.5)/9*3.65, .8, f'{value}', 10, MUTED, ha='center')
        self.text(7.62, .33, 'Mode amplitude Q', 12, MUTED, ha='center')
        self.text(2.45, .33, 'Equal spacing: one quantum = ℏω', 11, GOLD, ha='center')
        self.moving.extend([self.selection, self.highlight, self.fill, self.density])

    def render(self, seconds):
        n = int(seconds/4) % 5
        self.revision = n
        density = oscillator_density(n, self.q)
        curve = 1.25+6.0*density
        self.density.set_data(self.qx, curve)
        self.fill.set_xy(np.vstack([[self.qx[0], 1.25], np.column_stack([self.qx, curve]), [self.qx[-1], 1.25]]))
        self.highlight.set_y(1.11+.91*n)
        self.selection.set_text(f'Selected example: n = {n}   ·   {n} '+('quantum' if n == 1 else 'quanta')+' in this mode')
        return dict(kicker='03 / QUANTIZATION', title='Energy comes in steps',
            body='A free bosonic field mode acts\nlike a quantum oscillator. Its\nexcitation number is an integer.',
            equation=r'$E_n=(n+\frac{1}{2})\hbar\omega$'+'\n'+rf'$n={n},\quad \langle Q\rangle=0$',
            detail='The right-hand curve gives the\nprobabilities of mode-amplitude\nmeasurements in this state.\n\nA definite number state has a\nstationary probability density.',
            takeaway='Particles are quanta\nof the corresponding field.',
            note='Q is a mode amplitude, not position. The tour selects separate prepared states; no spontaneous jumps are being simulated.')


class VacuumScene(Scene):
    def __init__(self, ax, model):
        super().__init__(ax)
        from matplotlib.patches import Polygon
        self.model = model
        self.sample = lru_cache(maxsize=6)(model.vacuum_sample)
        self.text(5, 6.86, 'VACUUM: ZERO QUANTA, NONZERO UNCERTAINTY', 14,
                  ha='center', fontweight='bold')
        self.text(5, 6.35, 'Possible field measurements · not a movie of vacuum motion',
                  11, MUTED, ha='center')
        self.surface = FieldSurface(self, model, center=4.55, height=.22, limit=2.)
        q = np.linspace(-3, 3, 300)
        probability = oscillator_density(0, q)
        for x0, color, label in [(.7, ACCENT, 'Q measurements'), (5.35, PURPLE, 'P measurements')]:
            x = x0+(q+3)/6*3.9
            y = .83+1.7*probability
            self.patch(Polygon(np.vstack([[x[0], .83], np.column_stack([x, y]), [x[-1], .83]]),
                               facecolor=color, alpha=.12, edgecolor='none'))
            self.line(x, y, color=color, lw=2)
            self.line([x0, x0+3.9], [.83, .83], color='#30465d', lw=1)
            self.text(x0+1.95, 2.03, label, 11, color, ha='center')
            self.text(x0+1.95, .49, '0', 9, MUTED, ha='center')
        self.text(5, .10, 'Separate, stationary distributions of conjugate mode variables', 11, MUTED, ha='center')

    def render(self, seconds):
        progress = (seconds % 18)/3
        index = int(progress)
        phase = progress-index
        theta = .5*np.pi*phase*phase*(3-2*phase)
        # cos² + sin² = 1 preserves each Gaussian marginal's covariance.
        field = np.cos(theta)*self.sample(1000+index)+np.sin(theta)*self.sample(1000+(index+1)%6)
        self.surface.update(field)
        return dict(kicker='04 / THE QUANTUM VACUUM', title='Empty is not definite',
            body='The vacuum is the lowest-energy\nstate: zero quanta above it.\nField measurements still vary.',
            equation=r'$\langle Q\rangle=\langle P\rangle=0$'+'\n'+r'$\Delta Q\,\Delta P=\frac{1}{2}$',
            detail='The surface explores possible\nmeasurement configurations.\nThe order is a visual guide,\nnot actual time evolution.\n\nNo particles pop out of nothing.',
            takeaway='Zero mean does not\nmean zero uncertainty.',
            note='Finite-mode scalar vacuum. Q and P are dimensionless conjugate quadratures; the two curves describe separate measurement ensembles.')


class CouplingScene(Scene):
    def __init__(self, ax, model):
        super().__init__(ax)
        from matplotlib.patches import Circle, Wedge
        self.text(5, 6.86, 'TWO MODES CAN EXCHANGE AN EXCITATION', 15,
                  ha='center', fontweight='bold')
        self.text(5, 6.35, 'An exactly solvable quantum model · total excitation = 1', 11, MUTED, ha='center')
        self.rings, self.numbers = [], []
        for x, color, label in [(2.35, ACCENT, 'MODE A'), (7.65, PURPLE, 'MODE B')]:
            self.patch(Circle((x, 4.52), .97, facecolor=PANEL, edgecolor='#263c54', lw=9))
            self.rings.append(self.patch(Wedge((x, 4.52), 1.04, 90, 450,
                                      width=.17, facecolor=color, edgecolor='none', zorder=3)))
            self.text(x, 5.91, label, 12, color, ha='center')
            self.numbers.append(self.text(x, 4.55, '', 23, color, ha='center', va='center', fontweight='bold'))
            self.text(x, 3.18, 'Detection probability', 11, MUTED, ha='center')
        self.link = self.line([3.6, 6.4], [4.52, 4.52], color=GOLD, lw=3)
        self.text(5, 4.99, 'coupling g', 11, GOLD, ha='center')
        t = np.linspace(0, 16, 400)
        a, b = np.array([mode_transfer(value) for value in t]).T
        self.line(.7+8.6*t/16, .90+1.45*a, color=ACCENT, lw=1.7, alpha=.5)
        self.line(.7+8.6*t/16, .90+1.45*b, color=PURPLE, lw=1.7, alpha=.5)
        self.line([.7, 9.3], [.9, .9], color='#30465d', lw=1)
        self.playhead = self.line([.7, .7], [.86, 2.42], color=GOLD, lw=1.4)
        self.text(.45, 2.3, '1', 10, MUTED, ha='right')
        self.text(.45, .85, '0', 10, MUTED, ha='right')
        self.text(5, .29, 'One shared excitation · changing probabilities', 12, ACCENT, ha='center')
        self.moving.extend([*self.rings, *self.numbers, self.link, self.playhead])

    def render(self, seconds):
        a, b = mode_transfer(seconds)
        for ring, label, value in zip(self.rings, self.numbers, (a, b)):
            ring.set_theta2(90+360*float(value))
            label.set_text(f'{value:.0%}')
        self.link.set_alpha(.2+.7*4*a*b)
        self.playhead.set_xdata([.7+8.6*seconds/16]*2)
        return dict(kicker='05 / INTERACTION', title='An excitation is shared',
            body='Two resonant bosonic modes\nare coupled. The quantum state\nmoves between their occupations.',
            equation=r'$P_A=\cos^2(gt),\quad P_B=\sin^2(gt)$'+'\n'+r'$P_A+P_B=1$',
            detail='The rings show the probability\nof finding the quantum in each\nmode, not a fraction of a particle.\n\nBoth field means remain zero.\nThis is a two-mode toy model.',
            takeaway='Interaction redistributes\na conserved excitation.',
            note='Resonant mode mixing from |1,0⟩. This is a unitary quantum example, not a simulation of Standard Model scattering.')


class Simulator:
    def __init__(self, animate=True, scene='field', seconds=0.):
        import matplotlib.pyplot as plt
        from matplotlib.animation import FuncAnimation
        from matplotlib.widgets import Button, Slider
        from matplotlib.patches import FancyBboxPatch, Rectangle

        self.plt = plt
        self.model = FreeScalarField()
        self.scene_index = SCENE_NAMES.index(scene)
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
        self.fig.canvas.manager.set_window_title('Quantum fields · an animated introduction')
        self.fig.text(.055, .905, 'Quantum fields, made visible', fontsize=28, fontweight='bold')
        self.fig.text(.055, .868, 'Fields · waves · quanta · vacuum · interactions',
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

        self.scenes = [scene_type(self.ax, self.model) for scene_type in
                       (FieldScene, PacketScene, QuantaScene, VacuumScene, CouplingScene)]
        self.controls = []
        for i, label in enumerate(('1  Field', '2  Packet', '3  Quanta', '4  Vacuum', '5  Coupling')):
            button = Button(self.fig.add_axes([.055+i*.086, .103, .080, .048]), label,
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
        self.fig.text(.49, .060, 'Space: pause    R: restart    A: auto tour    1–5: chapter',
                       fontsize=9, color=MUTED)
        self.fig.text(.055, .022,
            'Teaching models: scalar fields and bosonic modes in natural units. '
            'The geometry is a visualization, not a material sheet.', fontsize=9, color=MUTED)
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
        # Capture a CLEAN background before showing the immediate frame. Drawing
        # artists by hand here used to bake that frame into FuncAnimation's next
        # background, leaving old curves and percentages visible indefinitely.
        if self.use_blit:
            self.fig.canvas.draw()
            artists = sorted(self.artists(), key=lambda item: item.get_zorder())
            self.animation._blit_cache.clear()
            self.animation._drawn_artists = artists
            self.animation._blit_draw(artists)
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
        elif event.key in ('1', '2', '3', '4', '5'):
            self.select_scene(int(event.key)-1)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--save', metavar='IMAGE.png',
                        help='Save a preview without opening a window.')
    parser.add_argument('--scene', choices=SCENE_NAMES, default='field',
                        help='Choose the starting chapter.')
    parser.add_argument('--time', type=float, default=0.,
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
