import numpy as np
from core.bodies import CelestialBody

# Gravitational Constant G in m^3 kg^-1 s^-2
G = 6.67430e-11
# Speed of light in m/s
c = 299792458.0

class GravityEngine:
    """
    Handles the N-body gravitational physics of the system.
    Will be extended with Barnes-Hut for massive numbers of particles.
    """
    def __init__(self):
        self.bodies = []
        # Simulation parameters
        self.dt = 3600  # Default 1 hr per step
        self.use_numba = True

    def add_body(self, body: CelestialBody):
        self.bodies.append(body)

    def calculate_accelerations(self):
        """
        O(N^2) gravity calculation. Can use fast Numba implementation for N > 50.
        Returns an array of accelerations corresponding to `self.bodies`.
        """
        n = len(self.bodies)
        # Using vectorized numpy calculations rather than slow nested loops
        positions = np.array([body.position for body in self.bodies])
        masses = np.array([body.mass for body in self.bodies])
        
        if self.use_numba and n > 50:
            from core.barnes_hut import calculate_gravity_fast
            accelerations = calculate_gravity_fast(positions, masses, n)
            return accelerations

        # Using vectorized numpy calculations rather than slow nested loops (for small N)
        
        # Reshape for broadcasting
        pos_i = positions[:, np.newaxis, :]  # Shape (N, 1, 3)
        pos_j = positions[np.newaxis, :, :]            # Shape (1, N, 3)
        
        # Difference vectors
        r_vec = pos_j - pos_i  # Shape (N, N, 3)
        
        # Distances: r = sqrt(dx^2 + dy^2 + dz^2)
        r_sq = np.sum(r_vec**2, axis=-1)  # Shape (N, N)
        
        # Exclude self-gravity (prevent division by zero)
        np.fill_diagonal(r_sq, 1.0)
        
        r_mag = np.sqrt(r_sq)  # Shape (N, N)
        
        # Calculate force magnitudes divided by test mass (a = G * M / r^2)
        # We need a vector, so: a_vec = a * (r_vec / r) = G * M * r_vec / r^3
        r_cubed = r_sq * r_mag
        
        # Combine everything
        # a_ij = G * m_j * r_vec_ij / r_ij^3
        # We add a small eps to prevent explosion just in case of overlaps
        eps = 1e-10
        accel_component = G * masses[np.newaxis, :] / (r_cubed + eps)
        
        # Shape adjustment for broadcasting with vectors
        accel_component = accel_component[:, :, np.newaxis] * r_vec
        
        # Sum over all interacting bodies (along axis 1)
        accelerations = np.sum(accel_component, axis=1)
        
        return accelerations
        

    def step(self, delta_time):
        """
        Advances the simulation by delta_time seconds using Velocity Verlet integration.
        Velocity Verlet is symplectic (conserves energy well for orbital mechanics).
        1. Calculate v(t + dt/2) = v(t) + 0.5 * a(t) * dt
        2. Calculate r(t + dt) = r(t) + v(t + dt/2) * dt
        3. Calculate new a(t + dt)
        4. Calculate v(t + dt) = v(t + dt/2) + 0.5 * a(t + dt) * dt
        """
        if not self.bodies:
            return

        dt = float(delta_time)

        # 1. Update positions using current velocity and acceleration
        for body in self.bodies:
            # r(t+dt) = r(t) + v(t)*dt + 0.5*a(t)*dt^2
            body.position += body.velocity * dt + 0.5 * body.acceleration * (dt**2)
            
            # v(t+dt/2) = v(t) + 0.5*a(t)*dt
            # We temporarily store this in velocity
            body.velocity += 0.5 * body.acceleration * dt

        # 2. Calculate new accelerations (at new positions)
        new_accelerations = self.calculate_accelerations()

        # 3. Complete velocity update and apply new accelerations
        for i, body in enumerate(self.bodies):
            # v(t+dt) = v(t+dt/2) + 0.5*a(t+dt)*dt
            body.velocity += 0.5 * new_accelerations[i] * dt
            
            # Real Physics: Relativistic speed limit - nothing can exceed the speed of light
            v_mag = np.linalg.norm(body.velocity)
            if v_mag > c:
                # Cap velocity to the speed of light (prevents NaN math explosions near Black Holes)
                body.velocity = (body.velocity / v_mag) * (c * 0.99)
                
            body.acceleration = new_accelerations[i]
            body.update_trail()
            
        # 4. Handle collisions
        self.check_collisions()

    def check_collisions(self):
        """
        Perfectly inelastic collisions conserving momentum.
        If two bodies collide, they merge into one.
        O(N^2) but we only do it for core bodies, not the whole asteroid belt.
        """
        i = 0
        while i < len(self.bodies):
            j = i + 1
            while j < len(self.bodies):
                b1 = self.bodies[i]
                b2 = self.bodies[j]
                
                dist = np.linalg.norm(b1.position - b2.position)
                
                # Real Physics: Event Horizon (Schwarzschild radius)
                b1_radius = b1.radius
                b2_radius = b2.radius
                if b1.name == 'BlackHole':
                    b1_radius = (2 * G * b1.mass) / (c**2) # R_s = 2GM/c^2
                if b2.name == 'BlackHole':
                    b2_radius = (2 * G * b2.mass) / (c**2)
                
                # Collision occurs if distance is less than sum of physical radii or event horizons
                if dist < (b1_radius + b2_radius):
                    # Merge bodies. Conservation of momentum: m1v1 + m2v2 = (m1+m2)vf
                    total_mass = b1.mass + b2.mass
                    new_velocity = (b1.mass * b1.velocity + b2.mass * b2.velocity) / total_mass
                    
                    # New position is the center of mass
                    new_position = (b1.mass * b1.position + b2.mass * b2.position) / total_mass
                    
                    # Conserve volume to find new radius: V = V1 + V2 -> r = (r1^3 + r2^3)^(1/3)
                    # For Black Holes, radius isn't conserved this way, but it gets overwritten by Schwarzschild anyway
                    new_radius = (b1.radius**3 + b2.radius**3)**(1/3)
                    
                    # Update b1 in place with new properties
                    b1.mass = total_mass
                    b1.velocity = new_velocity
                    b1.position = new_position
                    b1.radius = new_radius
                    # Keep b1's color or mix them, for now keep the larger body's color
                    # Black Hole always wins
                    if b2.name == 'BlackHole' or (b1.name != 'BlackHole' and b2.mass > b1.mass):
                        b1.color = b2.color
                        b1.name = b2.name # Assume the larger body (or Black Hole) "eats" the smaller
                    
                    # Remove b2 from the simulation
                    self.bodies.pop(j)
                    # Don't increment j since the list shifted 
                else:
                    j += 1
            i += 1

    def get_system_energy(self):
        """
        Calculates total kinetic and potential energy of the system.
        Used to verify conservation of energy.
        """
        kinetic = 0.0
        potential = 0.0
        
        for i, body in enumerate(self.bodies):
            # KE = 1/2 * m * v^2
            kinetic += 0.5 * body.mass * np.sum(body.velocity**2)
            
            # PE = -G * m1 * m2 / r
            for j in range(i + 1, len(self.bodies)):
                other = self.bodies[j]
                r = np.linalg.norm(body.position - other.position)
                potential -= G * body.mass * other.mass / (r + 1e-10)
                
        return kinetic, potential, kinetic + potential
