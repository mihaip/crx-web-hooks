var prefs = {};

prefs.PrefKey = {
  CLIENT_ID: {id: 'client-id'},
  APP_HOSTNAME: {id: 'app-hostname', defaultValue: 'crx-web-hooks.appspot.com'},
  IS_FIRST_LAUNCH: {id: 'is-first-launch', defaultValue: 'true'}
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

prefs.isFirstLaunch = function() {
  return prefs.getPref_(prefs.PrefKey.IS_FIRST_LAUNCH) == 'true';
};

prefs.setIsFirstLaunch = function(value) {
  return prefs.setPref_(prefs.PrefKey.IS_FIRST_LAUNCH, value.toString());
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

data.clientExists = function(clientId, callback) {
  data.get_(
      '/client/' + clientId,
      function(client) { callback(true); },
      function() { callback(false); }
  );
};

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

data.get_ = function(path, opt_callback, opt_errorCallback) {
  data.send_('GET', path, opt_callback, undefined, opt_errorCallback);
};

data.post_ = function(path, opt_callback, opt_params, opt_errorCallback) {
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
  data.send_('POST', path, opt_callback, postData, opt_errorCallback);
};

data.send_ = function(method, path, opt_callback, opt_postData, opt_errorCallback) {
  var xhr = new XMLHttpRequest();
  var url = 'http://' + prefs.getAppHostname() + path;
  xhr.open(method, url, true);
  xhr.onreadystatechange = function() {
    if (xhr.readyState == 4) {
      if (xhr.status == 200) {
        if (opt_callback) {
          opt_callback(JSON.parse(xhr.responseText));
        }
      } else if (opt_errorCallback) {
        opt_errorCallback();
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
