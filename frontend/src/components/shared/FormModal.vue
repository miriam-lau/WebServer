<template>
  <Modal :show="show" :close="close">
    <div class="modal-header">
     <h3>{{ title }}</h3>
    </div>
    <div class="modal-error" v-if="shouldShowError">
      {{ errorText }}
    </div>
    <div class="modal-body">
      <div :key="formLine.id" v-for="(formLine, index) in formLines">
        <label class="form-label">
          {{ formLine.displayName }}
          <input v-model="formLine.value" :ref="'form-modal-input-' + index" class="form-control">
        </label>
      </div>
    </div>
    <div class="modal-footer text-right">
      <button class="modal-default-button" ref="form-modal-button"
          @click="handleClick">
        {{ buttonText }}
      </button>
    </div>
  </Modal>
</template>
<style>
  @import "../../assets/style/modal.css"
</style>
<script>
/**
 * This modal takes in a list of form lines that will be displayed to the user as text input fields. When the
 * modal button is clicked, it will make an ajax request to the url passed in and call the callback function
 * passed in. Upon ajax success, it will close the modal. On ajax error, it will leave the modal open and display the
 * error message.
 */
import Modal from './Modal'
import Vue from 'vue'

export default {
  name: 'FormModal',
  props: {
    /** See Modal for explanation. */
    close: Function,
    /** See Modal for explanation. */
    show: Boolean,
    /** The error text to display in this modal. */
    errorText: String,
    /** The title of this modal. */
    title: String,
    /**
     * Initial form lines represents the values of the lines of the modal when it is first opened.
     * It is an array of objects of the form:
     * {
     *   id: An app-wide unique identifier for the form lines.
     *   name: The name of the property to set the value of when this form is saved.
     *   displayName: The text to display when this form is shown.
     *   value: The value of the property. This is bound to the model for the form.
     * }
     * When the form is saved, the callback function is called with the properties of the form saved in an object
     * with key 'name' and value 'value'.
     */
    initialFormLines: Array,
    /**
     * The properties to pass directly into the response returned on handleSave.
     */
    passThroughProps: Object,
    /**
     * The function to run when the button is clicked on this modal.
     * It is passed a parameter composed of two types of key/values:
     * 1. The form lines are returned with 'name' as the key and 'value' as the value.
     * 2. The passThroughProps are populated into the response with exactly the same key/value pairs.
     */
    callback: Function,
    /** The text to display on the action button. */
    buttonText: String,
    /**
     * Whether or not to show the error message.
     */
    shouldShowError: Boolean
  },
  watch: {
    initialFormLines () {
      this.formLines = this.initialFormLines
    },
    show () {
      if (this.show) {
        let self = this
        Vue.nextTick()
          .then(function () {
            let elements = self.$refs['form-modal-input-0']
            if (elements && elements.length > 0) {
              elements[0].focus()
            } else {
              self.$refs['form-modal-button'].focus()
            }
          })
      }
    }
  },
  data () {
    return {
      /*
       * This generates a copy of the initial form lines which can be modified as the user interacts with the modal.
       */
      formLines: this.initialFormLines
    }
  },
  methods: {
    handleClick () {
      let modalOutput = this.generateModalOutput()
      this.callback(modalOutput)
    },
    generateModalOutput () {
      let ret = Object.assign({}, this.passThroughProps)
      for (let index in this.formLines) {
        let formLine = this.formLines[index]
        ret[formLine.name] = formLine.value
      }
      return ret
    }
  },
  components: {
    Modal
  }
}
</script>
