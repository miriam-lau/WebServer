<template>
  <div>
    <p>Welcome, {{ username }}</p>
  </div>
</template>

<script>
export default {
  name: 'Home',
  data () {
    return {
      username: this.$cookies.get('username')
    }
  }
}
</script>
