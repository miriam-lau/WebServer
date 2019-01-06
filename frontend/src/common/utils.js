import axios from 'axios'

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

/**
 * Use axios to make a call to a backend then call one of the callback functions.
 * @param {string} backendPath the backend path.
 * @param {Object} params the params object to pass to the backend.
 * @param {Function?} successCallback optional.
 * @param {Function?} errorCallback optional.
 */
function callAxios (backendPath, params, successCallback, errorCallback) {
  axios.post(backendPath, params)
    .then(
      response => {
        if (successCallback) {
          successCallback(response)
        }
      })
    .catch(error => {
      console.warn(error)
      console.warn('Backend exception:\n' + error.response.data.exception)
      if (errorCallback) {
        errorCallback(error.response)
      }
    })
}

/**
 * Finds the path of keys to a given variable within an object. The return is represented as as an array.
 * From https://stackoverflow.com/questions/43636000/javascript-find-path-to-object-reference-in-nested-object
 */
function findPath (a, obj) {
  for (var key in obj) {
    if (obj.hasOwnProperty(key)) {
      if (a === obj[key]) return [key]
      else if (obj[key] && typeof obj[key] === 'object') {
        var path = findPath(a, obj[key])
        if (path) return [key].concat(path)
      }
    }
  }
}

function fetchFromPath (obj, path) {
  let curObj = obj
  for (var idx in path) {
    curObj = curObj[path[idx]]
  }
  return curObj
}

function emptyArray (arr) {
  for (let i = arr.length; i > 0; --i) {
    arr.pop()
  }
}

/**
 * Moves all items in the original array to the destination array.
 */
function transferContents (original, destination) {
  destination.push(...original)
  emptyArray(original)
}

export { getElementById, getValueOfElementWithDefault, getFullBackendUrlForPath, playSound, generateExpandIcon,
  isEqual, getDisplayDate, callAxios, findPath, fetchFromPath, emptyArray, transferContents }
