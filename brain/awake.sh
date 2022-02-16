#! /bin/bash
is_prod=$([[ $1 = 'prod' ]] && echo true || echo false);
no_server=$([[ $2 = 'no-server' ]] && echo true || echo false);
auth_token=$3

export FLASK_APP=server:create_app;
export FLASK_ENV=$($is_prod && echo 'production' || echo 'development');

if [[ $is_prod = false && -z $auth_token ]];
then
    export AUTH_TOKEN='test-auth';
else
    export AUTH_TOKEN=$auth_token
fi

# Initialize database
python3 db/db.py;
python3 jarvis.py;

$no_server && exit 0;

$is_prod && waitress-serve --port=8000 --call 'server:create_app' || python3 -m flask run;