import json
import socket

from flask import Flask, request, make_response, abort
import requests

application = Flask(__name__, static_url_path='/static')

RECV_BUF = 2048


@application.route('/', methods=['GET'])
def homepage():
    return "<h1>HTTP User Server</h1>"


@application.route('/fibonacci', methods=['GET'])
def fibonacci():
    args = request.args
    hostname = None
    fs_port = None
    number = None
    as_ip = None
    as_port = None
    try:
        hostname = args["hostname"]
        fs_port = int(args["fs_port"])
        number = int(args["number"])
        as_ip = args["as_ip"]
        as_port = int(args["as_port"])
    except Exception:
        abort(400, "Invalid request params")

    # STEP 1: query AS to get the IP address of the FS
    as_addr = (as_ip, as_port)
    dns_query_data = {
        "TYPE": "A",
        "NAME": hostname,
    }
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(json.dumps(dns_query_data).encode(), as_addr)
    as_msg, _ = sock.recvfrom(RECV_BUF)
    as_response = json.loads(as_msg.decode())

    fs_ip = as_response.get("VALUE")
    time_to_live = int(as_response.get("TTL"))

    # STEP 2: query FS to get the calculation result
    fs_http_url = "http://" + fs_ip + ":" + str(fs_port) + "/fibonacci"
    result = requests.get(fs_http_url, params={"number": number}).text
    response = make_response(result, 200)
    response.mimetype = "text/plain"
    return response


# run the app.
if __name__ == "__main__":
    application.run(port=8080)
