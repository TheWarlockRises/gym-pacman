from numpy import zeros


def get_tile_info(env):
    door_h = env.tileID["door-h"]
    door_v = env.tileID["door-v"]
    pel = env.tileID["pellet"]
    p_pel = env.tileID["pellet-power"]
    fx = env.thisFruit.nearestCol
    fy = env.thisFruit.nearestRow
    gxy = list((g.nearestCol, g.nearestRow) for g in
               filter(lambda g: g.state == 1, env.ghosts.values()))
    vxy = list((g.nearestCol, g.nearestRow) for g in
               filter(lambda g: g.state == 2, env.ghosts.values()))
    return door_h, door_v, pel, p_pel, fx, fy, gxy, vxy


def sensor_1d_1(sensor_range, block=False, door_skip=False, offset=False,
                view=None, width=0):
    """
    A sensor that extends in the direction the player is facing.

    :param sensor_range: The length of the sensor/vision.
    :param block: Whether walls block the remaining sensor data or not.
    :param door_skip: Skip the adjacent door when recording doors in sensor.
    :param offset: Whether to shift the sensor data one tile forward or not.
    :param view: The length of vision to zero pad the sensor data to fit.
    :param width: Additional thickness to each direction's sensor.
    :return: A 2D array of shape (length=max(sensor_range, view),
        features=width * 2 + 1)
    """
    dirs = ((1, 0), (0, -1), (-1, 0), (0, 1))
    if view is not None:
        view = max(sensor_range, view)
    else:
        view = sensor_range

    def sensor(env):
        vision = zeros((view, width * 2 + 1), dtype=int)
        if env is None:
            return vision
        door_h, door_v, pel, p_pel, fx, fy, gxy, vxy = get_tile_info(env)

        for w in range(-width, width + 1):
            dir1 = dirs[env.action]
            dir2 = dirs[(env.action + 1) % 4]
            x = env.player.nearestCol + dir2[0] * w
            y = env.player.nearestRow + dir2[1] * w
            if offset:
                x += dir1[0]
                y += dir1[1]
            w += width
            for r in range(sensor_range):
                x %= env.thisLevel.lvlWidth
                y %= env.thisLevel.lvlHeight
                tile = env.thisLevel.GetMapTile((y, x))
                if any(x == g[0] and y == g[1] for g in gxy):
                    vision[r][w] = -1
                elif any(x == g[0] and y == g[1] for g in vxy):
                    vision[r][w] = 4
                elif env.thisFruit.active and fx == x and fy == y:
                    vision[r][w] = 5
                elif tile == 0:
                    vision[r][w] = 1
                elif tile == pel:
                    vision[r][w] = 2
                elif tile == p_pel:
                    vision[r][w] = 3
                elif tile == door_h or tile == door_v:
                    vision[r][w] = 1
                    if door_skip:
                        x += dir1[0]
                        y += dir1[1]
                elif block:
                    break
                x += dir1[0]
                y += dir1[1]
        return vision

    return sensor


def sensor_1d_2(sensor_range, block=False, door_skip=False, offset=False,
                view=None, width=0):
    """
    A sensor that extends in the forward and backward directions based on the
    direction the player is facing.

    :param sensor_range: The length of the sensor/vision.
    :param block: Whether walls block the remaining sensor data or not.
    :param door_skip: Skip the adjacent door when recording doors in sensor.
    :param offset: Whether to shift the sensor data one tile forward or not.
    :param view: The length of vision to zero pad the sensor data to fit.
    :param width: Additional thickness to each direction's sensor.
    :return: A 2D array of shape (length=max(sensor_range, view),
        features=2 * (width * 2 + 1))
    """
    dirs = ((1, 0), (0, -1), (-1, 0), (0, 1))
    if view is not None:
        view = max(sensor_range, view)
    else:
        view = sensor_range

    def sensor(env):
        vision = zeros((view, 2 * (width * 2 + 1)), dtype=int)
        if env is None:
            return vision
        door_h, door_v, pel, p_pel, fx, fy, gxy, vxy = get_tile_info(env)

        for d in range(2):  # d * 2: front and back
            dir1 = dirs[(env.action + d * 2) % 4]
            dir2 = dirs[(env.action + d * 2 + 1) % 4]
            for w in range(-width, width + 1):
                x = env.player.nearestCol + dir2[0] * w
                y = env.player.nearestRow + dir2[1] * w
                if offset:
                    x += dir1[0]
                    y += dir1[1]
                w += width
                d_index = d * (width * 2 + 1) + w
                for r in range(sensor_range):
                    x %= env.thisLevel.lvlWidth
                    y %= env.thisLevel.lvlHeight
                    tile = env.thisLevel.GetMapTile((y, x))
                    if any(x == g[0] and y == g[1] for g in gxy):
                        vision[r][d_index] = -1
                    elif any(x == g[0] and y == g[1] for g in vxy):
                        vision[r][d_index] = 4
                    elif env.thisFruit.active and fx == x and fy == y:
                        vision[r][d_index] = 5
                    elif tile == 0:
                        vision[r][d_index] = 1
                    elif tile == pel:
                        vision[r][d_index] = 2
                    elif tile == p_pel:
                        vision[r][d_index] = 3
                    elif tile == door_h or tile == door_v:
                        vision[r][d_index] = 1
                        if door_skip:
                            x += dir1[0]
                            y += dir1[1]
                    elif block:
                        break
                    x += dir1[0]
                    y += dir1[1]
        return vision

    return sensor


