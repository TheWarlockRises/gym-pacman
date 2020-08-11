from numpy import rot90, zeros


def get_tile_info(env, door_skip):
    door_h = env.tileID["door-h"]
    door_v = env.tileID["door-v"]
    pel = env.tileID["pellet"]
    p_pel = env.tileID["pellet-power"]
    fx = env.thisFruit.nearestCol
    fy = env.thisFruit.nearestRow
    gxy = list((g.nearestCol, g.nearestRow) for g in
               filter(lambda gk: gk.id < 4 and gk.state == 1,
                      env.ghosts.values()))
    vxy = list((g.nearestCol, g.nearestRow) for g in
               filter(lambda gk: gk.id < 4 and gk.state == 2,
                      env.ghosts.values()))
    lvl_height = env.thisLevel.lvlHeight
    lvl_width = env.thisLevel.lvlWidth
    if door_skip:
        lvl_height -= 1
        lvl_width -= 1
    return door_h, door_v, pel, p_pel, fx, fy, gxy, vxy, lvl_height, lvl_width


def sensor_1d_1(sensor_range, block=False, door_skip=False, offset=False,
                rotate=True, tile_map=True, view=None, width=0):
    """
    A sensor that extends in the direction the player is facing.

    :param sensor_range: The length of the sensor/vision.
    :param block: Whether walls block the remaining sensor data or not.
    :param door_skip: Skip the adjacent door when recording doors in sensor
        if tile_map is True. In other words, this crops the bottom row and
        rightmost column of the map.
    :param offset: Whether to shift the sensor data one tile forward or not.
    :param rotate: Dummy parameter.
    :param tile_map: Whether to repeat the map past a door.
    :param view: The length of vision to zero pad the sensor data to fit.
    :param width: Additional thickness to each direction's sensor.
    :return: A 2D array of shape (length=max(sensor_range, view),
        features=width * 2 + 1)
    """
    dirs = ((1, 0), (0, -1), (-1, 0), (0, 1))
    if rotate:
        pass
    if view is not None:
        view = max(sensor_range, view)
    else:
        view = sensor_range

    def sensor(env):
        vision = zeros((view, width * 2 + 1), dtype=int)
        if env is None:
            return vision
        door_h, door_v, pel, p_pel, fx, fy, gxy, vxy, lvl_height, lvl_width = \
            get_tile_info(env, door_skip)
        blocked = [False] * (width * 2 + 1)
        dir1 = dirs[env.action]
        dir2 = dirs[(env.action + 1) % 4]
        offset_r = 1 if offset else 0
        for r in range(sensor_range):
            x = env.player.nearestCol + dir1[0] * (r + offset_r)
            y = env.player.nearestRow + dir1[1] * (r + offset_r)
            for w in range(-width, width + 1):
                px = x + dir2[0] * w
                py = y + dir2[1] * w
                w += width
                if blocked[w]:
                    continue
                elif not tile_map and (
                        px < 0 or px >= env.thisLevel.lvlWidth or
                        py < 0 or py >= env.thisLevel.lvlHeight):
                    blocked[w] = True
                    continue
                px %= lvl_width
                py %= lvl_height
                tile = env.thisLevel.GetMapTile((py, px))
                if any(px == g[0] and py == g[1] for g in gxy):
                    vision[r][w] = -1
                elif any(px == g[0] and py == g[1] for g in vxy):
                    vision[r][w] = 4
                elif env.thisFruit.active and fx == px and fy == py:
                    vision[r][w] = 5
                elif tile == 0:
                    vision[r][w] = 1
                elif tile == pel:
                    vision[r][w] = 2
                elif tile == p_pel:
                    vision[r][w] = 3
                elif tile == door_h or tile == door_v:
                    vision[r][w] = 1
                elif block:
                    blocked[w] = True
        return vision

    return sensor


