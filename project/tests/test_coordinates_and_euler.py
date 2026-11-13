"""Comprehensive tests for Coordinate System and Semi-Implicit Euler equations (Sections 1 & 2)."""

import pytest
from project.src.physics import semi_implicit_euler_step
from project.src.simulator import BouncingBallSimulator, SimulationConfig


def test_upward_positive_coordinate_convention():
    """Verify upward-positive coordinate system: ground y=0, ball center at y=radius."""
    cfg = SimulationConfig(initial_height=8.0, radius=0.15)
    sim = BouncingBallSimulator(cfg)

    # Initial ball-center position must be h_initial + radius
    assert sim.y == 8.0 + 0.15
    # Velocity starts at zero
    assert sim.v == 0.0

    # After one free-fall step, gravity (-g) should produce negative velocity
    state = sim.step(dt=0.01)
    assert state.v < 0.0, "Downward velocity must be negative in upward-positive coordinates"
    assert state.y < (8.0 + 0.15), "Ball position must decrease under gravity -g"


def test_semi_implicit_euler_discrete_step():
    """Verify semi-implicit Euler equations: v_new = v_old - g*dt, y_new = y_old + v_new*dt."""
    y_old = 10.0
    v_old = -2.0
    g = 9.8
    dt = 0.05

    v_expected = v_old - g * dt  # -2.0 - 0.49 = -2.49
    y_expected = y_old + v_expected * dt  # 10.0 + (-2.49 * 0.05) = 10.0 - 0.1245 = 9.8755

    y_new, v_new = semi_implicit_euler_step(y_old, v_old, g, dt)

    assert pytest.approx(v_expected, rel=1e-7) == v_new
    assert pytest.approx(y_expected, rel=1e-7) == y_new


def test_upward_velocity_sign():
    """Verify upward motion has positive velocity (v > 0)."""
    cfg = SimulationConfig(initial_height=1.0, radius=0.1, restitution=0.9, dt=0.001)
    sim = BouncingBallSimulator(cfg)

    # Let the ball fall and bounce
    bounced = False
    for _ in range(1000):
        sim.step()
        if sim.collision_count >= 1 and sim.v > 0:
            bounced = True
            break

    assert bounced is True, "Rebound must have positive upward velocity (v > 0)"
