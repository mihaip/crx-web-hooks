import os

from django.utils import simplejson
from google.appengine.api import channel as appengine_channel
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

import data

class BaseHandler(webapp.RequestHandler):
    def _render_template(self, template_file_name, template_values={}):
        rendered_template = template.render(template_file_name, template_values)
        # Django templates are returned as utf-8 encoded by default
        if not isinstance(rendered_template, unicode):
          rendered_template = unicode(rendered_template, 'utf-8')
        return rendered_template

    def _write_template(
            self,
            template_file_name,
            template_values={},
            content_type='text/html',
            charset='utf-8'):
        self.response.headers['Content-Type'] = '%s; charset=%s' % (content_type, charset)
        self.response.out.write(
            self._render_template(template_file_name, template_values))

    def _write_error(self, error_code):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.set_status(error_code)

    def _write_not_found(self):
        self._write_error(404)

    def _write_input_error(self, error_message):
        self._write_error(400)
        self.response.out.write('Input error: %s' % error_message)

    def _write_json(self, obj):
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(simplejson.dumps(obj, indent=4) + '\n')

class MainHandler(webapp.RequestHandler):
    def get(self):
        self.response.out.write('Hello world!')

class HookCreateHandler(BaseHandler):
    def post(self):
        client_id = self.request.get('client_id')
        if not client_id:
            self._write_input_error('client_id is required')
            return

        client = data.Client.get_by_id(client_id)
        if not client:
            self._write_input_error('no client found')
            return

        hook = data.Hook.create(client_id)
        hook.put()

        self._write_json(hook.as_json())

class HookHandler(BaseHandler):
    def get(self, hook_id):
        self.response.out.write('TODO(mihaip): explanatory page about POST '
            'request goes here');

    def post(self, hook_id):
        request = self.request
        arguments = {}
        for arg_name in request.arguments():
            arguments[arg_name] = request.get_all(arg_name)
        cookies = {}
        for cookie_name, cookie_value in request.cookies.items():
            cookies[cookie_name] = cookie_value
        headers = {}
        for header_name, header_value in request.headers.items():
            cookies[header_name] = header_value

        request_as_json = {
          'remoteAddress': request.remote_addr,
          'arguments': arguments,
          'cookies': cookies,
          'headers': headers,
        }

        hook = data.Hook.get_by_id(hook_id)
        if not hook:
            self._write_not_found()
            return

        client = data.Client.get_by_id(hook.owner_client_id)
        if not client:
            self._write_input_error('no owning client found')
            return

        channel_ids = client.channels.get_active_channel_ids()
        for channel_id in channel_ids:
            appengine_channel.send_message(
                channel_id, simplejson.dumps(request_as_json))

        # Echo what was sent to the channel for debugging
        self._write_json(request_as_json)

class ClientHooksHandler(BaseHandler):
    def get(self, client_id):
        client = data.Client.get_by_id(client_id)

        if not client:
            self._write_not_found()
            return

        hooks = data.Hook.get_hooks_for_client_id(client_id)
        self._write_json([h.as_json() for h in hooks])

class ClientCreateHandler(BaseHandler):
    def post(self):
        client = data.Client.create()
        client.put()

        self._write_json(client.as_json())

class ClientChannelCreateHandler(BaseHandler):
    def post(self, client_id):
        client = data.Client.get_by_id(client_id)

        if not client:
            self._write_not_found()
            return

        client.channels.add_channel()
        client.put()

        self._write_json(client.as_json())

class ClientHandler(BaseHandler):
    def get(self, client_id):
        client = data.Client.get_by_id(client_id)

        if not client:
            self._write_not_found()
            return

        self._write_json(client.as_json())

class ClientChannelPingHandler(BaseHandler):
    def post(self, client_id, channel_id):
        client = data.Client.get_by_id(client_id)

        if not client or not client.channels.contains_channel(channel_id):
            self._write_not_found()
            return

        client.channels.ping_channel(channel_id)
        client.put()

        self._write_json(client.as_json())

class ClientChannelLeaveHandler(BaseHandler):
    def post(self, client_id, channel_id):
        client = data.Client.get_by_id(client_id)

        if not client or not client.channels.contains_channel(channel_id):
            self._write_not_found()
            return

        client.channels.remove_channel(channel_id)
        client.put()

        self._write_json(client.as_json())

class ClientChannelHandler(BaseHandler):
    def get(self, client_id):
        client = data.Client.get_by_id(client_id)

        if not client:
            self._write_not_found()
            return

        channel_id = client.channels.add_channel()
        client.put()

        channel_token = appengine_channel.create_channel(channel_id)

        self._write_template(
            'templates/channel.html', {
                'channel_id': channel_id,
                'channel_token': channel_token
            })
