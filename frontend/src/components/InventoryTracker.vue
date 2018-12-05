<template>
  <div>
    <ButterBar
      :message="butterBar_message"
      :css="butterBar_css"
    />
    <div>
      <h2>Inventory</h2>
      <div class="input-form">
        <input v-model="boxTitleToAdd" /> <button @click="addBox">Add Box</button>
      </div>
      <div class="textarea-div" v-for="box in inventory" :key="box['id']">
        <div class="textarea-title">
          {{ box['title'] }}
          <font-awesome-icon icon="pencil-alt" class="icon"
              @click="showEditBoxMetadataModal(box)" />
          <font-awesome-icon icon="trash" class="icon"
              @click="showDeleteBoxModal(box)" />
        </div>
        <div class="textarea-text">
          <EditableDiv
            :key="boxKey"
            :content="box['text']"
            :handleUpdate="updateBoxText.bind(this, box)"
          />
        </div>
        <div v-if="!box['saved']">
          Unsaved.
          <button @click="editBox(box)">Save</button>
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
        :shouldShowError="formModal_shouldShowError" />
    </div>
  </div>
</template>
<style>
  @import "../assets/style/inventory.css"
</style>
<script>
import ButterBar from './shared/ButterBar'
import { setButterBarMessage, ButterBarType, callAxiosAndSetButterBar } from '../common/butterbar_component'

import FormModal from './shared/FormModal'
import { showModal, createFormModalEntry, generateAxiosModalCallback } from '../common/form_modal_component'

import EditableDiv from './shared/EditableDiv'
import axios from 'axios'
import { getFullBackendUrlForPath } from '../common/utils'

const GET_INVENTORY_PAGE_URL = getFullBackendUrlForPath('/get_inventory_page')
const EDIT_BOX_METADATA_URL = getFullBackendUrlForPath('/edit_box_metadata')
const DELETE_BOX_URL = getFullBackendUrlForPath('/delete_box')
const EDIT_BOX_URL = getFullBackendUrlForPath('/edit_box')
const ADD_BOX_URL = getFullBackendUrlForPath('/add_box')

export default {
  name: 'InventoryPage',
  data () {
    return {
      inventory: [],
      boxTitleToAdd: '',

      boxKey: 0,

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
  components: {
    FormModal, EditableDiv, ButterBar
  },
  created () {
    this.updateInventoryPageDisplay()
  },
  watch: {
    inventorySaved: function (oldValue, newValue) {
      if (newValue) {
        window.onbeforeunload = function () { return '' }
      } else {
        window.onbeforeunload = function () { return null }
      }
    }
  },
  beforeRouteLeave (to, from, next) {
    if (!this.inventorySaved) {
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
  computed: {
    inventorySaved: function () {
      for (let index in this.inventory) {
        if (!this.inventory[index]['saved']) {
          return false
        }
      }
      return true
    }
  },
  methods: {
    formModal_close () {
      this.formModal_show = false
    },
    updateBoxText (box, newText) {
      if (box['saved']) {
        box['saved'] = false
      }
      box['text'] = newText.target.innerText
    },
    showEditBoxMetadataModal (box) {
      let modalFormLines = [
        createFormModalEntry(
          'edit-box-metadata-modal-title-' + box['id'], 'title', 'Title:', box['title'])
      ]
      showModal(
        this,
        'Editing ' + box['title'],
        modalFormLines,
        box,
        generateAxiosModalCallback(this, EDIT_BOX_METADATA_URL, this.editBoxMetadata),
        'Save',
        'Error editing ' + box['title'])
    },
    showDeleteBoxModal (box) {
      showModal(
        this,
        'Deleting ' + box['title'],
        [],
        { id: box['id'] },
        generateAxiosModalCallback(this, DELETE_BOX_URL, this.deleteBox),
        'Delete',
        'Error deleting ' + box['title'])
    },
    editBoxMetadata (response) {
      let currentBoxIndex = this.inventory.findIndex(box => box['id'] === response['data']['id'])
      let newBoxItem = this.inventory[currentBoxIndex]
      let oldTitle = this.inventory[currentBoxIndex]['title']
      newBoxItem['title'] = response['data']['title']
      this.inventory.splice(currentBoxIndex, 1, newBoxItem)
      setButterBarMessage(this, 'Saved title of ' + oldTitle, ButterBarType.INFO)
    },
    editBox (box) {
      callAxiosAndSetButterBar(
        this, EDIT_BOX_URL, { id: box['id'], text: box['text'] },
        'Saved contents of ' + box['title'],
        'Error saving contents of ' + box['title'],
        response => {
          let currentBoxIndex =
            this.inventory.findIndex(box => box['id'] === response['data']['id'])
          response['data']['saved'] = true
          this.inventory.splice(currentBoxIndex, 1, response['data'])
        })
    },
    deleteBox (response) {
      let deletedBox = response['data']
      this.inventory.splice(
        this.inventory.findIndex(box => box['id'] === deletedBox['id']), 1)
      setButterBarMessage(this, 'Deleted ' + deletedBox['title'], ButterBarType.INFO)
    },
    addBox () {
      callAxiosAndSetButterBar(
        this, ADD_BOX_URL, { title: this.boxTitleToAdd },
        'Added ' + this.boxTitleToAdd,
        'Error adding ' + this.boxTitleToAdd,
        response => {
          this.boxTitleToAdd = ''
          let box = response['data']
          box['saved'] = true
          this.inventory.push(box)
        })
    },
    updateInventoryPageDisplay () {
      axios.post(GET_INVENTORY_PAGE_URL).then(
        response => {
          for (let index in response['data']) {
            response['data'][index]['saved'] = true
          }
          this.inventory = response['data']
        })
    }
  }
}
</script>
