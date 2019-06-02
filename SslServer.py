import param_parser
import sys
import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

params = param_parser.parse_params(sys.argv[1:])

ip = params["-i"] if "-i" in params.keys() else "78.47.182.60"
port = int(params["-p"]) if "-p" in params.keys() else 11999

print(ip, port)
sock.bind((ip, port))
sock.listen(999)

while True:
    try:
        while True:
            conn, addr = sock.accept()
            conn.settimeout(1)
            data_res = ''
            while True:
                data1 = conn.recv(1024)

                if not data1.endswith('#'.encode('utf-8')):
                    data_res += data1.decode('utf-8')
                else:
                    data_res += data1.decode('utf-8')[0:-1:1]
                    break

            with open("cert.pem", "rb") as file:
                conn.sendall(file.read())
            conn.close()
            continue
    except Exception as exc:
        print(exc)
    continue
