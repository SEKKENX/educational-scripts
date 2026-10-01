
from pathlib import Path
import argparse
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.colors import to_rgb


def suave(t):
    t = np.clip(t, 0, 1)
    return t * t * (3 - 2 * t)


def petalo(angulo, capa, resolucion):
    
    u, v = np.meshgrid(np.linspace(0, 1, resolucion),
                       np.linspace(-1, 1, resolucion))
    largo = 0.64 + capa * 0.32
    radio = 0.08 + capa * 0.085 + largo * u ** 1.35
    ancho = (0.32 + capa * 0.13) * np.sin(np.pi * u * 0.86) ** 0.8
    lateral = ancho * v
    z = (0.10 + (1.28 - capa * 0.12) * np.sin(u * np.pi * 0.66)
         - 0.23 * v ** 2 * u + 0.055 * np.cos(v * np.pi * 2) * u ** 5)
    x = radio * np.cos(angulo) - lateral * np.sin(angulo)
    y = radio * np.sin(angulo) + lateral * np.cos(angulo)
    return x, y, z, u, v


def crear_rosa(rapido=False, giro=True):
    fig = plt.figure(figsize=(8, 8), facecolor='black')
    ax = fig.add_subplot(111, projection='3d', facecolor='black')
    fig.subplots_adjust(0, 0, 1, 1)
    ax.set(xlim=(-2, 2), ylim=(-2, 2), zlim=(-2.6, 1.7))
    ax.set_box_aspect((4, 4, 4.3))
    ax.set_axis_off()
    ax.view_init(elev=23, azim=-65)
    titulo = fig.text(0.5, 0.94, 'Una rosa para ti', color='#ffacd2',
                      ha='center', fontsize=23, fontfamily='serif')
    fig.text(0.5, 0.045, 'ESPACIO: pausar / continuar', color='#90647b',
             ha='center', fontsize=9)
    resolucion = 15 if rapido else 25
    petalos = []
    for capa, cantidad in enumerate((4, 5, 7, 9)):
        for k in range(cantidad):
            angulo = k * 2 * np.pi / cantidad + capa * 1.18
            petalos.append((capa, petalo(angulo, capa, resolucion)))
    superficies = []
    tallo, = ax.plot([], [], [], color='#328957', linewidth=5)
    hojas = []

    def dibujar(frame):
        for superficie in superficies + hojas:
            superficie.remove()
        superficies.clear()
        hojas.clear()
        t = frame / 179
        crecimiento = suave(t / 0.22)
        s = np.linspace(0, crecimiento, 65)
        tallo.set_data_3d(0.09 * np.sin(s * np.pi), np.zeros_like(s), -2.5 + 2.5 * s)
        # Las hojas crecen junto con el tallo.
        for lado, altura in ((1, -1.65), (-1, -1.05)):
            g = suave((t - 0.12) / 0.18)
            u, v = np.meshgrid(np.linspace(0, 1, 18), np.linspace(-1, 1, 9))
            x = lado * 0.95 * u * g
            y = 0.25 * np.sin(np.pi * u) * v * g
            z = altura + (0.55 * u + 0.13 * np.sin(np.pi * u) * (1 - v*v)) * g
            if g > 0:
                hojas.append(ax.plot_surface(x, y, z, color='#287b46',
                                             linewidth=0, antialiased=True))
        # Desde el centro hacia afuera, cada pétalo se despliega suavemente.
        for i, (capa, datos) in enumerate(petalos):
            g = suave((t - 0.22 - i * 0.019) / 0.22)
            if g <= 0:
                continue
            x, y, z, u, v = datos
            base = np.array(to_rgb(('#d92d79', '#ed458e', '#f568a7', '#ff8cbd')[capa]))
            luz = np.clip(0.69 + 0.24 * u + 0.08 * np.cos(v * np.pi), 0, 1)
            colores = np.ones((*u.shape, 4))
            colores[..., :3] = base * luz[..., None]
            superficies.append(ax.plot_surface(x * g, y * g, z * g,
                                facecolors=colores, shade=True, linewidth=0,
                                antialiased=True, rstride=1, cstride=1))
        if giro:
            ax.view_init(elev=23, azim=-65 + 38 * t)
        titulo.set_alpha(0.5 + 0.5 * suave(t / 0.3))
        return [tallo, titulo, *superficies, *hojas]

    return fig, dibujar


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--guardar', type=Path, help='Exportar la animación como GIF')
    parser.add_argument('--imagen', type=Path, help='Guardar la rosa completa como PNG')
    parser.add_argument('--rapido', action='store_true', help='Menos detalle')
    parser.add_argument('--sin-giro', action='store_true', help='Mantener fija la cámara')
    args = parser.parse_args()
    fig, dibujar = crear_rosa(args.rapido, not args.sin_giro)
    if args.imagen:
        dibujar(179)
        fig.savefig(args.imagen, dpi=180, facecolor='black')
        print(f'Imagen guardada en: {args.imagen.resolve()}')
    if args.guardar or not args.imagen:
        animacion = FuncAnimation(fig, dibujar, frames=range(210), interval=50,
                                  blit=False, repeat=True, repeat_delay=1400,
                                  cache_frame_data=False)
        pausada = False

        def teclado(event):
            nonlocal pausada
            if event.key == ' ':
                pausada = not pausada
                animacion.pause() if pausada else animacion.resume()

        fig.canvas.mpl_connect('key_press_event', teclado)
        if args.guardar:
            animacion.save(args.guardar, writer=PillowWriter(fps=20), dpi=100)
            print(f'Animación guardada en: {args.guardar.resolve()}')
        else:
            plt.show()
    plt.close(fig)


if __name__ == '__main__':
    main()
