function writeEventTime(eventTimeSec) {
  var eventDate = new Date(eventTimeSec * 1000);

  var eventDateString = '';
  if (new Date().toLocaleDateString() != eventDate.toLocaleDateString()) {
    eventDateString = eventDate.toLocaleDateString();
  }
  
  eventDateString += ' ' + eventDate.toLocaleTimeString();
  
  document.write(eventDateString);
}
