#from baseClasses import Environment
from baseClasses import BaseLayer
import random

class FireLayer(BaseLayer):
    UNBURNED, BURNING, BURNED = 0,1,2

    def __init__(self, w, h, *, p_ignite=0.6, burn_time=3, spread_interval=2):
        super().__init__(w, h)
        self.p_ignite        = p_ignite
        self.burn_time       = burn_time
        self.spread_interval = spread_interval
        self._timer          = [[0]*w for _ in range(h)]
        self._step_count     = 0

    def ignite(self, x: int, y: int):
        self.grid[y][x]    = self.BURNING
        self._timer[y][x]  = self.burn_time

    def update(self, env: 'Environment'):
        struct    = env.get_layer('structure')
        new_grid  = [row.copy() for row in self.grid]
        new_timer = [row.copy() for row in self._timer]
        self._step_count += 1

        for y in range(self.height):
            for x in range(self.width):
                if struct and struct.grid[y][x] == struct.WALL:
                    new_grid[y][x]   = self.UNBURNED
                    new_timer[y][x]  = 0
                    continue

                state = self.grid[y][x]
                if state == self.BURNING:
                    if self._timer[y][x] > 1:
                        new_timer[y][x] = self._timer[y][x] - 1
                        new_grid[y][x]  = self.BURNING
                    else:
                        new_timer[y][x] = 0
                        new_grid[y][x]  = self.BURNED

                elif state == self.UNBURNED and \
                     (self._step_count % self.spread_interval) == 0:
                    for dy in (-1,0,1):
                        for dx in (-1,0,1):
                            if dx==0 and dy==0: continue
                            ny, nx = y+dy, x+dx
                            if (0 <= nx < self.width and
                                0 <= ny < self.height and
                                self.grid[ny][nx] == self.BURNING and
                                random.random() <= self.p_ignite):
                                new_grid[y][x]   = self.BURNING
                                new_timer[y][x]  = self.burn_time
                                break
                        else:
                            continue
                        break

        self.grid  = new_grid
        self._timer = new_timer


class SmokeLayer(BaseLayer):
    def __init__(self, w, h, diff_rate=0.2, emit_rate=0.5):
        super().__init__(w, h)
        self.grid      = [[0.0]*w for _ in range(h)]
        self.diff_rate = diff_rate
        self.emit_rate = emit_rate

    def update(self, env: 'Environment'):
        fire   = env.get_layer('fire')
        struct = env.get_layer('structure')
        new    = [row.copy() for row in self.grid]

        for y in range(self.height):
            for x in range(self.width):
                if struct and struct.grid[y][x] == struct.WALL:
                    new[y][x] = 0.0
                    continue
                if fire and fire.grid[y][x] == FireLayer.BURNING:
                    new[y][x] = min(1.0, new[y][x] + self.emit_rate)
                delta = 0.0
                for dy,dx in [(-1,0),(1,0),(0,-1),(0,1)]:
                    ny, nx = y+dy, x+dx
                    if (0 <= nx < self.width and 0 <= ny < self.height and
                        not (struct and struct.grid[ny][nx] == struct.WALL)):
                        delta += (self.grid[ny][nx] - self.grid[y][x])
                new[y][x] = max(0.0, min(1.0, new[y][x] + self.diff_rate*delta))

        self.grid = new