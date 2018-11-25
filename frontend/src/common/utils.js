/*
 * Gets the element specified by the id.
 */
function getElementById (id) {
  return document.getElementById(id)
}

/*
 * Gets the value of the element with the given id. Uses the default value if none is specified.
 */
function getValueOfElementWithDefault (id, defaultValue) {
  if (defaultValue === undefined) {
    defaultValue = ''
  }
  var value = getElementById(id).value
  if (value === '') {
    return defaultValue
  }
  return value
}

/*
 * Gets the full http address to the python server given a relative path. It is always on the same server as
 * the Vue frontend.
 */
function getFullBackendUrlForPath (path) {
  return 'http://' + window.location.hostname + ':5000' + path
}

function playSound (url) {
  var audio = new Audio(url)
  audio.play()
}

/*
 * Creates the expand icon based on whether the icon is expanded or not.
 */
function generateExpandIcon (isExpanded) {
  if (isExpanded) {
    return '[-]'
  } else {
    return '[+]'
  }
}

function isEqual (x, y) {
  return Math.abs(x - y) < Number.EPSILON
}

function getDisplayDate (dateString) {
  let date = new Date(Date.parse(dateString))
  let options = {month: 'short', day: 'numeric', year: 'numeric', timeZone: 'UTC'}
  return date.toLocaleDateString('en-US', options)
}

function createFormModalEntry (id, name, displayName, value) {
  if (value === null || value === undefined) {
    value = ''
  }
  return {
    id: id,
    name: name,
    displayName: displayName,
    value: value
  }
}

export { getElementById, getValueOfElementWithDefault, getFullBackendUrlForPath, playSound, generateExpandIcon,
  isEqual, getDisplayDate, createFormModalEntry }
