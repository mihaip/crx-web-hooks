#!/usr/bin/env python

from google.appengine.dist import use_library
use_library('django', '1.2')

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util

import handlers

def main():
    application = webapp.WSGIApplication([
            ('/', handlers.MainHandler),

            ('/hook/create', handlers.HookCreateHandler),
            ('/hook/delete', handlers.HookDeleteHandler),
            ('/hook/(.+)', handlers.HookHandler),

            ('/client/create', handlers.ClientCreateHandler),

            ('/client/(.+)/channel', handlers.ClientChannelHandler),
            ('/client/(.+)/channel/create', handlers.ClientChannelCreateHandler),
            ('/client/(.+)/channel/(.+)/ping', handlers.ClientChannelPingHandler),
            ('/client/(.+)/channel/(.+)/leave', handlers.ClientChannelLeaveHandler),

            ('/client/(.+)/hooks', handlers.ClientHooksHandler),
            ('/client/(.+)/undelivered', handlers.ClientUndeliveredHandler),
            ('/client/(.+)', handlers.ClientHandler),
        ],
        debug=True)
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()
