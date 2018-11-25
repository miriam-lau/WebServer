<template>
  <div>
    <div class="nav-container">
      <nav :class="navigationClass" v-on:click.prevent>
        <a href="#" class="nav-pantry-grocery-lists" v-on:click="navigateToSubPath('grocery-lists')">Grocery Lists</a>
        <a href="#" class="nav-pantry-pantry-store" v-on:click="navigateToSubPath('pantry-store')">Pantry Store</a>
        <a href="#" class="nav-pantry-known-words" v-on:click="navigateToSubPath('known-words')">Known Words</a>
      </nav>
    </div>
    <div class="status" v-if="currentStatus != ''">
      {{ currentStatus }}
    </div>
    <div v-if="currentPage === 'grocery-lists'">
      <h2>Grocery Lists</h2>
      <div class="pantry-single-grocery-list" v-for="groceryList in groceryLists" :key="groceryList['id']">
        <div>
          {{ groceryList['title'] }}
          <font-awesome-icon icon="pencil-alt" class="pantry-icon"
              @click="showEditGroceryMetadataModal(groceryList)" />
          <font-awesome-icon icon="trash" class="pantry-icon"
              @click="showDeleteGroceryListModal(groceryList)" />
        </div>
        <div class="pantry-grocery-list-text">
          <EditableDiv
            :key="pantryGroceryListKey"
            :content="groceryList['list']"
            :handleUpdate="updateGroceryListText.bind(this, groceryList)"
          />
        </div>
        <div v-if="groceryList['saved']">
          Saved.
          <span v-if="groceryList['imported']">
            Imported.
          </span>
          <button @click="attemptAddToPantry(groceryList)">Add to Pantry</button>
        </div>
        <div v-else>
          Unsaved.
          <button @click="editGroceryList(groceryList)">Save</button>
          <button @click="cancelEditGroceryListText(groceryList)">Cancel</button>
        </div>
      </div>
      <input v-model="groceryListTitleToAdd" /> <button @click="addGroceryList">Add Grocery List</button>
      <ImportToPantryModal
        :close="closeImportModal"
        :show="shouldShowImportModal"
        :errorText="importModalErrorText"
        :alreadyInPantryWords="alreadyInPantryWords"
        :groceryList="groceryListToImport"
        :willImportWords="willImportWords"
        :willIgnoreWords="willIgnoreWords"
        :unrecognizedWords="unrecognizedWords"
        :handleImportButtonClick="this.addToPantry"
      />
    </div>
    <div v-else-if="currentPage === 'pantry-store'">
      <h2>Pantry</h2>
      <table class="table">
        <tr>
          <th>Name</th><th>Delete</th>
        </tr>
        <tr :key="pantryItem['item']" v-for="pantryItem in pantry">
          <td>{{ pantryItem['item'] }}</td>
          <td><font-awesome-icon icon="trash" class="icon"
              @click="showDeletePantryItemModal(pantryItem)" />
          </td>
        </tr>
      </table>
      <input v-model="pantryItemToAdd" /> <button @click="addPantryItem">Add Item</button>
    </div>
    <div v-else-if="currentPage === 'known-words'">
      <h2>Known Words</h2>
      <table class="table">
        <tr>
          <th>Name</th><th>Addable to Pantry</th><th>Delete</th>
        </tr>
        <tr :key="knownWord['word']" v-for="knownWord in knownWords">
          <td>{{ knownWord['word'] }}</td>
          <td>{{ knownWord['should_save'] }}</td>
          <td><font-awesome-icon icon="trash" class="icon"
              @click="showDeleteKnownWordModal(knownWord)" />
          </td>
        </tr>
      </table>
      <input v-model="knownWordToAdd" />
      <select v-model="knownWordToAddShouldSave">
        <option>True</option>
        <option>False</option>
      </select>
      <button @click="addKnownWord">Add Word</button>
    </div>
    <FormModal
      :show="shouldShowModal"
      :close="closeModal"
      :title="modalTitle"
      :initialFormLines="modalFormLines"
      :errorText="modalErrorText"
      :handleButtonClick="modalCallback"
      :passThroughProps="modalPassThroughProps"
      :buttonText="modalButtonText" />
  </div>
