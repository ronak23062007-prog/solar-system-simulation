import sys
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QSlider, QComboBox, QGroupBox, QFormLayout, QLineEdit)
from PyQt6.QtCore import Qt, QTimer
import pyqtgraph as pg

from core.physics import GravityEngine
from core.bodies import CelestialBody
from data.system_data import SYSTEM_DATA
from graphics.renderer import SolarSystemRenderer

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Advanced Solar System Simulation")
        self.resize(1280, 800)
        
        # 1. Physics Engine Setup
        self.engine = GravityEngine()
        self.load_system_data()
        
        # 2. UI Layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        
        # Left Panel: 3D Render
        self.renderer = SolarSystemRenderer(self.engine)
        main_layout.addWidget(self.renderer, stretch=3)
        
        # Right Panel: Controls & Charts
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        main_layout.addWidget(right_panel, stretch=1)
        
        # -- Controls Box --
        control_group = QGroupBox("Simulation Controls")
        control_layout = QFormLayout()
        
        # Play/Pause
        self.btn_play = QPushButton("Pause")
        self.btn_play.clicked.connect(self.toggle_play)
        self.is_playing = True
        control_layout.addRow(self.btn_play)
        
        # Time Step Slider
        self.slider_speed = QSlider(Qt.Orientation.Horizontal)
        self.slider_speed.setMinimum(1)
        self.slider_speed.setMaximum(100) # corresponds to steps per frame
        self.slider_speed.setValue(10)
        self.lbl_speed = QLabel("Speed: 10x")
        self.slider_speed.valueChanged.connect(self.update_speed)
        control_layout.addRow(self.lbl_speed, self.slider_speed)
        
        # Camera Focus
        self.combo_focus = QComboBox()
        self.combo_focus.addItem("Free Camera")
        for body in self.engine.bodies:
            self.combo_focus.addItem(body.name)
        self.combo_focus.currentIndexChanged.connect(self.change_focus)
        control_layout.addRow("Follow Object:", self.combo_focus)
        
        # Sandbox Controls
        self.btn_add_asteroid = QPushButton("Spawn 100 Asteroids")
        self.btn_add_asteroid.clicked.connect(self.spawn_asteroids)
        
        self.btn_add_moons = QPushButton("Spawn Real Moons")
        self.btn_add_moons.clicked.connect(self.spawn_moons)
        
        sandbox_layout = QHBoxLayout()
        sandbox_layout.addWidget(self.btn_add_asteroid)
        sandbox_layout.addWidget(self.btn_add_moons)
        control_layout.addRow(sandbox_layout)
        
        # Black Hole Config
        self.btn_bh = QPushButton("Spawn Black Hole")
        self.btn_bh.clicked.connect(self.spawn_black_hole)
        bh_inputs = QHBoxLayout()
        self.bh_x = QLineEdit("50")
        self.bh_y = QLineEdit("0")
        self.bh_z = QLineEdit("0")
        bh_inputs.addWidget(QLabel("X(AU):"))
        bh_inputs.addWidget(self.bh_x)
        bh_inputs.addWidget(QLabel("Y:"))
        bh_inputs.addWidget(self.bh_y)
        bh_inputs.addWidget(QLabel("Z:"))
        bh_inputs.addWidget(self.bh_z)
        control_layout.addRow(bh_inputs)
        control_layout.addRow(self.btn_bh)
        
        # Spacecraft Controls
        self.btn_spacecraft = QPushButton("Launch Spacecraft (LEO)")
        self.btn_spacecraft.clicked.connect(self.launch_spacecraft)
        control_layout.addRow(self.btn_spacecraft)
        
        self.btn_thrust = QPushButton("Fire Prograde Thrust (+2000 m/s)")
        self.btn_thrust.clicked.connect(self.fire_thrust)
        control_layout.addRow(self.btn_thrust)
        
        # Save / Load
        self.btn_save = QPushButton("Save")
        self.btn_save.clicked.connect(self.save_simulation)
        self.btn_load = QPushButton("Load")
        self.btn_load.clicked.connect(self.load_simulation)
        control_layout.addRow(self.btn_save, self.btn_load)
        
        control_group.setLayout(control_layout)
        right_layout.addWidget(control_group)
        
        # -- Energy Plot --
        plot_group = QGroupBox("System Energy (Joules)")
        plot_layout = QVBoxLayout()
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('w')
        self.plot_widget.showGrid(x=True, y=True)
        # Using lists for line plotting
        self.time_history = []
        self.ke_history = []
        self.pe_history = []
        self.te_history = []
        
        self.ke_line = self.plot_widget.plot(pen='b', name="Kinetic Energy")
        self.pe_line = self.plot_widget.plot(pen='r', name="Potential Energy")
        self.te_line = self.plot_widget.plot(pen='g', name="Total Energy")
        
        # Setup legend
        self.plot_widget.addLegend()
        self.plot_widget.plot([], [], pen='b', name="Kinetic Energy")
        self.plot_widget.plot([], [], pen='r', name="Potential Energy")
        self.plot_widget.plot([], [], pen='g', name="Total Energy")
        
        plot_layout.addWidget(self.plot_widget)
        plot_group.setLayout(plot_layout)
        right_layout.addWidget(plot_group)
        
        # -- Info Panel --
        self.info_label = QLabel("Focus: Free Camera")
        self.info_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2B82C9;")
        right_layout.addWidget(self.info_label)
        
        # 3. Main Loop Timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_simulation)
        self.timer.start(16) # ~60 FPS
        self.sim_time = 0.0
        self.sim_steps_per_frame = 10
        self.renderer.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def load_system_data(self):
        for name, data in SYSTEM_DATA.items():
            body = CelestialBody(
                name=name,
                mass=data["mass"],
                radius=data["radius"],
                position=data["position"],
                velocity=data["velocity"],
                color=data["color"]
            )
            self.engine.add_body(body)

    def toggle_play(self):
        self.is_playing = not self.is_playing
        self.btn_play.setText("Pause" if self.is_playing else "Play")

    def update_speed(self, value):
        self.sim_steps_per_frame = value
        self.lbl_speed.setText(f"Speed: {value}x")

    def change_focus(self, index):
        if index == 0:
            # Revert to overview distance if we just manually freed the camera through the dropdown
            self.renderer.setCameraPosition(distance=2e12)
        else:
            # We don't have a rigid link yet, but we could update camera center here
            body = self.engine.bodies[index - 1]
            # Instantly scale the camera distance to fit the properly visible scaled body
            vis_radius = self.renderer.get_visual_radius(body)
            from PyQt6.QtGui import QVector3D
            self.renderer.setCameraPosition(pos=QVector3D(*body.position), distance=vis_radius * 2.5)

    def update_simulation(self):
        if not self.is_playing:
            return
            
        # Run physics steps
        for _ in range(self.sim_steps_per_frame):
            self.engine.step(3600) # 1 hour per physics step
            self.sim_time += 3600
            
        self.renderer.update_frame()
        
        # Update Camera
        idx = self.combo_focus.currentIndex()
        
        # Determine movement from Arrow Keys via Renderer
        df, dr, dz = 0, 0, 0 # Forward, Right, Z(global)
        speed = self.renderer.opts['distance'] * 0.05
        keys = self.renderer.keys_pressed
        if Qt.Key.Key_Up in keys: df += speed
        if Qt.Key.Key_Down in keys: df -= speed
        if Qt.Key.Key_Left in keys: dr -= speed
        if Qt.Key.Key_Right in keys: dr += speed
        if Qt.Key.Key_Space in keys: dz += speed
        if Qt.Key.Key_Shift in keys: dz -= speed

        if df != 0 or dr != 0 or dz != 0:
            # If user moves camera manually, break Follow focus automatically
            if idx > 0:
                self.combo_focus.setCurrentIndex(0)
                idx = 0
            
            # Proper 3D Coordinate Mapping for free-fly movement
            import numpy as np
            az = np.radians(self.renderer.opts.get('azimuth', 0))
            el = np.radians(self.renderer.opts.get('elevation', 0))
            
            # Forward vector (into the screen): unit vector from Camera to Center
            fx = -np.cos(el) * np.cos(az)
            fy = -np.cos(el) * np.sin(az)
            fz = -np.sin(el)
            
            # Right vector (perpendicular to Forward and Z-axis):
            rx = -np.sin(az)
            ry = np.cos(az)
            # rz = 0
            
            move_x = fx * df + rx * dr
            move_y = fy * df + ry * dr
            move_z = fz * df + dz # 'Up' key moves 'Forward', which includes Z if tilted
            
            # Use definitive setCameraPosition API to bypass opts['center'] quirks
            from PyQt6.QtGui import QVector3D
            cc = self.renderer.opts['center']
            # center can be pg.Vector or array-like
            if hasattr(cc, 'x'):
                cx, cy, cz = cc.x(), cc.y(), cc.z()
            else:
                cx, cy, cz = cc[0], cc[1], cc[2]
            
            self.renderer.setCameraPosition(pos=QVector3D(cx + move_x, cy + move_y, cz + move_z))

        if idx > 0 and idx - 1 < len(self.engine.bodies):
            body = self.engine.bodies[idx - 1]
            from PyQt6.QtGui import QVector3D
            self.renderer.setCameraPosition(pos=QVector3D(*body.position))
            import numpy as np
            dist_au = np.linalg.norm(body.position) / 149.596e9
            self.info_label.setText(f"Focus: {body.name} | Mass: {body.mass:.2e} kg | Dist: {dist_au:.2f} AU")
        else:
            self.info_label.setText("Focus: Free Camera (Use Arrow Keys + Shift/Space to Move)")

        # Periodically update the plot (not every frame to save UI lag)
        if len(self.time_history) == 0 or self.sim_time - self.time_history[-1] > 3600 * 24:
            ke, pe, te = self.engine.get_system_energy()
            self.time_history.append(self.sim_time / (3600 * 24)) # Days
            self.ke_history.append(ke)
            self.pe_history.append(pe)
            self.te_history.append(te)
            
            # Keep history short-ish
            max_points = 500
            if len(self.time_history) > max_points:
                self.time_history = self.time_history[-max_points:]
                self.ke_history = self.ke_history[-max_points:]
                self.pe_history = self.pe_history[-max_points:]
                self.te_history = self.te_history[-max_points:]
                
            self.ke_line.setData(self.time_history, self.ke_history)
            self.pe_line.setData(self.time_history, self.pe_history)
            self.te_line.setData(self.time_history, self.te_history)

    def spawn_asteroids(self):
        """
        Spawns 100 asteroids in the asteroid belt.
        """
        import numpy as np
        
        # Asteroid belt is between Mars and Jupiter (~2.2 to 3.2 AU)
        AU = 149.596e9
        count = 100 # Changed from 1000 to 100
        
        # Random radii between 2.2 and 3.2 AU
        r = np.random.uniform(2.2 * AU, 3.2 * AU, count)
        theta = np.random.uniform(0, 2 * np.pi, count)
        
        x = r * np.cos(theta)
        y = r * np.sin(theta)
        z = np.random.normal(0, 0.05 * AU, count) # Slight vertical scatter
        
        # Orbital velocity approximation: v = sqrt(G * M_sun / r)
        M_sun = SYSTEM_DATA["Sun"]["mass"]
        G = 6.67430e-11
        v_mag = np.sqrt(G * M_sun / (r))
        
        vx = -v_mag * np.sin(theta)
        vy = v_mag * np.cos(theta)
        vz = np.random.normal(0, 1000, count) # Slight vertical velocity
        
        for i in range(count):
            body = CelestialBody(
                name=f"Asteroid_{len(self.engine.bodies)}",
                mass=np.random.uniform(1e12, 1e15),
                radius=np.random.uniform(1000, 50000),
                position=[x[i], y[i], z[i]],
                velocity=[vx[i], vy[i], vz[i]],
                color="#888888"
            )
            self.engine.add_body(body)
            # Add to dropdown
            # Not adding to dropdown to avoid 50,000 items freezing UI
        
        # Update renderer visuals
        self.renderer.init_visuals()

    def launch_spacecraft(self):
        # Find Earth
        earth = next((b for b in self.engine.bodies if b.name == "Earth"), None)
        if not earth:
            return
            
        import numpy as np
        from core.bodies import Spacecraft
        
        # LEO: roughly Earth radius + 400km
        r_orbit = earth.radius + 400000
        # Orbital velocity: v = sqrt(G * M_earth / r)
        G = 6.67430e-11
        v_orbit = np.sqrt(G * earth.mass / r_orbit)
        
        pos = earth.position + np.array([r_orbit, 0, 0], dtype=np.float64)
        vel = earth.velocity + np.array([0, v_orbit, 0], dtype=np.float64)
        
        sc = Spacecraft(
            name="Apollo-1X",
            mass=50000,
            radius=100000, # Visually enlarged
            position=pos,
            velocity=vel,
            color="#FF00FF",
            fuel_mass=20000
        )
        self.engine.add_body(sc)
        self.combo_focus.addItem(sc.name)
        self.combo_focus.setCurrentIndex(self.combo_focus.count() - 1)
        self.renderer.init_visuals()

    def fire_thrust(self):
        import numpy as np
        # Find the spacecraft
        for b in self.engine.bodies:
            if b.name == "Apollo-1X":
                # Prograde vector = normalized velocity vector relative to dominant body (Earth or Sun)
                # For simplicity, boost current velocity magnitude by 2000 m/s
                v_mag = np.linalg.norm(b.velocity)
                if v_mag > 0:
                    v_dir = b.velocity / v_mag
                    b.velocity += v_dir * 2000
                break

    def save_simulation(self):
        import json
        data = []
        for b in self.engine.bodies:
            data.append({
                "name": b.name,
                "mass": b.mass,
                "radius": b.radius,
                "position": b.position.tolist(),
                "velocity": b.velocity.tolist(),
                "color": b.color
            })
        with open("save.json", "w") as f:
            json.dump(data, f)
            
    def load_simulation(self):
        import json, os
        from core.bodies import CelestialBody
        if not os.path.exists("save.json"):
            return
        with open("save.json", "r") as f:
            data = json.load(f)
            
        self.engine.bodies = []
        for d in data:
            self.engine.add_body(CelestialBody(
                d["name"], d["mass"], d["radius"], 
                d["position"], d["velocity"], d["color"]
            ))
            
        self.combo_focus.clear()
        self.combo_focus.addItem("Free Camera")
        for b in self.engine.bodies:
            self.combo_focus.addItem(b.name)
            
        self.renderer.init_visuals()

    def spawn_black_hole(self):
        try:
            x = float(self.bh_x.text()) * 149.596e9
            y = float(self.bh_y.text()) * 149.596e9
            z = float(self.bh_z.text()) * 149.596e9
            
            from core.bodies import CelestialBody
            bh = CelestialBody(
                name="BlackHole",
                mass=4e34, # 20,000 Solar Masses. Safe now because velocity is capped at Speed of Light.
                radius=10000, 
                position=[x, y, z],
                velocity=[0.0, 0.0, 0.0],
                color="#000000" # Pure black core
            )
            self.engine.add_body(bh)
            self.combo_focus.addItem(bh.name)
            self.renderer.init_visuals()
        except Exception as e:
            print(f"Could not spawn black hole: {e}")

    def spawn_moons(self):
        import numpy as np
        from core.bodies import CelestialBody
        moon_counts = {
            "Earth": 1, "Mars": 2, "Jupiter": 95, 
            "Saturn": 146, "Uranus": 28, "Neptune": 16
        }
        G = 6.67430e-11
        
        for p_name, m_count in moon_counts.items():
            planet = next((b for b in self.engine.bodies if b.name == p_name), None)
            if not planet: continue
            
            for i in range(m_count):
                if p_name == "Earth" and i == 0:
                    continue # Skip first earth moon as it's already in system_data
                    
                # Randomize orbit radius a bit larger than planet radius
                r_orbit = planet.radius * np.random.uniform(5.0, 30.0)
                theta = np.random.uniform(0, 2 * np.pi)
                
                pos = planet.position + np.array([r_orbit * np.cos(theta), r_orbit * np.sin(theta), np.random.normal(0, r_orbit*0.1)])
                
                v_orbit = np.sqrt(G * planet.mass / r_orbit)
                vel = planet.velocity + np.array([-v_orbit * np.sin(theta), v_orbit * np.cos(theta), np.random.normal(0, v_orbit*0.1)])
                
                moon = CelestialBody(
                    name=f"{p_name}_Moon_{i+1}",
                    mass=7.342e22 * np.random.uniform(0.01, 1.5), 
                    radius=1737400.0 * np.random.uniform(0.1, 1.5),
                    position=pos,
                    velocity=vel,
                    color="#BBBBBB"
                )
                self.engine.add_body(moon)
                # Don't add to dropdown to prevent massive lists
                
        self.renderer.init_visuals()
