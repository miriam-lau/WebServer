<template>
  <div class="inventory-tracker">
    <div class="inventory-title">
      <header>Inventory</header>
      <button class="button" @click="addInventoryBox">Add New Box</button>
    </div>
  </div>
</template>

<style>
  @import "../assets/style/inventory-tracker.css"
</style>

<script>
import { store } from '../store/store'

export default {
  name: 'InventoryTracker',
  data () {
    return {
      inventory: []
    }
  },
  computed: {
    username () {
      return store.state.username
    }
  },
  methods: {
    addInventoryBox () {
      console.log('add new inventory box')
    }
  }
}
</script>
