import json

from flask import Flask, request, make_response, abort
import socket
import requests

application = Flask(__name__, static_url_path='/static')

DEFAULT_DNS_TTL = 10
RECV_BUF = 2048


def parse_fibonacci_arg(args):
    try:
        return int(args.get('number'))
    except TypeError:
        abort(400, 'no arg named \"number\"')
    except ValueError:
        abort(400, '\"number\" is not an int')


def parse_register_data(register_data):
    hostname = register_data["hostname"]
    ip = register_data["ip"]
    as_ip = register_data["as_ip"]
    as_port = int(register_data["as_port"])
    register_data["as_port"] = as_port


@application.route('/', methods=['GET'])
def homepage():
    return "<h1>HTTP Fibonacci Server</h1>"


@application.route('/fibonacci', methods=['GET'])
def fibonacci():
    number = parse_fibonacci_arg(request.args)
    a, b = 0, 1
    for _ in range(number):
        a, b = b, a + b
    response = make_response(str(a), 200)
    response.mimetype = "text/plain"
    return response


@application.route('/register', methods=['PUT'])
def register():
    register_data = request.get_json()

    try:
        parse_register_data(register_data)
    except Exception:
        abort(400)

    # register in the Authoritative Server via UDP over port 53533
    as_addr = (register_data.get("as_ip"), register_data.get("as_port"))
    fs_ip = requests.get('https://api.ipify.org').content.decode('utf8')
    dns_data = {
        "TYPE": "A",
        "NAME": register_data.get("hostname"),
        # TODO: replace actual export ip
        "VALUE": "127.0.0.1",
        "TTL": DEFAULT_DNS_TTL
    }
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(json.dumps(dns_data).encode(), as_addr)
    as_response, _ = sock.recvfrom(RECV_BUF)

    response = make_response(json.loads(as_response.decode()), 201)
    response.mimetype = "text/plain"
    return response


# run the app.
if __name__ == "__main__":
    application.run(port=9090)
