# BOUNCING BALL SIMULATOR — V4.0 FINAL CONSOLIDATED SPECIFICATION

## 1. Coordinate System Correction
Use an upward-positive vertical coordinate system throughout the application:
- Ground level: $y = 0$
- Ball center at rest: $y = \text{radius}$
- Upward velocity: positive ($v > 0$)
- Downward velocity: negative ($v < 0$)
- Gravitational acceleration: $-g$ ($g \approx 9.80665 \text{ m/s}^2$ or $9.8 \text{ m/s}^2$)

Initial ball-center position:
$$y_{\text{initial}} = h_{\text{initial}} + \text{radius}$$

This coordinate system must be used consistently in physics calculations, visualization, graphs, and analytical validation.

---

## 2. Free-Fall Equations
Use semi-implicit Euler (symplectic Euler) numerical integration:
$$v_{\text{new}} = v_{\text{old}} - g \times dt$$
$$y_{\text{new}} = y_{\text{old}} + v_{\text{new}} \times dt$$

---

## 3. Time-of-Impact (TOI) Handling
The ball collides with the ground when its center reaches:
$$y = \text{radius}$$

Within each timestep, solve:
$$0.5 \times g \times t^2 - v \times t - (y - \text{radius}) = 0$$

Choose the smallest physically valid positive root:
$$0 \le t^* \le dt$$

Before accepting the root, verify:
$$y + v \times t^* - 0.5 \times g \times (t^*)^2 \approx \text{radius}$$

At impact, calculate the actual impact velocity:
$$v_{\text{impact}} = v - g \times t^*$$

Apply restitution:
$$v_{\text{after}} = -e \times v_{\text{impact}}$$

Advance the remaining timestep:
$$\text{remaining\_dt} = dt - t^*$$

Continue the simulation using the updated velocity. Set the ball center exactly to $y = \text{radius}$ at contact.

---

## 4. Resting and Grazing Contact
If:
$$y \approx \text{radius} \quad \text{AND} \quad |v| < \text{SETTLE\_VELOCITY}$$

Then:
- Set $y = \text{radius}$
- Set $v = 0$
- Add remaining kinetic energy to cumulative dissipated energy
- Skip further collision detection while resting

Do not generate repeated collision events for a resting ball.
If no valid collision root exists within the timestep, continue normal free-fall integration.

---

## 5. Energy Accounting
- Potential energy:
  $$\text{PE} = m \times g \times (y - \text{radius})$$
- Kinetic energy:
  $$\text{KE} = 0.5 \times m \times v^2$$
- Total mechanical energy:
  $$E = \text{KE} + \text{PE}$$
- Collision energy loss:
  $$\Delta E = 0.5 \times m \times (1 - e^2) \times v_{\text{impact}}^2$$
- Settling energy loss:
  $$E_{\text{settle}} = 0.5 \times m \times v^2$$

Energy-budget tolerance must scale with timestep size. Document that numerical integration error is expected and decreases as $dt$ is reduced.

---

## 6. Experiment Reporting
Every experiment terminates when:
- The ball settles, OR
- Simulation time reaches 30 seconds.

For simulations that reach the 30-second limit without settling (e.g. $e = 1.0$):
- Report settling status as `"Did not settle"`.
- Report settling time as `">30 seconds"`.
- Record all collisions observed within the simulation period.

---

## 7. Additional Verification Tests
- **TOI test:** Verify the first collision time against $t = \sqrt{2h/g}$. Verify impact position equals the ball radius.
- **Event-cap test:** Verify that pathological collision conditions terminate without hanging.
- **Performance test:** Benchmark a 30-second simulation at 30 FPS on the reference machine. Record the result in `README.md`.
- **CSV test:** Verify consistent column names and valid numerical output.
- **Rendering independence:** Verify that 10 FPS and 60 FPS rendering produce identical physical simulation results for identical simulation durations (physics timestep decoupling).

---

## 8. Output File Handling
- Overwrite `results/simulation_data.csv` at the start of each new interactive simulation session.
- Save each experiment to its designated CSV file in `results/`.
- Store generated graphs under `reports/figures/`.
- Ensure experiment CSVs contain one row per tested parameter value.

---

## 9. Documentation Requirements
The technical report must explain:
- Why upward-positive coordinates were selected.
- How time-of-impact collision detection works.
- How restitution affects energy.
- Why semi-implicit Euler does not guarantee exact energy conservation.
- How numerical results were validated against analytical predictions.
- Embed all generated figures, including `validation.png`.

---

## 10. Specification Precedence
V4.0 supersedes all previous versions wherever instructions conflict.