</template>
<style>
  @import "../assets/style/pantry.css"
</style>
<script>
import EditableDiv from './shared/EditableDiv'
import FormModal from './shared/FormModal'
import ImportToPantryModal from './pantry_page/ImportToPantryModal'
import axios from 'axios'
import { getFullBackendUrlForPath, createFormModalEntry } from '../common/utils'

const GET_PANTRY_PAGE_URL = getFullBackendUrlForPath('/get_pantry_page')
const EDIT_GROCERY_LIST_METADATA_URL = getFullBackendUrlForPath('/edit_grocery_list_metadata')
const DELETE_GROCERY_LIST_URL = getFullBackendUrlForPath('/delete_grocery_list')
const EDIT_GROCERY_LIST_URL = getFullBackendUrlForPath('/edit_grocery_list')
const ADD_GROCERY_LIST_URL = getFullBackendUrlForPath('/add_grocery_list')
const ATTEMPT_IMPORT_GROCERY_LIST_TO_PANTRY_URL = getFullBackendUrlForPath('/attempt_add_to_pantry')
const IMPORT_GROCERY_LIST_TO_PANTRY_URL = getFullBackendUrlForPath('/add_to_pantry')
const DELETE_PANTRY_ITEM_URL = getFullBackendUrlForPath('/delete_pantry_item')
const ADD_PANTRY_ITEM_URL = getFullBackendUrlForPath('/add_pantry_item')
const DELETE_KNOWN_WORD_URL = getFullBackendUrlForPath('/delete_known_word')
const ADD_KNOWN_WORD_URL = getFullBackendUrlForPath('/add_known_word')

