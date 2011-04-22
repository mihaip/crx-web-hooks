var prefs = {};

prefs.PrefKey = {
  CLIENT_ID: {id: 'client-id'},
  APP_HOSTNAME: {id: 'app-hostname', defaultValue: 'crx-web-hooks.appspot.com'}
};

prefs.getClientId = function(callback) {
  var clientId = prefs.getPref_(prefs.PrefKey.CLIENT_ID);
  if (clientId) {
    callback(clientId);
    return;
  }

  data.post_('/client/create', function(client) {
    prefs.setPref_(prefs.PrefKey.CLIENT_ID, client.id);
    callback(client.id);
  });
};

prefs.setClientId = function(clientId) {
  prefs.setPref_(prefs.PrefKey.CLIENT_ID, clientId);
};

prefs.getAppHostname = function() {
  return prefs.getPref_(prefs.PrefKey.APP_HOSTNAME);
};

prefs.setAppHostname = function(appHostname) {
  prefs.setPref_(prefs.PrefKey.APP_HOSTNAME, appHostname);
};

prefs.getPref_ = function(key) {
  return localStorage[key.id] || key.defaultValue;
};

prefs.setPref_ = function(key, value) {
  if (value != prefs.getPref_(key)) {
    localStorage[key.id] = value;
  }
};

var data = {};

data.getClientHooks = function(clientId, callback) {
  data.get_('/client/' + clientId + '/hooks', function(hooks) {
    callback(hooks);
  });
};

data.createHook = function(clientId, callback) {
  data.post_('/hook/create', callback, {'client_id': clientId});
};

data.deleteHook = function(clientId, hookId, callback) {
  data.post_(
      '/hook/delete', callback, {'client_id': clientId, 'hook_id': hookId});
};

data.pingChannel = function(clientId, channelId) {
  data.post_('/client/' + clientId + '/channel/' + channelId + '/ping');
};

data.leaveChannel = function(clientId, channelId) {
  data.post_('/client/' + clientId + '/channel/' + channelId + '/leave');
};

data.get_ = function(path, opt_callback) {
  data.send_('GET', path, callback);
};

data.post_ = function(path, opt_callback, opt_params) {
  var postData = '';
  if (opt_params) {
    for (var name in opt_params) {
      var value = opt_params[name];
      if (postData) {
        postData += '&';
      }
      postData += encodeURIComponent(name) + '=' + encodeURIComponent(value);
    }
  }
  data.send_('POST', path, opt_callback, postData);
};

data.send_ = function(method, path, opt_callback, opt_postData) {
  var xhr = new XMLHttpRequest();
  var url = 'http://' + prefs.getAppHostname() + path;
  xhr.open(method, url, true);
  xhr.onreadystatechange = function() {
    if (xhr.readyState == 4) {
      if (xhr.status == 200) {
        if (opt_callback) {
          opt_callback(JSON.parse(xhr.responseText));
        }
      } else {
        localStorage.lastHttpErrorUrl = url;
        localStorage.lastHttpErrorStatus = xhr.status;
        var notification = webkitNotifications.createHTMLNotification('http-error.html');
        notification.show();
      }
    }
  };
  xhr.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
  xhr.send(opt_postData);
};
