# You’ll need display() to render in Colab/Jupyter
from IPython.display import display, HTML, Image
from src.structures import Environment
from src.structures import StructureLayer
from src.fireSimulation import FireLayer, SmokeLayer
from src.aids import LightStripLayer, FireAlarmLayer
import matplotlib; matplotlib.use("TkAgg") #to run the animations in PyCharm
import matplotlib.pyplot as plt
from src.mapLoading import *
import numpy as np
from src.EvaluationMetrics import Evaluation
from src.config.FireAlarm_config import get_firealarm_config
import random

if __name__ == "__main__":
    # build & seed

    filepath = 'maps/obstacles_2.png'

    floormap = loadFromImage(filepath)
    height, width = floormap.shape

    env = Environment(width, height).set_seed(0)
    struct = StructureLayer(width, height)
    struct.grid = floormap.tolist()
    env.add_layer('structure', struct)

    fire = FireLayer(width,height, p_ignite=0.5, burn_time=10, spread_interval=2)
    env.add_layer('fire', fire)
    #fire.ignite(5,5)
    #env.ignite_fire([(5, 5), (10, 10)])
    env.ignite_fire_randomly(n=1)

    smoke = SmokeLayer(width,height, diff_rate=0.1, emit_rate=0.4)
    env.add_layer('smoke', smoke)

    exits = env.get_exits()
    light = LightStripLayer(width, height, exits)
    env.add_layer('light', light)


    # ==== config settings ==== #
    # Select from baseline, threedoors, obstacles, offices for the first string
    # Select from from floor placement type located in FireAlarm_config
    config = get_firealarm_config('obstacles', 'one_exp3')

    # Initializing FireAlarmLayer
    firealarm = FireAlarmLayer(width, height, firealarm_coords=config['coords'], radius=config['radius']) 
    env.add_layer('firealarm', firealarm)

    #env.spawn_agents_randomly(270)
    env.spawn_agents(density='small')
    env.save_initial_state()

    # Evaluator
    evaluator = Evaluation(env)

    # animation
    anim = env.animate(steps=100, interval=100, evaluator=evaluator)
    plt.show()
    # if env.time > 100:
    # # if ((sum(1 for a in env.agents if not a.alive))+(sum(1 for a in env.agents if a.reached))) == len(env.agents):
    #     plt.pause(3)
    plt.close() # to show the animation in your IDE (pycharm)


    display(anim)
    #display(HTML(anim.to_jshtml()))
    #anim.save('evac-1.gif', writer='pillow', fps=5)

    print(evaluator.survival_rate)


