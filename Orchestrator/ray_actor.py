import ray

@ray.remote
class Actor(object):

    def __init__(self):
        pass

    def reset_env(self):
        pass

    def steps(self, actions):
        for a in actions:
            self.step(a)

    def step(self, action):
        pass

    def returnYields(self):
        pass