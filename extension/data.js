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

  data.post('/client/create', function(client) {
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

data.post = function(path, callback) {
  data.send_('POST', path, callback);
}

data.send_ = function(method, path, callback) {
  var xhr = new XMLHttpRequest();
  xhr.open(method, 'http://' + prefs.getAppHostname() + path, true);
  xhr.onreadystatechange = function() {
    if (xhr.readyState == 4 && xhr.status == 200) {
      callback(JSON.parse(xhr.responseText));
    }
  };
  xhr.send();
};
