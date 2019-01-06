<template>
  <div id="app">
    <Main/>
  </div>
</template>

<style>
  @import "./assets/style/style.css"
</style>
<script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/1.3.6/socket.io.min.js"></script>
<script>
import Main from './components/Main'
import { connect } from './common/socketio'

export default {
  name: 'App',
  components: {
    Main
  },
  beforeCreate () {
    connect()
  }
}
</script>
