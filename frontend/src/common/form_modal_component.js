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
 * @param {Function} successCallback
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
