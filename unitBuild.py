import json as js
from contextlib import closing
import sys
import time
from math import trunc


def addUnit(db, connSock, jsData):
    try:
        with closing(db.getConn()) as dbConn:
            with dbConn.cursor() as cur:

                idPlayer = jsData["authInfo"]["id"]
                token = jsData["authInfo"]["token"]
                idHangar = jsData["hangarId"]
                cur.execute("SELECT idSector FROM Buildings WHERE id={};".format(idHangar))
                idSector = cur.fetchall()[0][0]

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

                cur.execute("SELECT hangarSlot FROM Units WHERE hangarId={};".format(idHangar))
                units = cur.fetchall()
                if len(units) >= 4:
                    connSock.sendall(js.dumps({"type": "NoPlaceInHangar"}).encode("utf-8"))
                    connSock.close()
                    return None
                l = [0, 1, 2, 3]
                for unit in units:
                    l.remove(unit[0])
                slot = l[0]

                cur.execute("SELECT isBlocked FROM Sectors WHERE id={};".format(idSector))
                isBlocked = cur.fetchall()[0][0]
                if isBlocked == 1:
                    connSock.sendall(js.dumps({"type": "SectorBlocked"}).encode("utf-8"))
                    connSock.close()
                    return None

                if resources < 20:
                    connSock.sendall(js.dumps({"type": "NotEnoughResources", "required": 20}).encode("utf-8"))
                    connSock.close()
                    return None

                cur.execute("INSERT INTO Units (hangarId, hangarSlot) VALUES ({}, {});".format(idHangar, slot))
                cur.execute("UPDATE Players SET resources = {} WHERE id = {};".format(resources - 20, idPlayer))

                cur.execute("SELECT id FROM Units WHERE  hangarId={} AND hangarSlot={};".format(idHangar, slot))
                idPlane = cur.fetchall()[0][0]

                d = {"type": "UnitBuilt"}
                d["cost"] = 20
                d["info"] = {}
                d["info"]["playerIndex"] = idPlayer
                d["info"]["unit"] = {}
                d["info"]["unit"]["type"] = "Bomber"
                d["info"]["unit"]["id"] = idPlane
                d["info"]["unit"]["hangarId"] = idHangar
                d["info"]["unit"]["hangarSlot"] = slot

                connSock.sendall(js.dumps(d).encode("utf-8"))
                connSock.close()

                cur.execute("INSERT INTO Updater (timeT, json) VALUES ({}, '{}')".format(
                    trunc(time.time()), js.dumps(d)))

                return None

    except Exception as exc:
        print(exc)
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno))
    connSock.sendall(js.dumps({"type": "MalformedJson"}).encode("utf-8"))
    connSock.close()
    return None
