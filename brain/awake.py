import argparse
from multiprocessing.connection import wait
import sys
from os import environ

from db.db import init_db
from jarvis import init_jarvis
from waitress import serve
from server import create_app

[ DEV, PROD ] = [ 'development', 'production' ]
TEST_AUTH_TOKEN = 'test-auth'

print('got auth token', environ['AUTH_TOKEN'])

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--env', 
    choices=['production', 'development'], 
    help='The environment to run the server in (production or development)',
    required=True
)
parser.add_argument('--server', dest='server', action='store_true')
parser.add_argument('--no-server', dest='server', action='store_false')
parser.set_defaults(server=True)

args = parser.parse_args()

if 'AUTH_TOKEN' not in environ:
    if args.env == DEV:
        environ['AUTH_TOKEN'] = TEST_AUTH_TOKEN
    else:
        sys.exit('Invalid auth token configuration for production server environment')    

environ['FLASK_ENV'] = PROD if args.env == PROD else DEV

init_db()
init_jarvis()   

if not args.server:
    sys.exit('No server argument passed in. Skipping server initialization')

flask_app = create_app()
if args.env == PROD:
    serve(flask_app, port=8000)
else:
    flask_app.run()
