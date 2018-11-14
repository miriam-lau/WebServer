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

export { getElementById, getValueOfElementWithDefault, getFullBackendUrlForPath }