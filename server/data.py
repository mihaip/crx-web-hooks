import base64
import calendar
import datetime
import pickle
import time
import uuid

from google.appengine.ext import db
from google.appengine.api import datastore_errors

class PickledProperty(db.Property):
    data_type = db.Text
    force_type = None

    def __init__(
            self,
            verbose_name=None,
            name=None,
            default=None,
            required=False,
            validator=None,
            choices=None):
        db.Property.__init__(
            self,
            verbose_name=verbose_name,
            name=name,
            default=default,
            required=required,
            validator=validator,
            choices=choices,
            indexed=False)

    def validate(self, value):
        value = super(PickledProperty, self).validate(value)
        if value is not None and self.force_type and \
            not isinstance(value, self.force_type):
                raise datastore_errors.BadValueError(
                    'Property %s must be of type "%s".' % (self.name,
                        self.force_type))
        return value

    def get_value_for_datastore(self, model_instance):
        value = self.__get__(model_instance, model_instance.__class__)
        if value is not None:
            return db.Text(pickle.dumps(value))

    def make_value_from_datastore(self, value):
        if value is not None:
            return pickle.loads(str(value))

class ClientChannelList(object):
    def __init__(self):
        self.channel_ping_time_by_id = {}

    def contains_channel(self, id):
        return id in self.channel_ping_time_by_id

    def add_channel(self):
        id  = _generate_id('a')
        self.channel_ping_time_by_id[id] = time.time()
        return id

    def ping_channel(self, id):
        self.channel_ping_time_by_id[id] = time.time()

    def remove_channel(self, id):
        del self.channel_ping_time_by_id[id]

    def get_active_channel_ids(self):
        threshold_ping_time = time.time() - 10 * 60
        c = self.channel_ping_time_by_id
        return [k for k in c.keys() if c[k] > threshold_ping_time]

    def garbage_collect(self):
        threshold_ping_time = time.time() - 20 * 60
        c = self.channel_ping_time_by_id
        map(lambda k: c.pop(k), [k for k in c.keys() if c[k] < threshold_ping_time])

    def as_json(self):
        return {
            'channelPingTimeById': self.channel_ping_time_by_id
        }

class ClientChannelListProperty(PickledProperty):
    force_type = ClientChannelList

class Client(db.Model):
    id = db.StringProperty()
    channels = ClientChannelListProperty()

    def as_json(self):
        return {
            'id': self.id,
            'channels': self.channels.as_json(),
        }

    @staticmethod
    def get_by_id(id):
        return Client.get_by_key_name(id)

    @staticmethod
    def create():
        id = _generate_id('c')
        client = Client(
            key_name=id,
            id=id,
            channels=ClientChannelList()
        )
        return client

class HookEvent(object):
    def __init__(self, request_as_json, delivered):
        self.request_as_json = request_as_json
        self.delivered = delivered

    def time_as_date(self):
        return datetime.datetime.utcfromtimestamp(
            self.request_as_json['timeSec'])

class HookEventList(object):
    def __init__(self):
        self.events = []

    def add_event(self, event):
        self.events.append(event)
        self.garbage_collect()

    def garbage_collect(self):
        delivered_events = [e for e in self.events if e.delivered]
        if len(delivered_events) < 10:
            old_events = delivered_events[:len(delivered_events) - 10]
            for old_event in old_events:
                self.events.remove(old_event)

class HookEventListProperty(PickledProperty):
    force_type = HookEventList

class Hook(db.Model):
    id = db.StringProperty()
    owner_client_id = db.StringProperty()
    last_event_time = db.DateTimeProperty()
    events = HookEventListProperty()

    def as_json(self):
        return {
            'id': self.id,
            'ownerClientId': self.owner_client_id,
            'lastEventTimeSec': calendar.timegm(self.last_event_time.utctimetuple())
        }

    def add_event(self, request_as_json, delivered):
        event = HookEvent(request_as_json, delivered)
        self.events.add_event(event)
        self.last_event_time = datetime.datetime.utcnow()

    @staticmethod
    def get_by_id(id):
        return Hook.get_by_key_name(id)

    @staticmethod
    def get_hooks_for_client_id(client_id):
        return list(Hook.all().filter('owner_client_id = ', client_id))

    @staticmethod
    def create(owner_client_id):
        id = _generate_id('h')
        hook = Hook(
            key_name=id,
            id=id,
            owner_client_id=owner_client_id,
            last_event_time=datetime.datetime.utcfromtimestamp(0),
            events=HookEventList(),
        )
        return hook

def _generate_id(prefix):
    return prefix + base64.urlsafe_b64encode(uuid.uuid4().bytes).replace('=', '')
