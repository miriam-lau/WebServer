<template>
  <div id="app">
    <router-view/>
  </div>
</template>

<style>
  @import "./assets/style/style.css"
</style>
<script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/1.3.6/socket.io.min.js"></script>
<script>
export default {
  name: 'App'
}
</script>
