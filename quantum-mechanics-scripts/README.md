# Quantum mechanics and quantum fields

Five interactive Python visualizations introduce wave packets, hydrogen orbitals, quantum fields, and quark interactions. The well, tunneling, and hydrogen interfaces are in Spanish; the quantum-field and QCD interfaces are in English. The original filenames are retained.

## Install and run

Use Python 3.10 or newer. From the cloned repository's root, enter this folder and install its dependencies:

```powershell
cd quantum-mechanics-scripts
python -m pip install -r requirements.txt
```

If you already installed the repository's root `requirements.txt`, you can skip the installation step. **Run every command below from this folder.** On Windows, you can replace `python` with `py` if that is your installed Python launcher. Interactive use requires a desktop display and a Matplotlib GUI backend; image export works without opening a window.

| Program | Command | What it shows |
|---|---|---|
| Infinite well | `python atomo_pozo_infinito.py` | Reflection, dispersion, and interference of a confined wave packet |
| Quantum tunneling | `python efecto_tunel.py` | A packet meeting a finite rectangular barrier |
| Hydrogen orbitals | `python orbitales_hidrogeno.py` | An automatic tour of 91 stationary states |
| Quantum fields | `python campos_cuanticos.py` | Field, Packet, Quanta, Vacuum, and Coupling chapters |
| QCD and quark flavors | `python cromodinamica_cuantica.py` | Color exchange, six quark flavors, and neutron beta decay |

Keep `cuantica_animacion.py` beside the well and tunneling entry points. Keep `campos_cuanticos_modelos.py` beside `campos_cuanticos.py`. These two files are shared modules, rather than separate applications. All five entry points accept `-h` or `--help` to display their command-line options.

## Infinite well and tunneling

Both applications show probability density `|psi|²` above the real and imaginary parts of the wavefunction. The cloud represents probability, rather than a particle trajectory.

### Controls

| Control | Action |
|---|---|
| **Pausar / Continuar**, or **Space** | Pause or resume |
| **Reiniciar**, or lowercase **r** | Return to time zero and resume |
| **Velocidad** | Set speed between **0.2× and 3×**, initially **1×** |
| Matplotlib toolbar | Save a picture, pan, and zoom |

Both request 60 frames per second. The simulation advances a fixed amount of model time per frame, multiplied by the speed setting; actual playback speed depends on your computer and graphics backend.

### Command-line options

The options below apply to both `atomo_pozo_infinito.py` and `efecto_tunel.py`.

| Option | Default | Meaning |
|---|---|---|
| `--tiempo NUMBER` | `0` | Initial model time; must be finite and nonnegative |
| `--guardar FILE.png` | No file; open a window | Save a still image and exit without opening a window |

Examples:

```powershell
python efecto_tunel.py --tiempo 18 --guardar tunneling.png
python atomo_pozo_infinito.py --tiempo 1.5 --guardar infinite-well.png
python atomo_pozo_infinito.py --tiempo 180
```

**Infinite well:** the one-dimensional center of mass of an atom is free inside a box of length `L = 12` with impenetrable walls. The program uses a superposition of 100 sine states and evolves their exact phases. It omits the atom's internal structure and electrons. The wavefunction vanishes at both walls. The full packet revival time is `4 L² / pi ≈ 183.35`.

**Tunneling:** a Gaussian packet with mean energy about `2.01` meets a barrier of height `2.3` and width `1.3`. The code solves the Schrödinger equation using spectral Strang splitting, with internal steps no larger than `0.009`, without renormalizing the packet every frame. Its wide computational domain is periodic. Playback stops at `t = 34` to avoid the main packet returning through the opposite boundary; larger `--tiempo` values are limited to `34`. The percentages refer to the left region, barrier, and right region. They represent reflection and transmission after the outgoing packets have separated. The packet contains a spread of energies, including a small contribution above the barrier.

Both use dimensionless units with `hbar = m = 1`. For physical length scale `ell` and mass `M`, the time unit is `M ell² / hbar` and the energy unit is `hbar² / (M ell²)`.

## Hydrogen orbitals

```powershell
python orbitales_hidrogeno.py
python orbitales_hidrogeno.py --guardar hydrogen.png
```

The automatic tour covers all 91 states with `n = 1..6`, `l = 0..n-1`, and `m = -l..l`, then returns to `1s`. At **1×**, each state stays visible for two seconds and fades into the next over one second. A relative-density xz cross-section appears beside the radial probability curve and state information.

