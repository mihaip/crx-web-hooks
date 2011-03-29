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

data.get_ = function(path, callback) {
  data.send_('GET', path, callback);
};

data.post_ = function(path, callback, opt_params) {
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
  data.send_('POST', path, callback, postData);
};

data.send_ = function(method, path, callback, opt_postData) {
  var xhr = new XMLHttpRequest();
  xhr.open(method, 'http://' + prefs.getAppHostname() + path, true);
  xhr.onreadystatechange = function() {
    if (xhr.readyState == 4 && xhr.status == 200) {
      callback(JSON.parse(xhr.responseText));
    }
  };
  xhr.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
  xhr.send(opt_postData);
};
