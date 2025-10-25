# ngsidekick-server

Http endpoints to supplement neuroglancer scenes.

## Running the Development Server

```bash
# Option 1: Run directly
python src/ngsidekick_server/app.py

# Option 2: Use Flask CLI
export FLASK_APP=src/ngsidekick_server/app.py
export FLASK_ENV=development
flask run
```

The server will start on http://localhost:8000

## Docker Deployment

```
gcloud auth login
gcloud auth configure-docker us-east4-docker.pkg.dev  # first time only

docker build --platform linux/amd64 . -t us-east4-docker.pkg.dev/flyem-private/ngsidekick/ngsidekick-server
docker push us-east4-docker.pkg.dev/flyem-private/ngsidekick/ngsidekick-server
```

