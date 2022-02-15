import os.path
import time
import json
from socket import socket, AF_INET, SOCK_DGRAM

AS_IP = "127.0.0.1"
AS_PORT = 53533
RECV_BUF = 2048
DB_PATH = "./db.json"


def query_in_db(hostname):
    ip = None
    with open(DB_PATH, 'r') as f:
        db = json.loads(f.read())
        record = db.get(hostname)
        if record is not None:
            expire_time = record.get("expire_time")
            if time.time() < expire_time:
                ip = record.get("ip")
    return ip


def register_in_db(data):
    db = {}
    if os.path.exists(DB_PATH):
        with open(DB_PATH, 'r') as f:
            db = json.loads(f.read())
    db[data["NAME"]] = {
        "ip": data.get("VALUE"),
        "expire_time": time.time() + data.get("TTL")
    }
    with open(DB_PATH, 'w') as f:
        f.write(json.dumps(db))


def handle_request(request_msg):
    request_data = json.loads(request_msg.decode())
    if request_data.get("VALUE") is None:
        return query(request_data)
    else:
        return register(request_data)


def register(register_data):
    addr_type = register_data.get("TYPE")
    hostname = register_data.get("NAME")
    ip_addr = register_data.get("VALUE")
    time_to_live = register_data.get("TTL")

    response_data = {
        "TYPE": addr_type,
        "NAME": hostname,
        "VALUE": ip_addr,
        "TTL": time_to_live
    }

    register_in_db(response_data)

    return response_data


def query(query_data):
    addr_type = query_data.get("TYPE")
    hostname = query_data.get("NAME")

    ip_addr = query_in_db(hostname)

    # TODO: Search for local record
    expire_time = time.time()
    query_result = {
        "TYPE": addr_type,
        "NAME": hostname,
        "VALUE": ip_addr,
        "TTL": int(expire_time - time.time())
    }
    return query_result


def run(ip, port):
    sock = socket(AF_INET, SOCK_DGRAM)
    sock.bind((ip, port))
    while True:
        request_msg, client_addr = sock.recvfrom(RECV_BUF)
        response_data = handle_request(request_msg)
        response_msg = json.dumps(response_data).encode()
        sock.sendto(response_msg, client_addr)


if __name__ == '__main__':
    run(AS_IP, AS_PORT)
