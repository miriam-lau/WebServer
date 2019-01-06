import { callAxios } from './utils'

/**
 * This file defines utility functions for the ButterBar component. It relies on the
 * following data being defined in the component:
 *   butterBar_message: The message displayed in the butter bar.
 *   butterBar_css: The css class for the butter bar.
 *
 * It will automatically define a butterBar_timeoutHandle on the same component for its own use.
 *
 * To use it, add the ButterBar component.
 */

let ButterBarType = {
  INFO: 1,
  ERROR: 2
}

/**
 * Sets the butter bar message text on the component. It will automatically clear after ten seconds.
 * @param {Vue Component} component the Vue component calling this function.
 * @param {string} text the butter bar message.
 * @param {ButterBarType} type
 */
function setButterBarMessage (component, text, type) {
  if (component == null || text == null || type == null) {
    throw new Error('Invalid arguments')
  }
  component.butterBar_message = text
  component.butterBar_css = _getCssClassForButterBarType(type)
  window.clearTimeout(component.butterBar_timeoutHandle)
  component.butterBar_timeoutHandle = setTimeout(
    function () {
      component.butterBar_message = ''
      component.butterBar_css = ''
    }, 10000)
}

/**
 * @param {ButterBarType} type
 */
function _getCssClassForButterBarType (type) {
  switch (type) {
    case ButterBarType.INFO:
      return 'butter-bar-info'
    case ButterBarType.ERROR:
      return 'butter-bar-error'
  }
}

/**
 * Calls axios and sets the butter bar text on error.
 * @param {Vue Object} component the Vue component this is called from.
 * @param {string} backendPath the path to call using Axios.
 * @param {Data Object} params params to send to the backend.
 * @param {string?} successMessage the message to set the butter bar to on success. If null, does not set it.
 * @param {string?} errorMessage the message to set the butter bar to on error. If null, does not set it.
 * @param {Function?} successCallback the callback function to call on success if one exists.
 */
function callAxiosAndSetButterBar (component, backendPath, params, successMessage, errorMessage, successCallback) {
  callAxios(
    backendPath,
    params,
    function (response) {
      if (successCallback) {
        successCallback(response)
      }
      if (successMessage !== null) {
        setButterBarMessage(component, successMessage, ButterBarType.INFO)
      }
    },
    function () {
      setButterBarMessage(component, errorMessage, ButterBarType.ERROR)
    })
}

export { setButterBarMessage, ButterBarType, callAxiosAndSetButterBar }
