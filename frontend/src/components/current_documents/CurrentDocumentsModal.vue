<template>
  <Modal :show="show" @close="close">
    <div class="modal-header">
     <h3>{{ title }}</h3>
    </div>
    <div class="modal-body">
      <label class="form-label">
        Title
        <input v-model="documentTitle" class="form-control">
      </label>
      <label class="form-label">
        Url
        <input v-model="documentUrl" class="form-control">
      </label>
      <label class="form-label">
        Notes
        <input v-model="documentNotes" class="form-control">
      </label>
    </div>
    <div class="modal-footer text-right">
      <button class="modal-default-button"
          @click="addOrEditDocument(documentTitle, documentUrl, documentNotes, documentId)">
        Save
      </button>
    </div>
  </Modal>
</template>
<style>
  @import "../../assets/style/modal.css"
</style>
<script>
import Modal from '../shared/Modal'

export default {
  name: 'CurrentDocumentsModal',
  props: {
    show: Boolean,
    title: String,
    initialDocumentTitle: String,
    initialDocumentUrl: String,
    initialDocumentNotes: String,
    documentId: Number,
    addOrEditDocument: Function
  },
  watch: {
    initialDocumentTitle () {
      this.documentTitle = this.initialDocumentTitle
    },
    initialDocumentUrl () {
      this.documentUrl = this.initialDocumentUrl
    },
    initialDocumentNotes () {
      this.documentNotes = this.initialDocumentNotes
    }
  },
  data () {
    return {
      documentTitle: this.initialDocumentTitle,
      documentUrl: this.initialDocumentUrl,
      documentNotes: this.initialDocumentNotes
    }
  },
  methods: {
    close () {
      this.$emit('close')
    }
  },
  components: {
    Modal
  }
}
</script>
