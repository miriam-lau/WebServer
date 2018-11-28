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
 * @param {ButterBarType} type
 */
function setButterBarMessage (component, text, type) {
  if (component == null || text == null || type == null) {
    throw new Error('Invalid arguments')
  }
  component.butterBar_message = text
  component.butterBar_css = getCssClassForButterBarType(type)
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
function getCssClassForButterBarType (type) {
  switch (type) {
    case ButterBarType.INFO:
      return 'butter-bar-info'
    case ButterBarType.ERROR:
      return 'butter-bar-error'
  }
}

export { setButterBarMessage, ButterBarType }
