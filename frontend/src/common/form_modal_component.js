import { callAxios } from './utils'

/**
 * This file defines utility functions for the FormModal component. It relies on the
 * following data being defined in the component:
 *   formModal_title
 *   formModal_formLines
 *   formModal_passThroughProps
 *   formModal_callback
 *   formModal_buttonText
 *   formModal_errorText
 *   formModal_show
 *   formModal_shouldShowError
 */

/**
 * Displays the modal with the given properties set.
 * @param {Object} component the Vue component to display the modal on.
 * @param {string} title the title.
 * @param {array<Object{id, name, displayName, value}>} formLines the lines of the form. See createFormModalEntry.
 * @param {Object} a map of properties to pass through to the modal.
 * @param {Function} callback the callback function when the modal is clicked.
 * @param {string} buttonText the text of the button to save the modal.
 * @param {string} errorText the text to display upon error.
 */
function showModal (component, title, formLines, passThroughProps, callback, buttonText, errorText) {
  component.formModal_title = title
  component.formModal_formLines = formLines
  component.formModal_passThroughProps = passThroughProps
  component.formModal_callback = callback
  component.formModal_buttonText = buttonText
  component.formModal_errorText = errorText
  component.formModal_shouldShowError = false
  component.formModal_show = true
}

/**
 * Creates a single formLine object used to display a formModal.
 * @param {string} id the html id of the formModalLine.
 * @param {string} name the name of the form modal parameter when saving to the backend.
 * @param {string} displayName the name to display in html for the form line.
 * @param {any|null?} value the initial value of the formModalLine. If null or undefined, set it to the 
 *     empty string.
 * @returns {Object{id, name, displayName, value}} the object representing the form line.
 */
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

/**
 * Generates a callback function that can be called by the modal upon button click which will make an axios call
 * to the backend specified. Upon success, the callback passed into this function is called after which the modal
 * will be closed. On error, it will update the modal status with the error text specified
 * @param {Object} the Vue component.
 * @param {string} backendPath the path on the backend to call.
 * @param {Function({Object} response)} successCallback. The function to call upon success of calling the backend. Called
 *     with the response from the backend.
 */
function generateAxiosModalCallback (component, backendPath, successCallback) {
  return function (modalOutput) {
    callAxios(
      backendPath,
      modalOutput,
      function (response) {
        successCallback(response)
        component.formModal_close()
      },
      function (response) {
        component.formModal_shouldShowError = true
      })
  }
}

export { showModal, createFormModalEntry, generateAxiosModalCallback }
