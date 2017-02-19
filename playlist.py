from google.appengine.api import urlfetch
import cloudstorage as gcs 
from google.appengine.api import app_identity

import os
# import jinja2
import binascii
import logging 

from flask import Flask, url_for, render_template

from mutagen.easyid3 import EasyID3

from google.cloud import storage
storage_client = storage.Client()

flapp = Flask(__name__)

def check_metadata(blob):
    update_md = False
    md = blob.metadata
    if md is None :
        md = {}

    # Check if the ID3 tags have been scanned.            
    if 'id3.analyzed' not in md :
        update_md = True
        blobfilename = '/' + blob.bucket.name + '/' + blob.name
        logging.info("Attempting to analyze " + blobfilename)
        filelike = gcs.open(blobfilename)
        try :
            tagfile = EasyID3(filelike)
            # Copy all tags.
            for tag in tagfile :
                md['id3.' + tag] = tagfile[tag][0]
            md['id3.analyzed'] = 'ok'

        except Exception as e :
            logging.error("Error analyzing " + blob.name + ": " + e)
            md['id3.analyzed'] = 'error'

        filelike.close()

    # Verify that all metadata is intact. 
    if 'Title' not in md :
        update_md = True
        if 'id3.title' in md :
            md['Title'] = md['id3.title']
        else :
            md['Title'] = blob.name

    if 'Comment' not in md : 
        update_md = True
        if 'id3.comment' in md :
            md['Comment'] = md['id3.comment']
        else :
            md['Comment'] = ''

    if 'Image' not in md :
        update_md = True
        if 'id3.image' in md :
            md['Image'] = md['id3.image']
        else :
            md['Image'] = 'http://www.w3schools.com/w3images/lights.jpg'

    if update_md :           
        blob.metadata = md
        blob.patch()
    
    return md

def cache_image(bucket, image_url):
    image_name = "cached_images/image-%08x" % binascii.crc32(image_url)

    # Try to find the cached image in my bucket
    cached_image = bucket.get_blob(image_name)
    if cached_image is None :
        # Cache miss: Retrieve the URL and store the image
        try:
            result = urlfetch.fetch(image_url)
            if result.status_code == 200:
                cached_image = bucket.blob(image_name)
                cached_image.upload_from_string(result.content, result.headers['content-type'])
                cached_image.make_public()
            else:
                logging.error("Unable to fetch image URL " + image_url + " HTTP status: " + str(result.status_code))
                return image_url 
            
        except urlfetch.Error as e:
                logging.error("Unable to fetch image URL " + image_url + " Caught: " + repr(e))
                return image_url
    
    return cached_image.public_url   

def get_mix_info(mixname=None):
    mixes = []

    default_bucket = app_identity.get_application_id() + '.appspot.com'

    access_token = os.environ.get('GCLOUD_ACCESS_TOKEN') 
    if access_token is not None :            
        gcs.common.set_access_token(access_token)
            
    bucket = storage_client.get_bucket(default_bucket)
    for blob in bucket.list_blobs(prefix='mixes/') :
        if blob.content_type == 'audio/mp3' :

            # Check for the presence of id3 info in the metadata, generate it.
            md = check_metadata(blob)

            if mixname is not None and md['Title'] != mixname : 
                continue
        
            # Check the image cache.
            image_url = cache_image(bucket, md['Image'])

            mixes.append({
                    'name'      : md['Title'],
                    'comment'   : md['Comment'],
                    'permalink' : url_for('show_mix', mixname=md['Title']),
                    'url'       : blob.public_url,
                    'img'       : image_url,
                    'date'      : blob.updated
                })
    

    mixes = sorted (mixes, key=lambda k: k['date'], reverse=True)
    return mixes

@flapp.route('/')
def mix_list():
    return render_template('playlist.html', mixes=get_mix_info())
                   
@flapp.route('/mix/<mixname>')
def show_mix(mixname):
    return render_template('singlemix.html', mixes=get_mix_info(mixname))

@flapp.errorhandler(500)
def server_error(e):
    # Log the error and stacktrace.
    logging.exception('An error occurred during a request.')
    return 'An internal error occurred.', 500

