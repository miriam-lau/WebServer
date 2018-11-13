<template>
  <div>
    <div class="welcome-bar">
      <div class="welcome-message">
        Welcome, {{ $store.state.username }}
      </div>
      <div class="login-bar">
        <input v-model="loginUsername" placeholder='Username'/> <button v-on:click="saveUsername">Login</button>
      </div>
      <div class="clearfix"></div>
    </div>
    <CurrentDocuments/>
    <Codenames/>
  </div>
</template>

<script>
import Codenames from './Codenames'
import CurrentDocuments from './CurrentDocuments'
import { mapMutations } from 'vuex'

export default {
  name: 'Home',
  data () {
    return {
      loginUsername: ''
    }
  },
  created () {
    this.setUsername(this.$cookies.get('username'))
  },
  components: {
    CurrentDocuments, Codenames
  },
  methods: {
    ...mapMutations(['setUsername']),
    saveUsername () {
      this.setUsername(this.loginUsername)
      this.$cookies.set('username', this.loginUsername)
    }
  }
}
</script>
