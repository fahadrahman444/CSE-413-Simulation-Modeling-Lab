"""Interactive live 2D animation for Bouncing Ball Simulator V4.0.

Displays:
- Left panel: Physical 2D bouncing ball with ground plane (y = 0) and contact line (y = radius).
- Top right panel: Real-time position y(t) trajectory.
- Bottom right panel: Real-time energy breakdown (PE, KE, Dissipated).
"""

import sys
import os

repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Circle
import numpy as np

from project.src.simulator import BouncingBallSimulator, SimulationConfig


def run_live_animation(height: float = 10.0, restitution: float = 0.75, dt: float = 0.005):
    """Launch an interactive live animation of the simulation."""
    cfg = SimulationConfig(
        initial_height=height,
        restitution=restitution,
        radius=0.15,
        mass=1.0,
        gravity=9.8,
        dt=dt,
        max_time=25.0,
    )
    sim = BouncingBallSimulator(cfg)
    summary = sim.run()
    df = sim.to_dataframe()

    times = df["time"].to_numpy()
    ys = df["position_y"].to_numpy()
    vs = df["velocity"].to_numpy()
    pes = df["potential_energy"].to_numpy()
    kes = df["kinetic_energy"].to_numpy()
    ediss = df["dissipated_energy"].to_numpy()

    # Downsample frames for smooth ~30-60 FPS playback
    skip = max(1, int(0.02 / dt))
    frame_indices = list(range(0, len(times), skip))
    if frame_indices[-1] != len(times) - 1:
        frame_indices.append(len(times) - 1)

    fig = plt.figure(figsize=(12, 7))
    fig.canvas.manager.set_window_title("CSE 413: Bouncing Ball Simulator V4.0 — Live Visualizer")

    gs = fig.add_gridspec(2, 2, width_ratios=[1.2, 1.8], height_ratios=[1, 1])
    ax_ball = fig.add_subplot(gs[:, 0])
    ax_traj = fig.add_subplot(gs[0, 1])
    ax_energy = fig.add_subplot(gs[1, 1])

    # 1. Physical Ball Simulation View
    ax_ball.set_xlim(-1.0, 1.0)
    ax_ball.set_ylim(-0.2, height * 1.15 + cfg.radius)
    ax_ball.axhline(0, color="brown", lw=4, label="Ground (y=0)")
    ax_ball.axhline(cfg.radius, color="gray", linestyle="--", lw=1.2, label=f"Contact (y={cfg.radius:.2f}m)")
    ax_ball.set_title("Physical Simulation Space", fontweight="bold")
    ax_ball.set_ylabel("Vertical Position y (meters)")
    ax_ball.set_xticks([])
    ax_ball.grid(True, linestyle=":", alpha=0.6)
    ax_ball.legend(loc="upper right")

    ball_patch = Circle((0.0, ys[0]), cfg.radius, color="royalblue", zorder=5)
    ax_ball.add_patch(ball_patch)
    info_text = ax_ball.text(
        0.05, 0.05, "", transform=ax_ball.transAxes,
        fontsize=10, bbox=dict(boxstyle="round", facecolor="white", alpha=0.8)
    )

    # 2. Trajectory View
    ax_traj.set_xlim(0, max(times))
    ax_traj.set_ylim(0, height * 1.15 + cfg.radius)
    ax_traj.set_title("Live Position Trajectory y(t)", fontweight="bold")
    ax_traj.set_xlabel("Time (s)")
    ax_traj.set_ylabel("Height (m)")
    ax_traj.grid(True, linestyle="--", alpha=0.5)
    (traj_line,) = ax_traj.plot([], [], color="crimson", lw=2, label="y(t)")
    traj_point, = ax_traj.plot([], [], "bo", markersize=6)
    ax_traj.legend(loc="upper right")

    # 3. Energy View (Bar chart)
    ax_energy.set_title("Energy Breakdown (Joules)", fontweight="bold")
    ax_energy.set_ylim(0, summary["initial_energy"] * 1.15)
    categories = ["Potential (PE)", "Kinetic (KE)", "Dissipated", "Total Account"]
    colors = ["forestgreen", "goldenrod", "firebrick", "black"]
    bars = ax_energy.bar(categories, [pes[0], kes[0], ediss[0], pes[0] + kes[0] + ediss[0]], color=colors)
    ax_energy.grid(True, axis="y", linestyle=":", alpha=0.6)

    plt.tight_layout()

    def update(frame_idx):
        idx = frame_indices[frame_idx]
        cur_t = times[idx]
        cur_y = ys[idx]
        cur_v = vs[idx]
        cur_pe = pes[idx]
        cur_ke = kes[idx]
        cur_diss = ediss[idx]
        cur_tot = cur_pe + cur_ke + cur_diss

        # Update ball position
        ball_patch.center = (0.0, cur_y)
        info_text.set_text(
            f"Time: {cur_t:.2f} s\n"
            f"Height: {cur_y:.2f} m\n"
            f"Velocity: {cur_v:+.2f} m/s\n"
            f"Restitution: {restitution:.2f}"
        )

        # Update trajectory
        traj_line.set_data(times[:idx + 1], ys[:idx + 1])
        traj_point.set_data([cur_t], [cur_y])

        # Update energy bars
        vals = [cur_pe, cur_ke, cur_diss, cur_tot]
        for bar, val in zip(bars, vals):
            bar.set_height(val)

        return ball_patch, info_text, traj_line, traj_point, *bars

    anim = animation.FuncAnimation(
        fig,
        update,
        frames=len(frame_indices),
        interval=25,
        blit=False,
        repeat=True,
    )
    plt.show()


if __name__ == "__main__":
    run_live_animation()