| Control | Action |
|---|---|
| **Pausar / Continuar**, or **Space** | Pause or resume the tour |
| **Reiniciar**, or **r / R** | Return to `1s`, preserving whether playback was paused |
| **Velocidad** | Set speed between **0.2× and 3×**, initially **1×** |

| Option | Default | Meaning |
|---|---|---|
| `--guardar FILE.png` | No file; open a window | Save the initial `1s` view and exit |

There are no command-line or manual quantum-number selectors. The model is nonrelativistic, with a fixed nucleus and no external fields. Distances are displayed in units of `n² a0`, so the spatial scale changes between states; the window size in Bohr radii is shown on screen. The slice and radial curve are each normalized to their own maximum. The fade blends pictures at their respective scales; it illustrates a change of view rather than physical excitation of the atom. States with opposite signs of `m` have the same density.

## Quantum fields

```powershell
python campos_cuanticos.py
python campos_cuanticos.py --scene packet
python campos_cuanticos.py --save quantum-fields.png --scene packet --time 6
```

| Chapter (`--scene`) | Duration at 1× | Main idea |
|---|---:|---|
| `field` | 16 s | A scalar field assigns a value to every position |
| `packet` | 18 s | Many modes combine into a traveling disturbance |
| `quanta` | 20 s | A bosonic mode has discrete excitation energies |
| `vacuum` | 18 s | The ground state has uncertainty even with no quanta |
| `coupling` | 16 s | An interaction transfers an excitation between two modes |

| Option | Default | Meaning |
|---|---|---|
| `--scene NAME` | `field` | Starting chapter; choose a name from the table above |
| `--time NUMBER` | `0` | Illustrative seconds within that chapter; finite and nonnegative |
| `--save FILE.png` | No file; open a window | Save a still image and exit |

`--time` wraps within the selected chapter's duration. These durations control the presentation pace, rather than laboratory timescales.

| Control | Action |
|---|---|
| Chapter buttons, or **1–5** | Select a chapter and reset its clock |
| **Pause / Resume**, or **Space** | Pause or resume |
| **Restart**, or **r / R** | Return to the Field chapter |
| **Automatic tour ON / OFF**, or **a / A** | Toggle automatic chapter changes, initially on |
| **Speed** | Set speed between **0.25× and 2×**, initially **1×** |

With automatic changes off, the chosen chapter loops. Chapter selection and restart preserve the pause state and automatic-tour setting.

### What the model represents

- **Field and Packet:** classical solutions of a free Klein–Gordon scalar field, also interpretable as the mean field of a coherent quantum state. The periodic square has side `24`, a `48 × 48` grid, mass parameter `0.7`, and natural units `c = hbar = 1`. The field height and squared height are not single-particle position probabilities. Teal and purple indicate positive and negative field values, rather than electric charges.
- **Quanta:** separately prepared number states `n = 0..4` of one bosonic oscillator mode, with `E_n = (n + 1/2) hbar omega`. Changing examples does not show spontaneous jumps. The normalized curve describes a dimensionless mode quadrature, an amplitude-like observable, rather than a particle's position. A fermionic mode instead permits zero or one excitation.
- **Vacuum:** possible equal-time field measurement configurations from this finite model. Independent Gaussian samples are smoothly blended as `A cos(theta) + B sin(theta)` to preserve covariance. Consecutive pictures are correlated illustrations rather than physical vacuum evolution or particles appearing and disappearing. The finite cutoff affects the variance and zero-point energy; this illustration makes no prediction about dark energy.
- **Coupling:** two resonant bosonic modes exchange one excitation through `H_int = hbar g (a†b + ab†)`, starting in `|1,0>`. Occupation probabilities are `cos²(gt)` and `sin²(gt)` and sum to one. The rings show probabilities, rather than fractional particles. This solvable model is not a Standard Model scattering calculation.

## Quantum chromodynamics and quark flavors

```powershell
python cromodinamica_cuantica.py
python cromodinamica_cuantica.py --scene weak
python cromodinamica_cuantica.py --save qcd-colors.png --scene colors --time 2.5
```

| Chapter (`--scene`) | Duration at 1× | Main idea |
|---|---:|---|
| `colors` | 30 s | Six color exchanges between the valence quarks of a proton (`uud`) |
| `flavors` | 24 s | The six quark flavors and their generations |
| `weak` | 16 s | A schematic of neutron beta decay |

