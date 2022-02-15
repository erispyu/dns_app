import time
import json
from socket import socket, AF_INET, SOCK_DGRAM

AS_IP = "127.0.0.1"
AS_PORT = 53533
RECV_BUF = 2048


def handle_request(request_msg):
    request_data = json.loads(request_msg.decode())
    if request_data.get("VALUE") is None:
        return handle_query(request_data)
    else:
        return handle_register(request_data)


def handle_register(register_data):
    addr_type = register_data.get("TYPE")
    hostname = register_data.get("NAME")
    ip_addr = register_data.get("VALUE")
    time_to_live = register_data.get("TTL")
    expire_time = time.time() + int(time_to_live)

    # TODO: record the register info into file

    response_data = {
        "TYPE": addr_type,
        "NAME": hostname,
        "VALUE": ip_addr,
        "TTL": int(expire_time - time.time())
    }
    return response_data


def handle_query(query_data):
    addr_type = query_data.get("TYPE")
    hostname = query_data.get("NAME")
    # TODO: Search for local record
    ip_addr = "0.0.0.0"
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
