from app import app
#from flask import current_app
from paste.translogger import TransLogger
from werkzeug.debug import DebuggedApplication
import cherrypy
import time

#app = current_app
'''-------------CHERRYPY INTEGRATION-----------------'''
class FotsTransLogger(TransLogger):
    def write_log(self, environ, method, req_uri, start, status, bytes):
        """ We'll override the write_log function to remove the time offset so
        that the output aligns nicely with CherryPy's web server logging

        i.e.

        [08/Jan/2013:23:50:03] ENGINE Serving on 0.0.0.0:5000
        [08/Jan/2013:23:50:03] ENGINE Bus STARTED
        [08/Jan/2013:23:50:45 +1100] REQUES GET 200 / (192.168.172.1) 830

        becomes

        [08/Jan/2013:23:50:03] ENGINE Serving on 0.0.0.0:5000
        [08/Jan/2013:23:50:03] ENGINE Bus STARTED
        [08/Jan/2013:23:50:45] REQUES GET 200 / (192.168.172.1) 830
        """

        if bytes is None:
            bytes = '-'
        remote_addr = '-'
        if environ.get('HTTP_X_FORWARDED_FOR'):
            remote_addr = environ['HTTP_X_FORWARDED_FOR']
        elif environ.get('REMOTE_ADDR'):
            remote_addr = environ['REMOTE_ADDR']
        d = {
            'REMOTE_ADDR': remote_addr,
            'REMOTE_USER': environ.get('REMOTE_USER') or '-',
            'REQUEST_METHOD': method,
            'REQUEST_URI': req_uri,
            'HTTP_VERSION': environ.get('SERVER_PROTOCOL'),
            'time': time.strftime('%d/%b/%Y:%H:%M:%S', start),
            'status': status.split(None, 1)[0],
            'bytes': bytes,
            'HTTP_REFERER': environ.get('HTTP_REFERER', '-'),
            'HTTP_USER_AGENT': environ.get('HTTP_USER_AGENT', '-'),
        }
        message = self.format % d
        self.logger.log(self.logging_level, message)

        
def run_server():
	# Enable the Werkzeug Debugger
    #app_debug = DebuggedApplication(app, evalex=True)

    # Enable custom Paste access logging
    log_format = (
        '[%(time)s] REQUES %(REQUEST_METHOD)s %(status)s %(REQUEST_URI)s '
        '(%(REMOTE_ADDR)s) %(bytes)s bytes'
    )
    app_logged = FotsTransLogger(app, format=log_format)

    # Mount the WSGI callable object (app) on the root directory
    cherrypy.tree.graft(app_logged, '/')

    # Set the configuration of the web server
    cherrypy.config.update({
        'engine.autoreload.on': True,
        #'log.screen': True,
#'log.access_file':r'C:\Users\Admin\Desktop\REST\logs\log.txt',
        'server.socket_port': 5000,
        'server.socket_host': '0.0.0.0'
    })


    
    # Start the CherryPy WSGI web server
    #cherrypy.engine.console_control_handler.subscribe()
    cherrypy.engine.start()
    cherrypy.engine.block()
    
if __name__ == "__main__":
    run_server()

