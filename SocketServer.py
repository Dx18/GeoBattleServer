import ssl
import sys
import param_parser
import dbClass
import socket
import time
import dbNew
import json as js
from threading import Thread
import registration
import getpass
import sectorBuild
import build
import unitBuild
import getRating
from functions import applyChanges
import research
import state
import update
from atack import atack
import vsp
import updater


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
params = param_parser.parse_params(sys.argv[1:])
if "-i" in params.keys():
    ip = params["-i"]
else:
    ip = '78.47.182.60'
if "-p" in params.keys() and params["-p"].isdigit():
    port = int(params["-p"])
else:
    port = 12000
if "-s" in params.keys():
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
    context.load_cert_chain(certfile="cert.pem", keyfile="key.pem")
    m = True
else:
    m = False
print("Server uses postgresql!")
dbName = str(input("Enter database name: "))
dbUser = str(input("Enter database user: "))
password = str(getpass.getpass("Enter password user: "))
host = "localhost"
db = dbClass.dbParam(dbName, dbUser, password, host)
if "-c" in params.keys():
    dbNew.newDb(db)

thread = Thread(target=vsp.streamUpdate,
                        args=(db, ))
thread.start()

thread = Thread(target=vsp.apply,
                        args=(db, ))
thread.start()


print("Server start on ip={} and port={}".format(ip, port))
sock.bind((ip, port))
sock.listen(999)
sock.settimeout(1)

while True:
    try:
        while True:
            connSock, addr = sock.accept()
            connSock.settimeout(2)

            if m:
                connSock = context.wrap_socket(connSock, True, False)

            data_res = ''
            while True:
                data1 = connSock.recv(1024)
                if not data1.endswith('#'.encode('utf-8')):
                    data_res += data1.decode('utf-8')
                else:
                    data_res += data1.decode('utf-8')[0:-1:1]
                    break

            jsData = dict(js.loads(data_res))

            if jsData['type'] == 'RegistrationEvent':
                thread = Thread(target=registration.registration,
                                args=(db, connSock, jsData, ))
                thread.start()
            elif jsData['type'] == 'AuthorizationEvent':
                thread = Thread(target=registration.authorization,
                                args=(db, connSock, jsData, ))
                thread.start()
            elif jsData['type'] == 'EmailConfirmationEvent':
                thread = Thread(target=registration.emailConfirmationEvent,
                                args=(db, connSock, jsData, ))
                thread.start()
            elif jsData['type'] == 'ResendEmailEvent':
                thread = Thread(target=registration.resendEmailEvent,
                                args=(db, connSock, jsData, ))
                thread.start()
            elif jsData['type'] == 'SectorBuildEvent':
                thread = Thread(target=sectorBuild.sectorBuild,
                                args=(db, connSock, jsData, ))
                thread.start()
            elif jsData['type'] == 'BuildEvent':
                thread = Thread(target=build.build,
                                args=(db, connSock, jsData, ))
                thread.start()
            elif jsData['type'] == 'DestroyEvent':
                thread = Thread(target=build.destroy,
                                args=(db, connSock, jsData, ))
                thread.start()
            elif jsData['type'] == 'UnitBuildEvent':
                thread = Thread(target=unitBuild.addUnit,
                                args=(db, connSock, jsData, ))
                thread.start()
            elif jsData['type'] == 'RatingRequestEvent':
                thread = Thread(target=getRating.getRating,
                                args=(db, connSock, jsData, ))
                thread.start()
            elif jsData['type'] == 'ResearchEvent':
                thread = Thread(target=research.research,
                                args=(db, connSock, jsData, ))
                thread.start()
            elif jsData['type'] == 'StateRequestEvent':
                thread = Thread(target=state.state,
                                args=(db, connSock, jsData, ))
                thread.start()
            elif jsData['type'] == 'UpdateRequestEvent':
                thread = Thread(target=updater.updater,
                                args=(db, connSock, jsData, ))
                thread.start()
            elif jsData['type'] == 'AttackEvent':
                thread = Thread(target=atack,
                                args=(db, connSock, jsData, ))
                thread.start()
            else:
                connSock.close()

            continue

    except Exception as exc:
        pass

    continue
