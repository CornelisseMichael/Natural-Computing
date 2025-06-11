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
import random
import pandas as pd
import os


if __name__ == "__main__":
    # build & seed
    filepath = './maps/obstacles_2.png'
    # Get the filename with extension
    filename = os.path.basename(filepath)

    # Split the filename into base name and extension
    basename, extension = os.path.splitext(filename)
    config = get_firealarm_config('obstacles', 'one_exp3')

    floormap = loadFromImage(filepath)
    height, width = floormap.shape
    
    # Generate seeds randomly or define them manually
    seed_range = 1
    random.seed(42)
    seeds = [random.randint(0, 10000) for _ in range(seed_range)]
    print(seeds)
    
    #evacuee_densities = ["small", "medium", "large"]
    
    evacuee_densities = ["small"]

    #scenarios = ["no aids", "lightstrips", "firealarms", "combined"]
    
    scenarios = ["no aids"]
    
    all_experiment_results = []
    
    animation_directory_name = "simulation-gifs"
    os.makedirs(animation_directory_name, exist_ok=True)
    
    for seed in seeds:
        for density in evacuee_densities:
            for scene in scenarios:
                print(f"\n--- Starting Run: Seed={seed}, Density={density}, Scenario={scene} ---")

                env = Environment(width, height).set_seed(seed)
                struct = StructureLayer(width, height)
                struct.grid = floormap.tolist()
                env.add_layer('structure', struct)
                
                exits = env.get_exits()
                print(exits)

                fire = FireLayer(width,height, p_ignite=0.5, burn_time=10, spread_interval=2)
                env.add_layer('fire', fire)
                env.ignite_fire_randomly(n=1)
                
                smoke = SmokeLayer(width,height, diff_rate=0.1, emit_rate=0.4)
                env.add_layer('smoke', smoke)
                
                if scene == "lightstrips" or scene == "combined":
                    print(f"adding lightstrips for {scene}")
                    light = LightStripLayer(width, height, exits)
                    env.add_layer('light', light)
                
                if scene == "firealarms" or scene == "combined":
                    print(f"Adding firealarms for {scene}")
                    firealarm = FireAlarmLayer(width, height, firealarm_coords=config['coords'], radius=config['radius'])
                    env.add_layer('firealarm', firealarm)

                
                #env.spawn_agents_randomly(27)
                env.spawn_agents(density=density)
                env.save_initial_state()

                # Evaluator
                evaluator = Evaluation(env)

                # animation
                anim = env.animate(steps=1000, interval=100, evaluator= evaluator)
                #anim.save(f'{filename}_{density}_{scene}', writer='pillow', fps=5)

                plt.show() # to show the animation in your IDE (pycharm)
                display(anim)
                
                

                #print(evaluator.report())  

                run_results = {
                    "seed": seed,
                    "evacuee_density": density,
                    "scenario": scene,
                    "completion_time": evaluator.evac_complete_time, # None if not completed
                    "death_rate_percent": evaluator.evac_death_rate, # None if not completed
                }
                
                all_experiment_results.append(run_results)
                
                # Print the report for the current run
                print(evaluator.report()) 
                print(f"Finished Run: Seed={seed}, Density={density}, Scenario={scene}")

    # --- Saving All Results to CSV ---
    if all_experiment_results: # Check if there are results to save
        results_df = pd.DataFrame(all_experiment_results)
        output_filename = "simulation_results.csv"
        results_df.to_csv(output_filename, index=False)
        print(f"\nAll experiment results saved to {output_filename}")
        
        # print("\n--- Sample of Saved Results ---")
        # print(results_df.head())
    else:
        print("\nNo experiment results were collected.")
            
        