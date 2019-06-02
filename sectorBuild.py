import json as js
from contextlib import closing
import sys
from functions import *
import time
from math import trunc


def sectorBuild(db, connSock, jsData):
    try:
        with closing(db.getConn()) as dbConn:
            with dbConn.cursor() as cur:

                idPlayer = jsData["authInfo"]["id"]
                token = jsData["authInfo"]["token"]
                xbs = jsData["x"]
                ybs = jsData["y"]

                try:
                    cur.execute(
                        "SELECT token, resources FROM Players WHERE id={};".format(idPlayer))
                    validToken, resources = cur.fetchall()[0]
                    if token != validToken:
                        connSock.sendall(
                            js.dumps({"type": "WrongAuthInfo"}).encode(
                                "utf-8"))
                        connSock.close()
                        return None
                except Exception as exc:
                    connSock.sendall(
                        js.dumps({"type": "WrongAuthInfo"}).encode("utf-8"))
                    connSock.close()
                    return None

                cur.execute(
                    "SELECT x, y FROM Sectors WHERE idPlayer={};".format(idPlayer))
                mySectors = cur.fetchall()
                cash = 50 + 25 * len(mySectors)
                if resources < cash:
                    connSock.sendall(
                        js.dumps({"type": "NotEnoughResources", "required": cash}).encode("utf-8"))
                    connSock.close()
                    return None

                if len(mySectors) == 0:
                    canBuild = True
                else:
                    isNeighbour = False
                    exists = False
                    for mySector in mySectors:
                        horizontalNeighbour = abs(
                            mySector[0] - xbs) == 41 and mySector[1] == ybs
                        verticalNeighbour = abs(
                            mySector[1] - ybs) == 41 and mySector[0] == xbs
                        if horizontalNeighbour or verticalNeighbour:
                            isNeighbour = True
                        if mySector[0] == xbs and mySector[1] == ybs:
                            exists = True

                    canBuild = isNeighbour and not exists

                if canBuild:
                    pass
                else:
                    connSock.sendall(
                        js.dumps({"type": "WrongPosition"}).encode("utf-8"))
                    connSock.close()
                    return None

                cur.execute("SELECT x, y, idPlayer FROM Sectors;")
                sectors = cur.fetchall()
                for sector in sectors:
                    if rectangles_intersect(sector[0], sector[1], 41, 41, xbs, ybs, 41, 41):
                        d = {"type": "IntersectsWithEnemy"}
                        d["enemyIndex"] = sector[2]
                        connSock.sendall(js.dumps(d).encode("utf-8"))
                        connSock.close()
                        return None

                cur.execute("INSERT INTO Sectors (x, y, idPlayer, isBlocked) VALUES ({}, {}, {}, {}) RETURNING id;".format(
                    xbs, ybs, idPlayer, 0))
                idNewSector = cur.fetchall()[0][0]
                cur.execute("UPDATE Players SET resources = {} WHERE id = {};".format(
                    resources - cash, idPlayer))
                ret = {}
                ret["type"] = "SectorBuilt"
                ret["info"] = {}
                ret["info"]["playerIndex"] = idPlayer
                ret["info"]["x"] = xbs
                ret["info"]["y"] = ybs
                ret["info"]["id"] = idNewSector
                connSock.sendall(js.dumps(ret).encode("utf-8"))
                connSock.close()

                cur.execute("INSERT INTO Updater (timeT, json) VALUES ({}, '{}')".format(
                    trunc(time.time()), js.dumps(ret)))

                return None

    except Exception as exc:
        print(exc)
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno))
    connSock.sendall(js.dumps({"type": "MalformedJson"}).encode("utf-8"))
    connSock.close()
    return None
