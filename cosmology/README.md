# Cosmology and astrophysics simulations

Three interactive browser scenes for exploring compact objects and cosmic-ray showers. The Python scripts launch a local server; the accompanying HTML files contain the complete visualization. All three work offline and use no third-party Python packages.

| Simulation | Launcher | Scene |
| --- | --- | --- |
| Horizon: black hole, accretion disk, and gravitational lensing | `agujero_negro.py` | `agujero_negro.html` |
| Pulsar: neutron star, magnetic field, and emission beams | `estrella_neutrones.py` | `estrella_neutrones.html` |
| Cascade: cosmic-ray atmospheric showers | `rayos_cosmicos.py` | `rayos_cosmicos.html` |

## Requirements and setup

- Python 3 to use a launcher.
- A modern browser with **WebGL 2** and graphics acceleration enabled.
- The `.py` and matching `.html` file must stay together in this folder.

From the repository root, enter this folder:

```powershell
cd cosmology
```

All commands below run **inside `cosmology`**. There is nothing to install with `pip`; `requirements.txt` records that no additional packages are needed. On Windows, if your installation uses the `py` command, replace `python` with `py`.

You can also open any of the three HTML files directly in your browser, without Python or a running server.

## Run a simulation

```powershell
python agujero_negro.py
```

```powershell
python estrella_neutrones.py
```

```powershell
python rayos_cosmicos.py
```

Each launcher opens the browser and prints its local URL. Keep that terminal open while using the scene. Press **Ctrl+C** in the terminal to stop the server. If the browser does not open automatically, copy the printed URL into its address bar.

### Command-line options

All three launchers have the same options:

| Option | Default | Purpose |
| --- | --- | --- |
| `-h`, `--help` | — | Print usage and exit. |
| `--no-browser` | Off | Start the server without opening a browser. Open the printed URL yourself. |
| `--port PORT` | `0` | Set the local port. `0` lets the operating system choose an available port. Valid values: integers from `0` to `65535`. A chosen nonzero port must be available. |

Examples, using the black-hole scene:

```powershell
python agujero_negro.py --help
python agujero_negro.py --no-browser
python agujero_negro.py --port 8080
python agujero_negro.py --no-browser --port 8080
```

Use the same options with either of the other filenames. The server listens on `127.0.0.1` and serves only its simulation, rather than the other files in the folder. Reload the browser after editing the HTML.

## Shared controls

| Action | Control |
| --- | --- |
| Orbit the camera | Drag across the scene |
| Zoom | Mouse wheel |
| Pause or resume | **Space**, or the playback button |
| Hide or show the interface | **H**, or the presentation button |
| Enter or exit fullscreen | **F**, or the fullscreen button |
| Reset or replay | **R**; see the scene-specific behavior below |

For a presentation, frame the view, hide the interface with **H**, and enter fullscreen with **F**. Keyboard shortcuts can be ignored while an input or selection control has focus; click the scene first.

## Horizon: black hole

The scene shows an accretion disk and background stars around a spherical, nonrotating black hole. Gravitational lensing bends the apparent disk into multiple views.

| Setting | Initial value | Available values |
| --- | --- | --- |
| Camera elevation | `16°` | `4°`–`85°` |
| Distance | `16 rₛ` | `11`–`28 rₛ` |
| Brightness | `1.10` | `0.30`–`2.50` |
| Disk speed | `1.00×` | `0`–`2.00×` |
| Gravitational lensing | On | On/off; **L** toggles it |
| Show light rays | Off | On/off; **T** toggles it |
| Quality | Automatic | Automatic, High, Medium, Low |

**R** resets the view and resumes animation. **Photo ↓** saves a PNG of the rendered scene through your browser; the terminal has no image-export option.

### Model and limits

The renderer uses exterior **Schwarzschild** geometry and fourth-order Runge–Kutta integration of light trajectories. Distances use Schwarzschild radii (`rₛ`), with the event horizon at `r = rₛ`. Disk brightness includes gravitational and Doppler shifts for circular orbits. Turning lensing off compares this with straight rays and an absorbing sphere.

The thin disk's texture, colors, and motion are procedural. This is an explanatory visualization: it does not calculate plasma dynamics, full spectral transfer, light-path time delays, or the rotational spacetime effects of a Kerr black hole. Colors are not temperature measurements.

## Pulsar: neutron star

The scene shows a material stellar surface, a tilted magnetic dipole, rotating emission beams, and a relative beam-signal monitor. Explore the pulsar lighthouse effect by changing the magnetic tilt and viewing angle.

