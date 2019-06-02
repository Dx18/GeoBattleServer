import json as js
from contextlib import closing
import sys
import time
from state import state as stateEvent


def updater(db, connSock, jsData):
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

                cur.execute("SELECT json FROM Updater WHERE timeT>{}".format(time.time() - 10))
                text = cur.fetchall()

                if jsData["lastUpdateTime"] + 10 <= time.time():
                    stateEvent(db, connSock, jsData)
                    return None

                d = {"type": "UpdateRequestSuccess"}
                cur.execute("SELECT resources FROM Players WHERE id={};".format(id))
                d["resources"] = cur.fetchall()[0][0]
                d["playerId"] = id
                d["time"] = time.time()
                d["researchInfo"] = {}
                cur.execute("SELECT levelT FROM Players WHERE id={};".format(id))
                d["researchInfo"]["turretDamageLevel"] = cur.fetchall()[0][0]
                cur.execute("SELECT levelP FROM Players WHERE id={};".format(id))
                d["researchInfo"]["unitDamageLevel"] = cur.fetchall()[0][0]
                cur.execute("SELECT levelG FROM Players WHERE id={};".format(id))
                d["researchInfo"]["generatorEfficiencyLevel"] = cur.fetchall()[0][0]
                d["updates"] = []
                for tex in text:
                    dt = dict(js.loads(tex[0]))
                    d["updates"].append(dt)

                connSock.sendall(js.dumps(d).encode("utf-8"))
                connSock.close()
                return None

    except Exception as exc:
        print(exc)
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno))
    connSock.sendall(js.dumps({"type": "MalformedJson"}).encode("utf-8"))
    connSock.close()
    return None