| Option | Default | Meaning |
|---|---|---|
| `--scene NAME` / `--escena NAME` | `colors` | Starting chapter: `colors`, `flavors`, or `weak`; aliases `colores`, `sabores`, and `debil` also work |
| `--time NUMBER` / `--tiempo NUMBER` | `0` | Illustrative seconds within the chapter; finite and nonnegative |
| `--save FILE.png` / `--guardar FILE.png` | No file; open a window | Save a still image and exit |

`--time` wraps within the selected chapter's duration. All timing describes the presentation pace rather than physical timescales.

| Control | Action |
|---|---|
| **Colors / Flavors / Weak**, or **1 / 2 / 3** | Select a chapter and reset its clock |
| **Pause / Resume**, or **Space** | Pause or resume |
| **Restart**, or **r / R** | Return to the Colors chapter |
| **Automatic tour ON / OFF**, or **a / A** | Toggle automatic chapter changes, initially on |
| **Speed** | Set speed between **0.25× and 2×**, initially **1×** |

With automatic changes off, the chosen chapter loops. Chapter selection and restart preserve the pause state and automatic-tour setting.

### What to watch and model limits

Color, flavor, and electric charge are different properties. Red, green, and blue name quantum color-charge states rather than optical colors. A quark–gluon vertex changes color while preserving flavor. Gluon labels show color–anticolor flow. QCD has eight independent SU(3) gluon states; the animation illustrates off-diagonal exchanges rather than all possible states.

The flavor chapter shows `(u, d)`, `(c, s)`, and `(t, b)` in three generations. The first member of each pair has charge `+2/3 e`, and the second `-1/3 e`. Any flavor can carry any color; antiquarks have anticolor and opposite electric charge. The top quark decays before hadronization.

The weak chapter illustrates `d -> u + virtual W-`, followed by `virtual W- -> electron + electron antineutrino`, producing `n -> p + e- + anti-nu_e`. Color is retained at the weak vertex and electric charge is conserved. The virtual W and displayed paths are a teaching schematic rather than measurable trajectories.

The program does not solve QCD equations or calculate decay probabilities. Positions, sizes, and paths are chosen for clarity. The three circles show valence content; a real proton also includes gluons and quark–antiquark pairs. Its color-singlet state is a quantum superposition of color permutations, beyond a picture of three fixed-colored circles.

## Image export and troubleshooting

Export commands above produce still images, rather than videos, and do not open a GUI window. Relative filenames are saved in your current terminal folder. Use an existing output folder when supplying a path. Matplotlib's interactive toolbar can also save the current view.

- **`python` is not recognized:** install Python, reopen the terminal, and use `py` on Windows if available.
- **`No module named numpy` or `matplotlib`:** run `python -m pip install -r requirements.txt` with the same interpreter used to launch the script.
- **A shared module is missing:** keep all seven Python files together in this folder.
- **No interactive window in a remote or headless session:** use the image-export option, or run locally with a GUI-enabled Python installation.

## Existing rendering checks

The `tests` folder contains seven QFT regression tests that check changing animation frames, actual button events, automatic chapter changes, pause/restart, resizing, speed, and image-export recovery without opening a GUI:

```powershell
python -m unittest discover -s tests -v
```

## Further reading

- [NIST DLMF: Coulomb radial functions](https://dlmf.nist.gov/18.39)
- [David Tong: free fields and quantization](https://www.damtp.cam.ac.uk/user/tong/qft/qfthtml/S2.html)
- [MIT: quantum harmonic oscillator](https://ocw.mit.edu/courses/8-04-quantum-physics-i-spring-2013/808334d09369e3a726f6f20d82315c20_MIT8_04S13_Lec08.pdf)
- [MIT: single photons and beam splitters](https://ocw.mit.edu/courses/8-422-atomic-and-optical-physics-ii-spring-2013/resources/lecture-5-single-photons-part-1/)
- [CERN: the Standard Model](https://home.web.cern.ch/science/physics/standard-model/)
- [PDG: QCD](https://pdg.lbl.gov/2024/reviews/rpp2024-rev-qcd.pdf), [quark model](https://pdg.lbl.gov/2024/reviews/rpp2024-rev-quark-model.pdf), [top quark](https://pdg.lbl.gov/2024/reviews/rpp2024-rev-top-quark.pdf), and [CKM matrix](https://pdg.lbl.gov/2024/reviews/rpp2024-rev-ckm-matrix.pdf)
