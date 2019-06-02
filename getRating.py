import json as js
from contextlib import closing
import sys


def getRating(db, connSock, jsData):
    try:
        with closing(db.getConn()) as dbConn:
            with dbConn.cursor() as cur:

#                idPlayer = jsData["authInfo"]["id"]
#                token = jsData["authInfo"]["token"]
#
#                try:
#                    cur.execute(
#                        "SELECT token FROM Players WHERE id={};".format(idPlayer))
#                    if token != cur.fetchall()[0][0]:
#                        connSock.sendall(
#                            js.dumps({"type": "WrongAuthInfo"}).encode(
#                                "utf-8"))
#                        connSock.close()
#                        return None
#                except Exception as exc:
#                    connSock.sendall(
#                        js.dumps({"type": "WrongAuthInfo"}).encode("utf-8"))
#                    connSock.close()
#                    return None

                d = {"type": "RatingRequestSuccess"}
                d["rating"] = []

                cur.execute("SELECT id, resources, levelT, levelG, levelP FROM Players;")
                players = cur.fetchall()
                for player in players:
                    d["rating"].append({})
                    id = player[0]
                    resources = player[1]
                    levelT = player[2]
                    levelG = player[3]
                    levelP = player[4]
                    cash = 0
                    cash += 500 * (2**levelT + 2**levelG + 2**levelP)
                    cash += resources

                    cur.execute("SELECT id FROM Sectors WHERE idPlayer={};".format(id))
                    sectors = cur.fetchall()
                    n = len(sectors)
                    an = 25 * (1 + n)
                    a1 = 50
                    cash += (a1 + an) * n / 2

                    for sector in sectors:
                        cur.execute("SELECT type FROM Buildings WHERE idSector={};".format(sector[0]))
                        buildings = cur.fetchall()
                        for build in buildings:
                            buildType = build[0]
                            if buildType == 'Mine':
                                cashb = 25
                            elif buildType == 'Generator':
                                cashb = 25
                            elif buildType == 'Hangar':
                                cashb = 50
                            elif buildType == 'ResearchCenter':
                                cashb = 50
                            elif buildType == 'Turret':
                                cashb = 15
                            else:
                                cashb = 20
                            cash += cashb

                    d["rating"][-1]["wealth"] = cash
                    d["rating"][-1]["playerId"] = id

                connSock.sendall(js.dumps(d).encode("utf-8"))
                connSock.close()
                return None

    except Exception as exc:
        print(exc)
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno))
    connSock.sendall(js.dumps({"type": "MalformedJson"}).encode("utf-8"))
    connSock.close()
    return None