| Setting | Initial value | Available values |
| --- | --- | --- |
| Camera elevation | `26°` | `−75°`–`85°` |
| Distance | `8.5 R` | `6`–`16 R` |
| Spin speed | `0.65×` | `0`–`2.00×` |
| Magnetic tilt | `58°` | `0°`–`90°` |
| Brightness | `1.00` | `0.30`–`2.50` |
| Compactness (`rₛ/R`) | About `0.345` | `0.15`–`0.46` |
| Light bending | On | On/off; **L** toggles it |
| Magnetic field | On | On/off; **M** toggles it |
| Pulse monitor | On | On/off; **T** toggles it |
| Quality | Automatic | Automatic, High, Medium, Low |

**R** resets the view and resumes animation. **Photo ↓** saves a PNG of the rendered scene through your browser.

### Model and limits

The stellar radius is fixed at **12 km**. Compactness is `rₛ/R`; changing it changes the corresponding mass, with a default near **1.40 solar masses**. Camera distances use stellar radii (`R`). These are representative parameters, rather than measurements of a specific star.

Light bending integrates exterior Schwarzschild null geodesics using fourth-order Runge–Kutta, stopping rays at the material surface. Surface brightness includes a static gravitational redshift factor. Dipole field guides, procedural thermal colors, and beam scattering illustrate the geometry; they do not form a plasma or full radiative-transfer simulation.

Spin is slowed for viewing. Its slider sets visual rotation, rather than a physical period or the spacetime metric. Rotational metric effects and light travel-time delays are omitted. The pulse monitor displays geometric beam alignment over **one rotation**, with illustrative relative amplitude; it is not calibrated flux or a timeline in physical seconds.

## Cascade: cosmic rays

The scene follows a primary particle into the atmosphere and visualizes representative secondary tracks. Change the primary, energy, or zenith angle to generate a new shower and compare particle families.

| Setting | Initial value | Available values |
| --- | --- | --- |
| Primary | Proton | Proton, helium nucleus, iron nucleus, photon, electron |
| Energy | `1 PeV` (`10¹⁵ eV`) | `1 eV`–about `316 EeV`; logarithmic slider |
| Zenith angle | `15°` | `0°`–`65°` |
| Playback speed | `1.00×` | `0.20×`–`2.50×` |
| Particle labels | On | On/off |
| Interaction markers | On | On/off |
| Event progress | Starts at entry | `0`–`100%`; dragging it pauses playback |

- **R** replays the current event; **N** or **New shower** generates another random event. Completed events automatically advance to a new shower.
- Energy preset buttons select GeV, TeV, PeV, EeV, or 100 EeV.
- Click a particle-family chip to highlight photons, electrons, positrons, muons, hadrons, or neutrinos and read its explanation. Click it again to restore the full view.
- **How it works** and **Sources** explain shower processes and candidate accelerators. On narrow screens, **Learn & sources** opens the explanation panel.

### Model and limits

One unit on the energy slider multiplies the primary energy by ten. Charged primaries use kinetic energy; photons use photon energy. Nuclear kinetic energy is shared across nucleons, and the interface displays energy per nucleon.

Low-energy events show simplified deposition or passage, without an extensive cascade. Hadronic branching is enabled around **1 GeV per nucleon**, as an illustrative model boundary. Photons below **1.022 MeV** do not create electron–positron pairs in the scene; developed electromagnetic branching is enabled around **80 MeV**.

This is a statistical teaching visualization. Representative tracks are normalized for clarity and capped at **3,300**; their count is not the physical secondary-particle yield. A developed iron shower represents its 56 nucleons with nine initial bundles. Altitudes are schematic, lateral spread is expanded, and playback speed is set for viewing. Calibrated interaction lengths, energy spectra, detector responses, rigorous particle transport, and rare muon-producing electromagnetic channels are omitted.

Source cards discuss possible accelerators. They do not assign a displayed event to a confirmed source; the origins of the rarest ultrahigh-energy cosmic rays remain unresolved.

## Performance and troubleshooting

- If the scene cannot initialize WebGL 2, enable graphics acceleration in your browser and reload, or try another browser that supports it.
- For Horizon and Pulsar, leave **Quality** on Automatic, or select Medium/Low if the view is slow. Performance also depends on your GPU and window size.
- If Python reports that the simulation cannot be read, restore the matching HTML file beside its launcher.
- If a requested port is occupied, omit `--port` or use another available port.
- Image capture is available in Horizon and Pulsar through **Photo ↓**. Cascade has no built-in PNG-export button; use a browser or operating-system screenshot.
