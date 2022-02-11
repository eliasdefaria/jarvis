is_prod=$([[ $1 = 'prod' ]] && echo true || echo false)
no_server=$([[ $2 = 'no-server' ]] && echo true || echo false)

export FLASK_APP=jarvis:init_jarvis
export FLASK_ENV=$($is_prod && echo 'production' || echo 'development')

python3 db/db.py

if [ no_server ];
then
    python3 jarvis.py
else
    python3 -m flask run
fi