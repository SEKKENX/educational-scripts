"""Motor visual y modelos 1D. Unidades adimensionales: hbar = masa = 1."""
import argparse
import numpy as np


class Tunel:
    titulo = 'EFECTO TÚNEL'
    subtitulo = 'Un paquete cuántico frente a una barrera finita'
    limite = 34.0
    paso = 0.045

    def __init__(self):
        self.x = np.linspace(-100, 100, 4096, endpoint=False)
        self.dx = self.x[1] - self.x[0]
        self.altura, self.ancho, self.k0 = 2.3, 1.3, 2.0
        self.v = self.altura * (np.abs(self.x) <= self.ancho / 2)
        self.k = 2 * np.pi * np.fft.fftfreq(len(self.x), self.dx)
        self.inicial = np.exp(-((self.x + 23) / 5)**2 / 2) * np.exp(1j*self.k0*self.x)
        self.inicial /= np.sqrt(np.sum(abs(self.inicial)**2)*self.dx)
        self.reiniciar()

    def reiniciar(self):
        self.t = 0.0
        self.psi = self.inicial.copy()

    def avanzar(self, dt):
        # Strang: medio paso en V, paso completo en T, medio paso en V.
        # Caja periódica amplia; se detiene antes de que llegue a sus bordes.
        dt = min(dt, self.limite-self.t)
        if dt <= 0:
            return
        n = max(1, int(np.ceil(dt/0.009)))
        h = dt/n
        pv = np.exp(-0.5j*self.v*h)
        pk = np.exp(-0.5j*self.k**2*h)
        for _ in range(n):
            self.psi = pv*np.fft.ifft(pk*np.fft.fft(pv*self.psi))
        self.t += dt

    def informacion(self):
        p = abs(self.psi)**2*self.dx
        izq = p[self.x < -self.ancho/2].sum()
        der = p[self.x > self.ancho/2].sum()
        return (f'Izquierda  {izq:6.1%}     Barrera  {1-izq-der:6.1%}     Derecha  {der:6.1%}',
                f'Energía media ≈ 2.01   •   Barrera = {self.altura:.2f}   •   ⟨x⟩ = {np.sum(self.x*p):.2f}')


class Pozo:
    titulo = 'ÁTOMO EN UN POZO INFINITO'
    subtitulo = 'Centro de masa libre en el interior · paredes impenetrables'
    limite = np.inf
    paso = 0.016

    def __init__(self):
        self.largo = 12.0
        self.x = np.linspace(0, self.largo, 1400)
        self.dx = self.x[1]-self.x[0]
        n = np.arange(1, 101)
        self.base = np.sqrt(2/self.largo)*np.sin(np.pi*np.outer(self.x, n)/self.largo)
        self.base[[0, -1], :] = 0
        self.energias = (n*np.pi/self.largo)**2/2
        inicial = np.exp(-0.5*((self.x-3.2)/0.65)**2)*np.exp(4j*self.x)
        self.coef = self.base.T @ inicial * self.dx
        self.coef /= np.linalg.norm(self.coef)
        self.revival = 4*self.largo**2/np.pi
        self.reiniciar()

    def reiniciar(self):
        self.t = 0.0
        self.psi = self.base @ self.coef

    def avanzar(self, dt):
        self.t += dt
        c = self.coef*np.exp(-1j*self.energias*self.t)
        # Productos reales evitan copiar toda la base a complejos en cada cuadro.
        self.psi = self.base @ c.real + 1j*(self.base @ c.imag)

    def informacion(self):
        p = abs(self.psi)**2*self.dx
        media = np.sum(self.x*p)
        sigma = np.sqrt(np.sum((self.x-media)**2*p))
        return (f'⟨x⟩ = {media:.2f}     Incertidumbre Δx = {sigma:.2f}     Probabilidad total = {p.sum():.6f}',
                f'Longitud L = 12   •   Energía media = {np.sum(abs(self.coef)**2*self.energias):.2f}   •   Revival = {self.revival:.2f}')