def sensor_1d_2(sensor_range, block=False, door_skip=False, offset=False,
                rotate=True, tile_map=True, view=None, width=0):
    """
    A sensor that extends in the forward and backward directions based on the
    direction the player is facing.

    :param sensor_range: The length of the sensor/vision.
    :param block: Whether walls block the remaining sensor data or not.
    :param door_skip: Skip the adjacent door when recording doors in sensor
        if tile_map is True. In other words, this crops the bottom row and
        rightmost column of the map.
    :param offset: Whether to shift the sensor data one tile forward or not.
    :param rotate: Dummy parameter.
    :param tile_map: Whether to repeat the map past a door.
    :param view: The length of vision to zero pad the sensor data to fit.
    :param width: Additional thickness to each direction's sensor.
    :return: A 2D array of shape (length=max(sensor_range, view),
        features=2 * (width * 2 + 1))
    """
    dirs = ((1, 0), (0, -1), (-1, 0), (0, 1))
    if rotate:
        pass
    if view is not None:
        view = max(sensor_range, view)
    else:
        view = sensor_range

    def sensor(env):
        vision = zeros((view, 2 * (width * 2 + 1)), dtype=int)
        if env is None:
            return vision
        door_h, door_v, pel, p_pel, fx, fy, gxy, vxy, lvl_height, lvl_width = \
            get_tile_info(env, door_skip)
        offset_r = 1 if offset else 0
        for d in range(2):  # d * 2: front and back
            blocked = [False] * (width * 2 + 1)
            dir1 = dirs[(env.action + d * 2) % 4]
            dir2 = dirs[(env.action + d * 2 + 1) % 4]
            for r in range(sensor_range):
                x = env.player.nearestCol + dir1[0] * (r + offset_r)
                y = env.player.nearestRow + dir1[1] * (r + offset_r)
                for w in range(-width, width + 1):
                    px = x + dir2[0] * w
                    py = y + dir2[1] * w
                    w += width
                    if blocked[w]:
                        continue
                    elif not tile_map and (
                            px < 0 or px >= env.thisLevel.lvlWidth or
                            py < 0 or py >= env.thisLevel.lvlHeight):
                        blocked[w] = True
                        continue
                    d_index = d * (width * 2 + 1) + w
                    px %= lvl_width
                    py %= lvl_height
                    tile = env.thisLevel.GetMapTile((py, px))
                    if any(px == g[0] and py == g[1] for g in gxy):
                        vision[r][d_index] = -1
                    elif any(px == g[0] and py == g[1] for g in vxy):
                        vision[r][d_index] = 4
                    elif env.thisFruit.active and fx == px and fy == py:
                        vision[r][d_index] = 5
                    elif tile == 0:
                        vision[r][d_index] = 1
                    elif tile == pel:
                        vision[r][d_index] = 2
                    elif tile == p_pel:
                        vision[r][d_index] = 3
                    elif tile == door_h or tile == door_v:
                        vision[r][d_index] = 1
                    elif block:
                        blocked[w] = True
        return vision

    return sensor


def sensor_1d_4(sensor_range, block=False, door_skip=False, offset=False,
                rotate=False, tile_map=True, view=None, width=0):
    """
    A sensor that extends in all four cardinal directions.

    :param sensor_range: The length of the sensor/vision.
    :param block: Whether walls block the remaining sensor data or not.
    :param door_skip: Skip the adjacent door when recording doors in sensor
        if tile_map is True. In other words, this crops the bottom row and
        rightmost column of the map.
    :param offset: Whether to shift the sensor data one tile forward or not.
    :param rotate: Whether to rotate the sensor data based on the player's
        last nonzero velocity.
    :param tile_map: Whether to repeat the map past a door.
    :param view: The length of vision to zero pad the sensor data to fit.
    :param width: Additional thickness to each direction's sensor.
    :return: A 2D array of shape (length=max(sensor_range, view),
        features=4 * (width * 2 + 1))
    """
    dirs = ((1, 0), (0, -1), (-1, 0), (0, 1))
    rotation = 1 if rotate else 0
    if view is not None:
        view = max(sensor_range, view)
    else:
        view = sensor_range

    def sensor(env):
        vision = zeros((view, 4 * (width * 2 + 1)), dtype=int)
        if env is None:
            return vision
        door_h, door_v, pel, p_pel, fx, fy, gxy, vxy, lvl_height, lvl_width = \
            get_tile_info(env, door_skip)
        offset_r = 1 if offset else 0
        for d in range(4):
            blocked = [False] * (width * 2 + 1)
            dir1 = dirs[d]
            dir2 = dirs[(d + 1) % 4]
            for r in range(sensor_range):
                x = env.player.nearestCol + dir1[0] * (r + offset_r)
                y = env.player.nearestRow + dir1[1] * (r + offset_r)
                for w in range(-width, width + 1):
                    px = x + dir2[0] * w
                    py = y + dir2[1] * w
                    w += width
                    if blocked[w]:
                        continue
                    elif not tile_map and (
                            px < 0 or px >= env.thisLevel.lvlWidth or
                            py < 0 or py >= env.thisLevel.lvlHeight):
                        blocked[w] = True
                        continue
                    d_index = (d - rotation * env.action) * (
                            width * 2 + 1) + w
                    d_index %= 4 * (width * 2 + 1)
                    px %= lvl_width
                    py %= lvl_height
                    tile = env.thisLevel.GetMapTile((py, px))
                    if any(px == g[0] and py == g[1] for g in gxy):
                        vision[r][d_index] = -1
                    elif any(px == g[0] and py == g[1] for g in vxy):
                        vision[r][d_index] = 4
                    elif env.thisFruit.active and fx == px and fy == py:
                        vision[r][d_index] = 5
                    elif tile == 0:
                        vision[r][d_index] = 1
                    elif tile == pel:
                        vision[r][d_index] = 2
                    elif tile == p_pel:
                        vision[r][d_index] = 3
                    elif tile == door_h or tile == door_v:
                        vision[r][d_index] = 1
                    elif block:
                        blocked[w] = True
        return vision

    return sensor


