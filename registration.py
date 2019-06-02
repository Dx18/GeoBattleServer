import random as rand
import json as js
import sys
from functions import sendEmail
from threading import Thread
import hashlib
from contextlib import closing
import time
from math import trunc


def hash(s):
    sha = hashlib.sha256(s.encode("utf-8"))
    return sha.hexdigest()


def registration(db, connSock, jsData):

    try:
        with closing(db.getConn()) as dbConn:
            with dbConn.cursor() as cur:
                name = jsData['name']
                password = jsData['password']
                token = "".join([chr(rand.randint(65, 90)) for x in range(12)])
                email = jsData['email']
                r = jsData['color']['r']
                g = jsData['color']['g']
                b = jsData['color']['b']
                resources = 200
                levelT = 0
                levelG = 0
                levelP = 0
                code = rand.randint(1000, 9999)

                if (len(name) >= 15) or (len(name) <= 3):
                    d = {"type": 'InvalidNameLength', "min": 4, "max": 14}
                    d["actual"] = len(name)
                    connSock.sendall(js.dumps(d).encode("utf-8"))
                    connSock.close()
                    return None

                if (len(password) >= 20) or (len(password) <= 3):
                    d = {"type": 'InvalidPasswordLength', "min": 4, "max": 19}
                    d["actual"] = len(password)
                    connSock.sendall(js.dumps(d).encode("utf-8"))
                    connSock.close()
                    return None

                cur.execute("SELECT id, name, email FROM Players")

                for player in cur.fetchall():
                    if player[1] == name:
                        connSock.sendall(
                            js.dumps({'type': 'NameExists'}).encode("utf-8"))
                        connSock.close()
                        return None
                    if player[2] == email:
                        connSock.sendall(
                            js.dumps({'type': 'EmailExists'}).encode("utf-8"))
                        connSock.close()
                        return None

                t1 = Thread(target=sendEmail, args=(email, str(code),))
                t1.start()

                cur.execute("INSERT INTO Players (name, password, token, email, r, g, b, resources, levelT, levelG, levelP, activated, tries) VALUES ('{}', '{}', '{}', '{}', {}, {}, {}, {}, {}, {}, {}, {}, 5);".format(
                    name, str(hash(password)), token, email, r, g, b, resources, levelT, levelG, levelP, code))

                connSock.sendall(
                    js.dumps(
                        {"type": "Success", "name": name}).encode("utf-8"))
                connSock.close()
                return None
    except Exception as exc:
        print(exc)
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno))
    connSock.sendall(js.dumps({"type": "MalformedJson"}).encode("utf-8"))
    connSock.close()
    return None


def authorization(db, connSock, jsData):

    try:
        with closing(db.getConn()) as dbConn:
            with dbConn.cursor() as cur:

                cur.execute(
                    "SELECT id, name, password, token, activated FROM Players")
                data = cur.fetchall()
                token = "".join([chr(rand.randint(65, 90)) for x in range(12)])
                for i in range(len(data)):
                    if data[i][1] == jsData['name'] and data[i][2] == str(hash(jsData['password'])) and data[i][4] == -1:
                        cur.execute(
                            "UPDATE Players SET token = '{}' WHERE id = {};".format(token, data[i][0]))
                        d = {"type": "Success", "authInfo": {}}
                        d["authInfo"]['id'] = i
                        d["authInfo"]['token'] = token
                        connSock.sendall(js.dumps(d).encode("utf-8"))
                        connSock.close()
                        return None
                connSock.sendall(
                    js.dumps({"type": "PairNotFound"}).encode("utf-8"))
                connSock.close()
                return None
    except Exception as exc:
        print(exc)
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno))
    connSock.sendall(js.dumps({"type": "MalformedJson"}).encode("utf-8"))
    connSock.close()
    return None


def emailConfirmationEvent(db, connSock, jsData):

    try:
        with closing(db.getConn()) as dbConn:
            with dbConn.cursor() as cur:

                name = jsData["name"]
                code = jsData["code"]

                cur.execute(
                    "SELECT id, activated, tries FROM Players WHERE name='{}';".format(name))
                data = cur.fetchall()

                i = data[0][1]
                t = data[0][2]

                if i == -1:
                    connSock.sendall(
                        js.dumps({"type": "DoesNotExist"}).encode("utf-8"))
                    connSock.close()
                    return None
                if i != code:
                    cur.execute(
                        "UPDATE Players SET tries = {} WHERE name = '{}';".format(t - 1, name))
                    connSock.sendall(
                        js.dumps({"type": "WrongCode", "triesLeft": t - 1}).encode("utf-8"))
                    connSock.close()
                    return None

                id = data[0][0]
                token = "".join([chr(rand.randint(65, 90)) for x in range(12)])
                cur.execute(
                    "UPDATE Players SET token = '{}' WHERE id = {};".format(token, id))
                cur.execute(
                    "UPDATE Players SET activated = -1 WHERE id = {};".format(id))

                d = {"type": "EmailConfirmed", "authInfo": {}}
                d["authInfo"]['id'] = id
                d["authInfo"]['token'] = token

                dd = {"type": "PlayerAdded"}
                playerId = d["authInfo"]["id"]
                dd["playerId"] = playerId
                cur.execute("SELECT name, r, g, b FROM Players WHERE id={};".format(playerId))
                dataAbout = cur.fetchall()[0]
                dd["name"] = dataAbout[0]
                dd["color"] = {"r": dataAbout[1], "g": dataAbout[2], "b": dataAbout[3]}
                cur.execute("INSERT INTO Updater (timeT, json) VALUES ({}, '{}')".format(trunc(time.time()), js.dumps(dd)))

                connSock.sendall(js.dumps(d).encode("utf-8"))
                connSock.close()
                return None
    except Exception as exc:
        print(exc)
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno))
    connSock.sendall(js.dumps({"type": "MalformedJson"}).encode("utf-8"))
    connSock.close()
    return None


def resendEmailEvent(db, connSock, jsData):

    try:

        with closing(db.getConn()) as dbConn:
            with dbConn.cursor() as cur:
                name = jsData["name"]
                cur.execute("SELECT email, activated FROM Players WHERE name='{}';".format(name))
                data = cur.fetchall()
                i = data[0][1]
                if i == -1:
                    connSock.sendall(js.dumps({"type": "DoesNotExist"}).encode("utf-8"))
                    connSock.close()
                    return None

                code = i
                email = data[0][0]
                t1 = Thread(target=sendEmail, args=(email, str(code),))
                t1.start()

                d = {"type": "EmailResent"}
                connSock.sendall(js.dumps(d).encode("utf-8"))
                connSock.close()
                return None

    except Exception as exc:
        print(exc)
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno))
    connSock.sendall(js.dumps({"type": "DoesNotExist"}).encode("utf-8"))
    connSock.close()
    return None
