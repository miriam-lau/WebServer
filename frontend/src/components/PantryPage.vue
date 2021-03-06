<template>
  <div>
    <div class="nav-container">
      <nav :class="navigationClass" v-on:click.prevent>
        <a
          href="#"
          class="nav-pantry-grocery-lists"
          v-on:click="navigateToSubPath('grocery-lists')"
        >Grocery Lists</a>
        <a
          href="#"
          class="nav-pantry-pantry-store"
          v-on:click="navigateToSubPath('pantry-store')"
        >Pantry Store</a>
        <a
          href="#"
          class="nav-pantry-known-words"
          v-on:click="navigateToSubPath('known-words')"
        >Known Words</a>
        <a
          href="#"
          class="nav-pantry-categories"
          v-on:click="navigateToSubPath('store-categories')"
        >Categories</a>
      </nav>
    </div>
    <ButterBar :message="butterBar_message" :css="butterBar_css"/>
    <div v-if="currentPage === 'grocery-lists'">
      <h2>Grocery Lists</h2>
      <div class="input-form">
        Store:
        <input v-model="groceryListStoreToAdd" ref="grocery-list-store-to-add">
        <input v-model="groceryListDateToAdd" type="date">
        <button @click="addGroceryList">Add Grocery List</button>
      </div>
      <div v-masonry transition-duration="0" item-selector=".item">
        <div
          v-masonry-tile
          class="item textarea-div"
          v-for="groceryList in groceryLists"
          :key="groceryList['id']"
        >
          <div class="textarea-title">
            {{ groceryList['store'] }}: {{ getDisplayDate(groceryList['date']) }}
            <font-awesome-icon
              icon="pencil-alt"
              class="icon"
              @click="showEditGroceryMetadataModal(groceryList)"
            />
            <font-awesome-icon
              icon="trash"
              class="icon"
              @click="showDeleteGroceryListModal(groceryList)"
            />
          </div>
          <div class="textarea-text">
            <EditableDiv
              :key="pantryGroceryListKey"
              :content="groceryList['list']"
              :handleUpdate="updateGroceryListText.bind(this, groceryList)"
            />
          </div>
          <div v-if="groceryList['saved']">
            <span v-if="groceryList['imported']">Imported.</span>
            <button @click="validateKnownWords(groceryList, showExportGroceryListModal)">Export list</button>
            <button @click="validateKnownWords(groceryList, attemptAddToPantry)">Add to Pantry</button>
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
        :addToKnownWords="this.addToKnownWords"
        :showErrorText="this.importModalShowErrorText"
      />
      <AddToKnownWordsModal
        :callback="addToKnownWordsCallback"
        :close="closeAddToKnownWordsModal"
        :show="shouldShowAddToKnownWordsModal"
        :errorText="addToKnownWordsModalErrorText"
        :groceryList="groceryListToAddKnownWordsFor"
        :unrecognizedWords="unrecognizedWords"
        :addToKnownWords="addToKnownWords"
        :showErrorText="addToKnownWordsModalShowErrorText"
      />
      <ExportGroceryListModal
        :close="closeExportModal"
        :show="shouldShowExportModal"
        :exportLines="exportLines"
      />
    </div>
    <div v-else-if="currentPage === 'pantry-store'">
      <h2>Pantry</h2>
      <div class="input-form">
        <input v-model="pantryItemToAdd" ref="pantry-item-to-add">
        <button @click="addPantryItem">Add Item</button>
      </div>
      <table class="table">
        <tr>
          <th>Name</th>
          <th>Delete</th>
        </tr>
        <tr :key="pantryItem['item']" v-for="pantryItem in pantry">
          <td>{{ pantryItem['item'] }}</td>
          <td>
            <font-awesome-icon
              icon="trash"
              class="icon"
              @click="showDeletePantryItemModal(pantryItem)"
            />
          </td>
        </tr>
      </table>
    </div>
    <div v-else-if="currentPage === 'known-words'">
      <h2>Known Words</h2>
      <div class="input-form">
        Word:
        <input v-model="knownWordToAdd" ref="known-word-to-add">
        Category:
        <input v-model="knownWordToAddCategory">
        <select v-model="knownWordToAddShouldSave">
          <option>True</option>
          <option>False</option>
        </select>
        <button @click="addKnownWord">Add Word</button>
      </div>
      <table class="table">
        <tr>
          <th>Name</th>
          <th>Category</th>
          <th>Addable to Pantry</th>
          <th>Delete</th>
        </tr>
        <tr :key="knownWord['word']" v-for="knownWord in knownWords">
          <td>{{ knownWord['word'] }}</td>
          <td>{{ knownWord['category'] }}</td>
          <td>{{ knownWord['should_save'] }}</td>
          <td>
            <font-awesome-icon
              icon="trash"
              class="icon"
              @click="showDeleteKnownWordModal(knownWord)"
            />
          </td>
        </tr>
      </table>
    </div>
    <div v-else-if="currentPage === 'store-categories'">
      <h2>Store Categories</h2>
      <div class="add-store-input-form">
        Store:
        <input v-model="storeToAdd" ref="store-to-add">
        <button @click="addStore">Add Store</button>
      </div>
      Select store: <select v-model="selectedStore">
        <option disabled value="">Please select one</option>
        <option :key="store" v-for="store in stores">{{store}}</option>
      </select>
      <div v-if="selectedStore">
        Aisles for {{selectedStore}}
        <table class="table">
          <tr>
            <th>Category</th>
            <th>Aisle</th>
          </tr>
          <tr
            :key="selectedStore + '@@' + category"
            v-for="category in categories"
          >
            <td>{{ category }}</td>
            <td><input v-model="storeCategoriesToAisles[selectedStore][category]"></td>
          </tr>
        </table>
        <button @click="addStoreAisles">Save Store Aisles</button>
      </div>
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
      :shouldShowError="formModal_shouldShowError"
    />
  </div>
