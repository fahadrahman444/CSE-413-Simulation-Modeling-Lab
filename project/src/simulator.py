"""Discrete-time physics simulation engine for Bouncing Ball Simulator V4.0.

Implements:
- Upward-positive coordinate system
- Semi-implicit Euler integration
- Sub-timestep Time-of-Impact (TOI) quadratic collision detection
- Restitution and energy dissipation accounting
- Resting and grazing contact handling
- Event-cap safeguard against infinite chattering
- Export to simulation_data.csv and experiment formats
"""

from dataclasses import dataclass, field
import os
from typing import Dict, List, Optional
import pandas as pd

from .physics import (
    calculate_collision_energy_loss,
    calculate_mechanical_energy,
    find_time_of_impact,
    semi_implicit_euler_step,
)


@dataclass
class BallState:
    """Current state of the simulated ball."""
    time: float
    y: float
    v: float
    pe: float
    ke: float
    mechanical_energy: float
    dissipated_energy: float
    total_energy: float
    is_settled: bool
    collision_count: int


@dataclass
class SimulationConfig:
    """Configuration parameters for the simulation."""
    initial_height: float = 10.0  # Height above ground surface (m)
    radius: float = 0.1          # Ball radius (m)
    mass: float = 1.0            # Mass (kg)
    restitution: float = 0.75    # Coefficient of restitution e in [0, 1]
    gravity: float = 9.8         # Acceleration due to gravity g (m/s^2)
    dt: float = 0.002            # Physics timestep (s)
    max_time: float = 30.0       # Max simulation duration (s)
    settle_velocity: float = 0.08  # Velocity threshold below which contact settles (m/s)
    max_sub_events_per_step: int = 15  # Safety cap against Zeno / chattering freeze


@dataclass
class CollisionRecord:
    """Detailed record of an individual collision event."""
    collision_id: int
    time: float
    impact_position: float
    impact_velocity: float
    rebound_velocity: float
    energy_loss: float


