# Educational Scripts

A growing collection of educational visualizations and creative animations. Documentation is in English; the original filenames, command-line flags, and most on-screen labels are in Spanish.

## Explore the collection

| Folder | What you will find | Instructions |
| --- | --- | --- |
| [`cosmology`](cosmology/) | Black hole, neutron star, and cosmic ray visualizations in the browser. | [Cosmology README](cosmology/README.md) |
| [`quantum-mechanics-scripts`](quantum-mechanics-scripts/) | Infinite potential well, quantum tunneling, hydrogen orbitals, quantum fields, and quantum chromodynamics visualizations. | [Quantum mechanics README](quantum-mechanics-scripts/README.md) |
| [`heart`](heart/) | Animated 3D rose and beating heart, with PNG and GIF export. | [Heart and rose README](heart/README.md) |

Each folder has its own README with terminal commands, features, options, controls, and model limitations. Start there after downloading the repository.

## Get the repository

Open a terminal in the location where you want to save this collection, then run:

```sh
git clone https://github.com/SEKKENX/educational-scripts.git
cd educational-scripts
```

This creates an `educational-scripts` folder containing the collection. Cloning requires Git. If the terminal reports that `git` is not recognized, install [Git](https://git-scm.com/downloads), reopen the terminal, and check `git --version`. You can also use **Code > Download ZIP** on GitHub and extract the archive.

To update an existing clone, open a terminal inside `educational-scripts` and run `git pull`.

## Requirements

- Python 3.10 or newer.
- NumPy and Matplotlib for quantum mechanics and creative animations; Pillow for GIF export.
- A desktop graphical backend for interactive Matplotlib windows.
- A modern browser with WebGL 2 and hardware acceleration for the cosmology visualizations. These use Python's standard library and do not need pip packages.

Install all Python dependencies from the repository root:

```sh
python -m pip install -r requirements.txt
```

You can instead install only a category's dependencies using its own `requirements.txt`; see the corresponding README. On Windows, use `py` if `python` is unavailable. On macOS/Linux, you may need `python3`.

For an isolated installation, create an environment with `python -m venv .venv`. Activate it with `.\.venv\Scripts\Activate.ps1` in PowerShell, `.venv\Scripts\activate.bat` in Windows Command Prompt, or `source .venv/bin/activate` on macOS/Linux before installing dependencies.
