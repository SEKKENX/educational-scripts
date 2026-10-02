"""Small, reproducible models for a quantum-field teaching animation.

Natural units are used: hbar = c = 1.  The field lives on a finite,
periodic two-dimensional square.  A travelling wave or wave packet is a
classical solution, equivalently the mean field of a coherent state; it is
not the position wavefunction of a single particle.  Vacuum configurations
are independent samples of an equal-time probability distribution, not a
movie of particles appearing and disappearing.
"""

from __future__ import annotations

import numbers

import numpy as np


def _finite_real(value: float, name: str) -> float:
    """Convert a real scalar and reject nonfinite or nonscalar input."""
    if isinstance(value, (bool, np.bool_)) or not isinstance(value, numbers.Real):
        raise ValueError(f"{name} must be a finite real number")
    result = float(value)
    if not np.isfinite(result):
        raise ValueError(f"{name} must be a finite real number")
    return result


class FreeScalarField:
    """Spectral free Klein-Gordon field with a finite ultraviolet cutoff.

    ``size`` samples each side of a periodic square of side ``length``.
    ``mass`` must be positive: a massless finite-volume zero mode has no
    normalizable oscillator vacuum and is deliberately excluded here.
    Arrays use NumPy's ``meshgrid(..., indexing='xy')`` convention.
    """

    def __init__(self, size: int = 48, length: float = 24.0, mass: float = 0.7):
        if (isinstance(size, (bool, np.bool_))
                or not isinstance(size, numbers.Integral) or size < 8):
            raise ValueError("size must be an integer of at least 8")
        self.size = int(size)
        self.length = _finite_real(length, "length")
        self.mass = _finite_real(mass, "mass")
        if self.length <= 0 or self.mass <= 0:
            raise ValueError("length and mass must be positive")
        self.dx = self.length / self.size
        self.x = np.linspace(-self.length / 2, self.length / 2,
                             self.size, endpoint=False)
        self.X, self.Y = np.meshgrid(self.x, self.x, indexing="xy")
        k = 2 * np.pi * np.fft.fftfreq(self.size, d=self.dx)
        self.kx, self.ky = np.meshgrid(k, k, indexing="xy")
        self.omega = np.sqrt(self.kx**2 + self.ky**2 + self.mass**2)
        self._mode_phase = 2 * np.pi * (2 * self.X + self.Y) / self.length
        self._mode_omega = np.sqrt(5 * (2 * np.pi / self.length)**2
                                   + self.mass**2)
        sigma = 2.2
        carrier = 2 * np.pi * 6 / self.length
        initial = np.exp(-((self.X + 6)**2 + self.Y**2) / (2 * sigma**2))
        initial = initial * np.exp(1j * carrier * self.X)
        self._packet_spectrum = np.fft.fft2(initial)
        self._vacuum_scale = 1 / (self.dx * np.sqrt(2 * self.omega))

    def mode(self, t: float) -> np.ndarray:
        """Return a unit-amplitude travelling mode with wave numbers (2, 1)."""
        t = _finite_real(t, "t")
        return np.cos(self._mode_phase - self._mode_omega * t)

    def _evolved_spectrum(self, t: float) -> np.ndarray:
        t = _finite_real(t, "t")
        return self._packet_spectrum * np.exp(-1j * self.omega * t)

    def packet(self, t: float) -> np.ndarray:
        """Return the real coherent-state mean using exact Fourier phases.

        The initial complex envelope has centre (-6, 0), width sigma=2.2,
        and carrier kx=2*pi*6/length.  Its real part and the positive-
        frequency prescription determine the initial field and momentum.
        The evolution is exact for the retained periodic Fourier modes.
        """
        return np.fft.ifft2(self._evolved_spectrum(t)).real

    def packet_momentum(self, t: float) -> np.ndarray:
        """Return the canonical momentum pi = d(phi)/dt, exactly."""
        return np.fft.ifft2(-1j * self.omega * self._evolved_spectrum(t)).real

    def packet_energy(self, t: float) -> float:
        """Return the conserved discrete free-field Hamiltonian.

        This is dx**2/2 times sum(pi**2 + |grad(phi)|**2 + m**2*phi**2).
        Parseval's identity evaluates the gradient terms spectrally, which
        also retains the Nyquist-mode energy on an even grid.  No vacuum
        zero-point contribution is included in this classical mean energy.
        """
        evolved = self._evolved_spectrum(t)
        phi = np.fft.ifft2(evolved).real
        momentum = np.fft.ifft2(-1j * self.omega * evolved).real
        phi_hat = np.fft.fft2(phi, norm="ortho")
        potential = np.sum(self.omega**2 * np.abs(phi_hat)**2)
        return float(0.5 * self.dx**2 * (np.sum(momentum**2) + potential))

    def vacuum_sample(self, seed: int) -> np.ndarray:
        """Draw a real equal-time configuration of the free-field vacuum.

        An orthonormal FFT of real white noise preserves Hermitian symmetry.
        Filtering by 1/(dx*sqrt(2*omega)) gives covariance

            <phi(x) phi(y)> = sum_k exp(i*k*(x-y))/(2*L**2*omega_k).

        This finite-grid distribution describes possible field measurement
        configurations.  Changing seeds does not describe time evolution.
        """
        if (isinstance(seed, (bool, np.bool_))
                or not isinstance(seed, numbers.Integral) or seed < 0):
            raise ValueError("seed must be a nonnegative integer")
        white = np.random.default_rng(int(seed)).standard_normal(
            (self.size, self.size))
        spectrum = np.fft.fft2(white, norm="ortho") * self._vacuum_scale
        return np.fft.ifft2(spectrum, norm="ortho").real

    @property
    def vacuum_variance(self) -> float:
        """Return <phi(x)**2> for this grid; it depends on the cutoff."""
        return float(np.sum(1 / (2 * self.omega))
                     / (self.size**2 * self.dx**2))


