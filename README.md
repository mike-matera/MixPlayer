# MixPlayer

This is an app that streams audio stored in a GCS bucket using Google App Engine. Streaming happens from the bucket directly and uses the plain HTML5 element in the browser.

## Updated for CloudRun

I've always been a fan of Google's commitment to serverless applications. 

```console
gcloud run deploy mix-player \
--image=gcr.io/repo-path \
--allow-unauthenticated \
--service-account=250334710383-compute@developer.gserviceaccount.com \
--region=us-central1 \
````

App Engine updated the Standard Environment to include a Python 3 interpreter. Apps work differently and deploying a Python 3 app is much simpler and more standard than the Python 2.7 environment. You can use any Python library that can be installed by pip. You just list them in `requirements.txt`. 

## Flask Application 

This app is developed locally like any other Flask app, by simply executing the `main.py` file from the command line:

```
$ python3 main.py 
```

