import smtplib
import sys
import time
import json as js
from contextlib import closing


def rectangle_contains(x1, y1, width1, height1, x2, y2, width2, height2):
    return x2 >= x1 and x2 + width2 <= x1 + width1 and y2 >= y1 and y2 + height2 <= y1 + height1


def rectangles_intersect(x1, y1, width1, height1, x2, y2, width2, height2):
    return x1 + width1 > x2 and x2 + width2 > x1 and y1 + height1 > y2 and y2 + height2 > y1


def sendEmail(addr, code):
    try:
        txtparam = str(code)
        fromaddr = 'Mr. Robot - GeoBattle <geobattleit@gmail.com>'
        toaddr = 'Administrator <{}>'.format(addr)
        subj = 'Authorization code'
        msg_txt = 'Enter this authorization code in the application:\n\n ' + txtparam + \
            '\n\nIf you do not know what this letter is about, delete it. Do not give the activation code to anyone.\nBye!'
        msg = "From: %s\nTo: %s\nSubject: %s\n\n%s" % (fromaddr, toaddr, subj, msg_txt)
        username = 'geobattleit'
        password = 'Vlad400125'
        server = smtplib.SMTP('smtp.gmail.com:587')
        server.starttls()
        server.login(username, password)
        server.sendmail(fromaddr, toaddr, msg)
        server.quit()
    except Exception as exc:
        print(exc)


def applyChanges(db):
    try:
        with closing(db.getConn()) as dbConn:
            with dbConn.cursor() as cur:

                cur.execute("SELECT * FROM Attacks;")
                data = cur.fetchall()
                for dat in data:
                    if dat[1] > time.time():
                        continue
                    else:
                        need = dict(js.loads(dat[3]))

                        for idHan in need["hangarId"]:
                            cur.execute("SELECT idSector FROM Buildings WHERE id={};".format(idHan))
                            isb = cur.fetchall()[0][0]
                            cur.execute("UPDATE Sectors SET isBlocked = 0 WHERE id = {};".format(isb))

                        try:
                            for aIdH in need["aaa"].keys():
                                cur.execute("SELECT id, hangarSlot FROM Units WHERE hangarId={} ORDER BY hangarSlot ASC;".format(aIdH))
                                ad = cur.fetchall()
                                for pc in range(need["aaa"][aIdH]):
                                    cur.execute("DELETE FROM Units WHERE id={};".format(ad[pc][0]))
                        except Exception as exc:
                            print("Say Vlad, chto on chto-to pereputal")

                        if len(need["sectorDid"]) == 0:
                            cur.execute("UPDATE Sectors SET isBlocked = 0 WHERE id = {};".format(need["sectorId"]))
                        else:
                            idSectorDid = need["sectorId"]
                            cur.execute("SELECT id FROM Buildings WHERE idSector={};".format(idSectorDid))
                            aboutBuildings = cur.fetchall()
                            for b in aboutBuildings:
                                cur.execute("DELETE FROM Units WHERE hangarId={};".format(b[0]))
                                cur.execute("DELETE FROM Buildings WHERE id={};".format(b[0]))
                            cur.execute("DELETE FROM Sectors WHERE id={};".format(idSectorDid))

                        if len(need["hangarDid"]) != 0:
                            for n in need["hangarDid"]:
                                cur.execute("DELETE FROM Units WHERE hangarId={};".format(n))

                        cur.execute("DELETE FROM Attacks WHERE id={};".format(dat[0]))

    except Exception as exc:
        print(exc)
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno))
    return None
