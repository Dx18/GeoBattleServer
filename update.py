from contextlib import closing
import sys
from math import trunc
import time


def update(db):
    try:
        with closing(db.getConn()) as dbConn:
            with dbConn.cursor() as cur:
                cur.execute("SELECT id, resources FROM Players;")
                players = cur.fetchall()
                for player in players:
                    id = player[0]
                    res = player[1]
                    step = 0

                    cur.execute("SELECT id FROM Sectors WHERE isBlocked=0 AND idPlayer={}".format(id))
                    sectors = cur.fetchall()
                    for sector in sectors:
                        idSector = sector[0]
                        en = 10
                        re = 1

                        cur.execute("SELECT type FROM Buildings WHERE idSector={};".format(idSector))
                        buildings = cur.fetchall()
                        cur.execute("SELECT levelG FROM Players WHERE id={};".format(id))
                        levelG = cur.fetchall()[0][0]
                        for build in buildings:
                            if build[0] == 'Generator':
                                en += 30 + levelG
                            elif build[0] == 'Mine':
                                en -= 5
                                re += 1
                            elif build[0] == 'Hangar':
                                en -= 10
                            elif build[0] == 'Turret':
                                en -= 6
                            else:
                                en -= 4

                        if en >= 0:
                            step += re

                    max = 200 + len(sectors) * 50
                    line = max - step

                    if res < line:
                        res += step
                    else:
                        res = max

                    cur.execute("UPDATE Players SET resources = {} WHERE id = {};".format(res, id))

                return trunc(time.time() + 1)

    except Exception as exc:
        print(exc)
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno))
    return pTime
