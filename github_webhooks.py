from flask import Flask, abort, request, json
import hmac
import os
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_NAME = 'BMSTU'
key = os.environ[PROJECT_NAME]
command = os.path.join(BASE_DIR, 'script.sh')

app = Flask(__name__)


def sig_blob(body):
    return 'sha1={}'.format(hmac.new(key.encode(), body, digestmod='sha1')
                            .hexdigest())


@app.route('/', methods=['post'])
def main():
    try:
        received_sig = request.headers.get('x-hub-signature')
    except KeyError:
        return abort(404)

    computed_sig = sig_blob(request.data)

    if received_sig != computed_sig:
        return abort(404)

    ref = json.loads(request.data).get('ref')
    if ref and 'master' not in ref:
        return abort(404)

    subprocess.call(command, stdout=subprocess.PIPE, shell=True)

    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


if __name__ == '__main__':
    app.run(port=8000)
