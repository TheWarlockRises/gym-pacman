from numpy import array


def sensor_1d(sensor_range):
    def default_sensor(env):
        vision = [0] * sensor_range * 4
        dirs = ((1, 0), (0, -1), (-1, 0), (0, 1))
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

        for d in range(4):
            x = env.player.nearestCol
            y = env.player.nearestRow
            for r in range(sensor_range):
                index = d * sensor_range + r
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
        return array(vision)

    return default_sensor
