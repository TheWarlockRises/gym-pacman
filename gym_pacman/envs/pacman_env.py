from sys import exit

import gym
from gym.spaces import Box, Discrete
from gym.utils.seeding import np_random

from ..fruit import *
from ..game import *
from ..ghost import *
from ..level import *
from ..path_finder import *
from ..scorer import *
from ..sensor import *


# game "mode" variable
# 0 = ready to level start
# 1 = normal
# 2 = hit ghost
# 3 = game over
# 4 = wait to start
# 5 = wait after eating ghost
# 6 = wait after finishing level
# 7 = flashing maze after finishing level
# 8 = extra pacman, small ghost mode
# 9 = changed ghost to glasses
# 10 = blank screen before changing levels
# TODO: Skip over pause frames (e.g. pause when ghost eaten)


class PacmanEnv(gym.Env):
    metadata = {"render.modes": ["human"]}

    def __init__(self, invincible=False, level=None, randomized=False,
                 scorer=BasicScorer(), sensor=sensor_1d_4(10), sound=False):
        # OpenAI Variables
        self.action = 2
        self.action_space = Discrete(4)
        self.observation_space = Box(-1, 5, shape=sensor(None).shape,
                                     dtype=int)
        self.random, _ = np_random(None)

        # Pac-Man Variables
        self.gui = False
        self.invincible = invincible
        self.level = level
        self.scorer = scorer
        self.sensor = sensor
        self.sound = sound

        # create the pacman
        self.player = Pacman()

        # create a path_finder object
        self.path = path_finder()

        # create ghost objects
        self.ghosts = {}
        for i in range(0, 6, 1):
            # remember, ghost[4] is the blue, vulnerable ghost
            self.ghosts[i] = Ghost(i)

        # create piece of fruit
        self.thisFruit = Fruit()

        self.tileIDName = {}  # gives tile name (when the ID# is known)
        self.tileID = {}  # gives tile ID (when the name is known)
        self.tileIDImage = {}  # gives tile image (when the ID# is known)
        self.oldEdgeLightColor = None
        self.oldEdgeShadowColor = None
        self.oldFillColor = None

        # create game and level objects and load first level
        self.thisGame = Game()
        self.thisLevel = Level(randomized)

        self.thisGame.StartNewGame(self.thisLevel, self.thisGame,
                                   self.thisFruit, self.player, self.ghosts,
                                   self.path, self.tileID, self.tileIDName,
                                   self.random, self.level)

        # Rendering Variables
        self.screen = None

    def seed(self, seed=None):
        self.random, seed = np_random(seed)
        return [seed]

    def check_inputs(self, action):
        self.action = action
        if action == 0 and not self.thisLevel.CheckIfHitWall(
                (self.player.x + self.player.speed, self.player.y),
                (self.player.nearestRow, self.player.nearestCol)):
            self.player.velX = self.player.speed
            self.player.velY = 0
        elif action == 1 and not self.thisLevel.CheckIfHitWall(
                (self.player.x, self.player.y - self.player.speed),
                (self.player.nearestRow, self.player.nearestCol)):
            self.player.velX = 0
            self.player.velY = -self.player.speed
        elif action == 2 and not self.thisLevel.CheckIfHitWall(
                (self.player.x - self.player.speed, self.player.y),
                (self.player.nearestRow, self.player.nearestCol)):
            self.player.velX = -self.player.speed
            self.player.velY = 0
        elif action == 3 and not self.thisLevel.CheckIfHitWall(
                (self.player.x, self.player.y + self.player.speed),
                (self.player.nearestRow, self.player.nearestCol)):
            self.player.velX = 0
            self.player.velY = self.player.speed

    def step(self, action):
        # Use action param to control player.
        self.check_inputs(action)
        self.thisGame.modeTimer += 1

        # Extract observations from entity Move functions.
        self.scorer.reset()
        self.player.Move(self.thisLevel, self.ghosts, self.thisGame, self.path,
                         self.thisFruit, self.tileID, self.scorer, self.random)

        for i in range(0, 4, 1):
            self.ghosts[i].Move(self.path, self.player, self.thisLevel,
                                self.tileID, self.random)
        self.thisFruit.Move(self.thisGame)

        observation = self.sensor(self)

        if self.invincible and self.thisGame.mode == 2:
            self.thisGame.mode = 1
        done = self.thisGame.mode == 2 or self.thisGame.mode == 6
        # TODO: Return number of frames to pause for sound FX
        return observation, self.scorer.score, done, {
            "action": self.action, "pacmanx": self.player.velX,
            "pacmany": self.player.velY}

    def reset(self):
        # lines 125-127 in Move() in pacman.py regards running into a
        # non-vulnerable ghost
        # the static method CheckIfHitSomething() in lines 108-111 of level.py
        # regards obtaining all pellets
        self.thisLevel.gui = False  # Get renderer to call crossref again.
        self.action = 2  # Reset observation direction.
        self.thisGame.StartNewGame(self.thisLevel, self.thisGame,
                                   self.thisFruit, self.player, self.ghosts,
                                   self.path, self.tileID, self.tileIDName,
                                   self.random, self.level)
        return self.sensor(self)

    def render(self, mode="human"):
        if not self.gui:
            pygame.display.set_mode((1, 1))
            pygame.display.set_caption("Pacman")
            init_pygame()
            pygame.display.set_mode(self.thisGame.screenSize)
            self.screen = pygame.display.get_surface()
            for g in self.ghosts.values():
                g.init_pygame()
            self.gui = True

        # Keep Windows from calling window unresponsive.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit(0)

        self.thisGame.SmartMoveScreen(self.player, self.thisLevel,
                                      self.thisGame)
        self.screen.blit(get_img_background(), (0, 0))

        self.thisLevel.DrawMap(self.thisGame, self.tileID, self.screen,
                               self.tileIDImage)

        for i in range(0, 4, 1):
            self.ghosts[i].Draw(self.thisGame, self.player, self.screen,
                                self.ghosts, self.tileIDImage, self.tileID)
        self.thisFruit.Draw(self.thisGame, self.screen)
        self.player.Draw(self.thisGame, self.screen)

        self.thisGame.DrawScore(self.screen, self.thisFruit)

        pygame.display.update()

    def close(self):
        # I believe this would just exit the environment from render()
        pass
