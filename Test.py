from art import tprint
import numpy as np
import math
import Assets

#tprint('TITLE')

drones = {
    'Blinky': {
        'id': 0,
        'color': Assets.DroneColors.RED.value,
        'battery': 100,
        'status': 'Ready'
    },
    'Pinky': {
        'id': 1,
        'color': Assets.DroneColors.PINK.value,
        'battery': 100,
        'status': 'Ready'
    },
    'Inky': {
        'id': 2,
        'color': Assets.DroneColors.L_BLUE.value,
        'battery': 100,
        'status': 'Ready'
    },
    'Clyde': {
        'id': 3,
        'color': Assets.DroneColors.ORANGE.value,
        'battery': 100,
        'status': 'Ready'
    },
    'Sue': {
        'id': 4,
        'color': Assets.DroneColors.PURPLE.value,
        'battery': 100,
        'status': 'Ready'
    },
    'Tim': {
        'id': 5,
        'color': Assets.DroneColors.BROWN.value,
        'battery': 100,
        'status': 'Ready'
    },
    'Funky': {
        'id': 6,
        'color': Assets.DroneColors.GREEN.value,
        'battery': 100,
        'status': 'Ready'
    },
    'Kinky': {
        'id': 7,
        'color': Assets.DroneColors.GOLD.value,
        'battery': 100,
        'status': 'Ready'
    }
}

for drone in drones:
    print(drone + ":")
    for attribute in drones[drone]:
        print(f"    {attribute}: {drones[drone][attribute]}")