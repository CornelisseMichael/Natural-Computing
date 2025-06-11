# evaluation metrics: 
#- death rate (The percentage of evacuees that succesfully evacuated the grid)
#- Completion time (At what time step all agents have exited the building or got eliminated  )

class Evaluation:
    def __init__(self, env):
        self.env = env
        self.complete = False
        self.evac_complete_time = 0
        self.evac_death_rate = None
        self.survival_rate = []


    def update(self):
        """Call this once per step to check if evaluation is complete."""
        if self.complete:
            return

        total_agents = len(self.env.agents)
        escaped_agents = sum(1 for a in self.env.agents if a.reached)
        dead_agents = sum(1 for a in self.env.agents if not a.alive)

        self.survival_rate.append(total_agents - dead_agents)

        if (dead_agents + escaped_agents) == total_agents:
            self.complete = True
            self.evac_complete_time = self.env.time


    def report(self):
        if self.evac_complete_time is not None:
            return (
                f"Evacuation completed in {self.evac_complete_time} steps\n"
                f"Death rate at completion: {self.evac_death_rate:.1f}%"
            )
        else:
            return "Evacuation did not complete within the given steps."