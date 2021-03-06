from re import split

from .pacman import *


class Level:
    def __init__(self, randomized=False):
        self.lvlWidth = 0
        self.lvlHeight = 0
        self.edgeLightColor = (255, 255, 0, 255)
        self.edgeShadowColor = (255, 150, 0, 255)
        self.fillColor = (0, 255, 255, 255)
        self.pelletColor = (255, 255, 255, 255)

        self.map = {}

        self.pellets = 0
        self.powerPelletBlinkTimer = 0

        self.gui = False
        self.randomized = randomized

        # TODO: Refactor entire level setup because this is definitely not OOP.
        self.preload_width = {}
        self.preload_height = {}
        self.preload_edge_light = {}
        self.preload_edge_shadow = {}
        self.preload_fill = {}
        self.preload_pellet_color = {}
        self.preload_map = {}
        self.preload_pellets = {}
        self.preload_fruit_type = {}
        self.preload_player_home = {}
        self.preload_ghosts_home = {}

    def SetMapTile(self, row_col, newValue):
        (row, col) = row_col
        self.map[(row * self.lvlWidth) + col] = newValue

    def GetMapTile(self, row_col):
        (row, col) = row_col
        if 0 <= row < self.lvlHeight and 0 <= col < self.lvlWidth:
            return self.map[(row * self.lvlWidth) + col]
        else:
            return 0

    @staticmethod
    def IsWall(row_col, thisLevel):
        (row, col) = row_col
        if row > thisLevel.lvlHeight - 1 or row < 0:
            return True

        if col > thisLevel.lvlWidth - 1 or col < 0:
            return True

        # check the offending tile ID
        result = thisLevel.GetMapTile((row, col))

        # if the tile was a wall
        if 100 <= result <= 199:
            return True
        else:
            return False

    def CheckIfHitWall(self, possiblePlayerX_possiblePlayerY, row_col):
        (possiblePlayerX, possiblePlayerY) = possiblePlayerX_possiblePlayerY
        (row, col) = row_col
        numCollisions = 0

        # check each of the 9 surrounding tiles for a collision
        for iRow in range(row - 1, row + 2, 1):
            for iCol in range(col - 1, col + 2, 1):

                if (possiblePlayerX - (iCol * TILE_WIDTH) < TILE_WIDTH) and (
                        possiblePlayerX - (
                        iCol * TILE_WIDTH) > -TILE_WIDTH) and (
                        possiblePlayerY - (
                        iRow * TILE_HEIGHT) < TILE_HEIGHT) and (
                        possiblePlayerY - (iRow * TILE_HEIGHT) > -TILE_HEIGHT):

                    if self.IsWall((iRow, iCol), self):
                        numCollisions += 1

        if numCollisions > 0:
            return True
        else:
            return False

    @staticmethod
    def CheckIfHit(playerX_playerY, x_y, cushion):
        (playerX, playerY) = playerX_playerY
        (x, y) = x_y
        if (playerX - x < cushion) and (playerX - x > -cushion) and (
                playerY - y < cushion) and (
                playerY - y > -cushion):
            return True
        else:
            return False

    @staticmethod
    def CheckIfHitSomething(playerX_playerY, row_col, thisLevel, tileID,
                            player, thisGame, ghosts, scorer):
        (playerX, playerY) = playerX_playerY
        (row, col) = row_col
        for iRow in range(row - 1, row + 2, 1):
            for iCol in range(col - 1, col + 2, 1):

                if (playerX - (iCol * TILE_WIDTH) < TILE_WIDTH) and (
                        playerX - (iCol * TILE_WIDTH) > -TILE_WIDTH) and (
                        playerY - (iRow * TILE_HEIGHT) < TILE_HEIGHT) and (
                        playerY - (iRow * TILE_HEIGHT) > -TILE_HEIGHT):
                    # check the offending tile ID
                    result = thisLevel.GetMapTile((iRow, iCol))

                    if result == tileID['pellet']:
                        # got a pellet
                        thisLevel.SetMapTile((iRow, iCol), 0)
                        # snd_pellet[player.pelletSndNum].play()
                        player.pelletSndNum = 1 - player.pelletSndNum

                        thisLevel.pellets -= 1

                        thisGame.AddToScore(10, thisGame)
                        scorer.score_pellet_eat()

                        if thisLevel.pellets == 0:
                            # no more pellets left!
                            # WON THE LEVEL
                            if thisGame.mode != 6:
                                thisGame.SetMode(6)
                                scorer.score_level_finished()

                    elif result == tileID['pellet-power']:
                        # got a power pellet
                        thisGame.SetMode(9)
                        thisLevel.SetMapTile((iRow, iCol), 0)
                        # snd_powerpellet.play()

                        # thisGame.AddToScore(100, thisGame)
                        thisGame.AddToScore(50, thisGame)
                        scorer.score_power_pellet_eat()
                        thisGame.ghostValue = 200

                        thisGame.ghostTimer = 360
                        for i in range(0, 4, 1):
                            if ghosts[i].state == 1:
                                ghosts[i].state = 2

                    elif result == tileID['door-h']:
                        # ran into a horizontal door
                        scorer.score_door_entry()
                        for i in range(0, thisLevel.lvlWidth, 1):
                            if not i == iCol:
                                if thisLevel.GetMapTile((iRow, i)) == tileID[
                                    'door-h']:
                                    player.x = i * TILE_WIDTH

                                    if player.velX > 0:
                                        player.x += TILE_WIDTH
                                    else:
                                        player.x -= TILE_WIDTH

                    elif result == tileID['door-v']:
                        # ran into a vertical door
                        scorer.score_door_entry()
                        for i in range(0, thisLevel.lvlHeight, 1):
                            if not i == iRow:
                                if thisLevel.GetMapTile((i, iCol)) == tileID[
                                    'door-v']:
                                    player.y = i * TILE_HEIGHT

                                    if player.velY > 0:
                                        player.y += TILE_HEIGHT
                                    else:
                                        player.y -= TILE_HEIGHT
        return 0

    def GetGhostBoxPos(self, tileID):
        for row in range(0, self.lvlHeight, 1):
            for col in range(0, self.lvlWidth, 1):
                if self.GetMapTile((row, col)) == tileID['ghost-door']:
                    return row, col

        return False

    def GetPathwayPairPos(self, tileID, thisLevel, random):
        doorArray = []

        for row in range(0, self.lvlHeight, 1):
            for col in range(0, self.lvlWidth, 1):
                if self.GetMapTile((row, col)) == tileID['door-h']:
                    # found a horizontal door
                    doorArray.append((row, col))
                elif self.GetMapTile((row, col)) == tileID['door-v']:
                    # found a vertical door
                    doorArray.append((row, col))

        if len(doorArray) == 0:
            return False

        chosenDoor = random.randint(0, len(doorArray))  # - 1)

        if self.GetMapTile(doorArray[chosenDoor]) == tileID['door-h']:
            # horizontal door was chosen
            # look for the opposite one
            for i in range(0, thisLevel.lvlWidth, 1):
                if not i == doorArray[chosenDoor][1]:
                    if thisLevel.GetMapTile((doorArray[chosenDoor][0], i)) == \
                            tileID['door-h']:
                        return doorArray[chosenDoor], (
                            doorArray[chosenDoor][0], i)
        else:
            # vertical door was chosen
            # look for the opposite one
            for i in range(0, thisLevel.lvlHeight, 1):
                if not i == doorArray[chosenDoor][0]:
                    if thisLevel.GetMapTile((i, doorArray[chosenDoor][1])) == \
                            tileID['door-v']:
                        return doorArray[chosenDoor], (
                            i, doorArray[chosenDoor][1])

        return False

    def PrintMap(self):
        for row in range(0, self.lvlHeight, 1):
            outputLine = ""
            for col in range(0, self.lvlWidth, 1):
                outputLine += str(self.GetMapTile((row, col))) + ", "

    def DrawMap(self, thisGame, tileID, screen, tileIDImage):
        if not self.gui:
            GetImageCrossRef(tileIDImage, self)
            self.gui = True

        self.powerPelletBlinkTimer += 1
        if self.powerPelletBlinkTimer == 40:
            self.powerPelletBlinkTimer = 0

        for row in range(-1, thisGame.screenTileSize[0] + 1, 1):
            for col in range(-1, thisGame.screenTileSize[1] + 1, 1):

                # row containing tile that actually goes here
                actualRow = thisGame.screenNearestTilePos[0] + row
                actualCol = thisGame.screenNearestTilePos[1] + col

                useTile = self.GetMapTile((actualRow, actualCol))
                if useTile != 0 and useTile != tileID['door-h'] and useTile != \
                        tileID['door-v']:
                    # if this isn't a blank tile
                    if useTile == tileID['pellet-power']:
                        if self.powerPelletBlinkTimer < 20:
                            screen.blit(tileIDImage[useTile], (
                                col * TILE_WIDTH - thisGame.screenPixelOffset[
                                    0],
                                row * TILE_HEIGHT - thisGame.screenPixelOffset[
                                    1]))

                    elif useTile == tileID['showlogo']:
                        screen.blit(thisGame.imLogo, (
                            col * TILE_WIDTH - thisGame.screenPixelOffset[0],
                            row * TILE_HEIGHT - thisGame.screenPixelOffset[1]))

                    elif useTile == tileID['hiscores']:
                        screen.blit(thisGame.imHiscores, (
                            col * TILE_WIDTH - thisGame.screenPixelOffset[0],
                            row * TILE_HEIGHT - thisGame.screenPixelOffset[1]))

                    else:
                        screen.blit(tileIDImage[useTile], (
                            col * TILE_WIDTH - thisGame.screenPixelOffset[0],
                            row * TILE_HEIGHT - thisGame.screenPixelOffset[1]))

    def LoadLevel(self, levelNum, thisFruit, player, ghosts, path,
                  thisGame, tileID, tileIDName, random):
        levelNum = str(levelNum)
        # TODO: Find better way to mitigate IO bottleneck.
        if levelNum in self.preload_width:
            self.lvlWidth = self.preload_width[levelNum]
            self.lvlHeight = self.preload_height[levelNum]
            self.edgeLightColor = self.preload_edge_light[levelNum]
            self.edgeShadowColor = self.preload_edge_shadow[levelNum]
            self.pelletColor = self.preload_pellet_color[levelNum]
            self.fillColor = self.preload_fill[levelNum]
            self.pelletColor = self.preload_pellet_color[levelNum]
            self.map = self.preload_map[levelNum].copy()
            self.pellets = self.preload_pellets[levelNum]
            thisFruit.fruitType = self.preload_fruit_type[levelNum]
            player.homeX, player.homeY = self.preload_player_home[levelNum]
            for i in range(4):
                ghosts[i].homeX, ghosts[i].homeY = \
                    self.preload_ghosts_home[levelNum][i]
            # load map into the pathfinder object
            path.ResizeMap((self.lvlHeight, self.lvlWidth))
            for row in range(0, path.size[0], 1):
                for col in range(0, path.size[1], 1):
                    if self.IsWall((row, col), self):
                        path.SetType((row, col), 1)
                    else:
                        path.SetType((row, col), 0)
            # do all the level-starting stuff
            self.Restart(thisGame, player, ghosts, tileID, path, thisFruit,
                         random)
            return

        self.map = {}
        self.preload_ghosts_home[levelNum] = [(0, 0)] * 4
        self.pellets = 0

        f = open(
            os.path.join(SCRIPT_PATH, "res", "levels", str(levelNum) + ".txt"),
            'r')
        lineNum = -1
        rowNum = 0
        isReadingLevelData = False

        for line in f:

            lineNum += 1

            # print " ------- Level Line " + str(lineNum) + " -------- "
            while len(line) > 0 and (
                    line[-1] == "\n" or line[-1] == "\r"): line = line[:-1]
            while len(line) > 0 and (
                    line[0] == "\n" or line[0] == "\r"): line = line[1:]
            # str_splitBySpace = line.split(' ')
            # TODO: Check if whitespace split is fine.
            str_splitBySpace = split("\\s+", line)

            j = str_splitBySpace[0]

            if j == "'" or j == "":
                # comment / whitespace line
                # print " ignoring comment line.. "
                useLine = False
            elif j == "#":
                # special divider / attribute line
                useLine = False

                firstWord = str_splitBySpace[1]

                if firstWord == "lvlwidth":
                    self.lvlWidth = int(str_splitBySpace[2])

                elif firstWord == "lvlheight":
                    self.lvlHeight = int(str_splitBySpace[2])

                elif firstWord == "edgecolor":
                    # edge color keyword for backwards compatibility (single edge color) mazes
                    red = int(str_splitBySpace[2])
                    green = int(str_splitBySpace[3])
                    blue = int(str_splitBySpace[4])
                    self.edgeLightColor = (red, green, blue, 255)
                    self.edgeShadowColor = (red, green, blue, 255)

                elif firstWord == "edgelightcolor":
                    red = int(str_splitBySpace[2])
                    green = int(str_splitBySpace[3])
                    blue = int(str_splitBySpace[4])
                    self.edgeLightColor = (red, green, blue, 255)

                elif firstWord == "edgeshadowcolor":
                    red = int(str_splitBySpace[2])
                    green = int(str_splitBySpace[3])
                    blue = int(str_splitBySpace[4])
                    self.edgeShadowColor = (red, green, blue, 255)

                elif firstWord == "fillcolor":
                    red = int(str_splitBySpace[2])
                    green = int(str_splitBySpace[3])
                    blue = int(str_splitBySpace[4])
                    self.fillColor = (red, green, blue, 255)

                elif firstWord == "pelletcolor":
                    red = int(str_splitBySpace[2])
                    green = int(str_splitBySpace[3])
                    blue = int(str_splitBySpace[4])
                    self.pelletColor = (red, green, blue, 255)

                elif firstWord == "fruittype":
                    self.preload_fruit_type[levelNum] = int(
                        str_splitBySpace[2])
                    thisFruit.fruitType = int(str_splitBySpace[2])

                elif firstWord == "startleveldata":
                    isReadingLevelData = True
                    # print "Level data has begun"
                    rowNum = 0

                elif firstWord == "endleveldata":
                    isReadingLevelData = False
            # print "Level data has ended"

            else:
                useLine = True

            # this is a map data line
            if useLine:

                if isReadingLevelData:

                    # print str( len(str_splitBySpace) ) + " tiles in this column"

                    for k in range(0, self.lvlWidth, 1):
                        self.SetMapTile((rowNum, k), int(str_splitBySpace[k]))

                        thisID = int(str_splitBySpace[k])
                        if thisID == 4:
                            # starting position for pac-man

                            player.homeX = k * TILE_WIDTH
                            player.homeY = rowNum * TILE_HEIGHT
                            self.preload_player_home[levelNum] = (
                                player.homeX, player.homeY)
                            self.SetMapTile((rowNum, k), 0)

                        elif 10 <= thisID <= 13:
                            # one of the ghosts

                            ghosts[thisID - 10].homeX = k * TILE_WIDTH
                            ghosts[thisID - 10].homeY = rowNum * TILE_HEIGHT
                            self.preload_ghosts_home[levelNum][thisID - 10] = (
                                k * TILE_WIDTH, rowNum * TILE_HEIGHT)
                            self.SetMapTile((rowNum, k), 0)

                        elif thisID == 2:
                            # pellet

                            self.pellets += 1

                    rowNum += 1
        f.close()
        # reload all tiles and set appropriate colors
        GetCrossRef(tileIDName, tileID)

        # load map into the pathfinder object
        path.ResizeMap((self.lvlHeight, self.lvlWidth))

        for row in range(0, path.size[0], 1):
            for col in range(0, path.size[1], 1):
                if self.IsWall((row, col), self):
                    path.SetType((row, col), 1)
                else:
                    path.SetType((row, col), 0)

        # do all the level-starting stuff
        self.preload_width[levelNum] = self.lvlWidth
        self.preload_height[levelNum] = self.lvlHeight
        self.preload_edge_light[levelNum] = self.edgeLightColor
        self.preload_edge_shadow[levelNum] = self.edgeShadowColor
        self.preload_fill[levelNum] = self.fillColor
        self.preload_pellet_color[levelNum] = self.pelletColor
        self.preload_map[levelNum] = self.map.copy()
        self.preload_pellets[levelNum] = self.pellets
        self.Restart(thisGame, player, ghosts, tileID, path, thisFruit, random)

    def Restart(self, thisGame, player, ghosts, tileID, path, thisFruit,
                random):
        # if thisGame.levelNum == 2:
        # player.speed = 4

        for i in range(0, 4, 1):
            # move ghosts back to home
            ghosts[i].x = ghosts[i].homeX
            ghosts[i].y = ghosts[i].homeY
            if self.randomized:
                # (randRow, randCol) = (0, 0)
                # while not self.GetMapTile((randRow, randCol)) == tileID[
                # 'pellet'] or (randRow, randCol) == (0, 0):
                while True:
                    randRow = random.randint(1, self.lvlHeight - 1)  # 2)
                    randCol = random.randint(1, self.lvlWidth - 1)  # 2)
                    tile = self.GetMapTile((randRow, randCol))
                    if tile == tileID["ghost-door"] or \
                            tile == tileID["pellet"] or \
                            tile == tileID["pellet-power"]:
                        break
                ghosts[i].x = randCol * TILE_WIDTH
                ghosts[i].y = randRow * TILE_HEIGHT
            ghosts[i].velX = 0
            ghosts[i].velY = 0
            ghosts[i].state = 1
            ghosts[i].speed = 2
            ghosts[i].Move(path, player, self, tileID, random)

            # give each ghost a path to a random spot (containing a pellet)
            (randRow, randCol) = (0, 0)

            while not self.GetMapTile((randRow, randCol)) == tileID[
                'pellet'] or (randRow, randCol) == (0, 0):
                randRow = random.randint(1, self.lvlHeight - 1)  # 2)
                randCol = random.randint(1, self.lvlWidth - 1)  # 2)

            # print "Ghost " + str(i) + " headed towards " + str((randRow, randCol))
            ghosts[i].currentPath = path.FindPath(
                (ghosts[i].nearestRow, ghosts[i].nearestCol),
                (randRow, randCol))
            ghosts[i].FollowNextPathWay(path, player, self, tileID, random)

        thisFruit.active = False

        thisGame.fruitTimer = 0

        player.x = player.homeX
        player.y = player.homeY
        if self.randomized:
            # (randRow, randCol) = (0, 0)
            # while not self.GetMapTile((randRow, randCol)) == tileID[
            # 'pellet'] or (randRow, randCol) == (0, 0):
            while True:
                randRow = random.randint(1, self.lvlHeight - 1)  # 2)
                randCol = random.randint(1, self.lvlWidth - 1)  # 2)
                tile = self.GetMapTile((randRow, randCol))
                if tile == tileID["pellet"] or tile == tileID["pellet-power"]:
                    break
            player.x = randCol * TILE_WIDTH
            player.y = randRow * TILE_HEIGHT

        player.nearestRow = int(((player.y + (TILE_WIDTH / 2)) / TILE_WIDTH))
        player.nearestCol = int(((player.x + (TILE_HEIGHT / 2)) / TILE_HEIGHT))
        player.velX = 0
        player.velY = 0

        player.anim_pacmanCurrent = player.anim_pacmanS
        player.animFrame = 3
