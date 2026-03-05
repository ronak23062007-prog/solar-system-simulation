import numpy as np

class CelestialBody:
    """
    Represents a physical object in the simulation (planet, star, moon).
    All physical quantities are in standard SI units (kg, m, s) unless noted.
    """
    def __init__(self, name, mass, radius, position, velocity, color):
        self.name = name
        self.mass = float(mass)  # kg
        self.radius = float(radius)  # m
        # Using numpy arrays of shape (3,) for position and velocity vectors
        self.position = np.array(position, dtype=np.float64)  # m
        self.velocity = np.array(velocity, dtype=np.float64)  # m/s
        
        # Acceleration from the previous step (for Velocity Verlet)
        self.acceleration = np.zeros(3, dtype=np.float64)
        
        self.color = color
        
        # Trail history (for visualization)
        self.trail = []
        self.trail_max_len = 500

    def update_trail(self):
        # Sample position occasionally instead of every tick to save memory
        if len(self.trail) == 0 or np.linalg.norm(self.trail[-1] - self.position) > self.radius * 2:
            self.trail.append(self.position.copy())
            if len(self.trail) > self.trail_max_len:
                self.trail.pop(0)

class Spacecraft(CelestialBody):
    """
    A celestial body with thrust capabilities.
    """
    def __init__(self, name, mass, radius, position, velocity, color, fuel_mass):
        super().__init__(name, mass, radius, position, velocity, color)
        self.dry_mass = float(mass)
        self.fuel_mass = float(fuel_mass)
        self.thrust_active = False
        self.thrust_vector = np.zeros(3, dtype=np.float64)

    @property
    def total_mass(self):
        return self.dry_mass + max(0.0, self.fuel_mass)
