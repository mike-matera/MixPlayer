
dev:
	FLASK_APP=main FLASK_DEBUG=1 GOOGLE_APPLICATION_CREDENTIALS=./secrets/google-app-creds.json flask run --host=127.0.0.1

build:
	podman build -t mixplayer .

run:
	podman run -it \
		-e PORT=8080 \
		-p 8080:8080 \
		-v $(shell pwd)/secrets:/app/secrets -e GOOGLE_APPLICATION_CREDENTIALS=./secrets/google-app-creds.json \
		--rm mixplayer
