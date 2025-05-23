#from baseClasses import Environment
from fireSimulation import FireLayer
from math import ceil
import random
import heapq

class EvacueeAgent:
    """
    A* pathfinder + smoke/fire avoidance + collision blocking + panic +
    gradual fire damage & health-based coloring +
    probabilistic smoke‐impairment (always one guaranteed move).
    """
    def __init__(self, x, y,
                 smoke_w=5.0, fire_w=100.0,
                 smoke_damage_rate=2.0, slow_threshold=0.5,
                 fire_damage_rate=20.0,
                 panic_radius=3, panic_smoke_threshold=0.1, panic_speed=1):
        self.x, self.y = x, y
        self.smoke_w, self.fire_w = smoke_w, fire_w
        self.smoke_damage_rate, self.slow_threshold = (
            smoke_damage_rate, slow_threshold)
        self.fire_damage_rate = fire_damage_rate
        self.panic_radius = panic_radius
        self.panic_smoke_threshold = panic_smoke_threshold
        self.panic_speed = panic_speed

        self.health = 100.0
        self.alive = True
        self.reached = False

    def snapshot(self):
        return {
            'x': self.x, 'y': self.y,
            'health': self.health,
            'alive': self.alive,
            'reached': self.reached
        }

    @classmethod
    def from_snapshot(cls, data):
        a = cls(data['x'], data['y'])
        a.health, a.alive, a.reached = (
            data['health'], data['alive'], data['reached']
        )
        return a

    def update(self, env: 'Environment'):
        if not self.alive or self.reached:
            return

        struct = env.get_layer('structure')
        fire   = env.get_layer('fire')
        smoke  = env.get_layer('smoke')

        # smoke damage
        conc = smoke.grid[self.y][self.x] if smoke else 0.0
        self.health -= conc * self.smoke_damage_rate

        # gradual fire damage
        if fire and fire.grid[self.y][self.x] == FireLayer.BURNING:
            self.health -= self.fire_damage_rate

        # check for death
        if self.health <= 0.0:
            self.alive = False
            return

        # detect panic in radius
        panic = False
        r = self.panic_radius
        for dy in range(-r, r+1):
            for dx in range(-r, r+1):
                ny, nx = self.y+dy, self.x+dx
                if 0 <= nx < env.width and 0 <= ny < env.height:
                    if ((fire and fire.grid[ny][nx] == FireLayer.BURNING) or
                        (smoke and smoke.grid[ny][nx] >= self.panic_smoke_threshold)):
                        panic = True
                        break
            if panic:
                break

        # compute number of moves with health‐based panic boost
        if panic:
            h = self.health
            if h >= 80:
                mult = 1.0
            elif h >= 40:
                mult = 2.0
            else:
                mult = max(0.1, h / 40.0)
        else:
            mult = 0.0

        moves = 1 + ceil(self.panic_speed * mult)
        exits = env.get_exits()
        if not exits:
            return

        # prepare occupancy and cost/heuristic functions
        occupied = {
            (a.x, a.y)
            for a in env.agents
            if a is not self and a.alive and not a.reached
        }

        def cost(cx, cy):
            if (cx, cy) in occupied:
                return float('inf')
            base = 1.0
            if fire:
                s = fire.grid[cy][cx]
                if s == FireLayer.BURNING:
                    base += self.fire_w
                elif s == FireLayer.BURNED:
                    base += self.fire_w / 2
            if smoke:
                base += smoke.grid[cy][cx] * self.smoke_w
            return base

        def heuristic(cx, cy):
            return min(abs(cx-ex) + abs(cy-ey) for ex,ey in exits)

        # perform up to `moves` steps, but probabilistically impaired by smoke
        for step_i in range(moves):
            conc = smoke.grid[self.y][self.x] if smoke else 0.0
            on_fire = (fire and fire.grid[self.y][self.x] == FireLayer.BURNING)

            # guaranteed first hop
            if step_i == 0:
                can_move = True
            else:
                # chance ∝ (1 - conc)
                can_move = (random.random() < max(0.0, 1 - conc))
                # adrenaline override if on fire
                if on_fire:
                    can_move = can_move or (random.random() < 0.5)

            if not can_move:
                break

            # run one‐step A* toward nearest exit
            start = (self.x, self.y)
            open_set = [(heuristic(*start), 0.0, start, None)]
            came_from = {}
            g_score = {start: 0.0}
            visited = set()
            target = None

            while open_set:
                f, g, (cx,cy), parent = heapq.heappop(open_set)
                if (cx,cy) in visited:
                    continue
                visited.add((cx,cy))
                came_from[(cx,cy)] = parent
                if (cx,cy) in exits:
                    target = (cx,cy)
                    break
                for dx,dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                    nx, ny = cx+dx, cy+dy
                    if not (0<=nx<env.width and 0<=ny<env.height):
                        continue
                    if struct and struct.grid[ny][nx] == struct.WALL:
                        continue
                    step = cost(nx,ny)
                    if step == float('inf'):
                        continue
                    tg = g + step
                    if tg < g_score.get((nx,ny), float('inf')):
                        g_score[(nx,ny)] = tg
                        heapq.heappush(open_set,
                            (tg + heuristic(nx,ny), tg, (nx,ny), (cx,cy)))

            if not target:
                return  # no path

            # reconstruct one‐cell move
            node = target
            path = []
            while node != start:
                path.append(node)
                node = came_from.get(node)
                if node is None:
                    return
            nx, ny = path[-1]
            self.x, self.y = nx, ny

            if (nx,ny) in exits:
                self.reached = True
                break