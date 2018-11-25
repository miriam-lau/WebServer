<template>
  <div class="current-documents">
    <div class="current-documents-status" v-if="currentStatus != ''">
      {{ currentStatus }}
    </div>
    <table class="current-documents-list table">
      <tr>
        <th>Title</th><th>Notes</th><th>Modify</th>
      </tr>
      <tr class="current-documents-item" :key="currentDocument['id']"
          v-for="currentDocument in currentDocuments">
        <td><a :href="currentDocument['url']" target="_blank">{{ currentDocument['title'] }}</a></td>
        <td>{{ currentDocument['notes'] }}</td>
        <td><font-awesome-icon icon="pencil-alt" class="icon"
            @click="showEditModal(currentDocument)" />
            <font-awesome-icon icon="trash" class="icon"
            @click="showDeleteModal(currentDocument)" />
            <font-awesome-icon icon="long-arrow-alt-up" class="icon"
            @click="moveDocumentUp(currentDocument)" />
            <font-awesome-icon icon="long-arrow-alt-down" class="icon"
            @click="moveDocumentDown(currentDocument)" />
        </td>
      </tr>
    </table>
    <button @click="showAddModal">Add Document</button>
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
  @import "../assets/style/current-documents.css"
</style>
<script>
import FormModal from './shared/FormModal'
import axios from 'axios'
import { getFullBackendUrlForPath, createFormModalEntry } from '../common/utils'
import { store } from '../store/store'

const GET_CURRENT_DOCUMENTS_URL = getFullBackendUrlForPath('/get_current_documents')
const DELETE_DOCUMENT_URL = getFullBackendUrlForPath('/delete_document')
const EDIT_DOCUMENT_URL = getFullBackendUrlForPath('/edit_document')
const ADD_DOCUMENT_URL = getFullBackendUrlForPath('/add_document')
const REORDER_DOCUMENTS_URL = getFullBackendUrlForPath('/reorder_documents')

export default {
  name: 'CurrentDocuments',
  data () {
    return {
      currentDocuments: [],
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
    this.reloadCurrentDocumentsData()
  },
  computed: {
    username () {
      return store.state.username
    }
  },
  watch: {
    username () {
      this.reloadCurrentDocumentsData()
    }
  },
  components: {
    FormModal
  },
  methods: {
    closeModal () {
      this.shouldShowModal = false
    },
    reloadCurrentDocumentsData () {
      axios.post(GET_CURRENT_DOCUMENTS_URL, {username: this.username}).then(
        response => {
          this.currentDocuments = response['data']
        })
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
    showEditModal (document) {
      let modalFormLines = [
        createFormModalEntry('edit-document-modal-title-' + document['id'], 'title', 'Title:', document['title']),
        createFormModalEntry('edit-document-modal-url-' + document['id'], 'url', 'URL:', document['url']),
        createFormModalEntry('edit-document-modal-notes-' + document['id'], 'notes', 'Notes:', document['notes'])
      ]
      this.showModal(
        'Editing ' + document['title'],
        modalFormLines,
        document,
        this.editDocument,
        'Save')
    },
    showDeleteModal (document) {
      this.showModal(
        'Deleting ' + document['title'],
        [],
        { id: document['id'] },
        this.deleteDocument,
        'Delete')
    },
    showAddModal () {
      let modalFormLines = [
        createFormModalEntry('add-document-modal-title', 'title', 'Title:'),
        createFormModalEntry('add-document-modal-url', 'url', 'URL:'),
        createFormModalEntry('add-document-modal-notes', 'notes', 'Notes:')
      ]
      this.showModal(
        'Adding a new document',
        modalFormLines,
        { username: this.username },
        this.addDocument,
        'Save')
    },
    moveDocumentUp (document) {
      let index = this.currentDocuments.indexOf(document)
      if (index === 0) {
        return
      }
      let documentIds = []
      for (let i = 0; i < this.currentDocuments.length; ++i) {
        let indexToAdd = i
        if (i === index) {
          indexToAdd = i - 1
        } else if (i === (index - 1)) {
          indexToAdd = i + 1
        }
        documentIds.push(this.currentDocuments[indexToAdd]['id'])
      }
      axios.post(REORDER_DOCUMENTS_URL, {username: this.username, document_ids: documentIds}).then(
        response => {
          this.reloadCurrentDocumentsData()
        })
    },
    moveDocumentDown (document) {
      let index = this.currentDocuments.indexOf(document)
      if (index === (this.currentDocuments.length - 1)) {
        return
      }
      let documentIds = []
      for (let i = 0; i < this.currentDocuments.length; ++i) {
        let indexToAdd = i
        if (i === index) {
          indexToAdd = i + 1
        } else if (i === (index + 1)) {
          indexToAdd = i - 1
        }
        documentIds.push(this.currentDocuments[indexToAdd]['id'])
      }
      axios.post(REORDER_DOCUMENTS_URL, {username: this.username, document_ids: documentIds}).then(
        response => {
          this.reloadCurrentDocumentsData()
        })
    },
    deleteDocument (modalOutput) {
      axios.post(DELETE_DOCUMENT_URL, {id: modalOutput['id']})
        .then(
          response => {
            let deletedDocument = response['data']
            this.currentDocuments.splice(
              this.currentDocuments.findIndex(document => document['id'] === deletedDocument['id']), 1)
            this.closeModal()
            this.setCurrentStatus('Deleted ' + deletedDocument['title'])
          })
        .catch(error => {
          this.modalErrorText = 'An error occurred during delete.'
          console.log(error)
        })
    },
    editDocument (document) {
      axios.post(EDIT_DOCUMENT_URL, {document: document})
        .then(
          response => {
            let currentDocumentIndex =
              this.currentDocuments.findIndex(document => document.id === response['data']['id'])
            this.currentDocuments[currentDocumentIndex] = response['data']
            this.closeModal()
            this.setCurrentStatus('Saved ' + document['title'])
          })
        .catch(error => {
          this.modalErrorText = 'An error occurred during edit.'
          console.log(error)
        })
    },
    addDocument (document) {
      axios.post(ADD_DOCUMENT_URL, {document: document})
        .then(
          response => {
            let document = response['data']
            this.currentDocuments.push(document)
            this.closeModal()
            this.setCurrentStatus('Added ' + document['title'])
          })
        .catch(error => {
          this.modalErrorText = 'An error occurred during add.'
          console.log(error)
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
