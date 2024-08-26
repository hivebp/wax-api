def run_loader(app):
    app.run(host='0.0.0.0', debug=False, port=5002)


def run_timed_loader(app):
    app.run(host='0.0.0.0', debug=False, port=5004)


def run_sets_loader(app):
    app.run(host='0.0.0.0', debug=False, port=5009)


def run_app(app, port=5003):
    print('App (WAX-API) is running on port ' + str(port))
    app.run(host='0.0.0.0', debug=False, port=port)
