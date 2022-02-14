from flask import Flask, request, make_response, abort
import requests

application = Flask(__name__, static_url_path='/static')


def parse_args(args):
    hostname = args.get('hostname')
    fs_port = args.get('fs_port')
    number = args.get('number')
    as_ip = args.get('as_ip')
    as_port = args.get('as_port')
    return hostname, fs_port, number, as_ip, as_port


@application.route('/', methods=['GET'])
def homepage():
    return "<h1>HTTP User Server</h1>"


@application.route('/fibonacci', methods=['GET'])
def fibonacci():
    number = request.args.get('number')
    result = requests.get("http://127.0.0.1:9090/fibonacci", params={"number": number}).text
    response = make_response(result, 200)
    response.mimetype = "text/plain"
    return response


# run the app.
if __name__ == "__main__":
    application.run(port=8080)
