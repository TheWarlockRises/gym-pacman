import os
import sys
import random

import pygame

if os.name == "nt":
    SCRIPT_PATH = os.path.join(os.getcwd(), "gym_pacman")
else:
    SCRIPT_PATH = sys.path[0]

SCREEN_TILE_SIZE_HEIGHT = 23
SCREEN_TILE_SIZE_WIDTH = 30

TILE_WIDTH = TILE_HEIGHT = 24

# constants for the high-score display
HS_FONT_SIZE = 16
HS_LINE_HEIGHT = 16
HS_WIDTH = 408
HS_HEIGHT = 120
HS_XOFFSET = 180
HS_YOFFSET = 400
HS_ALPHA = 200

# new constants for the score's position
SCORE_XOFFSET = 50  # pixels from left edge
SCORE_YOFFSET = 34  # pixels from bottom edge (to top of score)
SCORE_COLWIDTH = 13  # width of each character

# See GetCrossRef() -- where these colors occur in a GIF, they are replaced according to the level file
IMG_EDGE_LIGHT_COLOR = (255, 206, 255, 255)
IMG_FILL_COLOR = (132, 0, 132, 255)
IMG_EDGE_SHADOW_COLOR = (255, 0, 255, 255)
IMG_PELLET_COLOR = (128, 0, 128, 255)

# NO_GIF_TILES -- tile numbers which do not correspond to a GIF file
# currently only "23" for the high-score list
NO_GIF_TILES = [23]

NO_WX = 0  # if set, the high-score code will not attempt to ask the user his name
USER_NAME = "User"  # USER_NAME=os.getlogin() # the default user name if wx fails to load or NO_WX

# Joystick defaults - maybe add a Preferences dialog in the future?
JS_DEVNUM = 0  # device 0 (pygame joysticks always start at 0). if JS_DEVNUM is not a valid device, will use 0
JS_XAXIS = 0  # axis 0 for left/right (default for most joysticks)
JS_YAXIS = 1  # axis 1 for up/down (default for most joysticks)
JS_STARTBUTTON = 0  # button number to start the game. this is a matter of personal preference, and will vary from device to device

rect_list = []  # rect list for drawing

img_Background = None


def get_image_surface(file_path):
    image = pygame.image.load(file_path).convert()
    # image_rect = image.get_rect()
    # image_surface = pygame.Surface((image_rect.width, image_rect.height))
    # image_surface.blit(image, image_rect)
    return image


def init_pygame():
    global img_Background
    img_Background = get_image_surface(
        os.path.join(SCRIPT_PATH, "res", "backgrounds", "1.gif"))
    print(img_Background)


def get_img_background():
    return img_Background


