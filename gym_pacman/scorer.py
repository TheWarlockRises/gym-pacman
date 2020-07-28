from .pacman import Pacman


class Scorer:
    def __init__(self):
        self.score = 0

    def reset(self):
        self.score = 0

    def get_score(self):
        return self.score

    def score_door_entry(self):
        pass

    def score_fruit_eat(self):
        pass

    def score_ghost_eat(self):
        pass

    def score_ghost_hit(self):
        pass

    def score_movement(self, pacman: Pacman):
        pass

    def score_pellet_eat(self):
        pass

    def score_power_pellet_eat(self):
        pass

    def score_level_finished(self):
        pass

    def score_wall_hit(self):
        pass
