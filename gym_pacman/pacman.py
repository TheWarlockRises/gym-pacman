from .consts import *


class Pacman:
    def __init__(self, gui=False):
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

        self.prev_velx = 0
        self.prev_vely = 0

        if gui:
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
        score = 1

        # make sure the current velocity will not cause a collision before moving
        if not thisLevel.CheckIfHitWall(
                (self.x + self.velX, self.y + self.velY),
                (self.nearestRow, self.nearestCol)):
            # it's ok to Move
            self.x += self.velX
            self.y += self.velY

            # TODO: Score penalties for changing directions.
            if self.prev_velx != self.velX:
                score -= 1
            if self.prev_vely != self.velY:
                score -= 1

            # check for collisions with other tiles (pellets, etc)
            score += thisLevel.CheckIfHitSomething((self.x, self.y),
                                                   (self.nearestRow,
                                                    self.nearestCol),
                                                   thisLevel, tileID, self,
                                                   thisGame,
                                                   ghosts)

            # check for collisions with the ghosts
            for i in range(0, 4, 1):
                if thisLevel.CheckIfHit((self.x, self.y),
                                        (ghosts[i].x, ghosts[i].y),
                                        TILE_WIDTH / 2):
                    # hit a ghost

                    if ghosts[i].state == 1:
                        # ghost is normal
                        if thisGame.mode != 2:
                            score -= 9999
                        thisGame.SetMode(2)

                    elif ghosts[i].state == 2:
                        # ghost is vulnerable
                        # give them glasses
                        # make them run
                        thisGame.AddToScore(thisGame.ghostValue, thisGame)
                        score += thisGame.ghostValue
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
                        # thisGame.SetMode(5)

            # check for collisions with the fruit
            if thisFruit.active:
                if thisLevel.CheckIfHit((self.x, self.y),
                                        (thisFruit.x, thisFruit.y),
                                        TILE_WIDTH / 2):
                    thisGame.AddToScore(2500, thisGame)
                    score += 2500
                    thisFruit.active = False
                    thisGame.fruitTimer = 0
                    thisGame.fruitScoreTimer = 80
                    # snd_eatfruit.play()

        else:
            # we're going to hit a wall -- stop moving
            self.velX = 0
            self.velY = 0
            score = 0

        self.prev_velx = self.velX
        self.prev_vely = self.velY

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

        return score

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
