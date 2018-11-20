<template>
  <div class="current-documents">
    <table class="current-documents-list table">
      <tr>
        <th>Title</th><th>Notes</th><th>Modify</th>
      </tr>
      <tr class="current-documents-item" :key="index"
          v-for="(currentDocument, index) in currentDocuments">
        <td><a :href="currentDocument['url']" target="_blank">{{ currentDocument['title'] }}</a></td>
        <td>{{ currentDocument['notes'] }}</td>
        <td><font-awesome-icon icon="pencil-alt" class="current-documents-icon"
            @click="showEditModal(index)" />
            <font-awesome-icon icon="trash" class="current-documents-icon"
            @click="deleteDocument(index)" />
            <font-awesome-icon icon="long-arrow-alt-up" class="current-documents-icon"
            @click="moveDocumentUp(index)" />
            <font-awesome-icon icon="long-arrow-alt-down" class="current-documents-icon"
            @click="moveDocumentDown(index)" />
        </td>
      </tr>
    </table>
    <button @click="showAddModal()">Add Document</button>
    <CurrentDocumentsModal :show="showModal" @close="showModal = false"
        :title="modalTitle" :initialDocumentTitle="modalDocumentTitle" :initialDocumentUrl="modalDocumentUrl"
        :initialDocumentNotes="modalDocumentNotes" :documentId="modalDocumentId"
        :addOrEditDocument="addOrEditDocument" />
  </div>
</template>
<style>
  @import "../assets/style/current-documents.css"
</style>
<script>
import CurrentDocumentsModal from './current_documents/CurrentDocumentsModal'
import axios from 'axios'
import { getFullBackendUrlForPath } from '../common/utils'
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
      modalTitle: '',
      modalDocumentTitle: '',
      modalDocumentUrl: '',
      modalDocumentNotes: '',
      modalDocumentId: null,
      showModal: false
    }
  },
  created () {
    this.updateCurrentDocumentsDisplay()
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
  components: {
    CurrentDocumentsModal
  },
  methods: {
    updateCurrentDocumentsDisplay () {
      axios.post(GET_CURRENT_DOCUMENTS_URL, {username: this.username}).then(
        response => {
          this.currentDocuments = response['data']
        })
    },
    showEditModal (index) {
      let document = this.currentDocuments[index]
      this.modalTitle = 'Editing ' + document['title']
      this.modalDocumentTitle = document['title']
      this.modalDocumentUrl = document['url']
      this.modalDocumentNotes = document['notes']
      this.modalDocumentId = document['id']
      this.showModal = true
    },
    showAddModal () {
      this.modalTitle = 'Adding a new document'
      this.modalDocumentTitle = ''
      this.modalDocumentUrl = ''
      this.modalDocumentNotes = ''
      this.modalDocumentId = null
      this.showModal = true
    },
    deleteDocument (index) {
      axios.post(DELETE_DOCUMENT_URL, {id: this.currentDocuments[index]['id']}).then(
        response => {
          this.updateCurrentDocumentsDisplay()
        })
    },
    moveDocumentUp (index) {
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
          this.updateCurrentDocumentsDisplay()
        })
    },
    moveDocumentDown (index) {
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
          this.updateCurrentDocumentsDisplay()
        })
    },
    addOrEditDocument (title, url, notes, id) {
      var document = {}
      document['username'] = this.username
      document['title'] = title
      document['url'] = url
      document['notes'] = notes
      if (id != null) {
        document['id'] = id
        axios.post(EDIT_DOCUMENT_URL, {id: id, document: document}).then(
          response => {
            this.updateCurrentDocumentsDisplay()
            this.showModal = false
          })
      } else {
        axios.post(ADD_DOCUMENT_URL, {document: document}).then(
          response => {
            this.updateCurrentDocumentsDisplay()
            this.showModal = false
          })
      }
    }
  }
}
</script>