</template>
<style>
@import '../assets/style/pantry.css'
</style>
<script>
import ButterBar from './shared/ButterBar'
import {
  setButterBarMessage,
  ButterBarType,
  callAxiosAndSetButterBar
} from '../common/butterbar_component'

import FormModal from './shared/FormModal'
import {
  showModal,
  createFormModalEntry,
  generateAxiosModalCallback
} from '../common/form_modal_component'

import EditableDiv from './shared/EditableDiv'
import ImportToPantryModal from './pantry_page/ImportToPantryModal'
import AddToKnownWordsModal from './pantry_page/AddToKnownWordsModal'
import ExportGroceryListModal from './pantry_page/ExportGroceryListModal'
import {
  getFullBackendUrlForPath,
  getDisplayDate,
  callAxios
} from '../common/utils'

const GET_PANTRY_PAGE_URL = getFullBackendUrlForPath('/get_pantry_page')
const EDIT_GROCERY_LIST_METADATA_URL = getFullBackendUrlForPath(
  '/edit_grocery_list_metadata'
)
const DELETE_GROCERY_LIST_URL = getFullBackendUrlForPath(
  '/delete_grocery_list'
)
const EDIT_GROCERY_LIST_URL = getFullBackendUrlForPath('/edit_grocery_list')
const ADD_GROCERY_LIST_URL = getFullBackendUrlForPath('/add_grocery_list')
const ATTEMPT_IMPORT_GROCERY_LIST_TO_PANTRY_URL = getFullBackendUrlForPath(
  '/attempt_add_to_pantry'
)
const IMPORT_GROCERY_LIST_TO_PANTRY_URL = getFullBackendUrlForPath(
  '/add_to_pantry'
)
const DELETE_PANTRY_ITEM_URL = getFullBackendUrlForPath('/delete_pantry_item')
const ADD_PANTRY_ITEM_URL = getFullBackendUrlForPath('/add_pantry_item')
const DELETE_KNOWN_WORD_URL = getFullBackendUrlForPath('/delete_known_word')
const ADD_KNOWN_WORD_URL = getFullBackendUrlForPath('/add_known_word')
const ADD_KNOWN_WORDS_URL = getFullBackendUrlForPath('/add_known_words')
const VALIDATE_KNOWN_WORDS_URL = getFullBackendUrlForPath('/validate_known_words')
const ADD_STORE_URL = getFullBackendUrlForPath('/add_store')
const ADD_STORE_AISLES_URL = getFullBackendUrlForPath('/add_store_aisles')
const PANTRY_EXPORT_TEXT_URL = getFullBackendUrlForPath('/pantry_export_text')

