<template>
  <Modal :show="show" :close="close">
    <div class="modal-header">
     <h2>Importing to Pantry</h2>
    </div>
    <div class="modal-error" v-if="errorText != ''">
      {{ errorText }}
    </div>
    <div class="modal-body">
      <h4>Unrecognized Items</h4>
      <div :key="word" v-for="word in unrecognizedWords">
        {{ word }}
      </div>
      <h4>Items to Import</h4>
      <div :key="word" v-for="word in willImportWords">
        {{ word }}
      </div>
      <h4>Items already in pantry</h4>
      <div :key="word" v-for="word in alreadyInPantryWords">
        {{ word }}
      </div>
      <h4>Items to Ignore</h4>
      <div :key="word" v-for="word in willIgnoreWords">
        {{ word }}
      </div>
    </div>
    <div v-if="unrecognizedWords.length == 0" class="modal-footer text-right">
      <button class="modal-default-button"
          @click="handleImportButtonClick(groceryList)">
        Confirm
      </button>
    </div>
    <div v-else class="import-modal-import-failed">
      Import failed - unrecognized items
    </div>
  </Modal>
</template>
<style>
  @import "../../assets/style/modal.css"
</style>
<script>
import Modal from '../shared/Modal'

export default {
  name: 'ImportToPantryModal',
  props: {
    /** See Modal for explanation. */
    close: Function,
    /** See Modal for explanation. */
    show: Boolean,
    groceryList: Object,
    /** The error text to display in this modal. */
    errorText: String,
    /**
     * Words that will be added to the pantry.
     */
    willImportWords: Array,
    /**
     * Words that will be ignored.
     */
    willIgnoreWords: Array,
    /**
     * The unrecognized words.
     */
    unrecognizedWords: Array,
    /**
     * The words already in the pantry.
     */
    alreadyInPantryWords: Array,
    /**
     * The function to run when the import button is clicked.
     */
    handleImportButtonClick: Function
  },
  data () {
    return {
    }
  },
  components: {
    Modal
  }
}
</script>
