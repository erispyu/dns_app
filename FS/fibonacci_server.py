from flask import Flask, request, make_response, abort

application = Flask(__name__, static_url_path='/static')


def parse_request_arg(args):
    try:
        return int(args.get('number'))
    except TypeError:
        abort(400, 'no arg named \"number\"')
    except ValueError:
        abort(400, '\"number\" is not an int')


@application.route('/', methods=['GET'])
def homepage():
    return "<h1>HTTP Fibonacci Server</h1>"


@application.route('/fibonacci', methods=['GET'])
def fibonacci():
    x = parse_request_arg(request.args)
    a, b = 0, 1
    for _ in range(x):
        a, b = b, a + b
    response = make_response(str(a), 200)
    response.mimetype = "text/plain"
    return response


# run the app.
if __name__ == "__main__":
    application.run(port=9090)
