import gym

from ..fruit import *
from ..game import *
from ..ghost import *
from ..level import *
from ..path_finder import *

# Joystick defaults - maybe add a Preferences dialog in the future?
JS_DEVNUM = 0  # device 0 (pygame joysticks always start at 0). if JS_DEVNUM is not a valid device, will use 0
JS_XAXIS = 0  # axis 0 for left/right (default for most joysticks)
JS_YAXIS = 1  # axis 1 for up/down (default for most joysticks)
JS_STARTBUTTON = 0  # button number to start the game. this is a matter of personal preference, and will vary from
# device to device


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
    metadata = {"render.modes": ["default"]}

    def __init__(self):
        # create the pacman
        self.player = pacman()

        # create a path_finder object
        self.path = path_finder()

        # create ghost objects
        self.ghosts = {}
        for i in range(0, 6, 1):
            # remember, ghost[4] is the blue, vulnerable ghost
            self.ghosts[i] = ghost(i)

        # create piece of fruit
        self.thisFruit = fruit()

        self.tileIDName = {}  # gives tile name (when the ID# is known)
        self.tileID = {}  # gives tile ID (when the name is known)
        self.tileIDImage = {}  # gives tile image (when the ID# is known)
        self.oldEdgeLightColor = None
        self.oldEdgeShadowColor = None
        self.oldFillColor = None

        # create game and level objects and load first level
        self.thisGame = game()
        self.thisLevel = level()

    """def init_pygame(self):
        # initialise the joystick
        if pygame.joystick.get_count() > 0:
            if JS_DEVNUM < pygame.joystick.get_count():
                js = pygame.joystick.Joystick(JS_DEVNUM)
            else:
                js = pygame.joystick.Joystick(0)
            js.init()
        else:
            js = None"""

    """def CheckInputs(self): if self.thisGame.mode == 1 or self.thisGame.mode == 8 or self.thisGame.mode == 9: if 
    pygame.key.get_pressed()[pygame.K_RIGHT] or (js is not None and js.get_axis(JS_XAXIS) > 0.5): if not (
    self.player.velX == self.player.speed and self.player.velY == 0) and not self.thisLevel.CheckIfHitWall( (
    self.player.x + self.player.speed, self.player.y), (self.player.nearestRow, self.player.nearestCol)): 
    self.player.velX = self.player.speed self.player.velY = 0 

            elif pygame.key.get_pressed()[pygame.K_LEFT] or (js is not None and js.get_axis(JS_XAXIS) < -0.5): if not 
            (self.player.velX == -self.player.speed and self.player.velY == 0) and not self.thisLevel.CheckIfHitWall( 
            (self.player.x - self.player.speed, self.player.y), (self.player.nearestRow, self.player.nearestCol)): 
            self.player.velX = -self.player.speed self.player.velY = 0 

            elif pygame.key.get_pressed()[pygame.K_DOWN] or (js is not None and js.get_axis(JS_YAXIS) > 0.5): if not 
            (self.player.velX == 0 and self.player.velY == self.player.speed) and not self.thisLevel.CheckIfHitWall( 
            (self.player.x, self.player.y + self.player.speed), (self.player.nearestRow, self.player.nearestCol)): 
            self.player.velX = 0 self.player.velY = self.player.speed 

            elif pygame.key.get_pressed()[pygame.K_UP] or (js is not None and js.get_axis(JS_YAXIS) < -0.5): if not (
            self.player.velX == 0 and self.player.velY == -self.player.speed) and not self.thisLevel.CheckIfHitWall( 
            (self.player.x, self.player.y - self.player.speed), (self.player.nearestRow, self.player.nearestCol)): 
            self.player.velX = 0 self.player.velY = -self.player.speed 

        if pygame.key.get_pressed()[pygame.K_ESCAPE] or (js is not None and js.get_button(7)):
            sys.exit(0)

        elif thisGame.mode == 3:
            if pygame.key.get_pressed()[pygame.K_RETURN] or (js is not None and js.get_button(JS_STARTBUTTON)):
                thisGame.StartNewGame()"""

    def step(self, action):
        # CheckIfCloseButton(pygame.event.get())
        if self.thisGame.mode == 0:
            # ready to level start
            # self.thisGame.modeTimer += 1
            # if self.thisGame.modeTimer == 150:
            self.thisGame.SetMode(1)

        if self.thisGame.mode == 1:
            # normal gameplay mode
            # CheckInputs()
            # TODO: Use action param to control player.
            self.thisGame.modeTimer += 1

            self.player.Move()
            for i in range(0, 4, 1):
                self.ghosts[i].Move()
            self.thisFruit.Move()

        elif self.thisGame.mode == 2:
            # waiting after getting hit by a ghost
            self.thisGame.modeTimer += 1

            if self.thisGame.modeTimer == 60:
                self.thisLevel.Restart()

                self.thisGame.lives -= 1
                if self.thisGame.lives == -1:
                    self.thisGame.updatehiscores(self.thisGame.score)
                    self.thisGame.SetMode(3)
                    self.thisGame.drawmidgamehiscores()
                else:
                    self.thisGame.SetMode(4)

        elif self.thisGame.mode == 3:
            # TODO: Scoring
            pass
            # game over
            # CheckInputs()

        elif self.thisGame.mode == 4:
            # waiting to start
            self.thisGame.modeTimer += 1

            if self.thisGame.modeTimer == 60:
                self.thisGame.SetMode(1)
                self.player.velX = self.player.speed

        elif self.thisGame.mode == 5:
            # brief pause after munching a vulnerable ghost
            self.thisGame.modeTimer += 1

            if self.thisGame.modeTimer == 20:
                self.thisGame.SetMode(8)

        elif self.thisGame.mode == 6:
            # pause after eating all the pellets
            self.thisGame.modeTimer += 1

            if self.thisGame.modeTimer == 40:
                self.thisGame.SetMode(7)
                oldEdgeLightColor = self.thisLevel.edgeLightColor
                oldEdgeShadowColor = self.thisLevel.edgeShadowColor
                oldFillColor = self.thisLevel.fillColor

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
                GetCrossRef(self.tileIDName, self.tileID, self.tileIDImage,
                            self.thisLevel)
            elif not normalSet.count(self.thisGame.modeTimer) == 0:
                # member of normal set
                self.thisLevel.edgeLightColor = self.oldEdgeLightColor
                self.thisLevel.edgeShadowColor = self.oldEdgeShadowColor
                self.thisLevel.fillColor = self.oldFillColor
                GetCrossRef(self.tileIDName, self.tileID, self.tileIDImage,
                            self.thisLevel)
            elif self.thisGame.modeTimer == 100:
                self.thisGame.SetMode(10)

        elif self.thisGame.mode == 8:
            # CheckInputs()
            # TODO: Use action param to control player.
            ghostState = 1
            self.thisGame.modeTimer += 1

            self.player.Move()

            for i in range(0, 4, 1):
                self.ghosts[i].Move()

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

            self.thisFruit.Move()

        elif self.thisGame.mode == 9:
            # CheckInputs()
            # TODO: Use action param to control player.
            self.thisGame.modeTimer += 1

            self.player.Move()
            for i in range(0, 4, 1):
                self.ghosts[i].Move()
            self.thisFruit.Move()

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
                GetCrossRef(self.tileIDName, self.tileID, self.tileIDImage,
                            self.thisLevel)
            elif not normalSet.count(self.thisGame.modeTimer) == 0:
                # member of normal set
                self.thisLevel.edgeLightColor = self.oldEdgeLightColor
                self.thisLevel.edgeShadowColor = self.oldEdgeShadowColor
                self.thisLevel.fillColor = self.oldFillColor
                GetCrossRef(self.tileIDName, self.tileID, self.tileIDImage,
                            self.thisLevel)
            elif self.thisGame.modeTimer == 100:
                self.thisGame.modeTimer = 1

        self.thisGame.SmartMoveScreen()

        self.screen.blit(self.img_Background, (0, 0))

        if not self.thisGame.mode == 10:
            self.thisLevel.DrawMap()

            if self.thisGame.fruitScoreTimer > 0:
                if self.thisGame.modeTimer % 2 == 0:
                    self.thisGame.DrawNumber(2500, (
                        self.thisFruit.x - self.thisGame.screenPixelPos[
                            0] - 16,
                        self.thisFruit.y - self.thisGame.screenPixelPos[
                            1] + 4))

            for i in range(0, 4, 1):
                self.ghosts[i].Draw()
            self.thisFruit.Draw()
            self.player.Draw()

            if self.thisGame.mode == 3:
                self.screen.blit(self.thisGame.imHiscores,
                                 (HS_XOFFSET, HS_YOFFSET))

        if self.thisGame.mode == 5:
            self.thisGame.DrawNumber(self.thisGame.ghostValue / 2,
                                     (self.player.x -
                                      self.thisGame.screenPixelPos[0] - 4,
                                      self.player.y -
                                      self.thisGame.screenPixelPos[1] + 6))

        self.thisGame.DrawScore()

        pygame.display.update()
        del rect_list[:]

        # clock.tick(40)

    def reset(self):
        # lines 125-127 in Move() in pacman.py regards running into a non-vulnerable ghost
        # the static method CheckIfHitSomething() in lines 108-111 of level.py regards obtaining all pellets
        pass

    def render(self, mode="default"):
        # I believe the __init__() generates the level in level.py
        pass

    def close(self):
        # I believe this would just exit the environment from render()
        pass
