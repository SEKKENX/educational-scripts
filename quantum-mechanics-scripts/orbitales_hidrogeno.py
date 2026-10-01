"""Orbitales de hidrógeno: cortes 2D de estados estacionarios.

Instalar: python -m pip install numpy matplotlib
Ejecutar: python orbitales_hidrogeno.py
Vista previa sin ventana: python orbitales_hidrogeno.py --guardar vista.png
Modelo no relativista, núcleo fijo, sin campos externos. Distancias en a0.
Referencia: https://dlmf.nist.gov/18.39 (funciones radiales de Coulomb).
"""
import argparse
from math import factorial, pi
from time import perf_counter
import numpy as np


def laguerre(k, alpha, x):
    """L_k^alpha mediante recurrencia; convención estándar generalizada."""
    a = np.ones_like(x)
    if k == 0:
        return a
    b = 1 + alpha - x
    for j in range(1, k):
        a, b = b, ((2*j + 1 + alpha - x)*b - (j + alpha)*a)/(j + 1)
    return b


def radial(n, l, r):
    rho = 2*np.asarray(r)/n
    norm = np.sqrt((2/n)**3 * factorial(n-l-1)/(2*n*factorial(n+l)))
    return norm*np.exp(-rho/2)*rho**l*laguerre(n-l-1, 2*l+1, rho)


def harmonic(l, m, costheta, phi):
    """Y_l^m normalizado, incluida la fase de Condon–Shortley."""
    q = abs(m)
    x = np.clip(costheta, -1, 1)
    p = np.ones_like(x)
    for j in range(1, q+1):
        p *= -(2*j-1)*np.sqrt(np.maximum(0, 1-x*x))
    if l > q:
        a, b = p, (2*q+1)*x*p
        for j in range(q+2, l+1):
            a, b = b, ((2*j-1)*x*b-(j+q-1)*a)/(j-q)
        p = b
    norm = np.sqrt((2*l+1)/(4*pi)*factorial(l-q)/factorial(l+q))
    y = norm*p*np.exp(1j*q*phi)
    return (-1)**q*np.conjugate(y) if m < 0 else y


def wavefunction(n, l, m, x, y, z):
    if not (1 <= n <= 6 and 0 <= l < n and abs(m) <= l):
        raise ValueError('Se requiere 1 ≤ n ≤ 6, 0 ≤ l < n y |m| ≤ l.')
    r = np.sqrt(x*x+y*y+z*z)
    ct = np.divide(z, r, out=np.zeros_like(r), where=r > 0)
    return radial(n, l, r)*harmonic(l, m, ct, np.arctan2(y, x))


