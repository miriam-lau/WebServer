<template>
  <div class="current-documents">
    <div class="current-documents-title">Current Documents</div>
    <table class="current-documents-list table">
      <tr>
        <th>Title</th><th>Notes</th><th>Modify</th>
      </tr>
      <tr class="current-documents-item" :key="currentDocument.id" v-for="currentDocument in currentDocuments">
        <td><a :href="currentDocument.url" target="_blank">{{ currentDocument.title }}</a></td>
        <td>{{ currentDocument.notes }}</td>
        <td><font-awesome-icon icon="pencil-alt" class="current-documents-edit"
            @click="showEditModal(currentDocument.id)" />&nbsp;&nbsp;&nbsp;&nbsp;
            <font-awesome-icon icon="trash" class="current-documents-trash"
            @click="deleteItem(currentDocument.id)" /></td>
      </tr>
    </table>
    <button @click="showAddModal()">Add Item</button>
    <div id="current-documents-modal" class="current-documents-modal">
      <div class="current-documents-modal-content">
        <div class="current-documents-modal-container">
          <b>{{ modalDialogTitleHeader }}</b>
          <hr>
          <table>
            <tr>
              <td><label for="current-documents-title"><b>Title:</b></label></td>
              <td><input class="current-documents-input" v-model="modalDialogTitle" name="current-documents-title"></td>
            </tr>
            <tr>
              <td><label for="current-documents-url"><b>Url:</b></label></td>
              <td><input class="current-documents-input" v-model="modalDialogUrl" name="current-documents-url"></td>
            </tr>
            <tr>
              <td><label for="current-documents-notes"><b>Notes:</b></label></td>
              <td><input class="current-documents-input" v-model="modalDialogNotes" name="current-documents-notes"></td>
            </tr>
          </table>
          <button type="button" @click="hideModal()">Cancel</button>
          <button type="button" @click="addOrEditItem()">Save</button>
        </div>
      </div>
    </div>
  </div>
</template>
<style>
  @import "../assets/style/current-documents.css"
</style>
<script>
import axios from 'axios'
import { getElementById, getFullBackendUrlForPath } from '../common/utils'
import { store } from '../store/store'

const GET_CURRENT_DOCUMENTS_URL = getFullBackendUrlForPath('/get_current_documents')
const DELETE_DOCUMENT_URL = getFullBackendUrlForPath('/delete_document')
const EDIT_DOCUMENT_URL = getFullBackendUrlForPath('/edit_document')
const ADD_DOCUMENT_URL = getFullBackendUrlForPath('/add_document')

// TODO: Don't have nbsp;'s between the edit icons.
export default {
  name: 'CurrentDocuments',
  data () {
    return {
      currentDocuments: {},
      modalDialogTitleHeader: '',
      modalDialogTitle: '',
      modalDialogUrl: '',
      modalDialogNotes: '',
      modalDialogDocumentId: null
    }
  },
  created () {
    this.updateCurrentDocumentsDisplay()
  },
  updated () {
    modal = getElementById('current-documents-modal')
  },
  computed: {
    username () {
      return store.state.username
    }
  },
  watch: {
    username () {
      this.updateCurrentDocumentsDisplay()
    }
  },
  methods: {
    updateCurrentDocumentsDisplay () {
      axios.post(GET_CURRENT_DOCUMENTS_URL, {username: this.username}).then(
        response => {
          var newCurrentDocuments = {}
          for (var id in response.data) {
            newCurrentDocuments[id] = response.data[id]
          }
          this.currentDocuments = newCurrentDocuments
        })
    },
    showEditModal (id) {
      this.modalDialogTitleHeader = 'Editing ' + this.currentDocuments[id].title
      this.modalDialogTitle = this.currentDocuments[id].title
      this.modalDialogUrl = this.currentDocuments[id].url
      this.modalDialogNotes = this.currentDocuments[id].notes
      this.modalDialogDocumentId = id
      getElementById('current-documents-modal').style.display = 'block'
    },
    showAddModal () {
      this.modalDialogTitleHeader = 'Adding a new item'
      this.modalDialogTitle = ''
      this.modalDialogUrl = ''
      this.modalDialogNotes = ''
      this.modalDialogDocumentId = null
      getElementById('current-documents-modal').style.display = 'block'
    },
    hideModal () {
      getElementById('current-documents-modal').style.display = 'none'
    },
    deleteItem (id) {
      axios.post(DELETE_DOCUMENT_URL, {id: id}).then(
        response => {
          this.updateCurrentDocumentsDisplay()
        })
    },
    addOrEditItem () {
      var document = {}
      document.username = this.username
      document.title = this.modalDialogTitle
      document.url = this.modalDialogUrl
      document.notes = this.modalDialogNotes
      if (this.modalDialogDocumentId != null) {
        document.id = this.modalDialogDocumentId
        axios.post(EDIT_DOCUMENT_URL, {id: this.modalDialogDocumentId, document: document}).then(
          response => {
            this.updateCurrentDocumentsDisplay()
            this.hideModal()
          })
      } else {
        axios.post(ADD_DOCUMENT_URL, {document: document}).then(
          response => {
            this.updateCurrentDocumentsDisplay()
            this.hideModal()
          })
      }
    }
  }
}

var modal

// When the user clicks anywhere outside of the modal, close it
window.onclick = function (event) {
  if (event.target === modal) {
    modal.style.display = 'none'
  }
}
</script>
