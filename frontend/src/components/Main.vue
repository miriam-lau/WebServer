<template>
  <div>
    <div class="welcome-bar">
      <div class="welcome-message">Welcome, {{ $store.state.username }}</div>
      <div class="login-bar">
        <input class="login-input" v-model="loginUsername" placeholder="Username">
        <button v-on:click="saveUsername">Login</button>
      </div>
      <div class="clearfix"></div>
    </div>
    <div class="nav-container">
      <nav :class="navigationClass" v-on:click.prevent>
        <a href="#" class="nav-pantry-page" v-on:click="navigateTo('pantryPage')">Pantry</a>
        <a
          href="#"
          class="nav-inventory-tracker"
          style="display:none"
          v-on:click="navigateTo('inventoryTracker')"
        >Inventory</a>
        <a href="#" class="nav-recipes-page" v-on:click="navigateTo('recipesPage')">Recipes</a>
        <a
          href="#"
          class="nav-restaurants-page"
          v-on:click="navigateTo('restaurantsPage')"
        >Restaurants</a>
        <a href="#" style="display:none" class="nav-search-recipes-page" v-on:click="navigateTo('searchRecipesPage')">Search-Recipes</a>
        <a href="#" style="display:none" class="nav-search-restaurants-page" v-on:click="navigateTo('searchRestaurantsPage')">Search-Restaurants</a>
        <a href="#" class="nav-notes-page" v-on:click="navigateTo('notesPage')">Notes</a>
        <a
          href="#"
          class="nav-current-documents"
          v-on:click="navigateTo('currentDocuments')"
        >Documents</a>
        <a href="#" style="display:none" class="nav-codenames" v-on:click="navigateTo('codenames')">Codenames</a>
        <a href="#" class="nav-dominion" v-on:click="navigateTo('dominion')">Dominion</a>
        <a href="#" style="display:none" class="nav-dominion-game" v-on:click="navigateTo('dominionGame')">Dominion Game</a>
        <a href="#" style="display:none" class="nav-lotr-game" v-on:click="navigateTo('lotrGame')">Lotr Game</a>
      </nav>
    </div>
    <router-view/>
  </div>
</template>

<script>
// To add a new menu item, add it to:
//   Main.vue
//   router/index.js
//   Add a new component.
//   assets/style.css.
import Codenames from './Codenames'
import CurrentDocuments from './CurrentDocuments'
import InventoryTracker from './InventoryTracker'
import RecipesPage from './RecipesPage'
import RestaurantsPage from './RestaurantsPage'
import SearchRecipesPage from './SearchRecipesPage'
import SearchRestaurantsPage from './SearchRestaurantsPage'
import PantryPage from './PantryPage'
import NotesPage from './NotesPage'
import Dominion from './Dominion'
import DominionGame from './DominionGame'
import LotrGame from './LotrGame'
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
    $route: function () {
      this.navigationClass = this.setNavigationClass()
    }
  },
  components: {
    CurrentDocuments,
    Codenames,
    Dominion,
    DominionGame,
    InventoryTracker,
    LotrGame,
    RecipesPage,
    RestaurantsPage,
    SearchRecipesPage,
    SearchRestaurantsPage,
    PantryPage,
    NotesPage
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
        case 'codenames':
          return 'nav-codenames'
        case 'recipesPage':
          return 'nav-recipes-page'
        case 'restaurantsPage':
          return 'nav-restaurants-page'
        case 'searchRecipesPage':
          return 'nav-search-recipes-page'
        case 'searchRestaurantsPage':
          return 'nav-search-restaurants-page'
        case 'pantryPage':
          return 'nav-pantry-page'
        case 'notesPage':
          return 'nav-notes-page'
        case 'inventoryTracker':
          return 'nav-inventory-tracker'
        case 'dominion':
          return 'nav-dominion'
        case 'dominionGame':
          return 'nav-dominion-game'
        case 'lotrGame':
          return 'nav-lotr-game'
      }
    }
  }
}
</script>
