from baseClasses import BaseLayer

class LightStripLayer(BaseLayer):
    """
    Light strips placed near doors (which signify exits) + turn red if fire is near, stay cyan otherwise
    + Layer-based, so it stays in the same structure as the fire/smoke/firealarms and main grid.
    """

    def __init__(self, width, height, door_coords, check_radius=4):
        super().__init__(width, height)
        self.door_coords = door_coords  # list of (x, y) door locations can use all doors, or only exits
        self.check_radius = check_radius
        self.status = {}  # maps (x,y) to 'safe' or 'unsafe'

        for (x, y) in door_coords:
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.width and 0 <= ny < self.height:
                        self.status[(nx, ny)] = 'safe'  # Default: all safe

    def update(self, env):
        fire_layer = env.get_layer('fire')
        for (x, y) in self.status:
            x_min = max(0, x - self.check_radius)
            x_max = min(self.width, x + self.check_radius + 1)
            y_min = max(0, y - self.check_radius)
            y_max = min(self.height, y + self.check_radius + 1)

            fire_nearby = False
            for j in range(y_min, y_max):
                for i in range(x_min, x_max):
                    if fire_layer.grid[j][i] > 0:  # fire present
                        fire_nearby = True
                        break
                if fire_nearby:
                    break

            self.status[(x, y)] = 'unsafe' if fire_nearby else 'safe'

    def get_status(self, x, y):
        return self.status.get((x, y), 'safe')


class FireAlarmLayer(BaseLayer):
    def __init__(self, width, height, firealarm_coords, radius=6):
        super().__init__(width, height)
        self.radius = radius  # Radius of the hearing range
        self.firealarm_coords = self.set_firealarm(firealarm_coords)  # x, y coords of the fire alarm locations.
        self.activated = False  # which fire alarm have been triggered
        print(self.firealarm_coords)

    def set_firealarm(self, coords):
        if coords is None:
            grid_coords = []
            for x in range(self.radius, self.width-self.radius, 2*self.radius+padding):
                for y in range(self.radius, self.height-self.radius, 2*self.radius+padding):
                    grid_coords.append((x, y))
            return grid_coords
        else:
            return coords

    def trigger_firealarm(self):
        # After an evacuee/ agent detects the first they "pull the alarm" and trigger all fire alarms
        self.activated = True  # All speakers ON

    def is_agent_in_range(self, agent):
        # returns True if the agent is actually in hearing range of any nearby fire alarm
        if not self.activated or self.radius <= 0:
            return False
        for (sx, sy) in self.firealarm_coords:
            dx, dy = agent.x - sx, agent.y - sy
            if dx * dx + dy * dy <= self.radius * self.radius:
                return True
        return False

    def update(self, env):
        pass