class Simulator:
    """Recorrido automático; el fundido es visual, no una evolución física."""

    HOLD = 2.0
    FADE = 1.0

    def __init__(self, animate=True):
        import matplotlib.pyplot as plt
        from matplotlib.widgets import Slider, Button
        from matplotlib.animation import FuncAnimation
        from matplotlib.colors import PowerNorm
        from functools import lru_cache

        self.plt = plt
        self.states = [(n, l, m) for n in range(1, 7)
                       for l in range(n) for m in range(-l, l+1)]
        self.index = 0
        self.elapsed = 0.
        self.running = True
        self.last_time = perf_counter()
        self.coords = np.linspace(-4, 4, 201)
        self.u, self.v = np.meshgrid(self.coords, self.coords)
        self.r_scaled = np.linspace(0, 4, 800)
        self.norm = PowerNorm(gamma=.45, vmin=0, vmax=1)
        self.cmap = plt.get_cmap('magma')
        self.frame_for = lru_cache(maxsize=4)(self.make_frame)
        plt.style.use('dark_background')
        self.fig = plt.figure(figsize=(13, 8), facecolor='#101722')
        self.fig.canvas.manager.set_window_title('Recorrido automático de orbitales')
        self.fig.suptitle('HIDRÓGENO  /  Evolución visual de los orbitales',
                          fontsize=19, y=.96)
        self.ax = self.fig.add_axes([.07, .29, .46, .58])
        self.ax.set(xlabel='x / (n² a₀)', ylabel='z / (n² a₀)',
                    title='Densidad relativa · corte xz')
        self.ra = self.fig.add_axes([.64, .61, .30, .23])
        self.ra.set(xlim=(0, 4), ylim=(0, 1.05), xlabel='r / (n² a₀)',
                    ylabel='P(r) / máximo', title='Distribución radial relativa')
        self.ra.grid(alpha=.15)
        self.panel = self.fig.add_axes([.62, .29, .35, .25])
        self.panel.set_axis_off()
        self.info = self.panel.text(0, .98, '', va='top', fontsize=12, linespacing=1.6)
        self.status_ax = self.fig.add_axes([.07, .20, .88, .045])
        self.status_ax.set_axis_off()
        self.status = self.status_ax.text(0, .5, '', fontsize=11, color='#70e1d3')
        self.im = self.ax.imshow(self.frame_for(0)[0], origin='lower',
                                 extent=[-4, 4, -4, 4], interpolation='bilinear')
        from matplotlib.cm import ScalarMappable
        self.colorbar = self.fig.colorbar(ScalarMappable(norm=self.norm, cmap=self.cmap),
                                          ax=self.ax, fraction=.04, pad=.035)
        self.colorbar.set_label('Densidad relativa |ψ|² / máximo del corte')
        self.line, = self.ra.plot(self.r_scaled, self.frame_for(0)[1],
                                  color='#6ce4cf', lw=2)
        self.speed = Slider(self.fig.add_axes([.16, .125, .38, .025]),
                            'Velocidad', .2, 3, valinit=1, valfmt='%1.1f×')
        self.button = Button(self.fig.add_axes([.64, .11, .13, .06]), 'Pausar',
                             color='#254253', hovercolor='#386579')
        self.restart_button = Button(self.fig.add_axes([.80, .11, .14, .06]),
                                     'Reiniciar', color='#254253', hovercolor='#386579')
        self.fig.text(.07, .035,
            'Recorrido de estados estacionarios. El fundido entre orbitales es una transición visual.\n'
            'Escala ajustada con n²; a₀ ≈ 0.0529 nm. Espacio: pausar / continuar · R: volver a 1s.',
            fontsize=10, color='#becbdc')
        self.button.on_clicked(self.toggle)
        self.restart_button.on_clicked(self.restart)
        self.fig.canvas.mpl_connect('key_press_event', self.keypress)
        self.render()
        self.animation = (FuncAnimation(self.fig, self.tick, init_func=self.artists,
                          interval=1000/60, blit=self.fig.canvas.supports_blit,
                          cache_frame_data=False) if animate else None)
        self.last_time = perf_counter()

    def make_frame(self, index):
        n, l, m = self.states[index]
        scale = n*n
        density = abs(wavefunction(n, l, m, self.u*scale,
                                   np.zeros_like(self.u), self.v*scale))**2
        density /= density.max()
        # Precompute colors; each frame only blends the two endpoint images.
        rgba = self.cmap(self.norm(density)).astype(np.float32)
        r = self.r_scaled*scale
        probability = r*r*radial(n, l, r)**2
        probability /= probability.max()
        return rgba, probability

    def artists(self):
        return self.im, self.line, self.info, self.status

    def name(self, index):
        n, l, m = self.states[index]
        return f'{n}{"spdfgh"[l]} (m = {m:+d})'

    def render(self):
        nxt = (self.index+1) % len(self.states)
        fraction = np.clip((self.elapsed-self.HOLD)/self.FADE, 0., 1.)
        blend = fraction*fraction*(3-2*fraction)
        current, radial_current = self.frame_for(self.index)
        following, radial_following = self.frame_for(nxt)
        self.im.set_data(current if blend == 0 else (1-blend)*current+blend*following)
        self.line.set_ydata((1-blend)*radial_current+blend*radial_following)
        n, l, m = self.states[self.index]
        self.info.set_text(
            f'Orbital {self.name(self.index)}\n'
            f'n = {n}    l = {l}    m = {m:+d}\n'
            f'Energía ≈ {-13.605693/n**2:.4f} eV\n'
            f'Nodos radiales: {n-l-1} · angulares: {l}\n'
            f'Ventana: ±{4*n*n} a₀\n'
            f'Estado {self.index+1} de {len(self.states)}')
        if fraction > 0:
            self.status.set_text(f'Fundido: {self.name(self.index)} → {self.name(nxt)}'
                                 f'   ·   {fraction:.0%}   ·   escala ajustándose')
        else:
            self.status.set_text(f'Recorrido automático · Siguiente: {self.name(nxt)}'
                                 '   ·   +m y −m tienen la misma densidad')
        return self.artists()

    def advance(self, dt):
        """Avance determinista, también usado para comprobar el recorrido completo."""
        duration = self.HOLD+self.FADE
        self.elapsed += dt
        steps = int(self.elapsed/duration)
        if steps:
            self.index = (self.index+steps) % len(self.states)
            self.elapsed %= duration
        return self.render()

    def tick(self, _=None):
        now = perf_counter()
        dt = min(max(now-self.last_time, 0.), .1)*self.speed.val
        self.last_time = now
        if self.running:
            return self.advance(dt)
        return self.artists()

    def toggle(self, _=None):
        self.running = not self.running
        self.last_time = perf_counter()
        self.button.label.set_text('Pausar' if self.running else 'Continuar')
        self.fig.canvas.draw_idle()

    def restart(self, _=None):
        self.index, self.elapsed = 0, 0.
        self.last_time = perf_counter()
        self.render()
        self.fig.canvas.draw_idle()

    def keypress(self, event):
        if event.key == ' ':
            self.toggle()
        elif event.key in ('r', 'R'):
            self.restart()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--guardar', metavar='IMAGEN.png', help='Guarda una vista sin abrir ventana.')
    args = parser.parse_args()
    if args.guardar:
        import matplotlib
        matplotlib.use('Agg')
    sim = Simulator(animate=not bool(args.guardar))
    if args.guardar:
        sim.fig.savefig(args.guardar,dpi=150,facecolor=sim.fig.get_facecolor())
    else:
        sim.plt.show()


if __name__ == '__main__':
    main()
