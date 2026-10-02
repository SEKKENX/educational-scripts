# Heart and Rose

Two animated 3D drawings on a black background:

- `rosa_3d.py`: the stem and leaves grow before 25 pink petals open from the center outward. The camera moves slowly and the animation repeats.
- `corazon_3d.py`: a pink heart forms from bottom to top, then beats gently. The camera moves and the animation repeats.

## Setup

From the repository root, enter this folder:

```sh
cd heart
python -m pip install -r requirements.txt
```

Requires Python 3.10 or newer, NumPy, Matplotlib, and Pillow. If you installed the root `requirements.txt`, the dependencies are already installed. On Windows, replace `python` with `py` if needed; on macOS/Linux, you may need `python3`.

All commands below run from the `heart` folder.

## Run an animation

```sh
python rosa_3d.py
python corazon_3d.py
```

Run one command at a time to open the chosen animation in its own window. Press **Space** to pause or resume; close the window to exit. An interactive Matplotlib backend is required to display a window.

## Command-line options

Both scripts accept the same options. Without any options they open the animation at full detail with camera movement enabled.

| Option | Meaning |
| --- | --- |
| `--rapido` | Reduce rendering detail for faster drawing and export. |
| `--sin-giro` | Disable automatic camera movement. |
| `--guardar FILE.gif` | Export the complete animation as a GIF and exit. |
| `--imagen FILE.png` | Save a still image of the completed shape and exit. |
| `-h`, `--help` | Show command-line help. |

```sh
python rosa_3d.py --rapido
python rosa_3d.py --sin-giro
python rosa_3d.py --guardar rose.gif --rapido
python rosa_3d.py --imagen rose.png
python corazon_3d.py --guardar heart.gif --rapido
python corazon_3d.py --imagen heart.png --sin-giro
```

You may combine options. Using `--imagen` and `--guardar` together exports both formats. Export paths are relative to the terminal's current folder; absolute paths also work. GIFs use 20 frames per second, and export may take several minutes. Animation smoothness depends on your computer and graphical backend.

For export without a desktop display, select the non-interactive backend first:

```powershell
# PowerShell
$env:MPLBACKEND = 'Agg'
python corazon_3d.py --imagen heart.png
```

```sh
# macOS/Linux
MPLBACKEND=Agg python corazon_3d.py --imagen heart.png
```

These are artistic parametric drawings, not physical simulations of flower growth or cardiac mechanics.

[Back to the collection](../README.md)