class pacman:
    def __init__(self, init_gui=False):
        self.x = 0
        self.y = 0
        self.velX = 0
        self.velY = 0
        self.speed = 3

        self.nearestRow = 0
        self.nearestCol = 0

        self.homeX = 0
        self.homeY = 0

        self.anim_pacmanL = {}
        self.anim_pacmanR = {}
        self.anim_pacmanU = {}
        self.anim_pacmanD = {}
        self.anim_pacmanS = {}
        self.anim_pacmanCurrent = {}

        self.animFrame = 1

        if init_gui:
            for i in range(1, 9, 1):
                self.anim_pacmanL[i] = get_image_surface(
                    os.path.join(SCRIPT_PATH, "res", "sprite",
                                 "pacman-l " + str(i) + ".gif"))
                self.anim_pacmanR[i] = get_image_surface(
                    os.path.join(SCRIPT_PATH, "res", "sprite",
                                 "pacman-r " + str(i) + ".gif"))
                self.anim_pacmanU[i] = get_image_surface(
                    os.path.join(SCRIPT_PATH, "res", "sprite",
                                 "pacman-u " + str(i) + ".gif"))
                self.anim_pacmanD[i] = get_image_surface(
                    os.path.join(SCRIPT_PATH, "res", "sprite",
                                 "pacman-d " + str(i) + ".gif"))
                self.anim_pacmanS[i] = get_image_surface(
                    os.path.join(SCRIPT_PATH, "res", "sprite", "pacman.gif"))

        self.pelletSndNum = 0

    def Move(self, thisLevel, ghosts, thisGame, path, thisFruit, tileID):
        self.nearestRow = int(((self.y + (TILE_WIDTH / 2)) / TILE_WIDTH))
        self.nearestCol = int(((self.x + (TILE_HEIGHT / 2)) / TILE_HEIGHT))

        # make sure the current velocity will not cause a collision before moving
        if not thisLevel.CheckIfHitWall(
                (self.x + self.velX, self.y + self.velY),
                (self.nearestRow, self.nearestCol)):
            # it's ok to Move
            self.x += self.velX
            self.y += self.velY

            # check for collisions with other tiles (pellets, etc)
            thisLevel.CheckIfHitSomething((self.x, self.y),
                                          (self.nearestRow, self.nearestCol),
                                          thisLevel, tileID, self, thisGame,
                                          ghosts)

            # check for collisions with the ghosts
            for i in range(0, 4, 1):
                if thisLevel.CheckIfHit((self.x, self.y),
                                        (ghosts[i].x, ghosts[i].y),
                                        TILE_WIDTH / 2):
                    # hit a ghost

                    if ghosts[i].state == 1:
                        # ghost is normal
                        thisGame.SetMode(2)

                    elif ghosts[i].state == 2:
                        # ghost is vulnerable
                        # give them glasses
                        # make them run
                        thisGame.AddToScore(thisGame.ghostValue, thisGame)
                        thisGame.ghostValue = thisGame.ghostValue * 2
                        # snd_eatgh.play()

                        ghosts[i].state = 3
                        ghosts[i].speed = ghosts[i].speed * 4
                        # and send them to the ghost box
                        ghosts[i].x = ghosts[i].nearestCol * TILE_WIDTH
                        ghosts[i].y = ghosts[i].nearestRow * TILE_HEIGHT
                        ghosts[i].currentPath = path.FindPath(
                            (ghosts[i].nearestRow, ghosts[i].nearestCol), (
                                thisLevel.GetGhostBoxPos(tileID)[0] + 1,
                                thisLevel.GetGhostBoxPos(tileID)[1]))
                        ghosts[i].FollowNextPathWay(path, self, thisLevel,
                                                    tileID)

                        # set game mode to brief pause after eating
                        thisGame.SetMode(5)

            # check for collisions with the fruit
            if thisFruit.active:
                if thisLevel.CheckIfHit((self.x, self.y),
                                        (thisFruit.x, thisFruit.y),
                                        TILE_WIDTH / 2):
                    thisGame.AddToScore(2500)
                    thisFruit.active = False
                    thisGame.fruitTimer = 0
                    thisGame.fruitScoreTimer = 80
                    # snd_eatfruit.play()

        else:
            # we're going to hit a wall -- stop moving
            self.velX = 0
            self.velY = 0

        # deal with power-pellet ghost timer
        if thisGame.ghostTimer > 0:
            thisGame.ghostTimer -= 1

            if thisGame.ghostTimer == 0:
                # thisGame.PlayBackgoundSound(snd_default)
                for i in range(0, 4, 1):
                    if ghosts[i].state == 2:
                        ghosts[i].state = 1
                thisGame.ghostValue = 0

        # deal with fruit timer
        thisGame.fruitTimer += 1
        if thisGame.fruitTimer == 380:
            pathwayPair = thisLevel.GetPathwayPairPos(tileID, thisLevel)

            if not pathwayPair == False:
                pathwayEntrance = pathwayPair[0]
                pathwayExit = pathwayPair[1]

                thisFruit.active = True

                thisFruit.nearestRow = pathwayEntrance[0]
                thisFruit.nearestCol = pathwayEntrance[1]

                thisFruit.x = thisFruit.nearestCol * TILE_WIDTH
                thisFruit.y = thisFruit.nearestRow * TILE_HEIGHT

                thisFruit.currentPath = path.FindPath(
                    (thisFruit.nearestRow, thisFruit.nearestCol), pathwayExit)
                thisFruit.FollowNextPathWay()

        if thisGame.fruitScoreTimer > 0:
            thisGame.fruitScoreTimer -= 1

    def Draw(self, thisGame, screen):
        global rect_list
        if thisGame.mode == 3:
            return False

        # set the current frame array to match the direction pacman is facing
        if self.velX > 0:
            self.anim_pacmanCurrent = self.anim_pacmanR
        elif self.velX < 0:
            self.anim_pacmanCurrent = self.anim_pacmanL
        elif self.velY > 0:
            self.anim_pacmanCurrent = self.anim_pacmanD
        elif self.velY < 0:
            self.anim_pacmanCurrent = self.anim_pacmanU
        else: # TODO: remove after checking
            print("did not set cur anim")
            self.anim_pacmanCurrent = self.anim_pacmanR

        screen.blit(self.anim_pacmanCurrent[self.animFrame],
                    (self.x - thisGame.screenPixelPos[0],
                     self.y - thisGame.screenPixelPos[1]))

        if thisGame.mode == 1 or thisGame.mode == 8 or thisGame.mode == 9:
            if self.velX != 0 or self.velY != 0:
                # only Move mouth when pacman is moving
                self.animFrame += 1

            if self.animFrame == 9:
                # wrap to beginning
                self.animFrame = 1


