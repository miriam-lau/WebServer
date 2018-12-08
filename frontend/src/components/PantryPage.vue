<template>
  <div>
    <div class="nav-container">
      <nav :class="navigationClass" v-on:click.prevent>
        <a href="#" class="nav-pantry-grocery-lists" v-on:click="navigateToSubPath('grocery-lists')">Grocery Lists</a>
        <a href="#" class="nav-pantry-pantry-store" v-on:click="navigateToSubPath('pantry-store')">Pantry Store</a>
        <a href="#" class="nav-pantry-known-words" v-on:click="navigateToSubPath('known-words')">Known Words</a>
        <a href="#" class="nav-pantry-categories" v-on:click="navigateToSubPath('categories')">Categories</a>
      </nav>
    </div>
    <ButterBar
      :message="butterBar_message"
      :css="butterBar_css"
    />
    <div v-if="currentPage === 'grocery-lists'">
      <h2>Grocery Lists</h2>
      <div class="input-form">
        <input v-model="groceryListTitleToAdd" ref="grocery-list-to-add" />
        <input v-model="groceryListDateToAdd" type="date"/>
        <button @click="addGroceryList">Add Grocery List</button>
      </div>
      <div v-masonry transition-duration="0" item-selector=".item">
        <div v-masonry-tile class="item textarea-div" v-for="groceryList in groceryLists" :key="groceryList['id']">
          <div class="textarea-title">
            {{ groceryList['title'] }}: {{ getDisplayDate(groceryList['date']) }}
            <font-awesome-icon icon="pencil-alt" class="icon"
                @click="showEditGroceryMetadataModal(groceryList)" />
            <font-awesome-icon icon="trash" class="icon"
                @click="showDeleteGroceryListModal(groceryList)" />
          </div>
          <div class="textarea-text">
            <EditableDiv
              :key="pantryGroceryListKey"
              :content="groceryList['list']"
              :handleUpdate="updateGroceryListText.bind(this, groceryList)"
            />
          </div>
          <div v-if="groceryList['saved']">
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
      </div>
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
      <div class="input-form">
        <input v-model="pantryItemToAdd" ref="pantry-item-to-add" /> <button @click="addPantryItem">Add Item</button>
      </div>
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
    </div>
    <div v-else-if="currentPage === 'known-words'">
      <h2>Known Words</h2>
      <div class="input-form">
        Word: <input v-model="knownWordToAdd" ref="known-word-to-add" />
        Category: <input v-model="knownWordToAddCategory"/>
        <select v-model="knownWordToAddShouldSave">
          <option>True</option>
          <option>False</option>
        </select>
        <button @click="addKnownWord">Add Word</button>
      </div>
      <table class="table">
        <tr>
          <th>Name</th><th>Category</th><th>Addable to Pantry</th><th>Delete</th>
        </tr>
        <tr :key="knownWord['word']" v-for="knownWord in knownWords">
          <td>{{ knownWord['word'] }}</td>
          <td>{{ knownWord['category'] }}</td>
          <td>{{ knownWord['should_save'] }}</td>
          <td><font-awesome-icon icon="trash" class="icon"
              @click="showDeleteKnownWordModal(knownWord)" />
          </td>
        </tr>
      </table>
    </div>
    <div v-else-if="currentPage === 'categories'">
      <h2>Category</h2>
      <div class="input-form">
        <input v-model="categoryToAdd" ref="category-to-add" /> <button @click="addCategory">Add Category</button>
      </div>
      <table class="table">
        <tr>
          <th>Name</th><th>Delete</th>
        </tr>
        <tr :key="category['word']" v-for="category in categories">
          <td>{{ category['word'] }}</td>
          <td><font-awesome-icon icon="trash" class="icon"
              @click="showDeleteCategoryModal(category)" />
          </td>
        </tr>
      </table>
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
import { setButterBarMessage, ButterBarType, callAxiosAndSetButterBar } from '../common/butterbar_component'

import FormModal from './shared/FormModal'
import { showModal, createFormModalEntry, generateAxiosModalCallback } from '../common/form_modal_component'

import EditableDiv from './shared/EditableDiv'
import ImportToPantryModal from './pantry_page/ImportToPantryModal'
import axios from 'axios'
import { getFullBackendUrlForPath, getDisplayDate } from '../common/utils'

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
const DELETE_CATEGORY_URL = getFullBackendUrlForPath('/delete_category')
const ADD_CATEGORY_URL = getFullBackendUrlForPath('/add_category')

