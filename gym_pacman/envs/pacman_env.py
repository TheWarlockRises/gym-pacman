import gym

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

    def __init__(self, gui=False, pauses=False, sound=False):
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
        self.thisLevel = level(gui)

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
        if self.thisGame.mode == 0 or self.thisGame.mode == 4:
            # ready to level start
            # self.thisGame.modeTimer += 1
            # if self.thisGame.modeTimer == 150:
            self.thisGame.SetMode(1)

        if self.thisGame.mode == 1:
            # normal gameplay mode
            # CheckInputs()
            # TODO: Use action param to control player.
            self.check_inputs(action)
            self.thisGame.modeTimer += 1

            self.player.Move(self.thisLevel, self.ghosts, self.thisGame,
                             self.path, self.thisFruit, self.tileID)
            for i in range(0, 4, 1):
                self.ghosts[i].Move(self.path, self.player, self.thisLevel,
                                    self.tileID)
            self.thisFruit.Move(self.thisGame)

        # elif self.thisGame.mode == 2:
        # waiting after getting hit by a ghost
        # self.thisGame.modeTimer += 1

        # if self.thisGame.modeTimer == 60:
        # self.thisLevel.Restart()

        # self.thisGame.lives -= 1
        # if self.thisGame.lives == -1:
        # self.thisGame.updatehiscores(self.thisGame.score)
        # self.thisGame.SetMode(3)
        # self.thisGame.drawmidgamehiscores()
        # else:
        # self.thisGame.SetMode(4)

        elif self.thisGame.mode == 2 or self.thisGame.mode == 3:
            # TODO: Scoring
            pass
            # game over
            # CheckInputs()

        # elif self.thisGame.mode == 4:
        # waiting to start
        # self.thisGame.modeTimer += 1

        # if self.thisGame.modeTimer == 60:
        # self.thisGame.SetMode(1)
        # self.player.velX = self.player.speed

        elif self.thisGame.mode == 5:
            # brief pause after munching a vulnerable ghost
            # self.thisGame.modeTimer += 1

            # if self.thisGame.modeTimer == 20:
            self.thisGame.SetMode(8)

        elif self.thisGame.mode == 6:
            # pause after eating all the pellets
            self.thisGame.modeTimer += 1

            if self.thisGame.modeTimer == 40:
                self.thisGame.SetMode(7)
                self.oldEdgeLightColor = self.thisLevel.edgeLightColor
                self.oldEdgeShadowColor = self.thisLevel.edgeShadowColor
                self.oldFillColor = self.thisLevel.fillColor

        elif self.thisGame.mode == 7:
            # flashing maze after finishing level
            self.thisGame.modeTimer += 1

            whiteSet = [10, 30, 50, 70]
            normalSet = [20, 40, 60, 80]

            if not whiteSet.count(self.thisGame.modeTimer) == 0:
                # member of white set
                self.thisLevel.edgeLightColor = (255, 255, 254, 255)
                self.thisLevel.edgeShadowColor = (255, 255, 254, 255)
                self.thisLevel.fillColor = (0, 0, 0, 255)
                # TODO: GetCrossRef
                GetImageCrossRef(self.tileIDName, self.tileID,
                                 self.tileIDImage,
                                 self.thisLevel)
            elif not normalSet.count(self.thisGame.modeTimer) == 0:
                # member of normal set
                self.thisLevel.edgeLightColor = self.oldEdgeLightColor
                self.thisLevel.edgeShadowColor = self.oldEdgeShadowColor
                self.thisLevel.fillColor = self.oldFillColor
                GetImageCrossRef(self.tileIDName, self.tileID,
                                 self.tileIDImage,
                                 self.thisLevel)
            elif self.thisGame.modeTimer == 100:
                self.thisGame.SetMode(10)

        elif self.thisGame.mode == 8:
            # CheckInputs()
            # TODO: Use action param to control player.
            self.check_inputs(action)
            ghostState = 1
            self.thisGame.modeTimer += 1

            self.player.Move(self.thisLevel, self.ghosts, self.thisGame,
                             self.path, self.thisFruit, self.tileID)

            for i in range(0, 4, 1):
                self.ghosts[i].Move(self.path, self.player, self.thisLevel,
                                    self.tileID)

            for i in range(0, 4, 1):
                if self.ghosts[i].state == 3:
                    ghostState = 3
                    break
                elif self.ghosts[i].state == 2:
                    ghostState = 2

            if self.thisLevel.pellets == 0:
                # WON THE LEVEL
                self.thisGame.SetMode(6)
            elif ghostState == 1:
                self.thisGame.SetMode(1)
            elif ghostState == 2:
                self.thisGame.SetMode(9)

            self.thisFruit.Move(self.thisGame)

        elif self.thisGame.mode == 9:
            # CheckInputs()
            # TODO: Use action param to control player.
            self.check_inputs(action)
            self.thisGame.modeTimer += 1

            self.player.Move(self.thisLevel, self.ghosts, self.thisGame,
                             self.path, self.thisFruit, self.tileID)
            for i in range(0, 4, 1):
                self.ghosts[i].Move(self.path, self.player, self.thisLevel,
                                    self.tileID)
            self.thisFruit.Move(self.thisGame)

        elif self.thisGame.mode == 10:
            # blank screen before changing levels
            self.thisGame.modeTimer += 1
            if self.thisGame.modeTimer == 10:
                self.thisGame.SetNextLevel()

        elif self.thisGame.mode == 11:
            # flashing maze after finishing level
            self.thisGame.modeTimer += 1

            whiteSet = [10, 30, 50, 70]
            normalSet = [20, 40, 60, 80]

            if not whiteSet.count(self.thisGame.modeTimer) == 0:
                # member of white set
                self.thisLevel.edgeLightColor = (255, 255, 254, 255)
                self.thisLevel.edgeShadowColor = (255, 255, 254, 255)
                self.thisLevel.fillColor = (0, 0, 0, 255)
                # TODO: GetCrossRef
                GetImageCrossRef(self.tileIDName, self.tileID,
                                 self.tileIDImage,
                                 self.thisLevel)
            elif not normalSet.count(self.thisGame.modeTimer) == 0:
                # member of normal set
                self.thisLevel.edgeLightColor = self.oldEdgeLightColor
                self.thisLevel.edgeShadowColor = self.oldEdgeShadowColor
                self.thisLevel.fillColor = self.oldFillColor
                GetImageCrossRef(self.tileIDName, self.tileID,
                                 self.tileIDImage,
                                 self.thisLevel)
            elif self.thisGame.modeTimer == 100:
                self.thisGame.modeTimer = 1

        # render things were here

        # clock.tick(40)

    def reset(self):
        # lines 125-127 in Move() in pacman.py regards running into a non-vulnerable ghost
        # the static method CheckIfHitSomething() in lines 108-111 of level.py regards obtaining all pellets
        pass

    def render(self, mode="human"):
        if not self.gui:
            return
        global rect_list

        self.thisGame.SmartMoveScreen(self.player, self.thisLevel,
                                      self.thisGame)
        self.screen.blit(get_img_background(), (0, 0))

        if not self.thisGame.mode == 10:
            self.thisLevel.DrawMap(self.thisGame, self.tileID, self.screen,
                                   self.tileIDImage)

            if self.thisGame.fruitScoreTimer > 0:
                if self.thisGame.modeTimer % 2 == 0:
                    self.thisGame.DrawNumber(2500, (
                        self.thisFruit.x - self.thisGame.screenPixelPos[
                            0] - 16,
                        self.thisFruit.y - self.thisGame.screenPixelPos[
                            1] + 4), self.screen)

            for i in range(0, 4, 1):
                self.ghosts[i].Draw(self.thisGame, self.player, self.screen,
                                    self.ghosts, self.tileIDImage, self.tileID)
            self.thisFruit.Draw(self.thisGame, self.screen)
            self.player.Draw(self.thisGame, self.screen)

            if self.thisGame.mode == 3:
                self.screen.blit(self.thisGame.imHiscores,
                                 (HS_XOFFSET, HS_YOFFSET))

        if self.thisGame.mode == 5:
            self.thisGame.DrawNumber(self.thisGame.ghostValue / 2,
                                     (self.player.x -
                                      self.thisGame.screenPixelPos[0] - 4,
                                      self.player.y -
                                      self.thisGame.screenPixelPos[1] + 6),
                                     self.screen)

        self.thisGame.DrawScore(self.screen, self.thisFruit)

        pygame.display.update()
        del rect_list[:]

    def close(self):
        # I believe this would just exit the environment from render()
        pass
