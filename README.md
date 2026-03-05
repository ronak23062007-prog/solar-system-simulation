# solar-system-simulation

Advanced Solar System Simulation - Walkthrough
The Advanced Solar System Simulation has been fully developed, implementing real physics, 3D visualization, real data, and high-performance algorithms according to all of your requirements!

Core Physics & Data
Real Physics Integration: Built using Newtonian mechanics ($F = G \frac{m_1 m_2}{r^2}$) and stable Velocity Verlet integration to accurately conserve orbital energy.

3D Graphical Visuals
Starfield Background: A distant field of 15,000 stars provides a static reference for camera rotation and movement.
Volumetric Shading: Planets now use 3D shaders ('shaded') to respond to the view angle, giving them a rounded, volumetric appearance.
Atmospheric Halos: Added a subtle glowing aura to every planet to make them "pop" against the backdrops.
Vertical Height Markers: Implemented vertical reference lines (sticks) connecting each body to the orbital plane, solving the "depth perception" problem in 3D space.

SolarSystemRenderer
 using pyqtgraph.opengl. It renders massive grids, 3D spheres for celestial bodies, and dynamic trail lines for orbits.
Precision Camera Controls: Intuitive free-fly camera mode using Arrow Keys (Forward/Left/Back/Right) and Space/Shift (Up/Down). Movement is relative to where you are looking!

Advanced Physics & Entities
Real Black Holes: Implemented relativistic physics for black holes, including the Speed of Light velocity cap to prevent calculation errors and the Schwarzschild Radius for event horizon absorption.
Visual Black Hole: Black holes are rendered with a pitch-black event horizon and a massive purple accretion disk glow.

UI & Advanced Systems
Metrics Dashboard: Implemented real-time tracking of System Total Energy, Potential Energy, and Kinetic Energy using customized pyqtgraph charts.
Planet Tracking: A dynamic info panel continuously tracks the selected planet, reporting its name, mass, and precise distance from the system's barycenter in Astronomical Units (AU).

Spacecraft Orbit Simulation: A "Launch Spacecraft" feature spawns an Apollo-like spacecraft directly into Low Earth Orbit. A Prograde Thrust button allows manual Hohmann transfers (+2000 m/s impulse) to escape Earth's gravity well.

Asteroid Belt: A one-click Sandbox tool dynamically generates 100 randomized asteroids into an orbit between Mars and Jupiter. Thanks to Numba, the engine computes $N^2$ interactions for all spawned asteroids smoothly.

Real Moon Spawner: Instantly generate the exact real-world moon counts for all inner and outer planets (e.g. 146 for Saturn, 95 for Jupiter) into randomized, stable orbital trajectories around their host bodies.

Black Hole Generator: Inputs for X, Y, and Z (in AU) allow users to spawn supermassive black holes precisely anywhere in the system to observe chaotic disruptions.

System Graphics: The Sun has a custom visual atmospheric glow and has been colored red. All inner/outer planets are significantly upscaled visually for immediate recognition.

Save/Load State: The full system state (positions, vectors, masses) can serialize to a local save.json snapshot immediately restoring it when re-loaded.

NOTE
The visualization distances are vast. Zoom out significantly if the screen turns black when navigating in Free Camera mode, or simply select a planet directly from the Follow Object dropdown!

# how-to-run-solar-system-simulation

1.clone the solar system simulation on your pc   
-git clone https://github.com/ronak23062007-prog/solar-system-simulation.git

2.open the folder   
-open the folder in any code editor 

3.download requiremnts.txt   
-pip install requirements.txt

4.run solar system simulation   
-python3 main.py
