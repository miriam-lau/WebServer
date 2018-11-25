<template>
  <div>
    <div class="pantry-grocery-lists">
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
                  :content="groceryList['list']"
                  :handleUpdate="updateGroceryListText.bind(this, groceryList)"
                />
            </div>
            <div v-if="groceryList['saved']">
                Saved.
            </div>
            <div v-else>
                Unsaved. <button @click="editGroceryList(groceryList)">Save List</button>
            </div>
        </div>
        <input v-model="groceryListTitleToAdd" /> <button @click="addGroceryList">Add Grocery List</button>
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
    <div class="pantry-pantry">
        <h2>Pantry</h2>
        <div :key="pantryItem['id']" v-for="pantryItem in pantry">
            {{ pantryItem['item'] }}
        </div>
    </div>
  </div>
</template>
<style>
  @import "../assets/style/pantry.css"
</style>
<script>
// TODO: Only one grocery list can be modified at a time. Saving one will trigger a page refresh, overwriting the
// others.
import EditableDiv from './shared/EditableDiv'
import FormModal from './shared/FormModal'
import axios from 'axios'
import { getFullBackendUrlForPath, createFormModalEntry } from '../common/utils'

const GET_PANTRY_PAGE_URL = getFullBackendUrlForPath('/get_pantry_page')
const EDIT_GROCERY_LIST_METADATA_URL = getFullBackendUrlForPath('/edit_grocery_list_metadata')
const DELETE_GROCERY_LIST_URL = getFullBackendUrlForPath('/delete_grocery_list')
const EDIT_GROCERY_LIST_URL = getFullBackendUrlForPath('/edit_grocery_list')
const ADD_GROCERY_LIST_URL = getFullBackendUrlForPath('/add_grocery_list')
/*
const IMPORT_GROCERY_LIST_TO_PANTRY_URL = getFullBackendUrlForPath('/import_grocery_list_to_pantry')
const GET_PANTRY_URL = getFullBackendUrlForPath('/get_pantry')
const DELETE_PANTRY_ITEM_URL = getFullBackendUrlForPath('/delete_pantry_item')
const ADD_PANTRY_ITEM_URL = getFullBackendUrlForPath('/add_pantry_item')
*/

export default {
  name: 'PantryPage',
  data () {
    return {
      groceryLists: {},
      pantry: [],
      groceryListTitleToAdd: '',
      currentStatus: '',
      modalTitle: '',
      modalFormLines: [],
      modalPassThroughProps: {},
      modalCallback: Function,
      modalButtonText: '',
      modalErrorText: '',
      shouldShowModal: false,
      timeoutHandle: null
    }
  },
  created () {
    this.updatePantryPageDisplay()
  },
  components: {
    FormModal, EditableDiv
  },
  methods: {
    updateGroceryListText (groceryList, newText) {
      groceryList['saved'] = false
      groceryList['list'] = newText.target.innerText
    },
    closeModal () {
      this.shouldShowModal = false
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
    editGroceryListMetadata (groceryList) {
      axios.post(
        EDIT_GROCERY_LIST_METADATA_URL,
        {
          id: groceryList['id'],
          title: groceryList['title']
        }).then(response => {
        this.updatePantryPageDisplay()
        this.closeModal()
      })
    },
    editGroceryList (groceryList) {
      axios.post(EDIT_GROCERY_LIST_URL, {id: groceryList['id'], list: groceryList['list']}).then(response => {
        this.updatePantryPageDisplay()
      })
    },
    deleteGroceryList (groceryList) {
      axios.post(DELETE_GROCERY_LIST_URL, {id: groceryList['id']}).then(response => {
        this.updatePantryPageDisplay()
        this.closeModal()
      })
    },
    addGroceryList () {
      axios.post(ADD_GROCERY_LIST_URL, {title: this.groceryListTitleToAdd}).then(
        response => {
          this.groceryListTitleToAdd = ''
          this.updatePantryPageDisplay()
        }
      )
    },
    updatePantryPageDisplay () {
      axios.post(GET_PANTRY_PAGE_URL).then(
        response => {
          this.groceryLists = response['data']['grocery_lists']
          for (let index in this.groceryLists) {
            this.groceryLists[index]['saved'] = true
          }
          this.pantry = response['data']['pantry']
        })
    }
  }
}
</script>
