# firealarm_configs.py, holds the selection of experimental combination coordinates for the fire alarms. Also includes a function that gets the coords and radius values



FIRE_ALARM_CONFIGS = {
    'baseline': {
        'main': {
            'coords': [(7, 7), (7, 22), (22, 22), (22, 7)],
            'radius': 6
        },
        'corners_exp1': {
            'coords': [(7, 7), (7, 22), (22, 22), (22, 7)],
            'radius': 6
        },
        'vertical_exp1': {
            'coords': [(15, 7), (15, 22)],
            'radius': 8
        },
        'Rdiagonal_exp1': {
            'coords': [(7, 7), (22, 22)],
            'radius': 8
        },
        'Ldiagonal_exp1': {
            'coords': [(22, 7), (7, 22)],
            'radius': 8
        },
        'one_exp1': {
            'coords': [(15, 15)],
            'radius': 12
        }
    },

    'threedoors': {
        'main': {
            'coords': [(7, 7), (7, 22), (22, 22), (22, 7)],
            'radius': 6
        },
        'corners_exp2': {
            'coords': [(7, 7), (7, 22), (22, 22), (22, 7)],
            'radius': 6
        },
        'vertical_exp2': {
            'coords': [(15, 7), (15, 22)],
            'radius': 8
        },
        'Rdiagonal_exp2': {
            'coords': [(7, 7), (22, 22)],
            'radius': 8
        },
        'Ldiagonal_exp2': {
            'coords': [(22, 7), (7, 22)],
            'radius': 8
        },
        'one_exp2': {
            'coords': [(15, 13)],
            'radius': 12
        }
    },

    'obstacles': {
        'main': {
            'coords': [(8, 22), (8, 7), (21, 15), (32, 7), (32, 22)],
            'radius': 6
        },
        'five_exp3': {
            'coords': [(8, 22), (8, 7), (21, 15), (32, 7), (32, 22)],
            'radius': 6
        },
        'corners_exp3': {
            'coords': [(8, 22), (8, 7), (32, 7), (32, 22)],
            'radius': 8
        },
        'three_exp3': {
            'coords': [(8, 15), (21, 15), (32, 15)],
            'radius': 8
        },
        'two_exp3': {
            'coords': [(12, 15), (32, 15)],
            'radius': 10
        },
        'one_exp3': {
            'coords': [(22, 15)],
            'radius': 14
        }
    },

    'offices': {
        'main': {
            'coords': [(5, 7), (15, 7), (25, 7), (35, 7), (45, 7), (55, 7), (63, 7),
                       (5, 37), (15, 37), (25, 37), (35, 37), (47, 37), (11, 22), (33, 22), (55, 22)],
            'radius': 6
        },
        'max_exp4': {
            'coords': [(5, 7), (15, 7), (25, 7), (35, 7), (45, 7), (55, 7), (63, 7),
                       (5, 37), (15, 37), (25, 37), (35, 37), (47, 37), (11, 22), (33, 22), (55, 22)],
            'radius': 6
        },
        'rooms_exp4': {
            'coords': [(5, 7), (15, 7), (25, 7), (35, 7), (45, 7), (55, 7), (63, 7),
                       (5, 37), (15, 37), (25, 37), (35, 37), (47, 37)],
            'radius': 6
        },
        'three_exp4': {
            'coords': [(11, 22), (33, 22), (55, 22)],
            'radius': 12
        },
        'one_exp4': {
            'coords': [(33, 22)],
            'radius': 14
        }
    }
}


def get_firealarm_config(map_name: str, config_name: str):
    """
    Returns the fire alarm configuration dictionary for the given map and configuration name.
    """
    try:
        return FIRE_ALARM_CONFIGS[map_name][config_name]
    except KeyError:
        raise ValueError(f"Invalid config: '{map_name}.{config_name}' not found.")