export default {
  name: 'PantryPage',
  data () {
    return {
      groceryLists: [],
      pantry: [],
      storeCategories: [],
      knownWords: [],
      groceryListStoreToAdd: '',
      groceryListDateToAdd: '',
      pantryItemToAdd: '',
      storeToAdd: '',
      knownWordToAdd: '',
      knownWordToAddCategory: '',
      knownWordToAddShouldSave: 'True',
      groceryListToImport: {},
      groceryListToAddKnownWordsFor: {},
      exportLines: [],
      pantryGroceryListKey: 0,
      shouldShowImportModal: false,
      shouldShowExportModal: false,
      shouldShowAddToKnownWordsModal: false,
      currentPage: '',
      importModalErrorText: '',
      addToKnownWordsModalErrorText: '',
      willImportWords: [],
      willIgnoreWords: [],
      unrecognizedWords: [],
      alreadyInPantryWords: [],
      stores: [],
      selectedStore: '',
      categories: [],
      storeCategoriesToAisles: {},
      addToKnownWordsCallback: Function,

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
    FormModal,
    EditableDiv,
    ImportToPantryModal,
    ExportGroceryListModal,
    AddToKnownWordsModal,
    ButterBar
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
    $route: function () {
      this.setCurrentPage()
    },
    allGroceryListsSaved: function (oldValue, newValue) {
      if (newValue) {
        window.onbeforeunload = function () {
          return ''
        }
      } else {
        window.onbeforeunload = function () {
          return null
        }
      }
    }
  },
  beforeRouteLeave (to, from, next) {
    if (!this.allGroceryListsSaved) {
      const answer = window.confirm(
        'You haven\'t saved your changes. Are you sure you want to leave?'
      )
      if (answer) {
        window.onbeforeunload = function () {
          return null
        }
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
    importModalShowErrorText (text) {
      this.importModalErrorText = text
    },
    addToKnownWordsModalShowErrorText (text) {
      this.addToKnownWordsModalErrorText = text
    },
    attemptAddToPantry (groceryList) {
      callAxiosAndSetButterBar(
        this,
        ATTEMPT_IMPORT_GROCERY_LIST_TO_PANTRY_URL,
        { id: groceryList['id'] },
        null,
        'Failed to move note.',
        response => {
          this.showImportModal(
            groceryList,
            response['data']['add'],
            response['data']['ignore'],
            response['data']['unrecognized'],
            response['data']['already_in_pantry']
          )
        }
      )
    },
    showAddToKnownWordsModal (groceryList, unrecognizedWords, callback) {
      this.groceryListToAddKnownWordsFor = groceryList
      this.unrecognizedWords = unrecognizedWords
      this.shouldShowAddToKnownWordsModal = true
      this.addToKnownWordsModalErrorText = ''
      this.addToKnownWordsCallback = callback
    },
    validateKnownWords (groceryList, callback) {
      callAxiosAndSetButterBar(
        this,
        VALIDATE_KNOWN_WORDS_URL,
        { id: groceryList['id'] },
        null,
        'Failed to validate known words.',
        response => {
          if (response['data']['unrecognized'].length === 0) {
            callback(groceryList)
          } else {
            this.showAddToKnownWordsModal(groceryList, response['data']['unrecognized'], callback)
          }
        }
      )
    },
    showExportGroceryListModal (groceryList) {
      callAxiosAndSetButterBar(
        this,
        PANTRY_EXPORT_TEXT_URL,
        { id: groceryList['id'] },
        null,
        'Failed to export grocery list.',
        response => {
          this.showExportModal(groceryList, response['data'])
        }
      )
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
    closeAddToKnownWordsModal () {
      this.shouldShowAddToKnownWordsModal = false
    },
    showImportModal (
      groceryList,
      willImportWords,
      willIgnoreWords,
      unrecognizedWords,
      alreadyInPantryWords
    ) {
      this.groceryListToImport = groceryList
      this.willImportWords = willImportWords
      this.willIgnoreWords = willIgnoreWords
      this.unrecognizedWords = unrecognizedWords
      this.alreadyInPantryWords = alreadyInPantryWords
      this.importModalErrorText = ''
      this.shouldShowImportModal = true
    },
    closeExportModal () {
      this.shouldShowExportModal = false
    },
    showExportModal (groceryList, exportLines) {
      this.exportLines = exportLines
      this.shouldShowExportModal = true
    },
    showEditGroceryMetadataModal (groceryList) {
      let modalFormLines = [
        createFormModalEntry(
          'edit-grocery-metadata-modal-store-' + groceryList['id'],
          'store',
          'Store:',
          groceryList['store']
        ),
        createFormModalEntry(
          'edit-grocery-metadata-modal-date-' + groceryList['id'],
          'date',
          'Date:',
          groceryList['date']
        )
      ]
      showModal(
        this,
        'Editing ' + groceryList['store'],
        modalFormLines,
        groceryList,
        generateAxiosModalCallback(
          this,
          EDIT_GROCERY_LIST_METADATA_URL,
          this.editGroceryListMetadata
        ),
        'Save',
        'Error saving ' + groceryList['store']
      )
    },
    showDeleteGroceryListModal (groceryList) {
      showModal(
        this,
        'Deleting ' + groceryList['store'],
        [],
        { id: groceryList['id'] },
        generateAxiosModalCallback(
          this,
          DELETE_GROCERY_LIST_URL,
          this.deleteGroceryList
        ),
        'Delete',
        'Error deleting ' + groceryList['store']
      )
    },
    showDeletePantryItemModal (pantryItem) {
      showModal(
        this,
        'Deleting ' + pantryItem['item'],
        [],
        { item: pantryItem['item'] },
        generateAxiosModalCallback(
          this,
          DELETE_PANTRY_ITEM_URL,
          this.deletePantryItem
        ),
        'Delete',
        'Error deleting ' + pantryItem['item']
      )
    },
    showDeleteKnownWordModal (knownWord) {
      showModal(
        this,
        'Deleting ' + knownWord['word'],
        [],
        { word: knownWord['word'] },
        generateAxiosModalCallback(
          this,
          DELETE_KNOWN_WORD_URL,
          this.deleteKnownWord
        ),
        'Delete',
        'Error deleting ' + knownWord['word']
      )
    },
    addToPantry (groceryList) {
      callAxiosAndSetButterBar(
        this,
        IMPORT_GROCERY_LIST_TO_PANTRY_URL,
        { id: groceryList['id'] },
        'Imported ' + groceryList['store'] + ' to the pantry.',
        'Error importing ' + groceryList['store'] + ' to the pantry.',
        response => {
          this.updatePantryPageDisplay()
          this.closeImportModal()
        }
      )
    },
    editGroceryListMetadata (response) {
      let currentGroceryListIndex = this.groceryLists.findIndex(
        groceryList => groceryList['id'] === response['data']['id']
      )
      let newGroceryListItem = this.groceryLists[currentGroceryListIndex]
      let oldStore = this.groceryLists[currentGroceryListIndex]['store']
      newGroceryListItem['store'] = response['data']['store']
      newGroceryListItem['date'] = response['data']['date']
      this.groceryLists.splice(currentGroceryListIndex, 1, newGroceryListItem)
      setButterBarMessage(
        this,
        'Saved the data of ' + oldStore,
        ButterBarType.INFO
      )
    },
    editGroceryList (groceryList) {
      callAxiosAndSetButterBar(
        this,
        EDIT_GROCERY_LIST_URL,
        { id: groceryList['id'], list: groceryList['list'] },
        'Saved the contents of ' + groceryList['store'],
        'Error saving the contents of ' + groceryList['store'],
        response => {
          let currentGroceryListIndex = this.groceryLists.findIndex(
            groceryList => groceryList['id'] === response['data']['id']
          )
          response['data']['saved'] = true
          this.groceryLists.splice(
            currentGroceryListIndex,
            1,
            response['data']
          )
        }
      )
    },
    deleteGroceryList (response) {
      let deletedGroceryList = response['data']
      this.groceryLists.splice(
        this.groceryLists.findIndex(
          groceryList => groceryList['id'] === deletedGroceryList['id']
        ),
        1
      )
      setButterBarMessage(
        this,
        'Deleted ' + deletedGroceryList['store'],
        ButterBarType.INFO
      )
    },
    deletePantryItem (response) {
      let deletedPantryItem = response['data']
      this.pantry.splice(
        this.pantry.findIndex(
          pantry => pantry['item'] === deletedPantryItem['item']
        ),
        1
      )
      setButterBarMessage(
        this,
        'Deleted ' + deletedPantryItem['item'] + ' from the pantry',
        ButterBarType.INFO
      )
    },
    addPantryItem () {
      callAxiosAndSetButterBar(
        this,
        ADD_PANTRY_ITEM_URL,
        { item: this.pantryItemToAdd },
        'Added ' + this.pantryItemToAdd + ' to the pantry',
        'Error adding ' + this.pantryItemToAdd + ' to the pantry',
        response => {
          this.pantryItemToAdd = ''
          let pantryItem = response['data']
          this.pantry.push(pantryItem)
          this.$refs['pantry-item-to-add'].focus()
        }
      )
    },
    addStoreAisles () {
      callAxiosAndSetButterBar(
        this,
        ADD_STORE_AISLES_URL,
        {
          store: this.selectedStore,
          categories_to_aisles: this.storeCategoriesToAisles[this.selectedStore]
        },
        'Added aisles to the store ' +
          this.selectedStore,
        'Error adding aisles to the store ' +
          this.selectedStore,
        response => {}
      )
    },
    addStore () {
      callAxiosAndSetButterBar(
        this,
        ADD_STORE_URL,
        {
          store: this.storeToAdd
        },
        'Added ' + this.storeToAdd,
        'Error adding ' + this.storeToAdd,
        response => {
          this.storeToAdd = ''
          let store = response['data']['store']
          this.stores.push(store)
          this.storeCategoriesToAisles[store] = {}
          for (let category in this.categories) {
            this.storeCategoriesToAisles[store][category] = ''
          }
          this.$refs['store-to-add'].focus()
        }
      )
    },
    deleteKnownWord (response) {
      let deletedKnownWord = response['data']
      this.knownWords.splice(
        this.knownWords.findIndex(
          knownWord => knownWord['word'] === deletedKnownWord['word']
        ),
        1
      )
      setButterBarMessage(
        this,
        'Deleted ' + deletedKnownWord['word'] + ' from the list of known words',
        ButterBarType.INFO
      )
    },
    // TODO: Adding to known words should update categories.
    addToKnownWords (groceryList, knownWordsData, callback) {
      let knownWordsDataWithBooleans = knownWordsData.slice()
      for (let index in knownWordsDataWithBooleans) {
        knownWordsDataWithBooleans[index].should_save =
          knownWordsDataWithBooleans[index].shouldAddToPantry === 'true'
        delete knownWordsDataWithBooleans[index].shouldAddToPantry
      }
      let that = this
      callAxios(
        ADD_KNOWN_WORDS_URL,
        knownWordsDataWithBooleans,
        function (response) {
          let knownWords = response['data']
          for (let index in knownWords) {
            that.knownWords.push(knownWords[index])
          }
          callback(groceryList)
        },
        function () {
          that.importModalErrorText = 'Error in adding words.'
        }
      )
    },
    addKnownWord () {
      callAxiosAndSetButterBar(
        this,
        ADD_KNOWN_WORD_URL,
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
        }
      )
    },
    addGroceryList () {
      callAxiosAndSetButterBar(
        this,
        ADD_GROCERY_LIST_URL,
        {
          store: this.groceryListStoreToAdd,
          date: this.groceryListDateToAdd
        },
        'Added ' + this.groceryListStoreToAdd + ' to the grocery lists',
        'Error adding ' + this.groceryListStoreToAdd + ' to the grocery lists',
        response => {
          this.groceryListStoreToAdd = ''
          this.groceryListDateToAdd = ''
          let groceryList = response['data']
          groceryList['saved'] = true
          this.groceryLists.push(groceryList)
          this.$refs['grocery-list-store-to-add'].focus()
        }
      )
    },
    updatePantryPageDisplay () {
      callAxiosAndSetButterBar(
        this,
        GET_PANTRY_PAGE_URL,
        {},
        null,
        'Failed to move note.',
        response => {
          for (let index in response['data']['grocery_lists']) {
            response['data']['grocery_lists'][index]['saved'] = true
          }
          this.groceryLists = response['data']['grocery_lists']
          this.storeCategories = response['data']['store_categories']
          this.pantry = response['data']['pantry']
          this.knownWords = response['data']['known_words']
          this.stores = response['data']['stores']
          this.categories = response['data']['categories']
          this.storeCategoriesToAisles = response['data']['store_categories_to_aisles']
        }
      )
    }
  }
}
</script>
