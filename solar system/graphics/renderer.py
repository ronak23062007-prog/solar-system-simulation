import pyqtgraph.opengl as gl
import pyqtgraph as pg
import numpy as np
from PyQt6.QtGui import QColor

class SolarSystemRenderer(gl.GLViewWidget):
    def __init__(self, engine):
        super().__init__()
        self.engine = engine
        
        # Enable depth testing and anti-aliasing
        self.opts['distance'] = 1e12 # Camera distance
        self.setBackgroundColor('k') # Black background
        
        self.keys_pressed = set()
        
        self.body_visuals = {} # body_id -> GLMeshItem
        self.trail_visuals = {} # body_id -> GLLinePlotItem
        self.glow_visuals = {} # body_id -> GLMeshItem
        self.stick_visuals = {} # body_id -> GLLinePlotItem (Vertical position indicator)
        
        # Grid to visualize the orbital plane
        grid = gl.GLGridItem()
        # Make the grid massively larger to encompass Neptune/Pluto
        grid.setSpacing(x=1e11, y=1e11, z=1e11)
        grid.setSize(x=30e12, y=30e12, z=1e11)
        self.addItem(grid)
        
        # Add a distant Starfield to make space feel deeper
        self.add_starfield()
        
        # Add visual components for all existing bodies
        self.init_visuals()

    def add_starfield(self):
        n_stars = 15000
        # Distant points at ~50e12 meters
        dist = 60e12 
        pos = np.random.normal(size=(n_stars, 3))
        pos /= np.linalg.norm(pos, axis=1)[:, np.newaxis]
        pos *= dist
        
        # Random sizes and brightness
        colors = np.random.uniform(0.5, 1.0, (n_stars, 4))
        colors[:, 3] = 1.0 # Opacity
        
        stars = gl.GLScatterPlotItem(pos=pos, color=colors, size=1.5, pxMode=True)
        self.addItem(stars)

    def keyPressEvent(self, ev):
        self.keys_pressed.add(ev.key())
        # Block default rotation with arrow keys so we can pan instead
        if ev.key() in (Qt.Key.Key_Up, Qt.Key.Key_Down, Qt.Key.Key_Left, Qt.Key.Key_Right):
            ev.accept()
            return
        super().keyPressEvent(ev)

    def keyReleaseEvent(self, ev):
        if ev.key() in self.keys_pressed:
            self.keys_pressed.remove(ev.key())
        if ev.key() in (Qt.Key.Key_Up, Qt.Key.Key_Down, Qt.Key.Key_Left, Qt.Key.Key_Right):
            ev.accept()
            return
        super().keyReleaseEvent(ev)

    def init_visuals(self):
        # Clear existing visuals
        for vis in self.body_visuals.values():
            self.removeItem(vis)
        for trail in self.trail_visuals.values():
            self.removeItem(trail)
        for glow in self.glow_visuals.values():
            self.removeItem(glow)
        for stick in self.stick_visuals.values():
            self.removeItem(stick)
            
        self.body_visuals.clear()
        self.trail_visuals.clear()
        self.glow_visuals.clear()
        self.stick_visuals.clear()
        
        # Add spheres and lines
        for i, body in enumerate(self.engine.bodies):
            self.add_body_visual(body, i)

    def get_visual_radius(self, body):
        # Increased overall scale 
        if body.name == 'BlackHole':
             return 3e10
        if body.name == 'Sun':
             return body.radius * 70 # Noticeably bigger Sun
        return (body.radius ** 0.5) * 1500000 # Noticeably bigger planets

    def add_body_visual(self, body, b_id):
        # Apply the smart 1:1 ratio-preserving scale
        vis_radius = self.get_visual_radius(body)
        
        md = gl.MeshData.sphere(rows=32, cols=32, radius=vis_radius)
        c = QColor(body.color)
        r, g, b = c.redF(), c.greenF(), c.blueF()
        
        # Shading: Planets should be shaded by the Sun (0,0,0 approximately)
        # Note: Pyqtgraph's 'shaded' shader uses a default headlight. 
        # For true 3D feel, 'shaded' is better than flat colors.
        shader = 'shaded'
        if body.name == 'Sun' or body.name == 'BlackHole':
            shader = 'viewNormalColor' # Makes the sun look like a solid glowing sphere
            
        mesh = gl.GLMeshItem(
            meshdata=md, smooth=True, 
            color=(r, g, b, 1.0), 
            shader=shader, glOptions='opaque'
        )
        # Position
        mesh.translate(*body.position)
        
        self.addItem(mesh)
        self.body_visuals[b_id] = mesh
        
        if body.name == 'Sun' or body.name == 'BlackHole':
            # Add atmospheric glow
            glow_radius = vis_radius * 1.5
            
            # Custom glow colors
            if body.name == 'BlackHole':
                glow_r, glow_g, glow_b = 0.8, 0.2, 1.0 # Bright purple aura
                alpha = 0.4
            else:
                glow_r, glow_g, glow_b = r, g, b
                alpha = 0.3
                
            md_glow = gl.MeshData.sphere(rows=32, cols=32, radius=glow_radius)
            glow = gl.GLMeshItem(
                meshdata=md_glow, smooth=True,
                color=(glow_r, glow_g, glow_b, alpha),
                shader='balloon', glOptions='additive'
            )
            glow.translate(*body.position)
            self.addItem(glow)
            self.glow_visuals[b_id] = glow
            
        else:
            # Subtle glow for planets to make them "pop" 3D
            md_glow = gl.MeshData.sphere(rows=16, cols=16, radius=vis_radius * 1.1)
            glow = gl.GLMeshItem(
                meshdata=md_glow, smooth=True,
                color=(r, g, b, 0.15),
                shader='balloon', glOptions='additive'
            )
            glow.translate(*body.position)
            self.addItem(glow)
            self.glow_visuals[b_id] = glow
        
        # Add a vertical "stick" to show 3D height relative to the plane
        # This makes the 3D position much easier to read
        stick_pos = np.array([[body.position[0], body.position[1], 0], 
                             [body.position[0], body.position[1], body.position[2]]])
        stick = gl.GLLinePlotItem(pos=stick_pos, color=(1, 1, 1, 0.2), antialias=True)
        self.addItem(stick)
        self.stick_visuals[b_id] = stick
        
        # Add trails
        trail = gl.GLLinePlotItem(pos=np.zeros((2, 3)), color=(r, g, b, 0.5), antialias=True)
        self.addItem(trail)
        self.trail_visuals[b_id] = trail

    def update_frame(self):
        """
        Called periodically by UI timer.
        Synchronizes 3D objects with the current state of the physics engine.
        """
        # Check if bodies array changed (e.g. from collisions or user adding planets)
        if len(self.body_visuals) != len(self.engine.bodies):
            self.init_visuals()
            return
            
        for i, body in enumerate(self.engine.bodies):
            mesh = self.body_visuals[i]
            # Pyqtgraph doesn't have a direct setPosition on Mesh, so we reset transform
            mesh.resetTransform()
            mesh.translate(*body.position)
            
            if i in self.glow_visuals:
                glow = self.glow_visuals[i]
                glow.resetTransform()
                glow.translate(*body.position)
            
            # Update vertical stick
            stick = self.stick_visuals[i]
            stick_pos = np.array([[body.position[0], body.position[1], 0], 
                                 [body.position[0], body.position[1], body.position[2]]])
            stick.setData(pos=stick_pos)
            
            # Update trail
            if len(body.trail) > 1:
                trail_pts = np.array(body.trail)
                trail_item = self.trail_visuals[i]
                trail_item.setData(pos=trail_pts)
