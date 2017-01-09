from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

import os
import jinja2
import webapp2

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
                    template_values['mixes'].append({
                            'name' : blob.name,
                            'url' : blob.public_url,
                        })
        
        template = JINJA_ENVIRONMENT.get_template('playlist.html')
        self.response.write(template.render(template_values))
                   
application = webapp.WSGIApplication([('/', MainPage)], debug=True)


def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