class BouncingBallSimulator:
    """Simulation runner and state container."""

    def __init__(self, config: Optional[SimulationConfig] = None):
        self.config = config or SimulationConfig()
        self.reset()

    def reset(self) -> None:
        """Reset the simulator to initial conditions."""
        cfg = self.config
        self.current_time = 0.0
        # Initial ball-center position: y_initial = h_initial + radius
        self.y = cfg.initial_height + cfg.radius
        self.v = 0.0
        self.dissipated_energy = 0.0
        self.is_settled = False
        self.settle_time: Optional[float] = None
        self.collision_count = 0
        self.collisions: List[CollisionRecord] = []
        self.history: List[BallState] = []

        # Record initial state at t = 0
        pe, ke, me = calculate_mechanical_energy(
            self.y, self.v, cfg.mass, cfg.radius, cfg.gravity
        )
        self.initial_total_energy = me
        self.history.append(
            BallState(
                time=0.0,
                y=self.y,
                v=self.v,
                pe=pe,
                ke=ke,
                mechanical_energy=me,
                dissipated_energy=0.0,
                total_energy=me,
                is_settled=False,
                collision_count=0,
            )
        )

    def step(self, dt: Optional[float] = None) -> BallState:
        """Advance the simulation by one timestep dt."""
        cfg = self.config
        step_dt = dt if dt is not None else cfg.dt

        # If already resting, remain at rest and advance time
        if self.is_settled:
            self.current_time += step_dt
            self.y = cfg.radius
            self.v = 0.0
            pe, ke, me = calculate_mechanical_energy(
                self.y, self.v, cfg.mass, cfg.radius, cfg.gravity
            )
            state = BallState(
                time=self.current_time,
                y=self.y,
                v=0.0,
                pe=pe,
                ke=ke,
                mechanical_energy=me,
                dissipated_energy=self.dissipated_energy,
                total_energy=me + self.dissipated_energy,
                is_settled=True,
                collision_count=self.collision_count,
            )
            self.history.append(state)
            return state

        remaining_dt = step_dt
        sub_events = 0

        while remaining_dt > 1e-14 and not self.is_settled:
            # Event-cap safeguard to prevent pathological infinite chattering
            if sub_events >= cfg.max_sub_events_per_step:
                if abs(self.y - cfg.radius) < 1e-3:
                    self._settle(remaining_dt)
                else:
                    self.y, self.v = semi_implicit_euler_step(
                        self.y, self.v, cfg.gravity, remaining_dt
                    )
                    self.current_time += remaining_dt
                remaining_dt = 0.0
                break

            toi = find_time_of_impact(
                y=self.y,
                v=self.v,
                radius=cfg.radius,
                g=cfg.gravity,
                dt=remaining_dt,
            )

            if toi is None:
                # No collision within remaining timestep -> normal free fall
                self.y, self.v = semi_implicit_euler_step(
                    self.y, self.v, cfg.gravity, remaining_dt
                )
                if self.y < cfg.radius:
                    self.y = cfg.radius
                self.current_time += remaining_dt
                remaining_dt = 0.0
            else:
                # Collision detected at t* within current timestep
                t_star = toi
                self.current_time += t_star
                remaining_dt -= t_star

                # Ball position exactly at radius at contact
                self.y = cfg.radius
                # Actual impact velocity
                v_impact = self.v - cfg.gravity * t_star

                # Check resting / grazing contact condition
                if abs(v_impact) < cfg.settle_velocity:
                    self._settle(remaining_dt, v_residual=v_impact)
                    remaining_dt = 0.0
                    break

                # Apply restitution
                v_after = -cfg.restitution * v_impact
                if abs(v_after) < cfg.settle_velocity:
                    self._settle(remaining_dt, v_residual=v_after)
                    remaining_dt = 0.0
                    break

                loss = calculate_collision_energy_loss(cfg.mass, cfg.restitution, v_impact)
                self.dissipated_energy += loss
                self.collision_count += 1
                self.collisions.append(
                    CollisionRecord(
                        collision_id=self.collision_count,
                        time=self.current_time,
                        impact_position=self.y,
                        impact_velocity=v_impact,
                        rebound_velocity=v_after,
                        energy_loss=loss,
                    )
                )

                # Set post-collision state
                self.v = v_after
                sub_events += 1

        pe, ke, me = calculate_mechanical_energy(
            self.y, self.v, cfg.mass, cfg.radius, cfg.gravity
        )
        state = BallState(
            time=self.current_time,
            y=self.y,
            v=self.v,
            pe=pe,
            ke=ke,
            mechanical_energy=me,
            dissipated_energy=self.dissipated_energy,
            total_energy=me + self.dissipated_energy,
            is_settled=self.is_settled,
            collision_count=self.collision_count,
        )
        self.history.append(state)
        return state

    def _settle(self, remaining_time: float = 0.0, v_residual: float = 0.0) -> None:
        """Handle transition to resting state."""
        cfg = self.config
        self.is_settled = True
        self.settle_time = self.current_time
        self.y = cfg.radius
        residual_v = v_residual if v_residual != 0.0 else self.v
        e_settle = 0.5 * cfg.mass * (residual_v**2)
        self.dissipated_energy += e_settle
        self.v = 0.0
        self.current_time += remaining_time

    def run(self) -> Dict[str, any]:
        """Run simulation until settlement or reaching max_time (30.0s)."""
        cfg = self.config
        while self.current_time < (cfg.max_time - 1e-12) and not self.is_settled:
            step_dt = min(cfg.dt, cfg.max_time - self.current_time)
            if step_dt <= 1e-12:
                break
            self.step(step_dt)

        if self.is_settled:
            settling_status = "Settled"
            settling_time_str = f"{self.settle_time:.4f}"
        else:
            settling_status = "Did not settle"
            settling_time_str = ">30 seconds"

        summary = {
            "initial_height": cfg.initial_height,
            "restitution": cfg.restitution,
            "mass": cfg.mass,
            "radius": cfg.radius,
            "gravity": cfg.gravity,
            "dt": cfg.dt,
            "final_time": self.current_time,
            "settling_status": settling_status,
            "settling_time": settling_time_str,
            "total_collisions": self.collision_count,
            "initial_energy": self.initial_total_energy,
            "final_dissipated_energy": self.dissipated_energy,
            "final_mechanical_energy": self.history[-1].mechanical_energy if self.history else 0.0,
            "final_total_energy": self.history[-1].total_energy if self.history else 0.0,
        }
        return summary

    def to_dataframe(self) -> pd.DataFrame:
        """Export simulation trajectory history to a pandas DataFrame."""
        records = [
            {
                "time": s.time,
                "position_y": s.y,
                "velocity": s.v,
                "potential_energy": s.pe,
                "kinetic_energy": s.ke,
                "mechanical_energy": s.mechanical_energy,
                "dissipated_energy": s.dissipated_energy,
                "total_energy": s.total_energy,
                "is_settled": int(s.is_settled),
                "collision_count": s.collision_count,
            }
            for s in self.history
        ]
        return pd.DataFrame.from_records(records)

    def export_csv(self, filepath: str) -> str:
        """Save history DataFrame to CSV file, ensuring directories exist."""
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        df = self.to_dataframe()
        df.to_csv(filepath, index=False)
        return filepath
