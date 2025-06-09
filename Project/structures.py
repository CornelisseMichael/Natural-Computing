from baseClasses import BaseLayer
from agentEvacuee import EvacueeAgent
import random
import numpy as np
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.lines import Line2D
import copy
import matplotlib.pyplot as plt
from IPython.display import display, HTML, Image
import matplotlib.animation as animation


class StructureLayer(BaseLayer):
    EMPTY, WALL, DOOR = 0,1,2

    def add_wall(self, x1,y1,x2,y2):
        if x1==x2:
            for y in range(min(y1,y2), max(y1,y2)+1):
                self.grid[y][x1] = self.WALL
        elif y1==y2:
            for x in range(min(x1,x2), max(x1,x2)+1):
                self.grid[y1][x] = self.WALL
        else:
            raise ValueError("Only horiz/vert walls")

    def add_door(self, x,y):
        self.grid[y][x] = self.DOOR

    def create_room(self, x1,y1,x2,y2):
        self.add_wall(x1,y1,x2,y1)
        self.add_wall(x1,y2,x2,y2)
        self.add_wall(x1,y1,x1,y2)
        self.add_wall(x2,y1,x2,y2)

    def update(self, env): pass


fire_cmap = ListedColormap(['#ffffff', '#fd8d3c', '#e31a1c'])
fire_norm = BoundaryNorm([0, 1, 2, 3], fire_cmap.N)
class Environment:
    """
    Holds layers and agents.
    - .set_seed(seed): fix randomness before setup
    - .save_initial_state(): snapshot for reproducible runs
    - .display(): static frame
    - .animate(steps,interval): inline animation starting at Step 0
    """
    def __init__(self, width: int, height: int):
        self.width, self.height = width, height
        self.layers = {}
        self.agents = []
        self._layers_snapshot = None
        self._agents_snapshot = None
        self._rng_snapshot = None
        self.time = 0

    def set_seed(self, seed: int):
        random.seed(seed)
        return self

    def add_layer(self, name: str, layer: BaseLayer):
        if layer.width != self.width or layer.height != self.height:
            raise ValueError("Layer size mismatch")
        self.layers[name] = layer
        return self

    def get_layer(self, name: str):
        return self.layers.get(name)

    def add_agent(self, agent: 'EvacueeAgent'):
        self.agents.append(agent)
        return self

    def spawn_agents_randomly(self, n: int):
        struct = self.get_layer('structure')
        if struct is None:
            raise RuntimeError("Add structure layer first")
        print(len(struct.grid))
        empties = [
            (x,y)
            for y in range(self.height)
            for x in range(self.width)
            if struct.grid[y][x] == struct.EMPTY
        ]
        if n > len(empties):
            raise ValueError(f"Only {len(empties)} free cells")
        for x,y in random.sample(empties, n):
            self.add_agent(EvacueeAgent(x,y))
        return self

    def get_exits(self):
        struct = self.get_layer('structure')
        exits = []
        if struct:
            for y in range(self.height):
                for x in range(self.width):
                    if struct.grid[y][x] == struct.DOOR and (
                       x in (0, self.width-1) or y in (0, self.height-1)
                    ):
                        exits.append((x,y))
        return exits

    def update_layers(self):
        for layer in self.layers.values():
            layer.update(self)

    def update_agents(self):
        for a in self.agents:
            a.update(self)

    def step(self):
        self.update_layers()
        self.update_agents()
        self.time += 1

    def _draw(self, ax):
        # 1) Fire (bottom)
        fire = self.get_layer('fire')
        if fire:
            ax.imshow(
                np.array(fire.grid),
                cmap=fire_cmap,
                norm=fire_norm,
                alpha=1.0,
                origin='lower',
                zorder=1
            )

        # 2) Smoke
        smoke = self.get_layer('smoke')
        if smoke:
            ax.imshow(
                np.array(smoke.grid),
                cmap='Blues',
                alpha=0.2,
                origin='lower',
                zorder=2
            )

        # 3) Structure: walls & doors only
        struct = self.get_layer('structure')
        if struct:
            grid = np.array(struct.grid)

            walls_mask = (grid == struct.WALL)
            ax.imshow(
                np.ma.masked_where(~walls_mask, walls_mask),
                cmap=ListedColormap(['gray']),
                alpha=1.0,
                origin='lower',
                zorder=3
            )

            doors_mask = (grid == struct.DOOR)
            ax.imshow(
                np.ma.masked_where(~doors_mask, doors_mask),
                cmap=ListedColormap(['black']),
                alpha=1.0,
                origin='lower',
                zorder=4
            )

        # 4) Agents, color‐coded by health
        healthy   = [(a.x,a.y) for a in self.agents if a.alive and not a.reached and a.health > 66]
        mild      = [(a.x,a.y) for a in self.agents if a.alive and not a.reached and 33 < a.health <= 66]
        critical  = [(a.x,a.y) for a in self.agents if a.alive and not a.reached and 0 < a.health <= 33]
        dead      = [(a.x,a.y) for a in self.agents if not a.alive]

        for coords, color, marker in [
            (healthy,  'green', 'o'),
            (mild,     'yellow','o'),
            (critical, 'orange','o'),
        ]:
            if coords:
                xs, ys = zip(*coords)
                ax.scatter(xs, ys, c=color, s=20, edgecolors='black', marker=marker, zorder=5)

        if dead:
            xs, ys = zip(*dead)
            ax.scatter(xs, ys, c='red', s=20, marker='X', zorder=5)

        # 5) Legend with current counts
        count_healthy = sum(1 for a in self.agents if a.alive and a.health>66)
        count_mild = sum(1 for a in self.agents if a.alive and 33<a.health<=66)
        count_critical = sum(1 for a in self.agents if a.alive and 0<a.health<=33)
        count_dead = sum(1 for a in self.agents if not a.alive)

        legend_handles = [
            Line2D([0],[0], marker='o', color='w',
                   label=f'Healthy: {count_healthy}',
                   markerfacecolor='green',   markeredgecolor='black', markersize=8),
            Line2D([0],[0], marker='o', color='w',
                   label=f'Mildly: {count_mild}',
                   markerfacecolor='yellow',  markeredgecolor='black', markersize=8),
            Line2D([0],[0], marker='o', color='w',
                   label=f'Critical: {count_critical}',
                   markerfacecolor='orange',  markeredgecolor='black', markersize=8),
            Line2D([0],[0], marker='X', color='w',
                   label=f'Dead: {count_dead}',
                   markerfacecolor='red',     markersize=8),
        ]
        ax.legend(handles=legend_handles, loc='upper left', bbox_to_anchor=(1.05,1))

        # 6) Title
        alive_count  = sum(1 for a in self.agents if a.alive)
        dead_count   = count_dead
        exited_count = sum(1 for a in self.agents if a.reached)
        ax.set_title(f"Alive: {alive_count}, Dead: {dead_count}, Exited: {exited_count}")
        ax.set_xticks([]); ax.set_yticks([])

        #7) aids
        light = self.get_layer('light')
        if light:
            for (x, y), status in light.status.items():
                color = 'cyan' if status == 'safe' else 'red'
                ax.scatter(x, y, c=color, marker='s', s=100, edgecolors='black', linewidths=0.5, zorder=4.5)

        firealarm_layer = self.get_layer('firealarm')
        if firealarm_layer:
            for (x, y) in firealarm_layer.firealarm_coords:
                # Visual circle only if radius > 0 and speakers are activated
                if firealarm_layer.activated and firealarm_layer.radius > 0:
                    circle = plt.Circle((x, y), firealarm_layer.radius, color='blue', alpha=0.2, zorder=6)
                    ax.add_patch(circle)

                edge_color = 'lime' if firealarm_layer.activated else 'white'
                ax.scatter(x, y, c='black', s=60, marker='^', edgecolors=edge_color, linewidths=1.5, zorder=3)

    def display(self):
        fig, ax = plt.subplots(figsize=(6,6))
        fig.subplots_adjust(right=0.75)
        self._draw(ax)
        plt.show()

    def save_initial_state(self):
        """Snapshot all layers, agents, and RNG state."""
        self._layers_snapshot = copy.deepcopy(self.layers)
        self._agents_snapshot = copy.deepcopy(self.agents)
        self._rng_snapshot    = random.getstate()
        return self

    def reset(self):
        """Restore to the snapshot taken by save_initial_state()."""
        if self._layers_snapshot is None:
            raise RuntimeError("Call save_initial_state() first.")
        self.layers = copy.deepcopy(self._layers_snapshot)
        self.agents = copy.deepcopy(self._agents_snapshot)
        random.setstate(self._rng_snapshot)
        return self

    def animate(self, steps: int, interval: int=500, evaluator = None) -> HTML:
        self.reset()
        fig, ax = plt.subplots(figsize=(8,6))
        fig.subplots_adjust(right=0.75)

        def init():
            ax.clear()
            self._draw(ax)
            ax.set_title("Step 0")
            return []

        def update(i):
            ax.clear()
            self.step()
            if evaluator:
                evaluator.update() # Calling evaluator from evaluation metrics
            self._draw(ax)
            ax.set_title(f"Step {i}")
            return []

        ani = animation.FuncAnimation(
            fig, update,
            frames=range(1, steps+1),
            init_func=init,
            interval=interval,
            blit=True
        )
        return ani