from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import urlfetch

import os
import jinja2
import webapp2
import binascii
import logging 

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
        
        for bucket in storage_client.list_buckets() :
            for blob in bucket.list_blobs() : 
                if blob.content_type == 'audio/mp3' :
                    try :
                        base_url = blob.metadata['Image']
                    except: 
                        base_url = 'http://www.w3schools.com/w3images/lights.jpg'
                    
                    image_name = "cached_images/image-%08x" % binascii.crc32(base_url)
                    image_url = base_url
                    # Try to find the cached image in my bucket 
                    cached_image = bucket.get_blob(image_name)
                    if cached_image is None : 
                        # Retrieve the URL and store the image                         
                        try:
                            result = urlfetch.fetch(base_url)
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
                            'name' : blob.name,
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
