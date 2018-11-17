<template>
  <div class="current-documents">
    <div class="title">
      <span class="expand-icon" @click="toggleExpand">{{ expandIcon }}</span>&nbsp;Current Documents
    </div>
    <div v-if="isExpanded">
      <table class="current-documents-list table">
        <tr>
          <th>Title</th><th>Notes</th><th>Modify</th>
        </tr>
        <tr class="current-documents-item" :key="index"
            v-for="(currentDocument, index) in currentDocuments">
          <td><a :href="currentDocument.url" target="_blank">{{ currentDocument.title }}</a></td>
          <td>{{ currentDocument.notes }}</td>
          <td><font-awesome-icon icon="pencil-alt" class="current-documents-icon"
              @click="showEditModal(index)" />&nbsp;&nbsp;
              <font-awesome-icon icon="trash" class="current-documents-icon"
              @click="deleteDocument(index)" />&nbsp;&nbsp;
              <font-awesome-icon icon="long-arrow-alt-up" class="current-documents-icon"
              @click="moveDocumentUp(index)" />&nbsp;&nbsp;
              <font-awesome-icon icon="long-arrow-alt-down" class="current-documents-icon"
              @click="moveDocumentDown(index)" />
          </td>
        </tr>
      </table>
      <button @click="showAddModal()">Add Document</button>
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
            <button type="button" @click="addOrEditDocument()">Save</button>
          </div>
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
import { getElementById, getFullBackendUrlForPath, generateExpandIcon } from '../common/utils'
import { store } from '../store/store'

const GET_CURRENT_DOCUMENTS_URL = getFullBackendUrlForPath('/get_current_documents')
const DELETE_DOCUMENT_URL = getFullBackendUrlForPath('/delete_document')
const EDIT_DOCUMENT_URL = getFullBackendUrlForPath('/edit_document')
const ADD_DOCUMENT_URL = getFullBackendUrlForPath('/add_document')
const REORDER_DOCUMENTS_URL = getFullBackendUrlForPath('/reorder_documents')

// TODO: Don't have nbsp;'s between the edit icons.
export default {
  name: 'CurrentDocuments',
  data () {
    return {
      currentDocuments: [],
      currentDocumentsLength: 0,
      modalDialogTitleHeader: '',
      modalDialogTitle: '',
      modalDialogUrl: '',
      modalDialogNotes: '',
      modalDialogDocumentId: null,
      isExpanded: true
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
    },
    expandIcon () {
      return generateExpandIcon(this.isExpanded)
    }
  },
  watch: {
    username () {
      this.updateCurrentDocumentsDisplay()
    }
  },
  methods: {
    toggleExpand () {
      this.isExpanded = !this.isExpanded
    },
    updateCurrentDocumentsDisplay () {
      axios.post(GET_CURRENT_DOCUMENTS_URL, {username: this.username}).then(
        response => {
          this.currentDocuments = response.data
          this.currentDocumentsLength = response.data.length
        })
    },
    showEditModal (index) {
      let document = this.currentDocuments[index]
      this.modalDialogTitleHeader = 'Editing ' + document.title
      this.modalDialogTitle = document.title
      this.modalDialogUrl = document.url
      this.modalDialogNotes = document.notes
      this.modalDialogDocumentId = document.id
      getElementById('current-documents-modal').style.display = 'block'
    },
    showAddModal () {
      this.modalDialogTitleHeader = 'Adding a new document'
      this.modalDialogTitle = ''
      this.modalDialogUrl = ''
      this.modalDialogNotes = ''
      this.modalDialogDocumentId = null
      getElementById('current-documents-modal').style.display = 'block'
    },
    hideModal () {
      getElementById('current-documents-modal').style.display = 'none'
    },
    deleteDocument (index) {
      axios.post(DELETE_DOCUMENT_URL, {id: this.currentDocuments[index].id}).then(
        response => {
          this.updateCurrentDocumentsDisplay()
        })
    },
    moveDocumentUp (index) {
      if (index === 0) {
        return
      }
      let documentIds = []
      for (let i = 0; i < this.currentDocumentsLength; ++i) {
        let indexToAdd = i
        if (i === index) {
          indexToAdd = i - 1
        } else if (i === (index - 1)) {
          indexToAdd = i + 1
        }
        documentIds.push(this.currentDocuments[indexToAdd].id)
      }
      axios.post(REORDER_DOCUMENTS_URL, {username: this.username, document_ids: documentIds}).then(
        response => {
          this.updateCurrentDocumentsDisplay()
        })
    },
    moveDocumentDown (index) {
      if (index === (this.currentDocuments.length - 1)) {
        return
      }
      let documentIds = []
      for (let i = 0; i < this.currentDocumentsLength; ++i) {
        let indexToAdd = i
        if (i === index) {
          indexToAdd = i + 1
        } else if (i === (index + 1)) {
          indexToAdd = i - 1
        }
        documentIds.push(this.currentDocuments[indexToAdd].id)
      }
      axios.post(REORDER_DOCUMENTS_URL, {username: this.username, document_ids: documentIds}).then(
        response => {
          this.updateCurrentDocumentsDisplay()
        })
    },
    addOrEditDocument () {
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