def sensor_1d_4(sensor_range, block=False, door_skip=False, offset=False,
                rotate=False, view=None, width=0):
    """
    A sensor that extends in all four cardinal directions.

    :param sensor_range: The length of the sensor/vision.
    :param block: Whether walls block the remaining sensor data or not.
    :param door_skip: Skip the adjacent door when recording doors in sensor.
    :param offset: Whether to shift the sensor data one tile forward or not.
    :param rotate: Whether to rotate the sensor data based on the player.
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
        door_h, door_v, pel, p_pel, fx, fy, gxy, vxy = get_tile_info(env)

        for d in range(4):
            dir2 = dirs[(d + 1) % 4]
            for w in range(-width, width + 1):
                x = env.player.nearestCol + dir2[0] * w
                y = env.player.nearestRow + dir2[1] * w
                if offset:
                    x += dirs[d][0]
                    y += dirs[d][1]
                w += width
                # d_index = d * (width * 2 + 1) + w
                d_index = (d - rotation * env.action) * (width * 2 + 1) + w
                d_index %= 4 * (width * 2 + 1)
                for r in range(sensor_range):
                    x %= env.thisLevel.lvlWidth
                    y %= env.thisLevel.lvlHeight
                    tile = env.thisLevel.GetMapTile((y, x))
                    if any(x == g[0] and y == g[1] for g in gxy):
                        vision[r][d_index] = -1
                    elif any(x == g[0] and y == g[1] for g in vxy):
                        vision[r][d_index] = 4
                    elif env.thisFruit.active and fx == x and fy == y:
                        vision[r][d_index] = 5
                    elif tile == 0:
                        vision[r][d_index] = 1
                    elif tile == pel:
                        vision[r][d_index] = 2
                    elif tile == p_pel:
                        vision[r][d_index] = 3
                    elif tile == door_h or tile == door_v:
                        vision[r][d_index] = 1
                        if door_skip:
                            x += dirs[d][0]
                            y += dirs[d][1]
                    elif block:
                        break
                    x += dirs[d][0]
                    y += dirs[d][1]
        return vision

    return sensor


def sensor_2d(sensor_range, view=None):
    if view is not None:
        view = max(sensor_range, view)
    else:
        view = sensor_range

    def sensor(env):
        # TODO: Determine needed input for Conv2D
        vision = zeros((view * 2 + 1, view * 2 + 1), dtype=int)
        if env is None:
            return vision
        door_h, door_v, pel, p_pel, fx, fy, gxy, vxy = get_tile_info(env)
        for x in range(-view, view + 1):
            px = x + env.player.nearestCol
            px %= env.thisLevel.lvlWidth
            x += view
            for y in range(-view, view + 1):
                py = y + env.player.nearestRow
                py %= env.thisLevel.lvlHeight
                tile = env.thisLevel.GetMapTile((py, px))
                y += view
                if any(px == g[0] and py == g[1] for g in gxy):
                    vision[x][y] = -1
                elif any(px == g[0] and py == g[1] for g in vxy):
                    vision[x][y] = 4
                elif env.thisFruit.active and fx == px and fy == py:
                    vision[x][y] = 5
                elif tile == 0 or tile == door_h or tile == door_v:
                    vision[x][y] = 1
                elif tile == pel:
                    vision[x][y] = 2
                elif tile == p_pel:
                    vision[x][y] = 3
        # TODO: Implement sensor rotation
        return vision

    return sensor
