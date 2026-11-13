"""Tests for Energy Accounting and Conservation Budget (Section 5)."""

import pytest
from project.src.physics import calculate_collision_energy_loss, calculate_mechanical_energy
from project.src.simulator import BouncingBallSimulator, SimulationConfig


def test_energy_formulas():
    """Verify mechanical and collision energy calculation formulas."""
    mass = 2.0
    radius = 0.1
    g = 9.8
    y = 5.1  # 5.0m above ground
    v = -4.0

    pe, ke, me = calculate_mechanical_energy(y, v, mass, radius, g)
    assert pytest.approx(mass * g * 5.0, rel=1e-7) == pe
    assert pytest.approx(0.5 * mass * (v**2), rel=1e-7) == ke
    assert pytest.approx(pe + ke, rel=1e-7) == me

    # Collision loss for e = 0.8
    e = 0.8
    v_impact = -10.0
    expected_loss = 0.5 * mass * (1.0 - e**2) * (v_impact**2)
    assert pytest.approx(expected_loss, rel=1e-7) == calculate_collision_energy_loss(mass, e, v_impact)


def test_energy_conservation_budget_with_restitution():
    """Verify that total energy accounting (mechanical + cumulative dissipated) is conserved within numerical tolerance."""
    cfg = SimulationConfig(
        initial_height=10.0,
        radius=0.1,
        mass=1.0,
        restitution=0.8,
        gravity=9.8,
        dt=0.001,
        max_time=10.0,
    )
    sim = BouncingBallSimulator(cfg)
    summary = sim.run()
    initial_e = summary["initial_energy"]

    df = sim.to_dataframe()
    # Total energy at all points: mechanical + dissipated
    max_drift = (df["total_energy"] - initial_e).abs().max()
    rel_error = max_drift / initial_e

    # Relative numerical integration error should be strictly under 2% for dt=0.001
    assert rel_error < 0.02, f"Energy drift too high: {rel_error * 100:.2f}%"


def test_energy_error_decreases_as_dt_is_reduced():
    """Verify that numerical integration error scales with timestep dt and decreases as dt is refined."""
    def get_max_energy_drift(dt_val: float) -> float:
        cfg = SimulationConfig(
            initial_height=10.0,
            radius=0.1,
            mass=1.0,
            restitution=0.8,
            gravity=9.8,
            dt=dt_val,
            max_time=4.0,
        )
        sim = BouncingBallSimulator(cfg)
        sim.run()
        df = sim.to_dataframe()
        return float((df["total_energy"] - sim.initial_total_energy).abs().max())

    drift_coarse = get_max_energy_drift(0.01)
    drift_fine = get_max_energy_drift(0.001)

    assert drift_fine < drift_coarse, (
        f"Expected finer dt to reduce energy error: coarse={drift_coarse:.4f}J, fine={drift_fine:.4f}J"
    )
