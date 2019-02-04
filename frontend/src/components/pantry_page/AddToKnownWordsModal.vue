<template>
  <Modal :show="show" :close="close">
    <div class="modal-header">
     <h2>Add known words</h2>
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
    </div>
    <button class="modal-default-button"
        @click="handleAddToKnownWordsButtonClick()">
      Add to Known Words
    </button>
  </Modal>
</template>
<style>
  @import "../../assets/style/modal.css"
</style>
<script>
import Modal from '../shared/Modal'

export default {
  name: 'AddToKnownWordsModal',
  props: {
    /** See Modal for explanation. */
    close: Function,
    /** See Modal for explanation. */
    show: Boolean,
    groceryList: Object,
    /** The error text to display in this modal. */
    errorText: String,
    /**
     * The unrecognized words.
     */
    unrecognizedWords: Array,
    /**
     * The function to be called to add input words to the known words table.
     */
    addToKnownWords: Function,
    /**
     * Shows the error text.
     */
    showErrorText: Function,
    /**
     * The callback to call after words are added.
     */
    callback: Function
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
      this.close()
      this.addToKnownWords(this.groceryList, this.unrecognizedWordsData, this.callback)
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
