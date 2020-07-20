import sys

import gym
import numpy as np

from ..fruit import *
from ..game import *
from ..ghost import *
from ..level import *
from ..path_finder import *


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

    def __init__(self, gui=False, pauses=False, randomized=False, sound=False):
        self.gui = gui
        self.pauses = pauses
        self.sound = pauses and sound

        if gui:
            pygame.display.set_mode((1, 1))
            pygame.display.set_caption("Pacman")
            init_pygame()

        # create the pacman
        self.player = Pacman(gui)

        # create a path_finder object
        self.path = path_finder()

        # create ghost objects
        self.ghosts = {}
        for i in range(0, 6, 1):
            # remember, ghost[4] is the blue, vulnerable ghost
            self.ghosts[i] = Ghost(i, gui)

        # create piece of fruit
        self.thisFruit = Fruit(gui)

        self.tileIDName = {}  # gives tile name (when the ID# is known)
        self.tileID = {}  # gives tile ID (when the name is known)
        self.tileIDImage = {}  # gives tile image (when the ID# is known)
        self.oldEdgeLightColor = None
        self.oldEdgeShadowColor = None
        self.oldFillColor = None

        # create game and level objects and load first level
        self.thisGame = Game(gui)
        self.thisLevel = level(gui, randomized)

        self.thisGame.StartNewGame(self.thisLevel, self.thisGame,
                                   self.thisFruit, self.player, self.ghosts,
                                   self.path, self.tileID, self.tileIDName,
                                   self.tileIDImage)

        if gui:
            pygame.display.set_mode(self.thisGame.screenSize)
            self.screen = pygame.display.get_surface()

    def check_inputs(self, action):
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
        # CheckIfCloseButton(pygame.event.get())
        # TODO: Keep window from complaining unresponsive
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)

        # normal gameplay mode
        # CheckInputs()
        # TODO: Use action param to control player.
        self.check_inputs(action)
        self.thisGame.modeTimer += 1

        # TODO: Need to extract observations from entity Move functions.
        score = self.player.Move(self.thisLevel, self.ghosts, self.thisGame,
                                 self.path, self.thisFruit, self.tileID)
        for i in range(0, 4, 1):
            self.ghosts[i].Move(self.path, self.player, self.thisLevel,
                                self.tileID)
        self.thisFruit.Move(self.thisGame)

        # TODO: Set observations, reward, etc.
        vision = []
        dir = ((1, 0), (0, -1), (-1, 0), (0, 1))
        doorh = self.tileID["door-h"]
        doorv = self.tileID["door-v"]
        pel = self.tileID["pellet"]
        ppel = self.tileID["pellet-power"]
        fx = self.thisFruit.nearestCol
        fy = self.thisFruit.nearestRow
        gxy = list((g.nearestCol, g.nearestRow) for g in
                   filter(lambda x: x.state == 1, self.ghosts.values()))
        vxy = list((g.nearestCol, g.nearestRow) for g in
                   filter(lambda x: x.state == 2, self.ghosts.values()))

        for d in range(4):
            blocked = False
            x = self.player.nearestCol
            y = self.player.nearestRow
            tile = self.thisLevel.GetMapTile((y, x))
            if any(x == g[0] and y == g[1] for g in gxy):
                vision.append(-2)
            elif any(x == g[0] and y == g[1] for g in vxy):
                vision.append(3)
            elif self.thisFruit.active and fx == x and fy == y:
                vision.append(4)
            elif tile == 0 or tile == doorh or tile == doorv:
                vision.append(0)
            elif tile == pel:
                vision.append(1)
            elif tile == ppel:
                vision.append(2)
            else:
                vision.append(-1)

            for _ in range(5):
                if blocked:
                    vision.append(-1)
                else:
                    # y is row, x is col
                    x += dir[d][0]
                    y += dir[d][1]
                    x %= self.thisLevel.lvlWidth
                    y %= self.thisLevel.lvlHeight
                    tile = self.thisLevel.GetMapTile((y, x))
                    if any(x == g[0] and y == g[1] for g in gxy):
                        vision.append(-2)
                    elif any(x == g[0] and y == g[1] for g in vxy):
                        vision.append(3)
                    elif self.thisFruit.active and fx == x and fy == y:
                        vision.append(4)
                    elif tile == 0 or tile == doorh or tile == doorv:
                        vision.append(0)
                    elif tile == pel:
                        vision.append(1)
                    elif tile == ppel:
                        vision.append(2)
                    else:
                        vision.append(-1)
                        blocked = True

        done = self.thisGame.mode == 2 or self.thisGame.mode == 6
        return np.array(vision), score, done, {"pacmanx": self.player.velX,
                                               "pacmany": self.player.velY}

    def reset(self):
        # lines 125-127 in Move() in pacman.py regards running into a non-vulnerable ghost
        # the static method CheckIfHitSomething() in lines 108-111 of level.py regards obtaining all pellets
        self.thisGame.StartNewGame(self.thisLevel, self.thisGame,
                                   self.thisFruit, self.player, self.ghosts,
                                   self.path, self.tileID, self.tileIDName,
                                   self.tileIDImage)
        pass

    def render(self, mode="human"):
        if not self.gui:
            return

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
