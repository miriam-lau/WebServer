import axios from 'axios'

/*
 * Gets the element specified by the id.
 * @param {string} id the id of the html element.
 */
function getElementById (id) {
  return document.getElementById(id)
}

/*
 * Gets the value of the element with the given id. Uses {@code defaultValue} if the element has no value.
 * @param {string} id the id of the html element.
 * @param {string?} defaultValue the value to provide if the element has no value.
 * @returns {string} the value of the html element, the default value, or ''.
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
 * @param {string} path the relative path of the address.
 * @return {string} the full http address.
 */
function getFullBackendUrlForPath (path) {
  return 'http://' + window.location.hostname + ':5000' + path
}

/*
 * Plays the sound stored at the given url.
 * @param {string} url the url the sound is stored at.
 */
function playSound (url) {
  var audio = new Audio(url)
  audio.play()
}

/*
 * Creates the expand or collapse icon based on whether the icon is expanded or not.
 * @param {boolean} isExpanded whether or not the icon is expanded.
 */
function generateExpandIcon (isExpanded) {
  if (isExpanded) {
    return '[-]'
  } else {
    return '[+]'
  }
}

/**
 * Whether the two numbers are equal or not. Can handle floats/doubles.
 * @param {number} x the first number.
 * @param {number} y the second number.
 * @returns {boolean} whether or not the numbers are equal.
 */
function isEqual (x, y) {
  return Math.abs(x - y) < Number.EPSILON
}

/**
 * Given a date string, returns a reformatted version of the string for a standardized display.
 * @param {string} dateString the string representing the date.
 * @returns {string} a reformatted date string.
 */
function getDisplayDate (dateString) {
  let date = new Date(Date.parse(dateString))
  let options = { month: 'short', day: 'numeric', year: 'numeric', timeZone: 'UTC' }
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
 * For example, findPath({'a': { 'b': c } }, c) will return ['a', 'b']
 * From https://stackoverflow.com/questions/43636000/javascript-find-path-to-object-reference-in-nested-object
 * @param {Object} obj the object to search within.
 * @param {Object} target the target to find. Must be an object.
 * @param {array?} return an array with the path within the object to the target. Or null if it's not found.
 */
function findPath (obj, target) {
  if (target === obj) {
    return []
  }
  for (var key in obj) {
    if (obj.hasOwnProperty(key)) {
      if (target === obj[key]) {
        if (obj instanceof Array) {
          return [parseInt(key, 10)]
        } else {
          return [key]
        }
      } else if (obj[key] && typeof obj[key] === 'object') {
        let path = findPath(obj[key], target)
        if (path) {
          if (obj instanceof Array) {
            return [parseInt(key, 10)].concat(path)
          } else {
            return [key].concat(path)
          }
        }
      }
    }
  }
  return null
}

/**
 * Given a path to an object, (generated from {@code findPath}), retrieve the object.
 * @param {Object} obj the initial object to search within.
 * @param {array} path the path within {@code obj} to fetch the object. Possibly null.
 * @returns {Object?} the retrieved object or null if path is null.
 */
function fetchFromPath (obj, path) {
  if (!path) {
    return null
  }
  let curObj = obj
  for (var idx in path) {
    curObj = curObj[path[idx]]
  }
  return curObj
}

/**
 * Empties the given array in place. {@code arr} is modified.
 * @param {array} arr the array to modify.
 */
function emptyArray (arr) {
  for (let i = arr.length; i > 0; --i) {
    arr.pop()
  }
}

/**
 * Moves all items in the source array to the destination array.
 * @param {array} source the array to transfer items from.
 * @param {array} destination the array to transfer items to.
 */
function transferContents (source, destination) {
  destination.push(...source)
  emptyArray(source)
}

/**
 * Shuffles {@code array} in place and returns it.
 * Taken from https://gomakethings.com/how-to-shuffle-an-array-with-vanilla-js/
 * @param {array} array the array to shuffle. This is modified in place.
 * @returns {array} a reference to the shuffled array.
 */
function shuffle (array) {
  var currentIndex = array.length
  var temporaryValue, randomIndex

  while (currentIndex !== 0) {
    randomIndex = Math.floor(Math.random() * currentIndex)
    currentIndex -= 1

    temporaryValue = array[currentIndex]
    array[currentIndex] = array[randomIndex]
    array[randomIndex] = temporaryValue
  }
  return array
}

export {
  getElementById, getValueOfElementWithDefault, getFullBackendUrlForPath, playSound, generateExpandIcon,
  isEqual, getDisplayDate, callAxios, findPath, fetchFromPath, emptyArray, transferContents, shuffle
}
