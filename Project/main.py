# You’ll need display() to render in Colab/Jupyter
from IPython.display import display, HTML, Image
from structures import Environment
from structures import StructureLayer
from fireSimulation import FireLayer, SmokeLayer
from aids import LightStripLayer, FireAlarmLayer
import matplotlib ; matplotlib.use("TkAgg") #to run the animations in PyCharm
import matplotlib.pyplot as plt
from mapLoading import *
import numpy as np
from EvaluationMetrics import Evaluation
from FireAlarm_config import get_firealarm_config

if __name__ == "__main__":
    # build & seed

    filepath = './maps/obstacles_2.png'

    floormap = loadFromImage(filepath)
    height, width = floormap.shape

    env = Environment(width, height).set_seed(42)
    struct = StructureLayer(width, height)
    struct.grid = floormap.tolist()
    env.add_layer('structure', struct)

    fire = FireLayer(width,height, p_ignite=0.5, burn_time=10, spread_interval=2)
    env.add_layer('fire', fire)
    fire.ignite(5,5)

    smoke = SmokeLayer(width,height, diff_rate=0.1, emit_rate=0.4)
    env.add_layer('smoke', smoke)

    exits = env.get_exits()
    print(exits)
    light = LightStripLayer(width, height, exits)
    env.add_layer('light', light)


    # ==== config settings ==== #
    # Select from baseline, threedoors, obstacles, offices for the first string
    # Select from from floor placement type located in FireAlarm_config
    config = get_firealarm_config('obstacles', 'one_exp3')

    # Initializing FireAlarmLayer
    firealarm = FireAlarmLayer(width, height, firealarm_coords=config['coords'], radius=config['radius']) 
    env.add_layer('firealarm', firealarm)

    env.spawn_agents_randomly(270)
    env.save_initial_state()

    # Evaluator
    evaluator = Evaluation(env)

    # animation
    anim = env.animate(steps=100, interval=100, evaluator= evaluator)
    plt.show() # to show the animation in your IDE (pycharm)


    display(anim)
    #display(HTML(anim.to_jshtml()))
    #anim.save('evac-1.gif', writer='pillow', fps=5)

    print(evaluator.report()) 


