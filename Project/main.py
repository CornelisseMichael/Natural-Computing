# You’ll need display() to render in Colab/Jupyter
from IPython.display import display, HTML, Image
from structures import Environment
from structures import StructureLayer
from fireSimulation import FireLayer, SmokeLayer
import matplotlib; matplotlib.use("TkAgg") #to run the animations in PyCharm
import matplotlib.pyplot as plt



if __name__ == "__main__":
    # build & seed
    env = Environment(30,30).set_seed(42)

    # layers & ignition
    struct = StructureLayer(30,30)
    struct.create_room(0,0,29,29)
    struct.add_wall(0,15,29,15)
    struct.add_door(15,15)
    struct.add_door(10,0)
    struct.add_door(20,29)
    env.add_layer('structure', struct)

    fire = FireLayer(30,30, p_ignite=0.5, burn_time=5, spread_interval=2)
    env.add_layer('fire', fire)
    fire.ignite(5,25)

    smoke = SmokeLayer(30,30, diff_rate=0.1, emit_rate=0.4)
    env.add_layer('smoke', smoke)

    env.spawn_agents_randomly(75)
    env.save_initial_state()

    # static preview
    # for i in range(5):
    #     env.step()
    #     env.display()

    # animation
    anim = env.animate(steps=100, interval=100)
    plt.show() # to show the animation in your IDE (pycharm)


    #display(anim)
    #display(HTML(anim.to_jshtml()))

