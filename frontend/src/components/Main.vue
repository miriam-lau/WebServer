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
      <nav :class="navigationClass" v-on:click.prevent>
        <a href="#" class="nav-notes-page" v-on:click="navigateTo('notesPage')">Notes</a>
        <a href="#" class="nav-current-documents"
          v-on:click="navigateTo('currentDocuments')">Documents</a>
        <a href="#" class="nav-hobby-tracker" v-on:click="navigateTo('hobbyTracker')">Hobbies</a>
        <a href="#" class="nav-pantry-page" v-on:click="navigateTo('pantryPage')">Pantry</a>
        <a href="#" class="nav-inventory-tracker" v-on:click="navigateTo('inventoryTracker')">Inventory</a>
        <a href="#" class="nav-recipes-page" v-on:click="navigateTo('recipesPage')">Recipes</a>
        <a href="#" class="nav-restaurants-page" v-on:click="navigateTo('restaurantsPage')">Restaurants</a>
        <a href="#" class="nav-codenames" v-on:click="navigateTo('codenames')">Codenames</a>
        <a href="#" class="nav-dominion" v-on:click="navigateTo('dominion')">Dominion</a>
      </nav>
    </div>
    <router-view/>
  </div>
</template>

<script>
import Codenames from './Codenames'
import CurrentDocuments from './CurrentDocuments'
import HobbyTracker from './HobbyTracker'
import InventoryTracker from './InventoryTracker'
import RecipesPage from './RecipesPage'
import RestaurantsPage from './RestaurantsPage'
import PantryPage from './PantryPage'
import NotesPage from './NotesPage'
import Dominion from './Dominion'
import { mapMutations } from 'vuex'

export default {
  name: 'Main',
  data () {
    return {
      loginUsername: '',
      navigationClass: this.setNavigationClass()
    }
  },
  created () {
    this.setUsername(this.$cookies.get('username'))
  },
  watch: {
    '$route': function () {
      this.navigationClass = this.setNavigationClass()
    }
  },
  components: {
    CurrentDocuments, Codenames, Dominion, HobbyTracker, InventoryTracker, RecipesPage, RestaurantsPage, PantryPage, NotesPage
  },
  methods: {
    ...mapMutations(['setUsername']),
    saveUsername () {
      this.setUsername(this.loginUsername)
      this.$cookies.set('username', this.loginUsername, '1y')
    },
    navigateTo (path) {
      this.$router.push({ name: path })
    },
    setNavigationClass () {
      switch (this.$route.name) {
        case 'currentDocuments':
          return 'nav-current-documents'
        case 'hobbyTracker':
          return 'nav-hobby-tracker'
        case 'codenames':
          return 'nav-codenames'
        case 'recipesPage':
          return 'nav-recipes-page'
        case 'restaurantsPage':
          return 'nav-restaurants-page'
        case 'pantryPage':
          return 'nav-pantry-page'
        case 'notesPage':
          return 'nav-notes-page'
        case 'inventoryTracker':
          return 'nav-inventory-tracker'
        case 'dominion':
          return 'nav-dominion'
      }
    }
  }
}
</script>
