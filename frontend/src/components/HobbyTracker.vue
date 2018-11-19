<template>
  <div class="hobby-tracker">
    <div class="hobby-title">
      <header class="hobby-header">Hobbies</header>
      <button class="hobby-buttons" @click="showAddHobbyModal">Add Hobby</button>
      <button class="hobby-buttons">Edit</button>
      <button class="hobby-buttons">Save</button>
    </div>

    <div class="hobby-table">
      <div class="hobby-table-headers">
        <section>Hobby</section>
        <section>Assigned Hours</section>
        <section>Hours Completed</section>
        <section>Hours Remaining</section>
        <section>Completed?</section>
      </div>
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

export default {
  name: 'HobbyTracker',
  data () {
    return {
      showModal: false,
      hobbyName: '',
      assignedHoursPerWeek: 0
    }
  },
  computed: {
    username () {
      return store.state.username
    }
  },
  methods: {
    addHobby () {
      let hobbyItem = {}
      hobbyItem['username'] = this.username
      hobbyItem['hobby'] = this.hobbyName
      hobbyItem['assigned_hours_per_week'] = this.assignedHoursPerWeek

      axios.post(ADD_HOBBY_URL, { hobby: hobbyItem }).then(
        })

      this.showModal = false
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
