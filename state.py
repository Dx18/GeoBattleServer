import json as js
from contextlib import closing
import sys
import time


def state(db, connSock, jsData):
    try:
        with closing(db.getConn()) as dbConn:
            with dbConn.cursor() as cur:

                id = jsData["authInfo"]["id"]
                token = jsData["authInfo"]["token"]

                try:
                    cur.execute(
                        "SELECT token FROM Players WHERE id={};".format(id))
                    if token != cur.fetchall()[0][0]:
                        connSock.sendall(
                            js.dumps({"type": "WrongAuthInfo"}).encode(
                                "utf-8"))
                        connSock.close()
                        return None
                except Exception as exc:
                    print(exc)
                    connSock.sendall(
                        js.dumps({"type": "WrongAuthInfo"}).encode("utf-8"))
                    connSock.close()
                    return None

                d = {"type": "StateRequestSuccess"}
                d["gameState"] = {}
                d["gameState"]["playerId"] = id
                d["gameState"]["attackEvents"] = []

                cur.execute("SELECT * FROM Attacks;")
                data = cur.fetchall()
                for dat in data:
                    if dat[1] > time.time():
                        d["gameState"]["attackEvents"].append(dict(js.loads(dat[2])))

                cur.execute("SELECT resources FROM Players WHERE id={};".format(id))
                d["gameState"]["resources"] = cur.fetchall()[0][0]
                d["gameState"]["researchInfo"] = {}
                cur.execute("SELECT levelT FROM Players WHERE id={};".format(id))
                d["gameState"]["researchInfo"]["turretDamageLevel"] = cur.fetchall()[0][0]
                cur.execute("SELECT levelP FROM Players WHERE id={};".format(id))
                d["gameState"]["researchInfo"]["unitDamageLevel"] = cur.fetchall()[0][0]
                cur.execute("SELECT levelG FROM Players WHERE id={};".format(id))
                d["gameState"]["researchInfo"]["generatorEfficiencyLevel"] = cur.fetchall()[0][0]
                d["gameState"]["time"] = time.time()

                d["gameState"]["players"] = []
                cur.execute("SELECT id, name, r, g, b, levelT, levelG, levelP FROM Players;")
                players = cur.fetchall()
                for player in players:
                    d["gameState"]["players"].append({})
                    d["gameState"]["players"][-1]["researchInfo"] = {}
                    d["gameState"]["players"][-1]["researchInfo"]["turretDamageLevel"] = player[5]
                    d["gameState"]["players"][-1]["researchInfo"]["unitDamageLevel"] = player[7]
                    d["gameState"]["players"][-1]["researchInfo"]["generatorEfficiencyLevel"] = player[6]
                    d["gameState"]["players"][-1]["playerId"] = player[0]
                    d["gameState"]["players"][-1]["name"] = player[1]
                    d["gameState"]["players"][-1]["color"] = {}
                    d["gameState"]["players"][-1]["color"]["r"] = player[2]
                    d["gameState"]["players"][-1]["color"]["g"] = player[3]
                    d["gameState"]["players"][-1]["color"]["b"] = player[4]
                    d["gameState"]["players"][-1]["sectors"] = []
                    cur.execute("SELECT id, x, y, isBlocked FROM Sectors WHERE idPlayer={};".format(player[0]))
                    sectors = cur.fetchall()
                    for sector in sectors:
                        d["gameState"]["players"][-1]["sectors"].append({})
                        d["gameState"]["players"][-1]["sectors"][-1]["x"] = sector[1]
                        d["gameState"]["players"][-1]["sectors"][-1]["y"] = sector[2]
                        d["gameState"]["players"][-1]["sectors"][-1]["sectorId"] = sector[0]
                        d["gameState"]["players"][-1]["sectors"][-1]["isBlocked"] = bool(sector[3])
                        d["gameState"]["players"][-1]["sectors"][-1]["buildings"] = []
                        cur.execute("SELECT id, x, y, type, Data FROM Buildings WHERE idSector={};".format(sector[0]))
                        buildings = cur.fetchall()
                        for build in buildings:
                            d["gameState"]["players"][-1]["sectors"][-1]["buildings"].append({})
                            d["gameState"]["players"][-1]["sectors"][-1]["buildings"][-1]["type"] = build[3]
                            d["gameState"]["players"][-1]["sectors"][-1]["buildings"][-1]["x"] = build[1]
                            d["gameState"]["players"][-1]["sectors"][-1]["buildings"][-1]["y"] = build[2]
                            d["gameState"]["players"][-1]["sectors"][-1]["buildings"][-1]["id"] = build[0]
                            d["gameState"]["players"][-1]["sectors"][-1]["buildings"][-1]["playerId"] = player[0]
                            d["gameState"]["players"][-1]["sectors"][-1]["buildings"][-1]["sectorId"] = sector[0]
                            if build[3] == 'Hangar':
                                d["gameState"]["players"][-1]["sectors"][-1]["buildings"][-1]["units"] = {}
                                d["gameState"]["players"][-1]["sectors"][-1]["buildings"][-1]["units"]["units"] = []
                                cur.execute("SELECT id FROM Units WHERE hangarId={};".format(build[0]))
                                d["gameState"]["players"][-1]["sectors"][-1]["buildings"][-1]["units"]["health"] = 50 * len(cur.fetchall())
                                cur.execute("SELECT id, hangarSlot FROM Units WHERE hangarId={};".format(build[0]))
                                units = cur.fetchall()
                                for unit in units:
                                    d["gameState"]["players"][-1]["sectors"][-1]["buildings"][-1]["units"]["units"].append({})
                                    d["gameState"]["players"][-1]["sectors"][-1]["buildings"][-1]["units"]["units"][-1]["type"] = "Bomber"
                                    d["gameState"]["players"][-1]["sectors"][-1]["buildings"][-1]["units"]["units"][-1]["id"] = unit[0]
                                    d["gameState"]["players"][-1]["sectors"][-1]["buildings"][-1]["units"]["units"][-1]["hangarId"] = build[0]
                                    d["gameState"]["players"][-1]["sectors"][-1]["buildings"][-1]["units"]["units"][-1]["hangarSlot"] = unit[1]

                connSock.sendall(js.dumps(d).encode("utf-8"))
                connSock.close()
                return None

    except Exception as exc:
        print(exc)
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno))
    connSock.sendall(js.dumps({"type": "MalformedJson"}).encode("utf-8"))
    connSock.close()
    return None
