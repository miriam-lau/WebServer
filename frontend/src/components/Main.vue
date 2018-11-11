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
    <Codenames />
  </div>
</template>

<script>
import { mapMutations } from 'vuex'
import Codenames from './Codenames'

export default {
  name: 'Home',
  data () {
    return {
      loginUsername: ''
    }
  },
  created: function () {
    this.setUsername(this.$cookies.get('username'))
  },
  components: {
    Codenames
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
