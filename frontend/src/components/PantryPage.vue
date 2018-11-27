<template>
  <div>
    <div class="nav-container">
      <nav :class="navigationClass" v-on:click.prevent>
        <a href="#" class="nav-pantry-grocery-lists" v-on:click="navigateToSubPath('grocery-lists')">Grocery Lists</a>
        <a href="#" class="nav-pantry-pantry-store" v-on:click="navigateToSubPath('pantry-store')">Pantry Store</a>
        <a href="#" class="nav-pantry-known-words" v-on:click="navigateToSubPath('known-words')">Known Words</a>
      </nav>
    </div>
    <ButterBar
      :message="butterBar_message"
      :css="butterBar_css"
    />
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
      :show="formModal_show"
      :close="formModal_close"
      :title="formModal_title"
      :initialFormLines="formModal_formLines"
      :errorText="formModal_errorText"
      :callback="formModal_callback"
      :passThroughProps="formModal_passThroughProps"
      :buttonText="formModal_buttonText"
      :shouldShowError="formModal_shouldShowError" />
  </div>
</template>
<style>
  @import "../assets/style/pantry.css"
</style>
<script>
import ButterBar from './shared/ButterBar'
import { setButterBarMessage, ButterBarType } from '../common/butterbar_component'

import FormModal from './shared/FormModal'
import { showModal, createFormModalEntry, generateAxiosModalCallback } from '../common/form_modal_component'

