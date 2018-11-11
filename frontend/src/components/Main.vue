<template>
  <div>
    <div class="welcome-bar">
      <div class="welcome-message">
        Welcome, {{ username }}
      </div>
      <div class="login-bar">
        <input v-model="loginUsername" placeholder='Username'/> <button v-on:click="saveUsername">Login</button>
      </div>
      <div class="clearfix"></div>
    </div>
    <Codenames />
  </div>
</template>

<script>
import Codenames from './Codenames'

export default {
  name: 'Home',
  data () {
    return {
      username: this.$cookies.get('username'),
      loginUsername: ''
    }
  },
  components: {
    Codenames
  },
  methods: {
    saveUsername () {
      this.username = this.loginUsername
      this.$cookies.set('username', this.loginUsername)
    }
  }
}
</script>
