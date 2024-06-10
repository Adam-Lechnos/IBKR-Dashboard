import os
from flask import Flask, send_from_directory
import ssl

useTLS=os.environ.get('useTLS')
webPort=os.environ.get('webPort')
flaskDebug=os.environ.get('flaskDebug')

if flaskDebug == False == None: flaskDebug = False
print(f'Debug mode: {flaskDebug}')
print(f'Port: {webPort}')
print(f'Use TLS: {useTLS}')

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

    if useTLS == "yes":
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain('server.crt','server.key')
        app.run(debug=flaskDebug, host='0.0.0.0', port=webPort, ssl_context=context)
    else:
        app.run(debug=flaskDebug, host='0.0.0.0', port=webPort)