export default {
  name: 'PantryPage',
  data () {
    return {
      groceryLists: [],
      pantry: [],
      knownWords: [],
      groceryListTitleToAdd: '',
      pantryItemToAdd: '',
      knownWordToAdd: '',
      knownWordToAddShouldSave: 'True',
      currentStatus: '',
      modalTitle: '',
      modalFormLines: [],
      groceryListToImport: {},
      modalPassThroughProps: {},
      modalCallback: Function,
      modalButtonText: '',
      modalErrorText: '',
      pantryGroceryListKey: 0,
      shouldShowModal: false,
      shouldShowImportModal: false,
      timeoutHandle: null,
      currentPage: '',
      importModalErrorText: '',
      willImportWords: [],
      willIgnoreWords: [],
      unrecognizedWords: [],
      alreadyInPantryWords: []
    }
  },
  created () {
    this.updatePantryPageDisplay()
    this.setCurrentPage()
  },
  components: {
    FormModal, EditableDiv, ImportToPantryModal
  },
  computed: {
    navigationClass () {
      switch (this.currentPage) {
        case 'grocery-lists':
          return 'nav-pantry-grocery-lists'
        case 'pantry-store':
          return 'nav-pantry-pantry-store'
        case 'known-words':
          return 'nav-pantry-known-words'
      }
    }
  },
  watch: {
    '$route': function () {
      this.setCurrentPage()
    }
  },
  methods: {
    attemptAddToPantry (groceryList) {
      axios.post(
        ATTEMPT_IMPORT_GROCERY_LIST_TO_PANTRY_URL,
        { id: groceryList['id'] })
        .then(response => {
          this.showImportModal(groceryList, response['data']['add'], response['data']['ignore'], response['data']['unrecognized'],
            response['data']['already_in_pantry'])
        })
        .catch(error => {
          this.setCurrentStatus('An error occurred during import')
          console.log(error)
        })
    },
    navigateToSubPath (path) {
      this.$router.push({ path: '/pantry/' + path })
    },
    setCurrentPage () {
      let subPath = this.$route.path.split('/')[2]
      if (!subPath) {
        subPath = 'grocery-lists'
      }
      this.currentPage = subPath
    },
    updateGroceryListText (groceryList, newText) {
      if (groceryList['saved']) {
        groceryList['saved'] = false
        groceryList['backedUpListText'] = groceryList['list']
      }
      groceryList['list'] = newText.target.innerText
    },
    cancelEditGroceryListText (groceryList) {
      if (!groceryList['saved']) {
        groceryList['saved'] = true
        groceryList['list'] = groceryList['backedUpListText']
        delete groceryList['backedUpListText']
        this.pantryGroceryListKey += 1 // Force a re-render of the EditableDiv of this grocery list.
      }
    },
    closeModal () {
      this.shouldShowModal = false
    },
    closeImportModal () {
      this.shouldShowImportModal = false
    },
    showModal (title, formLines, passThroughProps, callback, buttonText) {
      this.modalTitle = title
      this.modalFormLines = formLines
      this.modalPassThroughProps = passThroughProps
      this.modalCallback = callback
      this.modalButtonText = buttonText
      this.modalErrorText = ''
      this.shouldShowModal = true
    },
    showImportModal (groceryList, willImportWords, willIgnoreWords, unrecognizedWords, alreadyInPantryWords) {
      this.groceryListToImport = groceryList
      this.willImportWords = willImportWords
      this.willIgnoreWords = willIgnoreWords
      this.unrecognizedWords = unrecognizedWords
      this.alreadyInPantryWords = alreadyInPantryWords
      this.importModalErrorText = ''
      this.shouldShowImportModal = true
    },
    showEditGroceryMetadataModal (groceryList) {
      let modalFormLines = [
        createFormModalEntry(
          'edit-grocery-metadata-modal-title-' + groceryList['id'], 'title', 'Title:', groceryList['title'])
      ]
      this.showModal(
        'Editing ' + groceryList['title'],
        modalFormLines,
        groceryList,
        this.editGroceryListMetadata,
        'Save')
    },
    showDeleteGroceryListModal (groceryList) {
      this.showModal(
        'Deleting ' + groceryList['title'],
        [],
        { id: groceryList['id'] },
        this.deleteGroceryList,
        'Delete')
    },
    showDeletePantryItemModal (pantryItem) {
      this.showModal(
        'Deleting ' + pantryItem['item'],
        [],
        { item: pantryItem['item'] },
        this.deletePantryItem,
        'Delete')
    },
    showDeleteKnownWordModal (knownWord) {
      this.showModal(
        'Deleting ' + knownWord['word'],
        [],
        { word: knownWord['word'] },
        this.deleteKnownWord,
        'Delete')
    },
    addToPantry (groceryList) {
      axios.post(
        IMPORT_GROCERY_LIST_TO_PANTRY_URL,
        { id: groceryList['id'] })
        .then(response => {
          this.updatePantryPageDisplay()
          this.closeImportModal()
          this.setCurrentStatus('Imported ' + groceryList['title'] + ' to the pantry.')
        })
        .catch(error => {
          this.importModalErrorText = 'An error occurred during import.'
          console.log(error)
        })
    },
    editGroceryListMetadata (groceryList) {
      axios.post(
        EDIT_GROCERY_LIST_METADATA_URL,
        {
          id: groceryList['id'],
          title: groceryList['title']
        })
        .then(response => {
          let currentGroceryListIndex =
            this.groceryLists.findIndex(groceryList => groceryList['id'] === response['data']['id'])
          let newGroceryListItem = this.groceryLists[currentGroceryListIndex]
          newGroceryListItem['title'] = response['data']['title']
          this.groceryLists.splice(currentGroceryListIndex, 1, newGroceryListItem)
          this.closeModal()
          this.setCurrentStatus('Saved ' + groceryList['title'])
        })
        .catch(error => {
          this.modalErrorText = 'An error occurred during edit.'
          console.log(error)
        })
    },
    editGroceryList (groceryList) {
      axios.post(EDIT_GROCERY_LIST_URL, {id: groceryList['id'], list: groceryList['list']})
        .then(response => {
          let currentGroceryListIndex =
            this.groceryLists.findIndex(groceryList => groceryList['id'] === response['data']['id'])
          response['data']['saved'] = true
          this.groceryLists.splice(currentGroceryListIndex, 1, response['data'])
          this.setCurrentStatus('Saved ' + groceryList['title'])
        })
        .catch(error => {
          this.modalErrorText = 'An error occurred during edit.'
          console.log(error)
        })
    },
    deleteGroceryList (groceryList) {
      axios.post(DELETE_GROCERY_LIST_URL, {id: groceryList['id']}).then(response => {
        let deletedGroceryList = response['data']
        this.groceryLists.splice(
          this.groceryLists.findIndex(groceryList => groceryList['id'] === deletedGroceryList['id']), 1)
        this.closeModal()
        this.setCurrentStatus('Deleted ' + deletedGroceryList['title'])
      })
        .catch(error => {
          this.modalErrorText = 'An error occurred during delete.'
          console.log(error)
        })
    },
    deletePantryItem (pantryItem) {
      axios.post(DELETE_PANTRY_ITEM_URL, {item: pantryItem['item']}).then(response => {
        let deletedPantryItem = response['data']
        this.pantry.splice(
          this.pantry.findIndex(pantry => pantry['item'] === deletedPantryItem['item']), 1)
        this.closeModal()
        this.setCurrentStatus('Deleted ' + deletedPantryItem['item'] + ' from the pantry')
      })
        .catch(error => {
          this.modalErrorText = 'An error occurred during delete.'
          console.log(error)
        })
    },
    addPantryItem () {
      axios.post(ADD_PANTRY_ITEM_URL, {item: this.pantryItemToAdd})
        .then(
          response => {
            this.pantryItemToAdd = ''
            let pantryItem = response['data']
            this.pantry.push(pantryItem)
            this.setCurrentStatus('Added ' + pantryItem['item'])
          })
        .catch(error => {
          this.modalErrorText = 'An error occurred during add.'
          this.setCurrentStatus('Error adding ' + this.pantryItemToAdd)
          console.log(error)
        })
    },
    deleteKnownWord (knownWord) {
      axios.post(DELETE_KNOWN_WORD_URL, {word: knownWord['word']}).then(response => {
        let deletedKnownWord = response['data']
        this.knownWords.splice(
          this.knownWords.findIndex(knownWord => knownWord['word'] === deletedKnownWord['word']), 1)
        this.closeModal()
        this.setCurrentStatus('Deleted ' + deletedKnownWord['word'] + ' from the list of known words')
      })
        .catch(error => {
          this.modalErrorText = 'An error occurred during delete.'
          console.log(error)
        })
    },
    addKnownWord () {
      axios.post(ADD_KNOWN_WORD_URL, {word: this.knownWordToAdd, should_save: this.knownWordToAddShouldSave === 'True'})
        .then(
          response => {
            this.knownWordToAdd = ''
            let knownWord = response['data']
            this.knownWords.push(knownWord)
            this.setCurrentStatus('Added ' + knownWord['word'])
          })
        .catch(error => {
          this.modalErrorText = 'An error occurred during add.'
          this.setCurrentStatus('Error adding ' + this.knownWordToAdd)
          console.log(error)
        })
    },
    addGroceryList () {
      axios.post(ADD_GROCERY_LIST_URL, {title: this.groceryListTitleToAdd})
        .then(
          response => {
            this.groceryListTitleToAdd = ''
            let groceryList = response['data']
            this.groceryLists.push(groceryList)
            this.closeModal()
            this.setCurrentStatus('Added ' + groceryList['title'])
          })
        .catch(error => {
          this.modalErrorText = 'An error occurred during add.'
          console.log(error)
        })
    },
    updatePantryPageDisplay () {
      axios.post(GET_PANTRY_PAGE_URL).then(
        response => {
          this.groceryLists = response['data']['grocery_lists']
          for (let index in this.groceryLists) {
            this.groceryLists[index]['saved'] = true
          }
          this.pantry = response['data']['pantry']
          this.knownWords = response['data']['known_words']
        })
    },
    setCurrentStatus (text) {
      this.currentStatus = text
      window.clearTimeout(this.timeoutHandle)
      this.timeoutHandle = setTimeout(function () { this.currentStatus = '' }.bind(this), 10000)
    }
  }
}
</script>
