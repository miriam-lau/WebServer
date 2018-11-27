<template>
  <div class="current-documents">
    <ButterBar
      :message="butterBar_message"
      :css="butterBar_css"
    />
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
  @import "../assets/style/current-documents.css"
</style>
<script>
import ButterBar from './shared/ButterBar'
import { setButterBarMessage, ButterBarType } from '../common/butterbar_component'

import FormModal from './shared/FormModal'
import { showModal, createFormModalEntry, generateAxiosModalCallback } from '../common/form_modal_component'

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
    FormModal, ButterBar
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
  methods: {
    formModal_close () {
      this.formModal_show = false
    },
    reloadCurrentDocumentsData () {
      axios.post(GET_CURRENT_DOCUMENTS_URL, {username: this.username}).then(
        response => {
          this.currentDocuments = response['data']
        })
    },
    showEditModal (document) {
      let formModalFormLines = [
        createFormModalEntry('edit-document-modal-title-' + document['id'], 'title', 'Title:', document['title']),
        createFormModalEntry('edit-document-modal-url-' + document['id'], 'url', 'URL:', document['url']),
        createFormModalEntry('edit-document-modal-notes-' + document['id'], 'notes', 'Notes:', document['notes'])
      ]
      showModal(
        this,
        'Editing ' + document['title'],
        formModalFormLines,
        document,
        generateAxiosModalCallback(this, EDIT_DOCUMENT_URL, this.editDocument),
        'Save',
        'Error saving ' + document['title'])
    },
    showDeleteModal (document) {
      showModal(
        this,
        'Deleting ' + document['title'],
        [],
        { id: document['id'] },
        generateAxiosModalCallback(this, DELETE_DOCUMENT_URL, this.deleteDocument),
        'Delete',
        'Error deleting ' + document['title'])
    },
    showAddModal () {
      let formModalFormLines = [
        createFormModalEntry('add-document-modal-title', 'title', 'Title:'),
        createFormModalEntry('add-document-modal-url', 'url', 'URL:'),
        createFormModalEntry('add-document-modal-notes', 'notes', 'Notes:')
      ]
      showModal(
        this,
        'Adding a new document',
        formModalFormLines,
        { username: this.username },
        generateAxiosModalCallback(this, ADD_DOCUMENT_URL, this.addDocument),
        'Save',
        'Error adding document')
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
    deleteDocument (response) {
      let deletedDocument = response['data']
      this.currentDocuments.splice(
        this.currentDocuments.findIndex(document => document['id'] === deletedDocument['id']), 1)
      setButterBarMessage(this, 'Deleted ' + deletedDocument['title'], ButterBarType.INFO)
    },
    editDocument (response) {
      let currentDocumentIndex =
        this.currentDocuments.findIndex(document => document.id === response['data']['id'])
      this.currentDocuments[currentDocumentIndex] = response['data']
      this.formModal_close()
      setButterBarMessage(this, 'Saved ' + document['title'], ButterBarType.INFO)
    },
    addDocument (response) {
      let document = response['data']
      this.currentDocuments.push(document)
      setButterBarMessage(this, 'Added ' + document['title'], ButterBarType.INFO)
    }
  }
}
</script>