def GetCrossRef(tileIDName, tileID):
    f = open(os.path.join(SCRIPT_PATH, "res", "crossref.txt"), 'r')

    lineNum = 0

    for i in f.readlines():
        # print " ========= Line " + str(lineNum) + " ============ "
        while len(i) > 0 and (i[-1] == '\n' or i[-1] == '\r'): i = i[:-1]
        while len(i) > 0 and (i[0] == '\n' or i[0] == '\r'): i = i[1:]
        str_splitBySpace = i.split(' ')

        j = str_splitBySpace[0]

        if j == "'" or j == "" or j == "#":
            # comment / whitespace line
            # print " ignoring comment line.. "
            useLine = False
        else:
            # print str(wordNum) + ". " + j
            useLine = True

        if useLine:
            tileIDName[int(str_splitBySpace[0])] = str_splitBySpace[1]
            tileID[str_splitBySpace[1]] = int(str_splitBySpace[0])

        lineNum += 1
    f.close()


def GetImageCrossRef(tileIDName, tileID, tileIDImage, thisLevel):
    f = open(os.path.join(SCRIPT_PATH, "res", "crossref.txt"), 'r')

    lineNum = 0

    for i in f.readlines():
        # print " ========= Line " + str(lineNum) + " ============ "
        while len(i) > 0 and (i[-1] == '\n' or i[-1] == '\r'): i = i[:-1]
        while len(i) > 0 and (i[0] == '\n' or i[0] == '\r'): i = i[1:]
        str_splitBySpace = i.split(' ')

        j = str_splitBySpace[0]

        if j == "'" or j == "" or j == "#":
            # comment / whitespace line
            # print " ignoring comment line.. "
            useLine = False
        else:
            # print str(wordNum) + ". " + j
            useLine = True

        if useLine:
            tileIDName[int(str_splitBySpace[0])] = str_splitBySpace[1]
            tileID[str_splitBySpace[1]] = int(str_splitBySpace[0])

            thisID = int(str_splitBySpace[0])
            if not thisID in NO_GIF_TILES:
                tileIDImage[thisID] = get_image_surface(
                    os.path.join(SCRIPT_PATH, "res", "tiles",
                                 str_splitBySpace[1] + ".gif"))
            else:
                tileIDImage[thisID] = pygame.Surface((TILE_WIDTH, TILE_HEIGHT))

            # change colors in tileIDImage to match maze colors
            for y in range(0, TILE_WIDTH, 1):
                for x in range(0, TILE_HEIGHT, 1):

                    if tileIDImage[thisID].get_at(
                            (x, y)) == IMG_EDGE_LIGHT_COLOR:
                        # wall edge
                        tileIDImage[thisID].set_at((x, y),
                                                   thisLevel.edgeLightColor)

                    elif tileIDImage[thisID].get_at((x, y)) == IMG_FILL_COLOR:
                        # wall fill
                        tileIDImage[thisID].set_at((x, y), thisLevel.fillColor)

                    elif tileIDImage[thisID].get_at(
                            (x, y)) == IMG_EDGE_SHADOW_COLOR:
                        # pellet color
                        tileIDImage[thisID].set_at((x, y),
                                                   thisLevel.edgeShadowColor)

                    elif tileIDImage[thisID].get_at(
                            (x, y)) == IMG_PELLET_COLOR:
                        # pellet color
                        tileIDImage[thisID].set_at((x, y),
                                                   thisLevel.pelletColor)

        lineNum += 1
    f.close()
