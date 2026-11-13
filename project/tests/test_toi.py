"""Tests for Time-of-Impact (TOI) calculation and contact positioning."""

import math
import pytest
from project.src.physics import calculate_analytical_first_impact_time, find_time_of_impact
from project.src.simulator import BouncingBallSimulator, SimulationConfig


def test_analytical_impact_time_formula():
    """Verify analytical formula t = sqrt(2h/g)."""
    h = 10.0
    g = 9.8
    expected = math.sqrt(2.0 * h / g)
    assert pytest.approx(expected, rel=1e-5) == calculate_analytical_first_impact_time(h, g)


def test_first_impact_time_and_position():
    """Verify numerical simulation detects first impact time and position accurately."""
    h0 = 10.0
    r = 0.1
    g = 9.8
    dt = 0.001

    cfg = SimulationConfig(
        initial_height=h0,
        radius=r,
        gravity=g,
        dt=dt,
        restitution=0.8,
        max_time=5.0,
    )
    sim = BouncingBallSimulator(cfg)

    # Expected first collision time
    t_expected = math.sqrt(2.0 * h0 / g)

    # Step until first collision is recorded
    first_col = None
    while sim.current_time < 3.0:
        sim.step()
        if len(sim.collisions) > 0:
            first_col = sim.collisions[0]
            break

    assert first_col is not None, "First collision was not recorded"
    # First collision time should match analytical t = sqrt(2h/g) within tight tolerance
    assert abs(first_col.time - t_expected) < dt * 1.5
    # Impact position must equal ball radius at contact
    assert pytest.approx(r, abs=1e-6) == first_col.impact_position


def test_substep_toi_precision():
    """Verify find_time_of_impact returns precise quadratic sub-timestep root."""
    g = 9.8
    r = 0.1
    # Ball dropping right before impact
    y_current = r + 0.05  # 5 cm above ground
    v_current = -5.0      # moving downwards
    dt = 0.02

    # Continuous trajectory: y(t) = y + v*t - 0.5*g*t^2 = r
    # 0.5*g*t^2 - v*t - (y - r) = 0
    # 4.9*t^2 + 5.0*t - 0.05 = 0
    toi = find_time_of_impact(y_current, v_current, r, g, dt)
    assert toi is not None
    assert 0.0 <= toi <= dt

    # Check predicted position at toi
    y_contact = y_current + v_current * toi - 0.5 * g * (toi**2)
    assert pytest.approx(r, abs=1e-5) == y_contact
