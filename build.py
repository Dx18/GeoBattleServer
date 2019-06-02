import json as js
from contextlib import closing
import sys
from functions import *
import time
from math import trunc


def build(db, connSock, jsData):
    try:
        with closing(db.getConn()) as dbConn:
            with dbConn.cursor() as cur:

                idPlayer = jsData["authInfo"]["id"]
                token = jsData["authInfo"]["token"]
                buildType = jsData["buildingType"]
                xb = jsData['x']
                yb = jsData['y']

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

                if buildType == 'Mine':
                    sx = 5
                    sy = 5
                    cash = 25
                elif buildType == 'Generator':
                    sx = 5
                    sy = 5
                    cash = 25
                elif buildType == 'Hangar':
                    sx = 7
                    sy = 7
                    cash = 50
                elif buildType == 'ResearchCenter':
                    sx = 6
                    sy = 5
                    cash = 50
                elif buildType == 'Turret':
                    sx = 2
                    sy = 2
                    cash = 15

                if resources < cash:
                    connSock.sendall(
                        js.dumps({"type": "NotEnoughResources", "required": cash}).encode("utf-8"))
                    connSock.close()
                    return None

                idSector = -1
                cur.execute("SELECT id, x, y, isBlocked FROM Sectors WHERE idPlayer={};".format(idPlayer))
                dataSectors = cur.fetchall()
                for sector in dataSectors:
                    xs = sector[1]
                    ys = sector[2]
                    if rectangle_contains(xs, ys, 41, 41, xb - 1, yb - 1, sx + 2, sy + 2):
                        if not rectangles_intersect(xs + 19, ys + 19, 3, 3, xb - 1, yb - 1, sx + 2, sy + 2):
                            idSector = sector[0]
                            isBlocked = sector[3]
                            break

                if idSector == -1:
                    connSock.sendall(js.dumps({"type": "NotInTerritory"}).encode("utf-8"))
                    connSock.close()
                    return None

                if isBlocked != 0:
                    connSock.sendall(js.dumps({"type": "SectorBlocked"}).encode("utf-8"))
                    connSock.close()
                    return None

                cur.execute("SELECT x, y, type FROM Buildings WHERE idSector={};".format(idSector))
                dataBuildings = cur.fetchall()
                for build in dataBuildings:
                    type = build[2]
                    dx = build[0]
                    dy = build[1]
                    if type == 'Mine':
                        dsx = 5
                        dsy = 5
                    elif type == 'Generator':
                        dsx = 5
                        dsy = 5
                    elif type == 'Hangar':
                        dsx = 7
                        dsy = 7
                    elif type == 'ResearchCenter':
                        dsx = 6
                        dsy = 5
                    elif type == 'Turret':
                        dsx = 2
                        dsy = 2

                    if not rectangles_intersect(dx, dy, dsx, dsy, xb - 1, yb - 1, sx + 2, sy + 2):
                        continue
                    else:
                        connSock.sendall(js.dumps({"type": "NotInTerritory"}).encode("utf-8"))
                        connSock.close()
                        return None

                cur.execute("INSERT INTO Buildings (x, y, type, idSector, Data) VALUES ({}, {}, '{}', {}, '') RETURNING id;".format(xb, yb, buildType, idSector))
                idNewBuild = cur.fetchall()[0][0]
                cur.execute("UPDATE Players SET resources = {} WHERE id = {};".format(resources - cash, idPlayer))

                ret = {"type": "BuildingBuilt"}
                ret['cost'] = cash
                ret['info'] = {}
                ret['info']['playerIndex'] = idPlayer
                ret['info']['building'] = {}
                ret['info']['building']['type'] = buildType
                ret['info']['building']['x'] = xb
                ret['info']['building']['y'] = yb
                ret['info']['building']['id'] = idNewBuild
                ret['info']['building']['playerId'] = idPlayer
                ret['info']['building']['sectorId'] = idSector
                if buildType == 'Hangar':
                    ret['info']['building']["units"] = {}
                    ret['info']['building']["units"]["units"] = []

                cur.execute("INSERT INTO Updater (timeT, json) VALUES ({}, '{}')".format(
                    trunc(time.time()), js.dumps(ret)))

                connSock.sendall(js.dumps(ret).encode('utf-8'))
                connSock.close()
                return None

    except Exception as exc:
        print(exc)
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno))
    connSock.sendall(js.dumps({"type": "MalformedJson"}).encode("utf-8"))
    connSock.close()
    return None


def destroy(db, connSock, jsData):
    try:
        with closing(db.getConn()) as dbConn:
            with dbConn.cursor() as cur:

                idPlayer = jsData['authInfo']['id']
                idB = jsData['id']
                token = jsData['authInfo']['token']

                try:
                    cur.execute(
                        "SELECT token FROM Players WHERE id={};".format(idPlayer))
                    if token != cur.fetchall()[0][0]:
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

                cur.execute("SELECT x, y, type, idSector FROM Buildings WHERE id={};".format(idB))
                x, y, type, idSector = cur.fetchall()[0]
#                type = cur.fetchall()[0][2]
#                x = cur.fetchall()[0][0]
#                y = cur.fetchall()[0][1]
#                idSector = cur.fetchall()[0][3]

                cur.execute("SELECT idPlayer FROM Sectors WHERE id={};".format(idSector))
                idPlayerB = cur.fetchall()[0][0]

                if idPlayer != idPlayerB:
                    connSock.sendall(js.dumps({"type": "NotOwningBuilding"}).encode("utf-8"))
                    connSock.close()
                    return None

                cur.execute("DELETE FROM Buildings WHERE id={};".format(idB))
                d = {"type": "BuildingDestroyed"}
                d["info"] = {}
                d["info"]["playerIndex"] = idPlayer
                d["info"]["building"] = {}
                d["info"]["building"]["type"] = type
                d["info"]["building"]["x"] = x
                d["info"]["building"]["y"] = y
                d["info"]["building"]["id"] = idB
                d["info"]["building"]["playerId"] = idPlayer
                d["info"]["building"]["sectorId"] = idSector
                if type == 'Hangar':
                    d["info"]["building"]["units"] = {}
                    d["info"]["building"]["units"]["units"] = []
                    cur.execute("SELECT id, hangarSlot FROM Units WHERE hangarId={};".format(idB))
                    units = cur.fetchall()
                    d["info"]["building"]["units"]["health"] = 50 * len(units)
                    for unit in units:
                        cur.execute("DELETE FROM Units WHERE id={};".format(unit[0]))
                        d["info"]["building"]["units"]["units"].append({})
                        d["info"]["building"]["units"]["units"][-1]["type"] = "Bomber"
                        d["info"]["building"]["units"]["units"][-1]["id"] = unit[0]
                        d["info"]["building"]["units"]["units"][-1]["hangarId"] = idB
                        d["info"]["building"]["units"]["units"][-1]["hangarSlot"] = unit[1]

                cur.execute("INSERT INTO Updater (timeT, json) VALUES ({}, '{}')".format(
                    trunc(time.time()), js.dumps(d)))

                connSock.sendall(js.dumps(d).encode("utf-8"))
                connSock.close()
                return None

    except Exception as exc:
        print(exc)
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno))
    connSock.sendall(js.dumps({"type": "MalformedJson"}).encode("utf-8"))
    connSock.close()
    return None
