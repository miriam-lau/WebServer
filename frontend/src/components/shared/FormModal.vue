<template>
  <Modal :show="show" @close="close">
    <div class="modal-header">
     <h3>{{ title }}</h3>
    </div>
    <div class="modal-body">
      <div :key="formLine['id']" v-for="formLine in formLines">
        <label class="form-label">
          {{ formLine['displayName'] }}
          <input v-model="formLine['value']" class="form-control">
        </label>
      </div>
    </div>
    <div class="modal-footer text-right">
      <button class="modal-default-button"
          @click="handleSave(convertFormLines(formLines))">
        {{ buttonText }}
      </button>
    </div>
  </Modal>
</template>
<style>
  @import "../../assets/style/modal.css"
</style>
<script>
import Modal from './Modal'

export default {
  name: 'CurrentDocumentsModal',
  props: {
    show: Boolean,
    title: String,
    /**
     * Form lines is an array of objects of the form:
     * {
     *   id: An app-wide unique identifier for the form lines.
     *   name: The name of the property to set the value of when this form is saved.
     *   displayName: The text to display when this form is shown.
     *   value: The value of the property. This is bound to the model for the form.
     * }
     * When the form is saved, the handleSave function is called with the properties of the form saved in an object
     * with key 'name' and value 'value'.
     */
    initialFormLines: Array,
    /** The function to run when the save button is clicked on this modal. */
    handleSave: Function,
    /** The text to display on the action button. */
    buttonText: String
  },
  watch: {
    initialFormLines () {
      this.formLines = this.initialFormLines
    }
  },
  data () {
    return {
      formLines: this.initialFormLines
    }
  },
  methods: {
    convertFormLines (formLines) {
      let ret = {}
      for (let index in formLines) {
        let formLine = formLines[index]
        ret[formLine['name']] = formLine['value']
      }
      return ret
    },
    close () {
      this.$emit('close')
    }
  },
  components: {
    Modal
  }
}
</script>
