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


class BasicScorer(Scorer):
    def __init__(self, end_score=1000000):
        Scorer.__init__(self)
        self.end_score = end_score
        self.ghost_value = 0

    def score_fruit_eat(self):
        self.score += 2500

    def score_ghost_eat(self):
        self.score += self.ghost_value
        self.ghost_value *= 2

    def score_ghost_hit(self):
        self.score -= self.end_score

    def score_pellet_eat(self):
        self.score += 10

    def score_power_pellet_eat(self):
        self.score += 100
        self.ghost_value = 200

    def score_level_finished(self):
        self.score += self.end_score
