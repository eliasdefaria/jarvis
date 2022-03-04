# jarvis
This project represents the custom-built smart home. Functionalities are currently limited to interfacing with lights, but this project aims to run all possible aspects of my home as I grow older.

## Development

To run Jarvis, awake with by running the `awake.sh` shell script

Run Jarvis in Development Mode:
```
    sh awake.sh dev
```

Run Jarvis in Production
```
    sh awake.sh prod
```

Run Jarvis w/out the Server
```
    sh awake.sh dev no-server
```

## Deployment & Logs

Jarvis is deployed via Github Actions. The deployment script can be found in .github/workflows/deploy-jarvis.yml

Running the server locally will produce logs in the console, but running the Docker container will produce logs in the filesystem.

View logs in production
```
    docker logs jarvis
```