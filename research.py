import json as js
from contextlib import closing
import sys


def research(db, connSock, jsData):
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
                    connSock.sendall(
                        js.dumps({"type": "WrongAuthInfo"}).encode("utf-8"))
                    connSock.close()
                    return None

                cur.execute("SELECT resources FROM Players WHERE id={};".format(id))
                res = cur.fetchall()[0][0]
                type = jsData["researchType"]

                if type == "TurretDamage":
                    cur.execute("SELECT levelT FROM Players WHERE id={};".format(id))
                    level = cur.fetchall()[0][0]
                    if level >= 5:
                        connSock.sendall(js.dumps({'type': 'MaxLevel'}).encode("utf-8"))
                        connSock.close()
                        return None
                    cash = 1000 * (2**level)
                    if cash > res:
                        connSock.sendall(js.dumps({'type': 'NotEnoughResources', 'required': cash}).encode("utf-8"))
                        connSock.close()
                        return None

                    cur.execute("UPDATE Players SET resources = {} WHERE id = {};".format(res - cash, id))
                    cur.execute("UPDATE Players SET levelT = {} WHERE id = {};".format(level + 1, id))

                    d = {"type": "Researched"}
                    d["researchType"] = type
                    d["cost"] = cash
                    d["level"] = level + 1

                    connSock.sendall(js.dumps(d).encode("utf-8"))
                    connSock.close()
                    return None
                elif type == "UnitDamage":
                    cur.execute("SELECT levelP FROM Players WHERE id={};".format(id))
                    level = cur.fetchall()[0][0]
                    if level >= 5:
                        connSock.sendall(js.dumps({'type': 'MaxLevel'}).encode("utf-8"))
                        connSock.close()
                        return None
                    cash = 1000 * (2**level)
                    if cash > res:
                        connSock.sendall(js.dumps({'type': 'NotEnoughResources', 'required': cash}).encode("utf-8"))
                        connSock.close()
                        return None

                    cur.execute("UPDATE Players SET resources = {} WHERE id = {};".format(res - cash, id))
                    cur.execute("UPDATE Players SET levelP = {} WHERE id = {};".format(level + 1, id))

                    d = {"type": "Researched"}
                    d["researchType"] = type
                    d["cost"] = cash
                    d["level"] = level + 1

                    connSock.sendall(js.dumps(d).encode("utf-8"))
                    connSock.close()
                    return None
                elif type == "GeneratorEfficiency":
                    cur.execute("SELECT levelG FROM Players WHERE id={};".format(id))
                    level = cur.fetchall()[0][0]
                    if level >= 5:
                        connSock.sendall(js.dumps({'type': 'MaxLevel'}).encode("utf-8"))
                        connSock.close()
                        return None
                    cash = 1000 * (2**level)
                    if cash > res:
                        connSock.sendall(js.dumps({'type': 'NotEnoughResources', 'required': cash}).encode("utf-8"))
                        connSock.close()
                        return None

                    cur.execute("UPDATE Players SET resources = {} WHERE id = {};".format(res - cash, id))
                    cur.execute("UPDATE Players SET levelG = {} WHERE id = {};".format(level + 1, id))

                    d = {"type": "Researched"}
                    d["researchType"] = type
                    d["cost"] = cash
                    d["level"] = level + 1

                    connSock.sendall(js.dumps(d).encode("utf-8"))
                    connSock.close()
                    return None

    except Exception as exc:
        print(exc)
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno))
    connSock.sendall(js.dumps({"type": "MalformedJson"}).encode("utf-8"))
    connSock.close()
    return None
