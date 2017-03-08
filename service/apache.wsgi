"""
Use this file to bind the app in apache with mod_wsgi

If you want to start the app directly with python/flask, use web.py instead
"""
from octopus.core import app as application, initialise, add_configuration

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-d", "--debug", action="store_true", help="pycharm debug support enable")
parser.add_argument("-c", "--config", help="additional configuration to load (e.g. for testing)")
args = parser.parse_args()

if args.config:
    add_configuration(application, args.config)

pycharm_debug = application.config.get('DEBUG_PYCHARM', False)
if args.debug:
    pycharm_debug = True

if pycharm_debug:
    application.config['DEBUG'] = False
    import pydevd
    pydevd.settrace(application.config.get('DEBUG_SERVER_HOST', 'localhost'), port=application.config.get('DEBUG_SERVER_PORT', 51234), stdoutToServer=True, stderrToServer=True)
    print "STARTED IN REMOTE DEBUG MODE"

initialise()

# most of the imports should be done here, after initialise()
from flask import render_template
from octopus.lib.webapp import custom_static

@application.route("/")
def index():
    return render_template("index.html")

# this allows us to override the standard static file handling with our own dynamic version
@application.route("/static/<path:filename>")
def static(filename):
    return custom_static(filename)

# this allows us to serve our standard javascript config
from octopus.modules.clientjs.configjs import blueprint as configjs
application.register_blueprint(configjs)

from service.views.main import blueprint as main
application.register_blueprint(main)

@application.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404


if __name__ == "__main__":
    application.run(host='0.0.0.0', debug=application.config['DEBUG'], port=application.config['PORT'], threaded=application.config["THREADED"])
