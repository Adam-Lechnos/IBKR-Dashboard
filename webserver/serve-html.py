import os
from flask import Flask, send_from_directory

app = Flask(__name__)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'webserver/static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/')
def index():
    return send_from_directory('webserver/static', 'index.html')

@app.route('/<path:path>')
def routes(path):
    return send_from_directory('webserver/static', path)


# @app.route('/risk-account-1')
# def riskAccount1():
#     return send_from_directory('static', 'Risk-Margin-Account-1.html')

# @app.route('/risk-account-2')
# def riskAccount2():
#     return send_from_directory('static', 'Risk-Margin-Account-2.html')

# @app.route('/pos-account-1')
# def posAccount1():
#     return send_from_directory('static', 'Pos-Margin-Account-1.html')

# @app.route('/pos-account-2')
# def posAccount2():
#     return send_from_directory('static', 'Pos-Margin-Account-2.html')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8081)