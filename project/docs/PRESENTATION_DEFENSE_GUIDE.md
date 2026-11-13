# 🎓 CSE 413: Project Viva & Presentation Defense Guide
## Bouncing Ball Simulator (V4.0 Final) — No-Slide Oral Defense

> **Student:** Md. Fahad Rahman (ID: 0432320005101071, Section B1)  
> **Course:** CSE 413 — Simulation & Modeling Lab  
> **Instructor:** Audity Ghosh, Lecturer, Dept. of CSE, UITS  

---

## 📌 Table of Contents
1. [The 30-Second Elevator Pitch](#1-the-30-second-elevator-pitch)
2. [High-Level Code Map (Where Everything Lives)](#2-high-level-code-map)
3. [Deep-Dive Code Walkthrough (How the Logic Works)](#3-deep-dive-code-walkthrough)
   - [A. Coordinate System & Ball Representation](#a-coordinate-system)
   - [B. Numerical Integration: Why Semi-Implicit Euler?](#b-semi-implicit-euler)
   - [C. Collision Detection: Time-of-Impact (TOI) Math](#c-time-of-impact-toi)
   - [D. Restitution, Energy Dissipation & Resting State](#d-restitution--resting-state)
   - [E. Preventing the Zeno Paradox (Event-Cap Safeguard)](#e-zeno-paradox--event-cap)
4. [Execution Flowchart: What Happens Inside Each `step()`](#4-execution-flowchart)
5. [Top 12 Viva / Defense Questions & Perfect Answers](#5-top-12-viva--defense-questions)
6. [Live Demo Script (What to Show on Screen)](#6-live-demo-script)

---

## 1. The 30-Second Elevator Pitch
*If your teacher starts by asking: "Tell me what your project is about and what makes it special?"*

> **Say this:**  
> *"Our project is a physically accurate discrete-event bouncing ball simulation. Many naive simulations suffer from ball tunneling, where a ball passes right through the floor, or unnatural energy gain that makes it bounce higher and higher.  
> To solve this, we implemented three key mechanisms:  
> 1. **Semi-implicit Euler integration** to preserve phase-space volume and avoid artificial energy explosion.  
> 2. **Sub-timestep Time-of-Impact (TOI)** using exact quadratic root solving, so collisions are detected at the exact microsecond of contact ($y = r$) without ground penetration.  
> 3. **Resting contact logic** with energy dissipation accounting to cleanly resolve the Zeno paradox when bounces become microscopic."*

---

## 2. High-Level Code Map
When the teacher asks: *"Show me your project structure and explain the responsibility of each module."*

```text
project/
├── src/
│   ├── physics.py          <-- Pure math & physics equations (no state, deterministic)
│   ├── simulator.py        <-- State manager, time-stepping loop, collision resolution
│   ├── experiments.py      <-- Runs parameter sweeps (e, height, dt) & exports CSVs
│   ├── visualization.py    <-- Generates analytical validation plots (validation.png)
│   └── animation.py        <-- Live interactive 2D GUI visualizer (Matplotlib animation)
├── tests/                  <-- 21 Pytest unit tests validating physics, TOI, CSV, and FPS
├── results/                <-- Output datasets (simulation_data.csv & experiment CSVs)
├── reports/                <-- Formal technical report & figures
└── main.py                 <-- CLI entry point for custom parameter simulations
```

---

## 3. Deep-Dive Code Walkthrough

### A. Coordinate System
**File:** [`project/src/physics.py`](file:///D:/sim/CSE-413-Simulation-Modeling-Lab/project/src/physics.py) and [`project/src/simulator.py`](file:///D:/sim/CSE-413-Simulation-Modeling-Lab/project/src/simulator.py)

* **Ground Level:** $y = 0$
* **Ball Surface Contact:** The center of the ball touches the ground when its center reaches $y = \text{radius}$.
* **Initial Position:** $y_0 = h_0 + \text{radius}$ (where $h_0$ is drop height above the floor).
* **Sign Convention:**
  * Upward position and velocity are **positive** ($+y, +v$).
  * Downward velocity is **negative** ($-v$).
  * Gravitational acceleration is downward: $\vec{a} = -g$ ($g = 9.8 \text{ m/s}^2$).

**Why this matters:**  
Potential energy is simply $PE = m \cdot g \cdot (y - \text{radius})$, which is zero when the ball touches the ground and strictly non-negative everywhere.

---

### B. Semi-Implicit Euler Integration
**Function:** `semi_implicit_euler_step(y, v, g, dt)` in [`physics.py`](file:///D:/sim/CSE-413-Simulation-Modeling-Lab/project/src/physics.py#L22-L38)

```python
def semi_implicit_euler_step(y, v, g, dt):
    v_new = v - g * dt         # 1. Update velocity first using current acceleration
    y_new = y + v_new * dt     # 2. Update position using NEW velocity
    return y_new, v_new
```

#### Why NOT standard Explicit Euler?
* In **Explicit Euler**: $y_{\text{new}} = y + v_{\text{old}} \cdot dt$.  
  In oscillatory systems, Explicit Euler constantly overestimates the area in phase space, meaning total mechanical energy artificially **increases** on every step until the simulation blows up!
* In **Semi-Implicit Euler (Symplectic Euler)**: by updating velocity *first* and then using $v_{\text{new}}$ to update position, the scheme is symplectic. It preserves phase-space volume and exhibits bounded, stable energy oscillations.

---

### C. Collision Detection: Time-of-Impact (TOI)
**Function:** `find_time_of_impact(y, v, radius, g, dt)` in [`physics.py`](file:///D:/sim/CSE-413-Simulation-Modeling-Lab/project/src/physics.py#L41-L93)

#### The Problem:
If $dt = 0.01$s, the ball might be at $y = 0.15$m at $t$, and by $t + dt$ it would end up at $y = 0.03$m (tunneling into the floor). Simply reversing the velocity at $t+dt$ causes artificial energy errors and incorrect bounce heights.

#### The Mathematical Solution:
We calculate the **exact fractional time $t^*$** within $[0, dt]$ when the bottom of the ball hits the floor:
$$y(t^*) = \text{radius}$$
Under uniform downward acceleration $-g$, continuous position is:
$$y(t) = y + v \cdot t - \frac{1}{2} g t^2 = \text{radius}$$
Rearranging into quadratic standard form $A t^2 + B t + C = 0$:
$$\frac{1}{2} g t^2 - v t - (y - \text{radius}) = 0$$
Where:
* $A = 0.5 \cdot g$
* $B = -v$
* $C = -(y - \text{radius})$

Discriminant:
$$D = B^2 - 4AC = v^2 + 2g(y - \text{radius})$$

The root representing downward collision into the ground is:
$$t^* = \frac{v + \sqrt{v^2 + 2g(y - \text{radius})}}{g}$$

#### In Code:
1. Check if $0 \le t^* \le dt$.
2. Advance ball to contact: set $y = \text{radius}$ exactly.
3. Compute exact instantaneous impact velocity:
   $$v_{\text{impact}} = v - g \cdot t^*$$
4. Apply coefficient of restitution $e$:
   $$v_{\text{after}} = -e \cdot v_{\text{impact}}$$
5. Deduct elapsed collision time: $\text{remaining\_dt} = dt - t^*$.
6. Free-fall integrate the remainder of the timestep with $v_{\text{after}}$.

---

### D. Restitution, Energy Dissipation & Resting State
**File:** [`simulator.py`](file:///D:/sim/CSE-413-Simulation-Modeling-Lab/project/src/simulator.py#L170-L215)

#### Energy Equations:
1. **Potential Energy:** $PE = m \cdot g \cdot (y - \text{radius})$
2. **Kinetic Energy:** $KE = \frac{1}{2} m v^2$
3. **Mechanical Energy:** $E_{\text{mech}} = PE + KE$
4. **Collision Dissipation:** $\Delta E_{\text{collision}} = \frac{1}{2} m (1 - e^2) v_{\text{impact}}^2$
5. **Settling Dissipation:** $E_{\text{settle}} = \frac{1}{2} m v^2$
6. **Total System Energy Budget:**  
   $$E_{\text{total}} = E_{\text{mech}} + E_{\text{dissipated}} \equiv E_{\text{initial}}$$

#### When Does the Ball Stop Bouncing? (Resting Contact)
Without a stopping condition, an inelastic ball undergoes an infinite number of ever-smaller bounces in finite time (the **Zeno paradox**).  
We define a threshold: `settle_velocity = 0.08 m/s`.
When:
$$|v_{\text{impact}}| < v_{\text{settle}} \quad \text{and} \quad y \approx \text{radius}$$
* The ball transitions to `is_settled = True`.
* $y$ is locked to $\text{radius}$, $v$ is set to $0$.
* Remaining kinetic energy is added to `dissipated_energy`.
* Further collision checks are skipped, keeping CPU usage minimal.

---

### E. Preventing the Zeno Paradox (Event-Cap Safeguard)
**File:** [`simulator.py`](file:///D:/sim/CSE-413-Simulation-Modeling-Lab/project/src/simulator.py#L145-L160)

If a user configures a very low restitution and large $dt$, dozens of microscopic bounces can occur inside a single $dt$.
We enforce an **event cap**: `max_sub_events_per_step = 15`.  
If 15 micro-collisions occur within a single timestep, the ball is safely settled. This ensures the simulation **never freezes or hangs** (verified by `test_event_cap.py`).

---

## 4. Execution Flowchart

```text
             Start timestep: step(dt)
                        │
                        ▼
             Is ball already settled?
                 /             \
               YES              NO
               /                 \
     Remain at y = radius,        Set remaining_dt = dt
     v = 0, advance time          sub_events = 0
                                         │
                 ┌───────────────────────┘
                 ▼
       remaining_dt > 0 AND not settled?
                 │
                 ├── YES ──> Check TOI: find_time_of_impact()
                 │                 │
                 │                 ├── TOI is None (No collision in this slice):
                 │                 │   - Advance y, v via semi-implicit Euler
                 │                 │   - Advance current_time += remaining_dt
                 │                 │   - remaining_dt = 0
                 │                 │
                 │                 └── TOI exists at t* (0 <= t* <= remaining_dt):
                 │                     - Advance current_time += t*
                 │                     - Set y = radius (contact position)
                 │                     - Calculate v_impact = v - g * t*
                 │                     - |v_impact| < settle_velocity?
                 │                         ├── YES: Ball Settles (v=0, is_settled=True)
                 │                         └── NO:  Bounce! v_after = -e * v_impact
                 │                                  Accumulate dissipated energy
                 │                                  remaining_dt -= t*
                 │                                  sub_events += 1
                 │
                 └── NO (Timestep complete)
                        │
                        ▼
            Compute PE, KE, Mechanical Energy,
            Total Energy = Mech + Dissipated
            Append state to history -> Return state
```

---

## 5. Top 12 Viva / Defense Questions & Perfect Answers

### Q1: "What is the difference between Modeling and Simulation?"
> **Answer:**  
> **Modeling** is the mathematical abstraction of the system—the differential equations $dv/dt = -g$, $dy/dt = v$, boundary conditions ($y \ge r$), and restitution formulas.  
> **Simulation** is the numerical execution of that model over time across discrete steps to observe and analyze dynamic behavior.

### Q2: "Why didn't you use standard Explicit Euler integration?"
> **Answer:**  
> Standard Explicit Euler calculates position using old velocity ($y_{n+1} = y_n + v_n dt$). In second-order conservative or oscillatory systems, this creates positive numerical drift, causing artificial energy gain.  
> Semi-implicit Euler updates velocity first ($v_{n+1} = v_n - g dt$) and uses that updated velocity for position ($y_{n+1} = y_n + v_{n+1} dt$). It is a **symplectic integrator**, meaning it preserves phase space volume and keeps energy bounded without explosive divergence.

### Q3: "What is tunneling in discrete physics and how did you prevent it?"
> **Answer:**  
> Tunneling happens when a fast-moving object moves past an obstacle between frames $t$ and $t + dt$, sinking below the floor.  
> We prevented it using sub-timestep **Time-of-Impact (TOI)**. Instead of checking position only at integer $dt$ steps, we solve the continuous quadratic equation $0.5gt^2 - vt - (y-r) = 0$ to find the exact fraction of the timestep $t^*$ when the ball touches the surface, clamp it to $y = r$, bounce it, and then integrate the remaining time $dt - t^*$.

### Q4: "Why does the quadratic TOI solver have two roots, and which one do you pick?"
> **Answer:**  
> The quadratic equation $y(t) = \text{radius}$ yields two mathematical intersection points with the horizontal plane $y = r$:
> * One root corresponds to downward entry into the ground ($v < 0$).
> * The other root corresponds to upward exit ($v > 0$).
> We select $t^* = \frac{v + \sqrt{v^2 + 2g(y - r)}}{g}$, which is strictly non-negative and represents the physically valid downward contact trajectory where $v(t^*) \le 0$.

### Q5: "How do you account for energy conservation when the ball loses energy?"
> **Answer:**  
> We track two forms of energy:
> 1. Current mechanical energy: $E_{\text{mech}} = PE + KE$.
> 2. Cumulative dissipated energy: $\sum \Delta E_{\text{collision}} + E_{\text{settle}}$, where each collision dissipates $\frac{1}{2}m(1-e^2)v_{\text{impact}}^2$.  
> The total energy budget $E_{\text{total}} = E_{\text{mech}} + E_{\text{dissipated}}$ remains constant within a small numerical tolerance that shrinks as $dt \to 0$.

### Q6: "What is the Zeno Paradox in bouncing ball simulations?"
> **Answer:**  
> For an inelastic ball ($0 < e < 1$), the bounce heights decrease geometrically ($h_n = e^{2n} h_0$) and time between bounces decreases as $t_n = e^n t_0$. Mathematically, an infinite number of collisions occur before a finite time $T_{\text{settle}}$.  
> On a computer, if you simulate every micro-bounce, the simulation will get trapped in an infinite loop. We solve this with a **settle velocity threshold** ($0.08$ m/s) and an **event cap** (max 15 sub-events per step).

### Q7: "What happens when $e = 1.0$ (perfect elasticity)?"
> **Answer:**  
> Mechanical energy is perfectly conserved ($\Delta E = 0$). The ball never settles. In our system, the 30-second cap halts the run, correctly reporting status as `"Did not settle"` and settling time as `">30 seconds"`, recording all observed bounces (11 collisions in 30 seconds from 10m).

### Q8: "How does your simulator decouple rendering frame rate from physics simulation?"
> **Answer:**  
> Physics runs at a fixed timestep (e.g., $dt = 0.002$s), while rendering runs at display frame rates (e.g., 10 FPS or 60 FPS). A time accumulator consumes physical steps in fixed $dt$ increments regardless of how frequently frames are drawn.  
> Our unit test `test_rendering_rate_independence()` proves that running at 10 FPS and 60 FPS yields **bitwise identical** physics and collision times.

### Q9: "How did you validate your numerical results against analytical physics?"
> **Answer:**  
> For free fall from height $h_0 = 10$m under $g = 9.8\text{ m/s}^2$:
> * Analytical first impact time: $t_1 = \sqrt{2h_0 / g} = \sqrt{20 / 9.8} \approx 1.42857$ seconds.
> * Analytical impact velocity: $v_1 = -\sqrt{2gh_0} \approx -14.0$ m/s.  
> Our simulator matched the analytical time within sub-millisecond precision ($\Delta t < 0.0001$s), verified by `test_toi.py`.

### Q10: "What does the phase portrait ($y$ vs. $v$) tell us?"
> **Answer:**  
> In [`validation.png`](file:///D:/sim/CSE-413-Simulation-Modeling-Lab/project/reports/figures/validation.png), the bottom-right panel shows position $y$ on the x-axis and velocity $v$ on the y-axis.  
> Each bounce traces a parabolic loop in phase space. Because energy is lost on each bounce, the loops spiral inwards toward the equilibrium point $(y = r, v = 0)$, visually proving asymptotic stability.

### Q11: "What are the test cases you wrote?"
> **Answer:**  
> We have 21 automated pytest unit tests organized in 9 test suites:
> 1. `test_coordinates_and_euler.py`: Upward-positive convention, $-g$ sign, semi-implicit step.
> 2. `test_toi.py`: Analytical formula $t = \sqrt{2h/g}$ and exact contact position $y = r$.
> 3. `test_resting_contact.py`: Zero velocity lock, no duplicate collision events.
> 4. `test_energy_conservation.py`: Energy budget accounting and $dt$ refinement convergence.
> 5. `test_event_cap.py`: Pathological chatter termination under 1 second.
> 6. `test_rendering_indep.py`: 10 FPS vs 60 FPS physics invariance.
> 7. `test_experiment_limits.py`: 30-second cap, $e=1.0$ unsettled status, CSV overwrite.
> 8. `test_csv_output.py`: Column schema and parameter row mapping.
> 9. `test_benchmark.py`: Performance benchmark (>650x real-time speedup).

### Q12: "How fast is your simulator?"
> **Answer:**  
> In our benchmark test (`test_benchmark.py`), simulating 30.0 seconds of physical time ($15,002$ steps) took only **0.0460 seconds** (~46 ms) of CPU time, which is **652 times faster than real-time**.

---

## 6. Live Demo Script (What to Show on Screen)

If the instructor says: *"Open your laptop and run your project."*

### Step 1: Launch with One Click
Double click [`run.bat`](file:///D:/sim/CSE-413-Simulation-Modeling-Lab/run.bat) in the root directory.  
Press `1` and hit `[Enter]`.

### Step 2: Explain What Appears on the Screen
* **Left Window:** Point to the blue ball dropping and bouncing. Point out the brown line ($y = 0$, ground) and the dashed line ($y = r$, the ball's center at contact). Show that the ball **never penetrates** below the dashed line.
* **Top Right:** Point to the red $y(t)$ trajectory curve. Explain how the peaks decay by $e^2$ on each rebound.
* **Bottom Right:** Point to the dynamic energy bar chart. Show that as the ball bounces, Green ($PE$) and Yellow ($KE$) convert back and forth, Red (Dissipated) climbs after each bounce, and Black (Total Account) remains strictly conserved!

### Step 3: Run the Test Suite
Press `4` in `run.bat` or run:
```bash
python -m pytest project/tests -v
```
Show the teacher that **21 out of 21 tests pass with green checkmarks in under 2 seconds**.

### Step 4: Show the Technical Report
Point to [`project/reports/TECHNICAL_REPORT.md`](file:///D:/sim/CSE-413-Simulation-Modeling-Lab/project/reports/TECHNICAL_REPORT.md) and [`validation.png`](file:///D:/sim/CSE-413-Simulation-Modeling-Lab/project/reports/figures/validation.png) for full mathematical rigor.
