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
      <div :key="word.name" v-for="word in unrecognizedWordsData">
        {{ word.name }}<br/>
        Category: <input v-model="word.category"/><br/>
        Should add to pantry:
        <input v-model="word.shouldAddToPantry" type="radio" value="unselected" :id="word.name + '-unselected'"/>
        <label :for="word.name + '-unselected'">Unselected</label>
        <input v-model="word.shouldAddToPantry" type="radio" value="true" :id="word.name + '-true'"/>
        <label :for="word.name + '-true'">True</label>
        <input v-model="word.shouldAddToPantry" type="radio" value=false :id="word.name + '-false'"/>
        <label :for="word.name + '-false'">False</label>
        <br/><br/>
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
    <div v-else>
      <button class="modal-default-button"
          @click="handleAddToKnownWordsButtonClick()">
        Add to Known Words
      </button>
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
    handleImportButtonClick: Function,
    /**
     * The function to be called to add input words to the known words table.
     */
    addToKnownWords: Function,
    /**
     * Shows the error text.
     */
    showErrorText: Function

  },
  data () {
    return {
      unrecognizedWordsData: []
    }
  },
  components: {
    Modal
  },
  methods: {
    handleAddToKnownWordsButtonClick () {
      for (let index in this.unrecognizedWordsData) {
        let word = this.unrecognizedWordsData[index]
        if (word.shouldAddToPantry === 'unselected') {
          this.showErrorText('Must select filter type for each word.')
          return
        }
      }
      this.addToKnownWords(this.groceryList, this.unrecognizedWordsData)
    }
  },
  watch: {
    unrecognizedWords () {
      let unrecognizedWordsData = []
      for (let index in this.unrecognizedWords) {
        let word = this.unrecognizedWords[index]
        unrecognizedWordsData.push({
          name: word,
          category: '',
          shouldAddToPantry: 'unselected'
        })
      }
      this.unrecognizedWordsData = unrecognizedWordsData
    }
  }
}
</script>
