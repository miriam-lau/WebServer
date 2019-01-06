<template>
  <div class="hobby-tracker">
    <ButterBar
      :message="butterBar_message"
      :css="butterBar_css"
    />

    <div class="hobby-title">
      <h2>Hobbies</h2>
      <div class="hobby-buttons">
        <button class="button" @click="showAddModal">Add Hobby</button>
        <button class="button" v-if="!editable" @click="editMode">Edit</button>
        <button class="button" v-else @click="editHobbies">Save</button>
      </div>
    </div>

    <div class="hobby-table-container">
      <table class="hobby-table table">
        <tr class="hobby-table-headers">
          <th>Hobby</th>
          <th>Assigned Hours</th>
          <th>Hours Completed</th>
          <th>Hours Remaining</th>
          <th>Completed?</th>
          <th>Delete</th>
        </tr>
        <tr class="hobby-items" :key="hobby['id']" v-for="hobby in hobbies">
          <template v-if="editable">
            <td><input v-model="hobby['hobby']"/></td>
            <td><input v-model="hobby['assigned_hours_per_week']"/></td>
            <td><input v-model="hobby['completed_hours_for_week']"/></td>
            <td>{{ getHoursRemaining(hobby) }}</td>
            <td>{{ isHobbyCompletedForWeek(hobby) }}</td>
            <td><font-awesome-icon icon="trash" class="icon" @click="showDeleteModal(hobby)"/></td>
          </template>
          <template v-else>
            <td class="hobby-item-name">{{ hobby['hobby'] }}</td>
            <td>{{ hobby['assigned_hours_per_week'] }}</td>
            <td>{{ hobby['completed_hours_for_week'] }}</td>
            <td>{{ getHoursRemaining(hobby) }} </td>
            <td>{{ isHobbyCompletedForWeek(hobby) }}</td>
            <td><font-awesome-icon icon="trash" class="icon" @click="showDeleteModal(hobby)" /></td>
          </template>
        </tr>
      </table><br/>
      <h3>Last week:</h3>
      <table class="hobby-table table">
        <tr class="hobby-table-headers">
          <th>Hobby</th>
          <th>Assigned Hours</th>
          <th>Hours Completed</th>
          <th>Hours Remaining</th>
          <th>Completed?</th>
        </tr>
        <tr class="hobby-items" :key="hobby['id']" v-for="hobby in last_week_hobbies">
          <td class="hobby-item-name">{{ hobby['hobby'] }}</td>
          <td>{{ hobby['assigned_hours_per_week'] }}</td>
          <td>{{ hobby['completed_hours_for_week'] }}</td>
          <td>{{ getHoursRemaining(hobby) }} </td>
          <td>{{ isHobbyCompletedForWeek(hobby) }}</td>
        </tr>
      </table>
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
</template>

<style>
  @import "../assets/style/hobby-tracker.css"
</style>

<script>
import ButterBar from './shared/ButterBar'
import { setButterBarMessage, ButterBarType, callAxiosAndSetButterBar } from '../common/butterbar_component'

import FormModal from './shared/FormModal'
import { showModal, createFormModalEntry, generateAxiosModalCallback } from '../common/form_modal_component'

import { getFullBackendUrlForPath } from '../common/utils'
import { store } from '../store/store'

const ADD_HOBBY_URL = getFullBackendUrlForPath('/add_hobby')
const DELETE_HOBBY_URL = getFullBackendUrlForPath('/delete_hobby')
const EDIT_HOBBIES_URL = getFullBackendUrlForPath('/edit_hobbies')
const GET_HOBBIES_URL = getFullBackendUrlForPath('/get_hobbies')

export default {
  name: 'HobbyTracker',
  data () {
    return {
      showModal: false,
      hobbyName: '',
      assignedHoursPerWeek: 0,
      hobbies: [],
      last_week_hobbies: [],
      editable: false,

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
    ButterBar,
    FormModal
  },
  computed: {
    username () {
      return store.state.username
    }
  },
  created () {
    this.updateHobbyDisplay()
  },
  methods: {
    formModal_close () {
      this.formModal_show = false
    },
    addHobby (response) {
      let addedHobby = response.data
      this.hobbies.push(addedHobby)
      setButterBarMessage(this, 'Added ' + addedHobby['hobby'], ButterBarType.INFO)
    },
    updateHobbyDisplay () {
      callAxiosAndSetButterBar(
        this,
        GET_HOBBIES_URL,
        { username: this.username },
        null,
        'Failed to update hobby display.',
        (response) => {
          this.hobbies = response.data['hobbies']
          this.last_week_hobbies = response.data['last_week_hobbies']
        })
    },
    showDeleteModal (hobby) {
      showModal(
        this,
        'Deleting ' + hobby['hobby'],
        [],
        { id: hobby['id'] },
        generateAxiosModalCallback(this, DELETE_HOBBY_URL, this.deleteHobby),
        'Delete',
        'Error deleting ' + hobby['hobby'])
    },
    deleteHobby (response) {
      let deletedHobby = response.data
      this.hobbies.splice(
        this.hobbies.findIndex(hobbies => hobbies['id'] === deletedHobby['id']), 1)
      setButterBarMessage(this, 'Deleted ' + deletedHobby['hobby'], ButterBarType.INFO)
    },
    editHobbies () {
      callAxiosAndSetButterBar(
        this, EDIT_HOBBIES_URL, { hobbies: this.hobbies },
        'Edits saved',
        'Error saving edits',
        response => {
          this.updateHobbyDisplay()
          this.editable = false
        })
    },
    showAddModal () {
      let formModalFormLines = [
        createFormModalEntry('add-hobby-modal-hobby', 'hobby', 'Hobby Name:'),
        createFormModalEntry('add-hobby-modal-assigned-hours', 'assigned_hours_per_week', 'Assigned Hours Per Week:')
      ]
      showModal(
        this,
        'Add a Hobby',
        formModalFormLines,
        { username: this.username },
        generateAxiosModalCallback(this, ADD_HOBBY_URL, this.addHobby),
        'Save',
        'Error adding hobby')
    },
    editMode () {
      this.editable = true
    },
    isHobbyCompletedForWeek (hobby) {
      return (hobby['completed_hours_for_week'] >= hobby['assigned_hours_per_week'])
    },
    getHoursRemaining (hobby) {
      if (this.isHobbyCompletedForWeek(hobby)) {
        return 0
      }
      return hobby['assigned_hours_per_week'] - hobby['completed_hours_for_week']
    }
  }
}
</script>
