"""Physics constants, analytical equations, and numerical integrators for Bouncing Ball Simulator V4.0.

Coordinate System:
- Upward-positive vertical coordinate system
- Ground level: y = 0
- Ball center at rest: y = radius
- Upward velocity: positive (v > 0)
- Downward velocity: negative (v < 0)
- Gravitational acceleration: -g (g > 0)
- Initial ball-center position: y_initial = h_initial + radius
"""

import math
from typing import Optional, Tuple


def semi_implicit_euler_step(y: float, v: float, g: float, dt: float) -> Tuple[float, float]:
    """Perform one semi-implicit Euler integration step under uniform gravity.

    v_new = v_old - g * dt
    y_new = y_old + v_new * dt

    Args:
        y: Current vertical position of ball center (m)
        v: Current vertical velocity (m/s)
        g: Gravitational acceleration magnitude (m/s^2)
        dt: Timestep duration (s)

    Returns:
        Tuple of (y_new, v_new)
    """
    v_new = v - g * dt
    y_new = y + v_new * dt
    return y_new, v_new


def find_time_of_impact(
    y: float,
    v: float,
    radius: float,
    g: float,
    dt: float,
    tol: float = 1e-5,
) -> Optional[float]:
    """Solve for the exact time-of-impact (TOI) within the current timestep [0, dt].

    The ball collides with the ground when its center reaches:
        y(t) = radius

    Within the timestep under continuous gravity:
        y(t) = y + v * t - 0.5 * g * t^2 = radius
        0.5 * g * t^2 - v * t - (y - radius) = 0

    Equation: A * t^2 + B * t + C = 0
        A = 0.5 * g
        B = -v
        C = -(y - radius)

    The physical impact root corresponds to the downward contact trajectory:
        t* = (v + sqrt(v^2 + 2 * g * (y - radius))) / g

    Args:
        y: Current vertical position of ball center (m)
        v: Current vertical velocity (m/s)
        radius: Radius of the ball (m)
        g: Gravitational acceleration magnitude (m/s^2)
        dt: Timestep duration (s)
        tol: Tolerance for position verification at contact

    Returns:
        Smallest physically valid root t* in [0, dt], or None if no collision occurs.
    """
    delta_y = y - radius
    if delta_y < 0.0 and abs(delta_y) < 1e-12:
        delta_y = 0.0

    discriminant = v * v + 2.0 * g * delta_y
    if discriminant < 0.0:
        return None

    sqrt_disc = math.sqrt(discriminant)
    # The physically valid impact time where v(t*) = -sqrt_disc <= 0 (heading into ground)
    t_star = (v + sqrt_disc) / g

    # Check if root falls within [0, dt]
    root_eps = 1e-12
    if -root_eps <= t_star <= (dt + root_eps):
        t_clamped = max(0.0, min(float(t_star), dt))
        # Verify position at impact
        y_pred = y + v * t_clamped - 0.5 * g * (t_clamped**2)
        if abs(y_pred - radius) <= (tol + 1e-4):
            return t_clamped

    return None


def calculate_analytical_first_impact_time(h: float, g: float) -> float:
    """Calculate the theoretical analytical time to first collision from rest.

    t = sqrt(2 * h / g)

    Args:
        h: Drop height above the ground surface (m)
        g: Gravitational acceleration (m/s^2)

    Returns:
        Impact time in seconds
    """
    if h < 0:
        raise ValueError("Drop height h cannot be negative.")
    return math.sqrt(2.0 * h / g)


def calculate_mechanical_energy(y: float, v: float, mass: float, radius: float, g: float) -> Tuple[float, float, float]:
    """Calculate potential, kinetic, and total mechanical energy.

    PE = m * g * (y - radius)
    KE = 0.5 * m * v^2
    E  = KE + PE

    Args:
        y: Position of ball center (m)
        v: Velocity (m/s)
        mass: Mass of ball (kg)
        radius: Radius of ball (m)
        g: Gravitational acceleration (m/s^2)

    Returns:
        Tuple of (PE, KE, Total_Energy)
    """
    pe = max(0.0, mass * g * (y - radius))
    ke = 0.5 * mass * (v**2)
    return pe, ke, pe + ke


def calculate_collision_energy_loss(mass: float, restitution: float, v_impact: float) -> float:
    """Calculate kinetic energy lost during collision.

    Delta_E = 0.5 * m * (1 - e^2) * v_impact^2

    Args:
        mass: Mass of ball (kg)
        restitution: Coefficient of restitution e in [0, 1]
        v_impact: Impact velocity immediately prior to rebound (m/s)

    Returns:
        Dissipated energy (Joules)
    """
    return 0.5 * mass * (1.0 - restitution**2) * (v_impact**2)
