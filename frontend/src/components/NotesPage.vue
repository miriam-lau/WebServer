<template>
  <div>
    <ButterBar
      :message="butterBar_message"
      :css="butterBar_css"
    />
    <div class="notes-notes">
        <h2>Notes</h2>
        <div class="notes-single-note" v-for="note in notes" :key="note['id']">
            <div>
                {{ note['title'] }}
                <font-awesome-icon icon="pencil-alt" class="notes-icon"
                    @click="showEditNoteMetadataModal(note)" />
                <font-awesome-icon icon="trash" class="notes-icon"
                    @click="showDeleteNoteModal(note)" />
            </div>
            <div class="notes-text">
                <EditableDiv
                  :key="noteKey"
                  :content="note['text']"
                  :handleUpdate="updateNoteText.bind(this, note)"
                />
            </div>
            <div v-if="note['saved']">
                Saved.
            </div>
            <div v-else>
                Unsaved.
                <button @click="editNote(note)">Save</button>
                <button @click="cancelEditNoteText(note)">Cancel</button>
            </div>
        </div>
        <input v-model="noteTitleToAdd" /> <button @click="addNote">Add Note</button>
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
  </div>
</template>
<style>
  @import "../assets/style/notes.css"
</style>
<script>
import ButterBar from './shared/ButterBar'
import { setButterBarMessage, ButterBarType } from '../common/butterbar_component'

import EditableDiv from './shared/EditableDiv'
import FormModal from './shared/FormModal'
import axios from 'axios'
import { getFullBackendUrlForPath, createFormModalEntry } from '../common/utils'

const GET_NOTES_PAGE_URL = getFullBackendUrlForPath('/get_notes_page')
const EDIT_NOTES_METADATA_URL = getFullBackendUrlForPath('/edit_note_metadata')
const DELETE_NOTES_URL = getFullBackendUrlForPath('/delete_note')
const EDIT_NOTES_URL = getFullBackendUrlForPath('/edit_note')
const ADD_NOTES_URL = getFullBackendUrlForPath('/add_note')

export default {
  name: 'NotesPage',
  data () {
    return {
      notes: [],
      noteTitleToAdd: '',
      modalTitle: '',
      modalFormLines: [],
      modalPassThroughProps: {},
      modalCallback: Function,
      modalButtonText: '',
      modalErrorText: '',
      noteKey: 0,
      shouldShowModal: false,

      butterBar_message: '',
      butterBar_css: ''
    }
  },
  components: {
    FormModal, EditableDiv, ButterBar
  },
  created () {
    this.updateNotesPageDisplay()
  },
  methods: {
    updateNoteText (note, newText) {
      console.log(note)
      if (note['saved']) {
        note['saved'] = false
        note['backedUpText'] = note['text']
      }
      note['text'] = newText.target.innerText
    },
    cancelEditNoteText (note) {
      if (!note['saved']) {
        note['saved'] = true
        note['text'] = note['backedUpText']
        delete note['backedUpText']
        this.noteKey += 1 // Force a re-render of the EditableDiv of this note.
      }
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
    showEditNoteMetadataModal (note) {
      let modalFormLines = [
        createFormModalEntry(
          'edit-note-metadata-modal-title-' + note['id'], 'title', 'Title:', note['title'])
      ]
      this.showModal(
        'Editing ' + note['title'],
        modalFormLines,
        note,
        this.editNoteMetadata,
        'Save')
    },
    showDeleteNoteModal (note) {
      this.showModal(
        'Deleting ' + note['title'],
        [],
        { id: note['id'] },
        this.deleteNote,
        'Delete')
    },
    editNoteMetadata (note) {
      axios.post(
        EDIT_NOTES_METADATA_URL,
        {
          id: note['id'],
          title: note['title']
        })
        .then(response => {
          let currentNoteIndex =
            this.notes.findIndex(note => note['id'] === response['data']['id'])
          let newNoteItem = this.notes[currentNoteIndex]
          newNoteItem['title'] = response['data']['title']
          this.notes.splice(currentNoteIndex, 1, newNoteItem)
          this.closeModal()
          setButterBarMessage(this, 'Saved title of ' + note['title'], ButterBarType.INFO)
        })
        .catch(error => {
          this.modalErrorText = 'An error occurred during edit.'
          console.log(error)
        })
    },
    editNote (note) {
      axios.post(EDIT_NOTES_URL, {id: note['id'], text: note['text']})
        .then(response => {
          let currentNoteIndex =
            this.notes.findIndex(note => note['id'] === response['data']['id'])
          response['data']['saved'] = true
          this.notes.splice(currentNoteIndex, 1, response['data'])
          setButterBarMessage(this, 'Saved contents of ' + note['title'], ButterBarType.INFO)
        })
        .catch(error => {
          this.modalErrorText = 'An error occurred during edit.'
          console.log(error)
        })
    },
    deleteNote (note) {
      axios.post(DELETE_NOTES_URL, {id: note['id']}).then(response => {
        let deletedNote = response['data']
        this.notes.splice(
          this.notes.findIndex(note => note['id'] === deletedNote['id']), 1)
        this.closeModal()
        setButterBarMessage(this, 'Deleted ' + deletedNote['title'], ButterBarType.INFO)
      })
        .catch(error => {
          this.modalErrorText = 'An error occurred during delete.'
          console.log(error)
        })
    },
    addNote () {
      axios.post(ADD_NOTES_URL, {title: this.noteTitleToAdd})
        .then(
          response => {
            this.noteTitleToAdd = ''
            let note = response['data']
            this.notes.push(note)
            this.closeModal()
            setButterBarMessage(this, 'Added ' + note['title'], ButterBarType.INFO)
          })
        .catch(error => {
          this.modalErrorText = 'An error occurred during add.'
          console.log(error)
        })
    },
    updateNotesPageDisplay () {
      axios.post(GET_NOTES_PAGE_URL).then(
        response => {
          this.notes = response['data']
          for (let index in this.notes) {
            this.notes[index]['saved'] = true
          }
        })
    }
  }
}
</script>