def ejecutar(tipo):
    parser = argparse.ArgumentParser(description='Animación cuántica 1D con controles interactivos.')
    parser.add_argument('--guardar', metavar='ARCHIVO.png', help='Guardar una imagen sin abrir ventana.')
    parser.add_argument('--tiempo', type=float, default=0, help='Tiempo inicial de la simulación.')
    args = parser.parse_args()
    if args.tiempo < 0 or not np.isfinite(args.tiempo):
        parser.error('--tiempo debe ser finito y no negativo')
    import matplotlib
    if args.guardar:
        matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.animation import FuncAnimation
    from matplotlib.widgets import Button, Slider
    from matplotlib.collections import PolyCollection

    modelo = tipo()
    if args.tiempo:
        modelo.avanzar(args.tiempo)
    tunel = isinstance(modelo, Tunel)
    fondo, panel, tinta = '#080f20', '#101c32', '#e7efff'
    cian, rosa, oro = '#40e3ed', '#e78acb', '#ffc76a'
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10,
                         'figure.facecolor': fondo, 'axes.facecolor': panel,
                         'text.color': tinta, 'axes.labelcolor': tinta,
                         'xtick.color': '#99abc8', 'ytick.color': '#99abc8',
                         'axes.edgecolor': '#34435e', 'savefig.facecolor': fondo})
    fig = plt.figure(figsize=(12.8, 8), layout=None)
    fig.canvas.manager.set_window_title(modelo.titulo)
    fig.text(.075, .944, modelo.titulo, size=23, weight='bold')
    fig.text(.075, .906, modelo.subtitulo, size=11, color='#99abc8')
    ax = fig.add_axes([.075, .49, .85, .34])
    onda = fig.add_axes([.075, .265, .85, .17], sharex=ax)
    for a in (ax, onda):
        a.spines[['top', 'right']].set_visible(False)
        a.grid(alpha=.10, color='#aec2e7')
    ax.set_ylabel('Densidad de probabilidad |ψ|²')
    onda.set_ylabel('Función de onda ψ')
    onda.set_xlabel('Posición x  ·  unidades adimensionales')
    plt.setp(ax.get_xticklabels(), visible=False)
    x = modelo.x
    ax.set_xlim((-65, 65) if tunel else (-.35, 12.35))
    ymax = .38 if tunel else 1.3
    ax.set_ylim(0, ymax)
    onda.set_ylim((-0.65, .65) if tunel else (-1.2, 1.2))
    if tunel:
        for a in (ax, onda):
            a.axvspan(-modelo.ancho/2, modelo.ancho/2, color=oro, alpha=.22)
        ax.text(0, ymax*.94, 'V₀', color=oro, ha='center')
        nota = 'Las probabilidades por región se interpretan como reflexión y transmisión tras separarse los paquetes.'
    else:
        for a in (ax, onda):
            for pared in (0, 12):
                a.axvline(pared, color=oro, lw=3)
        ax.text(.15, ymax*.91, 'V = ∞', color=oro)
        ax.text(11.85, ymax*.91, 'V = ∞', ha='right', color=oro)
        ax.text(6, ymax*.91, 'V = 0', color='#99abc8', ha='center')
        nota = 'La nube muestra probabilidad, no una trayectoria. Se omite la estructura interna del átomo.'
    relleno = PolyCollection([], facecolors=cian, alpha=.15, edgecolors='none')
    ax.add_collection(relleno)
    brillo, = ax.plot(x, abs(modelo.psi)**2, color=cian, lw=7, alpha=.10)
    densidad, = ax.plot(x, abs(modelo.psi)**2, color=cian, lw=2.2)
    real, = onda.plot(x, modelo.psi.real, color=cian, lw=1.4, label='Parte real')
    imag, = onda.plot(x, modelo.psi.imag, color=rosa, lw=1.3, label='Parte imaginaria')
    onda.legend(loc='upper right', facecolor=panel, edgecolor='none', labelcolor=tinta, ncol=2, fontsize=9)
    # Texto dentro de los ejes para que también se actualice con blitting.
    reloj = ax.text(.985, .80, '', transform=ax.transAxes, ha='right', color=tinta)
    resumen = fig.add_axes([.075, .14, .85, .067], facecolor=fondo)
    resumen.set_axis_off()
    estado = resumen.text(0, .70, '', transform=resumen.transAxes, color=cian, size=10)
    datos = resumen.text(0, .22, '', transform=resumen.transAxes, color='#99abc8', size=9)
    fig.text(.075, .035, nota, size=8.5, color='#99abc8')
    artistas = (relleno, brillo, densidad, real, imag, reloj, estado, datos)
    def dibujar():
        p = abs(modelo.psi)**2
        relleno.set_verts([np.column_stack((np.r_[x[0], x, x[-1]], np.r_[0, p, 0]))])
        brillo.set_ydata(p)
        densidad.set_ydata(p)
        real.set_ydata(modelo.psi.real)
        imag.set_ydata(modelo.psi.imag)
        reloj.set_text(f't = {modelo.t:6.2f}')
        texto, detalle = modelo.informacion()
        estado.set_text(texto)
        datos.set_text(detalle)
        return artistas
    dibujar()
    if args.guardar:
        fig.savefig(args.guardar, dpi=160)
        plt.close(fig)
        return
    pausa = Button(fig.add_axes([.075, .082, .12, .045]), 'Pausar', color=panel, hovercolor='#263c58')
    reset = Button(fig.add_axes([.21, .082, .12, .045]), 'Reiniciar', color=panel, hovercolor='#263c58')
    velocidad = Slider(fig.add_axes([.47, .092, .37, .022]), 'Velocidad', .2, 3, valinit=1, valfmt='%.1f×', color=cian)
    reproduciendo = [True]
    def alternar(event=None):
        reproduciendo[0] = not reproduciendo[0]
        pausa.label.set_text('Pausar' if reproduciendo[0] else 'Continuar')
        fig.canvas.draw_idle()
    def reiniciar(event=None):
        modelo.reiniciar()
        reproduciendo[0] = True
        pausa.label.set_text('Pausar')
        dibujar()
        fig.canvas.draw_idle()
    pausa.on_clicked(alternar)
    reset.on_clicked(reiniciar)
    def tecla(event):
        if event.key == ' ':
            alternar()
        elif event.key == 'r':
            reiniciar()
    fig.canvas.mpl_connect('key_press_event', tecla)
    def cuadro(_):
        if reproduciendo[0]:
            modelo.avanzar(modelo.paso*velocidad.val)
            if modelo.t >= modelo.limite:
                reproduciendo[0] = False
                pausa.label.set_text('Finalizado')
                fig.canvas.draw_idle()
        return dibujar()
    # Reutilización de artistas; sin limpiar ejes ni acumular cuadros en memoria.
    animacion = FuncAnimation(fig, cuadro, init_func=dibujar, interval=1000/60,
                              blit=fig.canvas.supports_blit, cache_frame_data=False)
    plt.show()
    return animacion
