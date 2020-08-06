from .pacman import Pacman


class Scorer:
    def __init__(self):
        self.score = 0

    def reset(self):
        self.score = 0

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
    def __init__(self, fruit_eat=2500, ghost_eat=200, ghost_hit=-1000000,
                 level_finished=0, pellet_eat=10, power_pellet_eat=50):
        Scorer.__init__(self)
        self.fruit_eat = fruit_eat
        self.ghost_hit = ghost_hit
        self.ghost_eat = ghost_eat
        self.ghost_value = ghost_eat
        self.level_finished = level_finished
        self.pellet_eat = pellet_eat
        self.power_pellet_eat = power_pellet_eat

    def score_fruit_eat(self):
        self.score += self.fruit_eat

    def score_ghost_eat(self):
        self.score += self.ghost_value
        self.ghost_value *= 2

    def score_ghost_hit(self):
        self.score += self.ghost_hit

    def score_pellet_eat(self):
        self.score += self.pellet_eat

    def score_power_pellet_eat(self):
        self.score += self.power_pellet_eat
        self.ghost_value = self.ghost_eat

    def score_level_finished(self):
        self.score += self.level_finished
