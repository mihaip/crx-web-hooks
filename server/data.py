import base64
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
        id  = _generate_channel_id()
        self.channel_ping_time_by_id[id] = time.time()
        return id
    
    def ping_channel(self, id):
        self.channel_ping_time_by_id[id] = time.time()
    
    def remove_channel(self, id):
        del self.channel_ping_time_by_id[id]
        
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
        id = _generate_client_id()
        client = Client(
            key_name=id,
            id=id,
            channels=ClientChannelList()
        )
        return client
        
def _generate_client_id():
    return _generate_id('client-')

def _generate_channel_id():
    return _generate_id('channel-')

def _generate_id(prefix):
    return prefix + base64.urlsafe_b64encode(uuid.uuid4().bytes).replace('=', '')
