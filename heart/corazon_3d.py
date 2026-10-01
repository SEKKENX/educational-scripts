
import argparse
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.colors import LightSource


def crear_corazon(rapido=False, giro=True):
    fig = plt.figure(figsize=(8, 8), facecolor='black')
    ax = fig.add_subplot(111, projection='3d', facecolor='black')
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
    ax.set(xlim=(-1.25, 1.25), ylim=(-0.9, 0.9), zlim=(-1.25, 1.15))
    ax.set_box_aspect((2.5, 1.8, 2.4))
    ax.set_axis_off()
    fig.text(0.5, 0.91, 'Un corazón para ti', ha='center',
             color='#ff9fc9', fontsize=24, fontfamily='serif')
    fig.text(0.5, 0.07, 'ESPACIO: pausar / continuar', ha='center',
             color='#ad728e', fontsize=10)
    n = 65 if rapido else 121
    theta, phi = np.meshgrid(np.linspace(0, 2 * np.pi, n),
                             np.linspace(0, np.pi, n // 2))
    # El contorno clásico de corazón se ensancha en profundidad.
    x = np.sin(theta) ** 3 * np.sin(phi)
    y = 0.48 * np.cos(phi)
    z = ((13 * np.cos(theta) - 5 * np.cos(2 * theta)
          - 2 * np.cos(3 * theta) - np.cos(4 * theta)) / 16) * np.sin(phi)
    superficie = None

    def dibujar(frame):
        nonlocal superficie
        if superficie is not None:
            superficie.remove()
            superficie = None
        progreso = np.clip(frame / 139, 0, 1)
        suave = progreso ** 2 * (3 - 2 * progreso)
        limite = z.min() + (z.max() - z.min() + 0.04) * suave
        visible = z <= limite
        # Una vez completo, late suavemente.
        latido = 1 + (0.035 * np.sin((frame - 139) * 2 * np.pi / 30)
                      if frame > 139 else 0)
        if np.any(visible) and frame > 0:
            superficie = ax.plot_surface(
                np.where(visible, x * latido, np.nan), y * latido, z * latido,
                color='#ff529b', linewidth=0, edgecolor='none',
                antialiased=False, shade=True,
                lightsource=LightSource(azdeg=315, altdeg=40),
                rstride=1, cstride=1)
        angulo = -90 + 22 * np.sin(frame * 2 * np.pi / 240) if giro else -75
        ax.view_init(elev=12, azim=angulo)
        return [] if superficie is None else [superficie]

    return fig, dibujar


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--guardar', type=Path, help='Exportar como GIF')
    parser.add_argument('--imagen', type=Path, help='Guardar imagen del corazón completo')
    parser.add_argument('--rapido', action='store_true', help='Reducir detalle')
    parser.add_argument('--sin-giro', action='store_true', help='Cámara fija')
    args = parser.parse_args()
    fig, dibujar = crear_corazon(args.rapido, not args.sin_giro)
    if args.imagen:
        dibujar(139)
        fig.savefig(args.imagen, dpi=160, facecolor='black')
        print(f'Imagen guardada en: {args.imagen.resolve()}')
    if args.guardar or not args.imagen:
        animacion = FuncAnimation(fig, dibujar, frames=200, interval=50,
                                  repeat=True, repeat_delay=1000,
                                  blit=False, cache_frame_data=False)
        pausada = False

        def teclado(event):
            nonlocal pausada
            if event.key == ' ':
                pausada = not pausada
                animacion.pause() if pausada else animacion.resume()

        fig.canvas.mpl_connect('key_press_event', teclado)
        if args.guardar:
            animacion.save(args.guardar, writer=PillowWriter(fps=20), dpi=90)
            print(f'Animación guardada en: {args.guardar.resolve()}')
        else:
            plt.show()
    plt.close(fig)


if __name__ == '__main__':
    main()
