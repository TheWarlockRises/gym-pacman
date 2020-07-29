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


def sensor_1d_1(sensor_range, view=None):
    def sensor(env):
        pass

    return sensor


def sensor_1d_2(sensor_range, view=None):
    def sensor(env):
        pass

    return sensor


def sensor_1d_4(sensor_range, view=None):
    if view is not None:
        view = max(sensor_range, view)
    else:
        view = sensor_range

    def sensor(env):
        vision = zeros(view * 4, dtype=int)
        dirs = ((1, 0), (0, -1), (-1, 0), (0, 1))
        door_h, door_v, pel, p_pel, fx, fy, gxy, vxy = get_tile_info(env)

        for d in range(4):
            x = env.player.nearestCol
            y = env.player.nearestRow
            for r in range(sensor_range):
                index = 4 * r + d
                x %= env.thisLevel.lvlWidth
                y %= env.thisLevel.lvlHeight
                tile = env.thisLevel.GetMapTile((y, x))
                if any(x == g[0] and y == g[1] for g in gxy):
                    vision[index] = -1
                elif any(x == g[0] and y == g[1] for g in vxy):
                    vision[index] = 4
                elif env.thisFruit.active and fx == x and fy == y:
                    vision[index] = 5
                elif tile == 0 or tile == door_h or tile == door_v:
                    vision[index] = 1
                elif tile == pel:
                    vision[index] = 2
                elif tile == p_pel:
                    vision[index] = 3
                else:
                    break
                x += dirs[d][0]
                y += dirs[d][1]
        return vision

    return sensor


def sensor_2d(sensor_range, view=None):
    def sensor(env):
        pass

    return sensor
