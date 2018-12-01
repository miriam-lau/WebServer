<template>
  <div>
    <ButterBar
      :message="butterBar_message"
      :css="butterBar_css"
    />
    <div class="notes-notes">
        <h2>Notes</h2>
        <div class="input-form">
          <input v-model="noteTitleToAdd" /> <button @click="addNote">Add Note</button>
        </div>
        <div class="notes-single-note" v-for="note in notes" :key="note['id']">
            <div>
                {{ note['title'] }}
                <font-awesome-icon icon="pencil-alt" class="icon"
                    @click="showEditNoteMetadataModal(note)" />
                <font-awesome-icon icon="trash" class="icon"
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
  @import "../assets/style/notes.css"
</style>
<script>
import ButterBar from './shared/ButterBar'
import { setButterBarMessage, ButterBarType, callAxiosAndSetButterBar } from '../common/butterbar_component'

import FormModal from './shared/FormModal'
import { showModal, createFormModalEntry, generateAxiosModalCallback } from '../common/form_modal_component'

import EditableDiv from './shared/EditableDiv'
import axios from 'axios'
import { getFullBackendUrlForPath } from '../common/utils'

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

      noteKey: 0,

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
    this.updateNotesPageDisplay()
  },
  watch: {
    allNotesSaved: function (oldValue, newValue) {
      if (newValue) {
        window.onbeforeunload = function () { return '' }
      } else {
        window.onbeforeunload = function () { return null }
      }
    }
  },
  beforeRouteLeave (to, from, next) {
    if (!this.allNotesSaved) {
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
    allNotesSaved: function () {
      for (let index in this.notes) {
        if (!this.notes[index]['saved']) {
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
    updateNoteText (note, newText) {
      if (note['saved']) {
        note['saved'] = false
      }
      note['text'] = newText.target.innerText
    },
    showEditNoteMetadataModal (note) {
      let modalFormLines = [
        createFormModalEntry(
          'edit-note-metadata-modal-title-' + note['id'], 'title', 'Title:', note['title'])
      ]
      showModal(
        this,
        'Editing ' + note['title'],
        modalFormLines,
        note,
        generateAxiosModalCallback(this, EDIT_NOTES_METADATA_URL, this.editNoteMetadata),
        'Save',
        'Error editing ' + note['title'])
    },
    showDeleteNoteModal (note) {
      showModal(
        this,
        'Deleting ' + note['title'],
        [],
        { id: note['id'] },
        generateAxiosModalCallback(this, DELETE_NOTES_URL, this.deleteNote),
        'Delete',
        'Error deleting ' + note['title'])
    },
    editNoteMetadata (response) {
      let currentNoteIndex = this.notes.findIndex(note => note['id'] === response['data']['id'])
      let newNoteItem = this.notes[currentNoteIndex]
      let oldTitle = this.notes[currentNoteIndex]['title']
      newNoteItem['title'] = response['data']['title']
      this.notes.splice(currentNoteIndex, 1, newNoteItem)
      setButterBarMessage(this, 'Saved title of ' + oldTitle, ButterBarType.INFO)
    },
    editNote (note) {
      callAxiosAndSetButterBar(
        this, EDIT_NOTES_URL, { id: note['id'], text: note['text'] },
        'Saved contents of ' + note['title'],
        'Error saving contents of ' + note['title'],
        response => {
          let currentNoteIndex =
            this.notes.findIndex(note => note['id'] === response['data']['id'])
          response['data']['saved'] = true
          this.notes.splice(currentNoteIndex, 1, response['data'])
        })
    },
    deleteNote (response) {
      let deletedNote = response['data']
      this.notes.splice(
        this.notes.findIndex(note => note['id'] === deletedNote['id']), 1)
      setButterBarMessage(this, 'Deleted ' + deletedNote['title'], ButterBarType.INFO)
    },
    addNote () {
      callAxiosAndSetButterBar(
        this, ADD_NOTES_URL, { title: this.noteTitleToAdd },
        'Added ' + this.noteTitleToAdd,
        'Error adding ' + this.noteTitleToAdd,
        response => {
          this.noteTitleToAdd = ''
          let note = response['data']
          note['saved'] = true
          this.notes.push(note)
        })
    },
    updateNotesPageDisplay () {
      axios.post(GET_NOTES_PAGE_URL).then(
        response => {
          for (let index in response['data']) {
            response['data'][index]['saved'] = true
          }
          this.notes = response['data']
        })
    }
  }
}
</script>