def oscillator_density(n: int, q: np.ndarray) -> np.ndarray:
    """Return the normalized oscillator density |psi_n(q)|**2.

    q = sqrt(omega/hbar) * mode_coordinate is dimensionless; this is a
    probability density for a field-mode amplitude, not particle position.
    The normalized physicists' Hermite recurrence avoids factorials and
    maintains stable values for levels 0 through 20.
    """
    if (isinstance(n, (bool, np.bool_))
            or not isinstance(n, numbers.Integral) or not 0 <= n <= 20):
        raise ValueError("n must be an integer between 0 and 20")
    q = np.asarray(q, dtype=float)
    if not np.all(np.isfinite(q)):
        raise ValueError("q must contain finite real values")
    with np.errstate(over="ignore"):
        previous = np.pi**(-0.25) * np.exp(-0.5 * q**2)
    if n == 0:
        return previous**2
    current = np.sqrt(2) * (q * previous)
    for level in range(1, int(n)):
        following = (np.sqrt(2 / (level + 1)) * (q * current)
                     - np.sqrt(level / (level + 1)) * previous)
        previous, current = current, following
    return current**2


def mode_transfer(t: float, g: float = 0.45) -> tuple[float, float]:
    """Return occupations of two resonantly coupled bosonic modes.

    For H_int = hbar*g*(a^dagger*b + b^dagger*a), initial state |1,0>
    evolves into cos(g*t)|1,0> - i*sin(g*t)|0,1>.  Occupations always sum
    to one.  This model transfers an existing quantum; its vacuum remains
    vacuum.  It is an idealized two-mode model, not a scattering simulation.
    """
    t = _finite_real(t, "t")
    g = _finite_real(g, "g")
    if g < 0:
        raise ValueError("g must be nonnegative")
    phase = g * t
    if not np.isfinite(phase):
        raise ValueError("g*t must remain finite")
    return float(np.cos(phase)**2), float(np.sin(phase)**2)
