# MixPlayer

This is an app that streams audio stored in a GCS bucket using Google App Engine. Streaming happens from the bucket directly and uses the plain HTML5 element in the browser.

## Updated for CloudRun

I've always been a fan of Google's serverless products. The first iteration of MixPlayer used the legacy AppEngine Python 2 runtime with AppEngine specific libraries (that were incomplete and deprecated). The second one updated to AppEngine Standard Edition with Python 3 and the Python client libraries that work everywhere. This version is based on CloudRun. 

Cloud run executes any container so the code in this repo uses the general Docker build process, eliminating Google Cloud Compute specific code here. Which is awesome. 

## Stuff to Do 

I put a `makefile` here because I'm old and typing `make build && make run` is easier than typing big `docker` commands. 
 

