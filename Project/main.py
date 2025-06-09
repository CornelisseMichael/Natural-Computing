# You’ll need display() to render in Colab/Jupyter
from IPython.display import display, HTML, Image
from structures import Environment
from structures import StructureLayer
from fireSimulation import FireLayer, SmokeLayer
from aids import LightStripLayer, SpeakerLayer
import matplotlib ; matplotlib.use("TkAgg") #to run the animations in PyCharm
import matplotlib.pyplot as plt
from mapLoading import *
import numpy as np



if __name__ == "__main__":
    # build & seed

    filepath = './maps/offices_1.png'

    floormap = loadFromImage(filepath)
    height, width = floormap.shape

    env = Environment(width, height).set_seed(42)
    struct = StructureLayer(width, height)
    struct.grid = floormap.tolist()
    env.add_layer('structure', struct)



    # layers & ignition
    # struct = StructureLayer(30,30)
    # struct.create_room(0,0,29,29)
    # struct.add_wall(0,15,29,15)
    # struct.add_door(15,15)
    # struct.add_door(10,0)
    # struct.add_door(20,29)
    # env.add_layer('structure', struct)

    fire = FireLayer(width,height, p_ignite=0.5, burn_time=10, spread_interval=2)
    env.add_layer('fire', fire)
    fire.ignite(5,5)

    smoke = SmokeLayer(width,height, diff_rate=0.1, emit_rate=0.4)
    env.add_layer('smoke', smoke)

    exits = env.get_exits()
    print(exits)
    light = LightStripLayer(width, height, exits)
    env.add_layer('light', light)

    speaker_positions = [(25, 5), (5, 25), (25, 25)]
    speakers = SpeakerLayer(width, height, speaker_coords=None, radius=8)
    env.add_layer('speakers', speakers)

    env.spawn_agents_randomly(75)
    env.save_initial_state()

    # static preview
    # for i in range(5):
    #     env.step()
    #     env.display()

    # animation
    anim = env.animate(steps=100, interval=100)
    plt.show() # to show the animation in your IDE (pycharm)


    display(anim)
    #display(HTML(anim.to_jshtml()))
    #anim.save('evac-1.gif', writer='pillow', fps=5)

