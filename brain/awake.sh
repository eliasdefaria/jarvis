is_prod=$([[ $1 = 'prod' ]] && echo true || echo false)
no_server=$([[ $2 = 'no-server' ]] && echo true || echo false)

export FLASK_APP=server:create_app
export FLASK_ENV=$($is_prod && echo 'production' || echo 'development')

if [ $is_prod = false ];
then
    export AUTH_TOKEN='test-auth'
fi

# Initialize database
python3 db/db.py

if $no_server;
then
    python3 jarvis.py;
else
    python3 jarvis.py
    python3 -m flask run
fi