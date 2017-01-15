from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import urlfetch
import cloudstorage as gcs 
from google.appengine.api import app_identity

import os
import jinja2
import webapp2
import binascii
import logging 

from mutagen.easyid3 import EasyID3

from google.cloud import storage
storage_client = storage.Client()

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class MainPage(webapp2.RequestHandler):    
    
    def get(self):
        
        template_values = {
            'mixes' : []
        }

        default_bucket = app_identity.get_application_id() + '.appspot.com'

        access_token = os.environ.get('GCLOUD_ACCESS_TOKEN') 
        if access_token is not None :            
            gcs.common.set_access_token(access_token)
                
        bucket = storage_client.get_bucket(default_bucket)
        for blob in bucket.list_blobs(prefix='mixes/') :
            if blob.content_type == 'audio/mp3' :

                # Check for the presence of id3 info in the metadata, generate it.
                md = blob.metadata
                if md is None :
                    md = {}

                if 'id3.analyzed' not in md :
                    logging.info("Attempting to analyze " + blob.name)
                    filelike = gcs.open('/' + bucket.name + '/' + blob.name)
                    try :
                        tagfile = EasyID3(filelike)
                        # Copy all tags.
                        for tag in tagfile :
                            md['id3.' + tag] = tagfile[tag][0]

                        # Check for the tags I'm interested in.
                        if 'title' in tagfile :
                            md['Title'] = tagfile['title'][0]
                        else :
                            md['Title'] = blob.name

                        if 'comment' in tagfile :
                            md['Comment'] = tagfile['comment'][0]
                        else :
                            md['Comment'] = ''

                        md['Image'] = 'http://www.w3schools.com/w3images/lights.jpg'

                        md['id3.analyzed'] = 'ok'
                    except Exception as e :
                        logging.error("Error analyzing " + blob.name + ": " + e)
                    
                    filelike.close()
                    blob.metadata = md
                    blob.patch()

                # Check for the image in metadata.
                if 'Image' in md :
                    base_image_url = md['Image']
                else :
                    base_image_url = 'http://www.w3schools.com/w3images/lights.jpg'

                # Check the title
                if 'Title' in md :
                    mix_title = md['Title']
                else :
                    mix_title = blob.name

                image_name = "cached_images/image-%08x" % binascii.crc32(base_image_url)
                image_url = base_image_url

                # Try to find the cached image in my bucket
                cached_image = bucket.get_blob(image_name)
                if cached_image is None :
                    # Retrieve the URL and store the image
                    try:
                        result = urlfetch.fetch(base_image_url)
                        if result.status_code == 200:
                            cached_image = bucket.blob(image_name)
                            cached_image.upload_from_string(result.content, result.headers['content-type'])
                            cached_image.make_public()
                            image_url = cached_image.public_url
                        else:
                            logging.error("Unable to fetch image URL " + image_url + " HTTP status: " + str(result.status_code))
                            pass
                    except urlfetch.Error as e:
                            logging.error("Unable to fetch image URL " + image_url + " Caught: " + repr(e))

                template_values['mixes'].append({
                        'name' : mix_title,
                        'url' : blob.public_url,
                        'img' : image_url
                    })
        
        template = JINJA_ENVIRONMENT.get_template('playlist.html')
        self.response.write(template.render(template_values))
                   
application = webapp.WSGIApplication([('/', MainPage)], debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