def sensor_2d(sensor_range, block=False, door_skip=False, offset=False,
              rotate=False, tile_map=True, view=None, width=0):
    """
    A sensor that produces a 2D square grid centered on the player.

    :param sensor_range: The length of the sensor/vision.
    :param block: Dummy parameter.
    :param door_skip: Skip the adjacent door when recording doors in sensor
        if tile_map is True. In other words, this crops the bottom row and
        rightmost column of the map.
    :param offset: Whether to shift the sensor data one tile forward or not.
        This adds 2 to the side length.
    :param rotate: Whether to rotate the sensor data based on the player's
        last nonzero velocity.
    :param tile_map: Whether to repeat the map past a door.
    :param view: The length of vision to zero pad the sensor data to fit.
        The size of the 2D array will be (view * 2 + 1, view * 2 + 1) assuming
        view is greater than sensor_range.
    :param width: Dummy parameter.
    :return: A 2D array of shape (max(sensor_range, view) * 2 + 1,
        max(sensor_range, view) * 2 + 1) if offset is True, otherwise,
        (max(sensor_range - 1, view) * 2 + 1,
        max(sensor_range - 1, view) * 2 + 1)
    """
    if block:
        pass
    elif width == 0:
        pass
    sensor_range -= 0 if offset else 1
    if view is not None:
        view = max(sensor_range, view)
    else:
        view = sensor_range

    def sensor(env):
        # TODO: Determine needed input for Conv2D
        vision = zeros((view * 2 + 1, view * 2 + 1), dtype=int)
        if env is None:
            return vision
        door_h, door_v, pel, p_pel, fx, fy, gxy, vxy, lvl_height, lvl_width = \
            get_tile_info(env, door_skip)
        door_x = 0
        for x in range(-sensor_range, sensor_range + 1):
            px = x + env.player.nearestCol + door_x
            # Skip recording tiles if out of bounds and map tiling = false.
            if not tile_map and (px < 0 or px >= env.thisLevel.lvlWidth):
                continue
            px %= env.thisLevel.lvlWidth
            x += view
            door_y = 0
            for y in range(-sensor_range, sensor_range + 1):
                py = y + env.player.nearestRow + door_y
                # Skip recording tiles if out of bounds and map tiling = false.
                if not tile_map and (py < 0 or py >= env.thisLevel.lvlHeight):
                    continue
                py %= env.thisLevel.lvlHeight
                tile = env.thisLevel.GetMapTile((py, px))
                y += view
                if any(px == g[0] and py == g[1] for g in gxy):
                    vision[x][y] = -1
                elif any(px == g[0] and py == g[1] for g in vxy):
                    vision[x][y] = 4
                elif env.thisFruit.active and fx == px and fy == py:
                    vision[x][y] = 5
                elif tile == 0:
                    vision[x][y] = 1
                elif tile == pel:
                    vision[x][y] = 2
                elif tile == p_pel:
                    vision[x][y] = 3
                elif tile == door_h:
                    if door_skip and px > 0:
                        door_x += 1
                    vision[x][y] = 1
                elif tile == door_v:
                    if door_skip and py > 0:
                        door_y += 1
                    vision[x][y] = 1
        if rotate:
            vision = rot90(vision, k=env.action)
        return vision

    return sensor
