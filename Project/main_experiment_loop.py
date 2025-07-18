# You’ll need display() to render in Colab/Jupyter
from IPython.display import display, HTML, Image
from src.structures import Environment
from src.structures import StructureLayer
from src.fireSimulation import FireLayer, SmokeLayer
from src.aids import LightStripLayer, FireAlarmLayer
import matplotlib ; matplotlib.use("TkAgg") #to run the animations in PyCharm
import matplotlib.pyplot as plt
from src.mapLoading import *
import numpy as np
from src.EvaluationMetrics import Evaluation
from src.config.FireAlarm_config import get_firealarm_config
import random
import pandas as pd
import os

def pad_lists(lists):
    max_length = max(len(sublist) for sublist in lists)
    padded_lists = [
        sublist + [sublist[-1]] * (max_length - len(sublist))
        for sublist in lists
    ]
    return padded_lists


if __name__ == "__main__":
    # build & seed
    filepath = 'maps/baseline_1.png'
    # Get the filename with extension
    filename = os.path.basename(filepath)

    # Split the filename into base name and extension
    basename, extension = os.path.splitext(filename)
    config = get_firealarm_config('baseline', 'main')

    floormap = loadFromImage(filepath)
    height, width = floormap.shape
    
    # Generate seeds randomly or define them manually
    seed_range = 10
    random.seed(42)
    seeds = [random.randint(0, 10000) for _ in range(seed_range)]
    print(seeds)
    
    evacuee_densities = ["small", "medium", "large"]
    #evacuee_densities = ["small"]

    scenarios = ["no aids", "lightstrips", "firealarms", "combined"]
    #scenarios = ["combined"]
    
    all_experiment_results = []

    animation_directory_name = "simulation-gifs"
    animation_sub_directory_name = f"{basename}"
    animation_directory_path = os.path.join(animation_directory_name, animation_sub_directory_name)
    os.makedirs(animation_directory_path, exist_ok=True)

    for scene in scenarios:
        for density in evacuee_densities:
            survival_rates = []
            completion_times = []
            for seed in seeds:
                print(f"\n--- Starting Run: Seed={seed}, Density={density}, Scenario={scene} ---")

                env = Environment(width, height).set_seed(seed)
                struct = StructureLayer(width, height)
                struct.grid = floormap.tolist()
                env.add_layer('structure', struct)
                
                exits = env.get_exits()

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
                anim = env.animate(steps=150, interval=100, evaluator=evaluator)
                # Construct the full path for the animation file
                animation_filename = f'{seed}_{basename}_{density}_{scene}.gif'
                full_animation_path = os.path.join(animation_directory_path, animation_filename)
                anim.save(full_animation_path, writer='pillow', fps=5)
                plt.close(anim._fig)

                survival_rates.append(evaluator.survival_rate)
                completion_times.append(evaluator.evac_complete_time)

                print(f"Finished Run: Seed={seed}, Density={density}, Scenario={scene}")

            survival_rates = pad_lists(survival_rates)
            run_results = {
                "map": basename,
                "scenario": scene,
                "evacuee_density": density,
                "average_completion_time": np.mean(completion_times),  # None if not completed
                "average_survival_rate": np.mean(survival_rates, axis=0).tolist(),
            }
            all_experiment_results.append(run_results)

    # --- Saving All Results to CSV ---
    if all_experiment_results: # Check if there are results to save
        results_df = pd.DataFrame(all_experiment_results)
        output_path = "./csv-outputs/" + basename + "_results.csv"
        results_df.to_csv(output_path, index=False)
        print(f"\nAll experiment results saved to {output_path}")
        
        # print("\n--- Sample of Saved Results ---")
        # print(results_df.head())
    else:
        print("\nNo experiment results were collected.")
            
        