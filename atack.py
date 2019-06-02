import json as js
from contextlib import closing
import sys
from Fighting import fighting, HangarInfo, SectorInfo
import time
from math import trunc


def atack(db, connSock, jsData):
    try:
        with closing(db.getConn()) as dbConn:
            with dbConn.cursor() as cur:

                id = jsData["authInfo"]["id"]
                token = jsData["authInfo"]["token"]
                vId = jsData["victimId"]
                vSector = jsData["sectorId"]
                idHangars = jsData["hangarIds"]

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

                cur.execute("SELECT x, y, isBlocked FROM Sectors WHERE id={};".format(vSector))
                sector = cur.fetchall()[0]
                if sector[2] == 1:
                    connSock.sendall(js.dumps({"type": "NotAttackable"}).encode("utf-8"))
                    connSock.close()
                    return None

                cur.execute("SELECT id FROM Sectors WHERE idPlayer={} AND isBlocked=0;".format(vId))
                if len(cur.fetchall()) <= 1:
                    connSock.sendall(js.dumps({"type": "NotAttackable"}).encode("utf-8"))
                    connSock.close()
                    return None

                try:
                    myRules = cur.execute("SELECT myRuleJson FROM Attacks;").fetchall()
                    for rule in myRules:
                        if len(list(set(dict(js.loads(rule[0]))["hangarId"]) & set(idHangars))) != 0:
                            connSock.sendall(js.dumps({"type": "HangarsAlreadyUsed"}).encode("utf-8"))
                            connSock.close()
                            return None
                except Exception as exc:
                    pass

                # DO ATTACK!!!!!!
                hangars = {}
                for i in idHangars:
                    cur.execute("SELECT x, y FROM Buildings WHERE id={};".format(i))
                    data = cur.fetchall()[0]
                    x = data[0]
                    y = data[1]
                    cur.execute("SELECT id FROM Units WHERE hangarId={};".format(i))
                    n = len(cur.fetchall())
                    hangars[i] = HangarInfo(x, y, n)

                cur.execute("SELECT id FROM Buildings WHERE type='Turret' AND idSector={};".format(vSector))
                t = len(cur.fetchall())
                vSectorHealth = 100
                cur.execute("SELECT type FROM Buildings WHERE idSector={};".format(vSector))
                data = cur.fetchall()
                for dat in data:
                    type = dat[0]
                    if type == 'Mine':
                        h = 200
                    elif type == 'Generator':
                        h = 200
                    elif type == 'Hangar':
                        h = 300
                    elif type == 'ResearchCenter':
                        h = 100
                    elif type == 'Turret':
                        h = 150
                    else:
                        h = 100

                    vSectorHealth += h

                energy = 10
                cur.execute("SELECT type FROM Buildings WHERE idSector={};".format(vSector))
                data = cur.fetchall()
                for i in data:
                    if i[0] == 'Generator':
                        cur.execute("SELECT levelG FROM Players WHERE id={};".format(vId))
                        energy += 30 + cur.fetchall()[0][0]
                    elif i[0] == 'Mine':
                        energy -= 5
                    elif i[0] == 'Hangar':
                        energy -= 10
                    elif i[0] == 'Turret':
                        energy -= 6
                    else:
                        energy -= 4
                if energy < 0:
                    t = 0

                sectorInfo = SectorInfo(vSector, sector[0] + 20, sector[1] + 20, t, vSectorHealth)

                fightingResult = str(fighting(id, vId, hangars, sectorInfo, time.time() + 5, db)).replace("'", '"')
                d = dict(js.loads(str(fightingResult)))
                sh = d["timePoints"][-1]["sectorHealth"]
                dah = d["timePoints"][0]["planeGroupsHealth"]
                ah = d["timePoints"][-1]["planeGroupsHealth"]
                timeStop = trunc(d["timePoints"][-1]["time"] + 1)

                myRules = {}
                myRules["aaa"] = {}

                for do in dah:
                    for posle in ah:
                        if do["hangarId"] == posle["hangarId"]:
                            myRules["aaa"][do["hangarId"]] = trunc((do["health"] - posle["health"]) / 50)

                myRules["sectorId"] = vSector
                myRules["hangarId"] = idHangars
                myRules["hangarDid"] = []
                for dd in ah:
                    if dd["health"] <= 0:
                        myRules["hangarDid"].append(dd["hangarId"])

                myRules["sectorDid"] = []
                if sh <= 0:
                    myRules["sectorDid"].append(vSector)

                cur.execute("INSERT INTO Attacks (timeStop, json, myRuleJson) VALUES ({}, '{}', '{}') RETURNING id;".format(
                    timeStop, fightingResult, js.dumps(myRules)))
                idMyAttack = cur.fetchall()[0][0]
                d["id"] = idMyAttack
                cur.execute(
                    "UPDATE Attacks SET json='{}' WHERE id = {};".format(js.dumps(d), idMyAttack))


                cur.execute("UPDATE Sectors SET isBlocked = 1 WHERE id = {};".format(vSector))

                for idHan in idHangars:
                    isb = cur.execute("SELECT idSector FROM Buildings WHERE id={};".format(idHan))
                    isb = cur.fetchall()[0][0]
                    cur.execute("UPDATE Sectors SET isBlocked = 1 WHERE id = {};".format(isb))

                d = {"type": "AttackStarted", "attackScript": d}
                cur.execute("INSERT INTO Updater (timeT, json) VALUES ({}, '{}');".format(
                    trunc(d["attackScript"]["timePoints"][-1]["time"]), js.dumps(d)))
                connSock.sendall(js.dumps(d).encode("utf-8"))
                connSock.close()
                return None

    except Exception as exc:
        print(exc)
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno))
    connSock.sendall(js.dumps({"type": "MalformedJson"}).encode("utf-8"))
    connSock.close()
    return None
