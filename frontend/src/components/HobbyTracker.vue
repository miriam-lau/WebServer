<template>
  <div class="hobby-tracker">
    <div class="hobby-title">
      <header class="hobby-header">Hobbies</header>
      <button class="hobby-buttons" @click="showAddHobbyModal">Add Hobby</button>
      <button class="hobby-buttons">Edit</button>
      <button class="hobby-buttons">Save</button>
    </div>

    <div class="hobby-table-container">
      <table class="hobby-table">
        <tr class="hobby-table-headers">
          <th>Hobby</th>
          <th>Assigned Hours</th>
          <th>Hours Completed</th>
          <th>Hours Remaining</th>
          <th>Completed?</th>
          <th>Delete</th>
        </tr>
        <tr class="hobby-items" :key="hobby['id']" v-for="hobby in hobbies">
          <td class="hobby-item-name">{{ hobby['hobby'] }}</td>
          <td>{{ hobby['assigned_hours_per_week'] }}</td>
          <td>{{ hobby['completed_hours_this_week'] }}</td>
          <td>{{ hobby['assigned_hours_per_week'] - hobby['completed_hours_this_week'] }} </td>
          <td>{{ hobby['completed'] }}</td>
          <td><font-awesome-icon icon="trash" class="hobby-icon" @click="deleteHobby(hobby['id'])" /></td>
        </tr>
      </table>
    </div>

    <div class="hobby-modal-container" v-if="showModal">
      <div class="hobby-modal">
        <section class="add-hobby-title">Add a Hobby</section>
        <section class="hobby-modal-sections">
          <article class="add-hobby-section-titles">Hobby Name</article>
          <input class="add-hobby-inputs" v-model="hobbyName" placeholder="What's your passion?">
        </section>
        <section class="hobby-modal-sections">
          <article class="add-hobby-section-titles">Assigned Hours Per Week</article>
          <input class="add-hobby-inputs" v-model="assignedHoursPerWeek" placeholder="Enter a number">
        </section>
        <section class="hobby-modal-button-container">
          <button class="hobby-buttons" @click="addHobby">Save</button>
          <button class="hobby-buttons close-hobby-button" @click="closeHobbyModal">Cancel</button>
        </section>
      </div>
    </div>

  </div>
</template>

<style>
  @import "../assets/style/hobby-tracker.css"
</style>

<script>
import axios from 'axios'
import { getFullBackendUrlForPath } from '../common/utils'
import { store } from '../store/store'

const ADD_HOBBY_URL = getFullBackendUrlForPath('/add_hobby')
const DELETE_HOBBY_URL = getFullBackendUrlForPath('/delete_hobby')
const GET_HOBBIES_URL = getFullBackendUrlForPath('/get_hobbies')

export default {
  name: 'HobbyTracker',
  data () {
    return {
      showModal: false,
      hobbyName: '',
      assignedHoursPerWeek: 0,
      hobbies: []
    }
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
    addHobby () {
      let hobbyItem = {}
      hobbyItem['username'] = this.username
      hobbyItem['hobby'] = this.hobbyName
      hobbyItem['assigned_hours_per_week'] = this.assignedHoursPerWeek

      axios.post(ADD_HOBBY_URL, { hobby: hobbyItem }).then(response => {
        this.updateHobbyDisplay()
        this.showModal = false
      })
    },
    updateHobbyDisplay () {
      axios.post(GET_HOBBIES_URL, { username: this.username }).then(response => { this.hobbies = response.data })
    },
    deleteHobby (id) {
      axios.post(DELETE_HOBBY_URL, { id }).then(response => { this.updateHobbyDisplay() })
    },
    showAddHobbyModal () {
      this.showModal = true
      this.hobbyName = ''
      this.assignedHoursPerWeek = 0
    },
    closeHobbyModal () {
      this.showModal = false
    }
  }
}
</script>