import EditableDiv from './shared/EditableDiv'
import ImportToPantryModal from './pantry_page/ImportToPantryModal'
import axios from 'axios'
import { getFullBackendUrlForPath } from '../common/utils'

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
      groceryListToImport: {},
      pantryGroceryListKey: 0,
      shouldShowImportModal: false,
      currentPage: '',
      importModalErrorText: '',
      willImportWords: [],
      willIgnoreWords: [],
      unrecognizedWords: [],
      alreadyInPantryWords: [],

      formModal_show: false,
      formModal_title: '',
      formModal_formLines: [],
      formModal_errorText: '',
      formModal_callback: Function,
      formModal_passThroughProps: {},
      formModal_buttonText: '',
      formModal_shouldShowError: false,

      butterBar_message: '',
      butterBar_css: ''
    }
  },
  created () {
    this.updatePantryPageDisplay()
    this.setCurrentPage()
  },
  components: {
    FormModal, EditableDiv, ImportToPantryModal, ButterBar
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
    formModal_close () {
      this.formModal_show = false
    },
    attemptAddToPantry (groceryList) {
      axios.post(
        ATTEMPT_IMPORT_GROCERY_LIST_TO_PANTRY_URL,
        { id: groceryList['id'] })
        .then(response => {
          this.showImportModal(groceryList, response['data']['add'], response['data']['ignore'], response['data']['unrecognized'],
            response['data']['already_in_pantry'])
        })
        .catch(error => {
          setButterBarMessage(this, 'An error occurred during import', ButterBarType.ERROR)
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
      }
      groceryList['list'] = newText.target.innerText
    },
    closeImportModal () {
      this.shouldShowImportModal = false
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
      showModal(
        this,
        'Editing ' + groceryList['title'],
        modalFormLines,
        groceryList,
        generateAxiosModalCallback(this, EDIT_GROCERY_LIST_METADATA_URL, this.editGroceryListMetadata),
        'Save',
        'Error saving ' + groceryList['title'])
    },
    showDeleteGroceryListModal (groceryList) {
      showModal(
        this,
        'Deleting ' + groceryList['title'],
        [],
        { id: groceryList['id'] },
        generateAxiosModalCallback(this, DELETE_GROCERY_LIST_URL, this.deleteGroceryList),
        'Delete',
        'Error deleting ' + groceryList['title'])
    },
    showDeletePantryItemModal (pantryItem) {
      showModal(
        this,
        'Deleting ' + pantryItem['item'],
        [],
        { item: pantryItem['item'] },
        generateAxiosModalCallback(this, DELETE_PANTRY_ITEM_URL, this.deletePantryItem),
        'Delete',
        'Error deleting ' + pantryItem['item'])
    },
    showDeleteKnownWordModal (knownWord) {
      showModal(
        this,
        'Deleting ' + knownWord['word'],
        [],
        { word: knownWord['word'] },
        generateAxiosModalCallback(this, DELETE_KNOWN_WORD_URL, this.deleteKnownWord),
        'Delete',
        'Error deleting ' + knownWord['word'])
    },
    addToPantry (groceryList) {
      axios.post(
        IMPORT_GROCERY_LIST_TO_PANTRY_URL,
        { id: groceryList['id'] })
        .then(response => {
          this.updatePantryPageDisplay()
          this.closeImportModal()
          setButterBarMessage(this, 'Imported ' + groceryList['title'] + ' to the pantry.', ButterBarType.INFO)
        })
        .catch(error => {
          this.importModalErrorText = 'An error occurred during import.'
          console.log(error)
        })
    },
    editGroceryListMetadata (response) {
      let currentGroceryListIndex =
        this.groceryLists.findIndex(groceryList => groceryList['id'] === response['data']['id'])
      let newGroceryListItem = this.groceryLists[currentGroceryListIndex]
      let oldTitle = this.groceryLists[currentGroceryListIndex]['title']
      newGroceryListItem['title'] = response['data']['title']
      this.groceryLists.splice(currentGroceryListIndex, 1, newGroceryListItem)
      setButterBarMessage(this, 'Saved the title of ' + oldTitle, ButterBarType.INFO)
    },
    editGroceryList (groceryList) {
      axios.post(EDIT_GROCERY_LIST_URL, {id: groceryList['id'], list: groceryList['list']})
        .then(response => {
          let currentGroceryListIndex =
            this.groceryLists.findIndex(groceryList => groceryList['id'] === response['data']['id'])
          response['data']['saved'] = true
          this.groceryLists.splice(currentGroceryListIndex, 1, response['data'])
          setButterBarMessage(this, 'Saved the contents of ' + groceryList['title'], ButterBarType.INFO)
        })
        .catch(error => {
          this.modalErrorText = 'An error occurred during edit.'
          console.log(error)
        })
    },
    deleteGroceryList (response) {
      let deletedGroceryList = response['data']
      this.groceryLists.splice(
        this.groceryLists.findIndex(groceryList => groceryList['id'] === deletedGroceryList['id']), 1)
      setButterBarMessage(this, 'Deleted ' + deletedGroceryList['title'], ButterBarType.INFO)
    },
    deletePantryItem (response) {
      let deletedPantryItem = response['data']
      this.pantry.splice(
        this.pantry.findIndex(pantry => pantry['item'] === deletedPantryItem['item']), 1)
      setButterBarMessage(this, 'Deleted ' + deletedPantryItem['item'] + ' from the pantry', ButterBarType.INFO)
    },
    addPantryItem () {
      axios.post(ADD_PANTRY_ITEM_URL, {item: this.pantryItemToAdd})
        .then(
          response => {
            this.pantryItemToAdd = ''
            let pantryItem = response['data']
            this.pantry.push(pantryItem)
            setButterBarMessage(this, 'Added ' + pantryItem['item'] + ' to the pantry', ButterBarType.INFO)
          })
        .catch(error => {
          this.modalErrorText = 'An error occurred during add.'
          setButterBarMessage(this, 'Error adding ' + this.pantryItemToAdd, ButterBarType.ERROR)
          console.log(error)
        })
    },
    deleteKnownWord (response) {
      let deletedKnownWord = response['data']
      this.knownWords.splice(
        this.knownWords.findIndex(knownWord => knownWord['word'] === deletedKnownWord['word']), 1)
      setButterBarMessage(this, 'Deleted ' + deletedKnownWord['word'] + ' from the list of known words', ButterBarType.INFO)
    },
    addKnownWord () {
      axios.post(ADD_KNOWN_WORD_URL, {word: this.knownWordToAdd, should_save: this.knownWordToAddShouldSave === 'True'})
        .then(
          response => {
            this.knownWordToAdd = ''
            let knownWord = response['data']
            this.knownWords.push(knownWord)
            setButterBarMessage(this, 'Added ' + knownWord['word'] + ' to the list of known words', ButterBarType.INFO)
          })
        .catch(error => {
          this.modalErrorText = 'An error occurred during add.'
          setButterBarMessage(this, 'Error adding ' + this.knownWordToAdd, ButterBarType.ERROR)
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
            setButterBarMessage(this, 'Added ' + groceryList['title'], ButterBarType.INFO)
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
    }
  }
}
</script>
