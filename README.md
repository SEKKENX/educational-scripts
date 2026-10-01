# Educational Scripts

Interactive Python visualizations for learning quantum mechanics, plus animated 3D rose and heart drawings. Documentation is in English; the original scripts, on-screen labels, and command-line flags are in Spanish.

## Repository layout

```text
quantum-mechanics-scripts/
    atomo_pozo_infinito.py   # Atom in a 1D infinite potential well
    efecto_tunel.py          # Quantum tunneling through a finite barrier
    orbitales_hidrogeno.py   # Hydrogen orbital visualization
    cuantica_animacion.py    # Shared module required by the well and tunneling scripts
heart/
    rosa_3d.py               # Animated 3D rose
    corazon_3d.py            # Animated 3D heart
requirements.txt
```

## Installation

Install Python 3.10 or newer with a graphical desktop backend (Tk support is useful for Matplotlib). Open a terminal and run:

```sh
git clone https://github.com/SEKKENX/educational-scripts.git
cd educational-scripts
python -m pip install -r requirements.txt
```

On Windows, replace `python` with `py` if your installation uses the Python launcher. On macOS or Linux, you may need `python3`. If your Python installation requires a virtual environment, create one with `python -m venv .venv`, then activate it using `.venv\Scripts\activate.bat` in Windows Command Prompt, `.\.venv\Scripts\Activate.ps1` in PowerShell, or `source .venv/bin/activate` on macOS/Linux before installing dependencies.

All commands below run from the repository root. Exported files are saved in your current terminal directory. Close an animation window to exit.

## Quantum mechanics scripts

Run each visualization in its own window:

```sh
python quantum-mechanics-scripts/atomo_pozo_infinito.py
python quantum-mechanics-scripts/efecto_tunel.py
python quantum-mechanics-scripts/orbitales_hidrogeno.py
```

The well and tunneling scripts must remain alongside `cuantica_animacion.py`.

### Infinite well and tunneling options

| Option | Meaning |
| --- | --- |
| `--tiempo NUMBER` | Initial simulation time; default is 0. Must be finite and nonnegative. |
| `--guardar FILE.png` | Save a static image without opening a window. |
| `-h`, `--help` | Show command-line help. |

```sh
python quantum-mechanics-scripts/efecto_tunel.py --tiempo 18 --guardar tunneling.png
python quantum-mechanics-scripts/atomo_pozo_infinito.py --tiempo 1.5 --guardar well.png
python quantum-mechanics-scripts/atomo_pozo_infinito.py --tiempo 180
```

Controls: press **Space** or click **Pausar / Continuar** to pause/resume; press **R** or click **Reiniciar** to restart. The **Velocidad** slider adjusts speed from 0.2x to 3x. The Matplotlib toolbar supports zooming and saving images.

The tunneling model evolves a Gaussian wave packet across a rectangular barrier using a split-operator method. It stops at time 34 to avoid the packet returning through the periodic computational boundary. Regional probabilities describe reflection/transmission only after the collision has separated the packets; the initial packet contains a distribution of energies.

The infinite well models the one-dimensional center of mass of an atom, with impenetrable walls, using a superposition of 100 stationary states. It does not model the atom's internal electrons. Both models use dimensionless units with hbar = mass = 1. The top curve is probability density; the lower curves show the real and imaginary parts of the wave function.

### Hydrogen orbitals

The animation automatically cycles through all 91 states with principal quantum number n = 1 through 6. Each state is displayed for two seconds and blends into the next over one second at the default speed. Press **Space** to pause/resume and **R** or **Reiniciar** to return to 1s. Use **Velocidad** to adjust the cycle speed. Quantum numbers are selected automatically.

| Option | Meaning |
| --- | --- |
| `--guardar FILE.png` | Save a static view without opening a window. |
| `-h`, `--help` | Show command-line help. |

```sh
python quantum-mechanics-scripts/orbitales_hidrogeno.py --guardar hydrogen.png
```

The xz slice shows relative density, and the radial curve is normalized to its maximum. Axes use distances scaled by n squared times the Bohr radius. Blends are visual transitions between stationary states, not a physical excitation simulation. States with opposite m have identical probability densities.

## Rose and heart animations

```sh
python heart/rosa_3d.py
python heart/corazon_3d.py
```

The rose grows its stem and leaves before opening its pink petals. The heart forms from bottom to top and then beats gently. Both have a black background and a moving camera, and repeat automatically. Press **Space** to pause/resume.

Both scripts accept the same options:

| Option | Meaning |
| --- | --- |
| `--rapido` | Reduce rendering detail for faster drawing/export. |
| `--sin-giro` | Keep the camera fixed. |
| `--guardar FILE.gif` | Export the animation as a GIF. |
| `--imagen FILE.png` | Save a still image of the completed shape. |
| `-h`, `--help` | Show command-line help. |

```sh
python heart/rosa_3d.py --rapido
python heart/rosa_3d.py --sin-giro
python heart/rosa_3d.py --guardar rose.gif --rapido
python heart/rosa_3d.py --imagen rose.png
python heart/corazon_3d.py --guardar heart.gif --rapido
python heart/corazon_3d.py --imagen heart.png --sin-giro
```

GIF export may take several minutes. Animation smoothness depends on your computer and graphical backend. Image-only and GIF export finish without displaying an interactive window. For export on a machine without a display, set the `MPLBACKEND` environment variable to `Agg` (for example, `$env:MPLBACKEND = 'Agg'` in PowerShell).
