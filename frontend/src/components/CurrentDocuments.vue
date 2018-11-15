<template>
  <div class="current-documents">
    <div class="current-documents-title">Current Documents</div>
    <table class="current-documents-list table">
      <tr>
        <th>Title</th><th>Url</th><th>Notes</th><th>Category</th><th>Edit</th><th>Cancel</th><th>Trash</th>
      </tr>
      <tr class="current-documents-item" :key="currentDocument.id" v-for="currentDocument in currentDocuments">
        <template v-if="currentDocument.editable">
          <td><input :id="'current-document-title-' + currentDocument.id" :value="currentDocument.title"/></td>
          <td><input :id="'current-document-url-' + currentDocument.id" :value="currentDocument.url"/></td>
          <td><input :id="'current-document-notes-' + currentDocument.id" :value="currentDocument.notes"/></td>
          <td><input :id="'current-document-category-' + currentDocument.id" :value="currentDocument.category"/></td>
          <td><font-awesome-icon icon="save" class="current-documents-edit" @click="saveRow(currentDocument.id)" /></td>
          <td><font-awesome-icon icon="times" class="current-documents-cancel"
              @click="cancelEditRow(currentDocument.id)" /></td>
          <td><font-awesome-icon icon="trash" class="current-documents-trash"
              @click="deleteRow(currentDocument.id)" /></td>
        </template>
        <template v-else>
          <td>{{ currentDocument.title }}</td>
          <td><a :href="currentDocument.url" target="_blank">Link</a></td>
          <td>{{ currentDocument.notes }}</td>
          <td>{{ currentDocument.category }}</td>
          <td><font-awesome-icon icon="pencil-alt" class="current-documents-edit"
              @click="makeRowEditable(currentDocument.id)" /></td>
          <td></td>
          <td><font-awesome-icon icon="trash" class="current-documents-trash"
              @click="deleteRow(currentDocument.id)" /></td>
        </template>
      </tr>
      <tr class="current-documents-item">
        <td><input id="current-document-title-add" placeholder="Title"/></td>
        <td><input id="current-document-url-add" placeholder="Url"/></td>
        <td><input id="current-document-notes-add" placeholder="Notes"/></td>
        <td><input id="current-document-category-add" placeholder="Category"/></td>
        <td><font-awesome-icon icon="save" class="current-documents-edit" @click="addRow()" /></td>
      </tr>
    </table>
  </div>
</template>
<style>
  @import "../assets/style/current-documents.css"
</style>
<script>
import axios from 'axios'
import { getFullBackendUrlForPath, getValueOfElementWithDefault } from '../common/utils'
import { store } from '../store/store'
import Vue from 'vue'

const GET_CURRENT_DOCUMENTS_URL = getFullBackendUrlForPath('/get_current_documents')
const DELETE_DOCUMENT_URL = getFullBackendUrlForPath('/delete_document')
const EDIT_DOCUMENT_URL = getFullBackendUrlForPath('/edit_document')
const ADD_DOCUMENT_URL = getFullBackendUrlForPath('/add_document')

export default {
  name: 'CurrentDocuments',
  data () {
    return {
      currentDocuments: {}
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
    makeRowEditable (id) {
      Vue.set(this.currentDocuments[id], 'editable', true)
    },
    deleteRow (id) {
      axios.post(DELETE_DOCUMENT_URL, {id: id}).then(
        response => {
          Vue.delete(this.currentDocuments, response.data.id)
        })
    },
    cancelEditRow (id) {
      Vue.set(this.currentDocuments[id], 'editable', false)
    },
    saveRow (id) {
      var document = this.currentDocuments[id]
      document.title = getValueOfElementWithDefault('current-document-title-' + id)
      document.url = getValueOfElementWithDefault('current-document-url-' + id)
      document.notes = getValueOfElementWithDefault('current-document-notes-' + id)
      document.category = getValueOfElementWithDefault('current-document-category-' + id)
      document.editable = false
      axios.post(EDIT_DOCUMENT_URL, {id: id, document: document}).then(
        response => {
          Vue.set(this.currentDocuments, id, response.data.document)
        })
    },
    addRow () {
      var document = {}
      document.username = this.username
      document.title = getValueOfElementWithDefault('current-document-title-add')
      document.url = getValueOfElementWithDefault('current-document-url-add')
      document.priority = 0
      document.notes = getValueOfElementWithDefault('current-document-notes-add')
      document.category = getValueOfElementWithDefault('current-document-category-add')
      axios.post(ADD_DOCUMENT_URL, {document: document}).then(
        response => {
          var id = response.data.id
          document.id = id
          Vue.set(this.currentDocuments, id, document)
        })
    }
  }
}
</script>
