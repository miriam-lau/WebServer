<template>
  <div>
    <div class="welcome-bar">
      <div class="welcome-message">
        Welcome, {{ $store.state.username }}
      </div>
      <div class="login-bar">
        <input class="login-input" v-model="loginUsername" placeholder='Username'/>
        <button v-on:click="saveUsername">Login</button>
      </div>
      <div class="clearfix"></div>
    </div>
    <div class="nav-container">
      <nav :class="activeTab" v-on:click.prevent>
        <a href="#" class="nav-current-documents"
          v-on:click="setActiveTab('nav-current-documents')">Current Documents</a>
        <a href="#" class="nav-hobby-tracker" v-on:click="setActiveTab('nav-hobby-tracker')">Hobby Tracker</a>
        <a href="#" class="nav-codenames-game" v-on:click="setActiveTab('nav-codenames-game')">Codenames</a>
      </nav>
    </div>
    <div v-if="isCurrentDocumentsActive">
      <CurrentDocuments/>
    </div>
    <div v-if="isHobbyTrackerActive">
      <HobbyTracker/>
    </div>
    <div v-if="isCodenamesGameActive">
      <Codenames/>
    </div>
  </div>
</template>

<script>
import Codenames from './Codenames'
import CurrentDocuments from './CurrentDocuments'
import HobbyTracker from './HobbyTracker'
import { mapMutations } from 'vuex'

export default {
  name: 'Home',
  data () {
    return {
      loginUsername: '',
      activeTab: 'nav-current-documents'
    }
  },
  computed: {
    isCurrentDocumentsActive () {
      return this.activeTab === 'nav-current-documents'
    },
    isHobbyTrackerActive () {
      return this.activeTab === 'nav-hobby-tracker'
    },
    isCodenamesGameActive () {
      return this.activeTab === 'nav-codenames-game'
    }
  },
  created () {
    this.setUsername(this.$cookies.get('username'))
  },
  components: {
    CurrentDocuments, Codenames, HobbyTracker
  },
  methods: {
    ...mapMutations(['setUsername']),
    saveUsername () {
      this.setUsername(this.loginUsername)
      this.$cookies.set('username', this.loginUsername)
    },
    setActiveTab (tab) {
      this.activeTab = tab
    }
  }
}
</script>
