import numpy as np

# JPL Horizons approximate data
# Positions in meters, Velocity in meters/second
# All data relative to the barycenter/sun roughly at J2000 epoch

SYSTEM_DATA = {
    "Sun": {
        "mass": 1.989e30, # kg
        "radius": 696340000, # m
        "position": [0.0, 0.0, 0.0],
        "velocity": [0.0, 0.0, 0.0],
        "color": "#FF3300"
    },
    "Mercury": {
        "mass": 3.3011e23,
        "radius": 2439700.0,
        "position": [57.909e9, 0.0, 0.0], # perihelion
        "velocity": [0.0, 47360.0, 0.0],
        "color": "#A8A8A8"
    },
    "Venus": {
        "mass": 4.8675e24,
        "radius": 6051800.0,
        "position": [108.209e9, 0.0, 0.0],
        "velocity": [0.0, 35020.0, 0.0],
        "color": "#E0C7A6"
    },
    "Earth": {
        "mass": 5.9724e24,
        "radius": 6371000.0,
        "position": [149.596e9, 0.0, 0.0],
        "velocity": [0.0, 29780.0, 0.0],
        "color": "#2B82C9"
    },
    "Mars": {
        "mass": 6.4171e23,
        "radius": 3389500.0,
        "position": [227.923e9, 0.0, 0.0],
        "velocity": [0.0, 24070.0, 0.0],
        "color": "#E27B58"
    },
    "Jupiter": {
        "mass": 1.8982e27,
        "radius": 69911000.0,
        "position": [778.570e9, 0.0, 0.0],
        "velocity": [0.0, 13060.0, 0.0],
        "color": "#C88B3A"
    },
    "Saturn": {
        "mass": 5.6834e26,
        "radius": 58232000.0,
        "position": [1433.529e9, 0.0, 0.0],
        "velocity": [0.0, 9680.0, 0.0],
        "color": "#E4D596"
    },
    "Uranus": {
        "mass": 8.6810e25,
        "radius": 25362000.0,
        "position": [2872.463e9, 0.0, 0.0],
        "velocity": [0.0, 6800.0, 0.0],
        "color": "#9BE4E0"
    },
    "Neptune": {
        "mass": 1.02413e26,
        "radius": 24622000.0,
        "position": [4495.060e9, 0.0, 0.0],
        "velocity": [0.0, 5430.0, 0.0],
        "color": "#3E6AF2"
    }
}

# The Moon (Added as a test for relative orbits)
SYSTEM_DATA["Moon"] = {
    "mass": 7.342e22,
    "radius": 1737400.0,
    "position": [149.596e9 + 384400000.0, 0.0, 0.0], # Earth dist + Lunar dist
    "velocity": [0.0, 29780.0 + 1022.0, 0.0], # Earth vel + Lunar vel
    "color": "#FFFFFF"
}