export default {
  name: 'PantryPage',
  data () {
    return {
      groceryLists: [],
      pantry: [],
      categories: [],
      knownWords: [],
      groceryListTitleToAdd: '',
      groceryListDateToAdd: '',
      pantryItemToAdd: '',
      categoryToAdd: '',
      knownWordToAdd: '',
      knownWordToAddCategory: '',
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
        case 'categories':
          return 'nav-pantry-categories'
      }
    },
    allGroceryListsSaved: function () {
      for (let index in this.groceryLists) {
        if (!this.groceryLists[index]['saved']) {
          return false
        }
      }
      return true
    }
  },
  watch: {
    '$route': function () {
      this.setCurrentPage()
    },
    allGroceryListsSaved: function (oldValue, newValue) {
      if (newValue) {
        window.onbeforeunload = function () { return '' }
      } else {
        window.onbeforeunload = function () { return null }
      }
    }
  },
  beforeRouteLeave (to, from, next) {
    if (!this.allGroceryListsSaved) {
      const answer = window.confirm('You haven\'t saved your changes. Are you sure you want to leave?')
      if (answer) {
        window.onbeforeunload = function () { return null }
        next()
      } else {
        next(false)
      }
    } else {
      next()
    }
  },
  methods: {
    formModal_close () {
      this.formModal_show = false
    },
    getDisplayDate (date) {
      return getDisplayDate(date)
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
      this.$redrawVueMasonry()
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
          'edit-grocery-metadata-modal-title-' + groceryList['id'], 'title', 'Title:', groceryList['title']),
        createFormModalEntry(
          'edit-grocery-metadata-modal-date-' + groceryList['id'], 'date', 'Date:', groceryList['date'])
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
    showDeleteCategoryModal (category) {
      showModal(
        this,
        'Deleting ' + category['word'],
        [],
        { word: category['word'] },
        generateAxiosModalCallback(this, DELETE_CATEGORY_URL, this.deleteCategory),
        'Delete',
        'Error deleting ' + category['word'])
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
      callAxiosAndSetButterBar(
        this, IMPORT_GROCERY_LIST_TO_PANTRY_URL, { id: groceryList['id'] },
        'Imported ' + groceryList['title'] + ' to the pantry.',
        'Error importing ' + groceryList['title'] + ' to the pantry.',
        response => {
          this.updatePantryPageDisplay()
          this.closeImportModal()
        })
    },
    editGroceryListMetadata (response) {
      let currentGroceryListIndex =
        this.groceryLists.findIndex(groceryList => groceryList['id'] === response['data']['id'])
      let newGroceryListItem = this.groceryLists[currentGroceryListIndex]
      let oldTitle = this.groceryLists[currentGroceryListIndex]['title']
      newGroceryListItem['title'] = response['data']['title']
      newGroceryListItem['date'] = response['data']['date']
      this.groceryLists.splice(currentGroceryListIndex, 1, newGroceryListItem)
      setButterBarMessage(this, 'Saved the title of ' + oldTitle, ButterBarType.INFO)
    },
    editGroceryList (groceryList) {
      callAxiosAndSetButterBar(
        this, EDIT_GROCERY_LIST_URL, { id: groceryList['id'], list: groceryList['list'] },
        'Saved the contents of ' + groceryList['title'],
        'Error saving the contents of ' + groceryList['title'],
        response => {
          let currentGroceryListIndex =
            this.groceryLists.findIndex(groceryList => groceryList['id'] === response['data']['id'])
          response['data']['saved'] = true
          this.groceryLists.splice(currentGroceryListIndex, 1, response['data'])
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
      callAxiosAndSetButterBar(
        this, ADD_PANTRY_ITEM_URL, { item: this.pantryItemToAdd },
        'Added ' + this.pantryItemToAdd + ' to the pantry',
        'Error adding ' + this.pantryItemToAdd + ' to the pantry',
        response => {
          this.pantryItemToAdd = ''
          let pantryItem = response['data']
          this.pantry.push(pantryItem)
          this.$refs['pantry-item-to-add'].focus()
        })
    },
    deleteCategory (response) {
      let deletedCategory = response['data']
      this.categories.splice(
        this.categories.findIndex(category => category['word'] === deletedCategory['word']), 1)
      setButterBarMessage(this, 'Deleted ' + deletedCategory['word'] + ' from the pantry', ButterBarType.INFO)
    },
    addCategory () {
      callAxiosAndSetButterBar(
        this, ADD_CATEGORY_URL, { word: this.categoryToAdd },
        'Added ' + this.categoryToAdd + ' to the categories',
        'Error adding ' + this.categoryToAdd + ' to the categories',
        response => {
          this.categoryToAdd = ''
          let category = response['data']
          this.categories.push(category)
          this.$refs['category-to-add'].focus()
        })
    },
    deleteKnownWord (response) {
      let deletedKnownWord = response['data']
      this.knownWords.splice(
        this.knownWords.findIndex(knownWord => knownWord['word'] === deletedKnownWord['word']), 1)
      setButterBarMessage(this, 'Deleted ' + deletedKnownWord['word'] + ' from the list of known words', ButterBarType.INFO)
    },
    addKnownWord () {
      callAxiosAndSetButterBar(
        this, ADD_KNOWN_WORD_URL,
        {
          word: this.knownWordToAdd,
          category: this.knownWordToAddCategory,
          should_save: this.knownWordToAddShouldSave === 'True'
        },
        'Added ' + this.knownWordToAdd + ' to the list of known words',
        'Error adding ' + this.knownWordToAdd + ' to the list of known words',
        response => {
          this.knownWordToAdd = ''
          this.knownWordToAddCategory = ''
          let knownWord = response['data']
          this.knownWords.push(knownWord)
          this.$refs['known-word-to-add'].focus()
        })
    },
    addGroceryList () {
      callAxiosAndSetButterBar(
        this, ADD_GROCERY_LIST_URL, { title: this.groceryListTitleToAdd, date: this.groceryListDateToAdd },
        'Added ' + this.groceryListTitleToAdd + ' to the grocery lists',
        'Error adding ' + this.groceryListTitleToAdd + ' to the grocery lists',
        response => {
          this.groceryListTitleToAdd = ''
          this.groceryListDateToAdd = ''
          let groceryList = response['data']
          response['data']['saved'] = true
          this.groceryLists.push(groceryList)
          this.$refs['grocery-list-to-add'].focus()
        })
    },
    updatePantryPageDisplay () {
      axios.post(GET_PANTRY_PAGE_URL).then(
        response => {
          for (let index in response['data']['grocery_lists']) {
            response['data']['grocery_lists'][index]['saved'] = true
          }
          this.groceryLists = response['data']['grocery_lists']
          this.categories = response['data']['categories']
          this.pantry = response['data']['pantry']
          this.knownWords = response['data']['known_words']
        })
    }
  }
}
</script>
