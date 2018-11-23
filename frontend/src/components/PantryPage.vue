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
                <EditableDiv :content="groceryList['list']" :handleUpdate="updateGroceryListText.bind(this, groceryList)" />
            </div>
            <div v-if="groceryList['saved']">
                Saved.
            </div>
            <div v-else>
                Unsaved. <button @click="editGroceryList(groceryList)">Save List</button>
            </div>
        </div>
        <input v-model="groceryListTitleToAdd" /> <button @click="addGroceryList">Add Grocery List</button>
        <FormModal :show="shouldShowEditGroceryMetadataModal" @close="shouldShowEditGroceryMetadataModal = false"
            :title="editGroceryMetadataModalTitle" :initialFormLines="editGroceryMetadataModalFormLines"
            :passThroughProps="editGroceryMetadataModalPassThroughProps"
            :handleSave="closeModalAndHandleEditGroceryMetadataModalSave" buttonText="Save" />
        <FormModal :show="shouldShowDeleteGroceryListModal" @close="shouldShowDeleteGroceryListModal = false"
            :title="deleteGroceryListModalTitle" :initialFormLines="[]"
            :passThroughProps="deleteGroceryListModalPassThroughProps"
            :handleSave="closeModalAndHandleDeleteGroceryListModalSave"
            buttonText="Delete" />
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
import { getFullBackendUrlForPath } from '../common/utils'

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
      shouldShowEditGroceryMetadataModal: false,
      editGroceryMetadataModalTitle: '',
      editGroceryMetadataModalFormLines: [],
      editGroceryMetadataModalPassThroughProps: {},
      shouldShowDeleteGroceryListModal: false,
      deleteGroceryListModalTitle: '',
      deleteGroceryListModalPassThroughProps: {}
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
    closeModalAndHandleEditGroceryMetadataModalSave (formSaveResponse) {
      axios.post(EDIT_GROCERY_LIST_METADATA_URL, formSaveResponse).then(response => {
        this.updatePantryPageDisplay()
        this.shouldShowEditGroceryMetadataModal = false
      })
    },
    closeModalAndHandleDeleteGroceryListModalSave (formSaveResponse) {
      axios.post(DELETE_GROCERY_LIST_URL, formSaveResponse).then(response => {
        this.updatePantryPageDisplay()
        this.shouldShowDeleteGroceryListModal = false
      })
    },
    editGroceryList (groceryList) {
      axios.post(EDIT_GROCERY_LIST_URL, {id: groceryList['id'], list: groceryList['list']}).then(response => {
        this.updatePantryPageDisplay()
      })
    },
    showDeleteGroceryListModal (groceryList) {
      this.deleteGroceryListModalPassThroughProps = { id: groceryList['id'] }
      this.deleteGroceryListModalTitle = 'Deleting ' + groceryList['title']
      this.shouldShowDeleteGroceryListModal = true
    },
    showEditGroceryMetadataModal (groceryList) {
      this.editGroceryMetadataModalPassThroughProps = { id: groceryList['id'] }
      this.editGroceryMetadataModalTitle = 'Editing ' + groceryList['title']
      this.editGroceryMetadataModalFormLines = [
        {
          id: 'grocery-modal-title-' + groceryList['id'],
          name: 'title',
          displayName: 'Title:',
          value: groceryList['title']
        }
      ]
      this.shouldShowEditGroceryMetadataModal = true
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
