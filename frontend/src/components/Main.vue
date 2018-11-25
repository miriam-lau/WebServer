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
        <a href="#" class="nav-current-documents"
          v-on:click="navigateTo('currentDocuments')">Current Documents</a>
        <a href="#" class="nav-hobby-tracker" v-on:click="navigateTo('hobbyTracker')">Hobby Tracker</a>
        <a href="#" class="nav-codenames" v-on:click="navigateTo('codenames')">Codenames</a>
        <a href="#" class="nav-recipes-page" v-on:click="navigateTo('recipesPage')">Recipes</a>
        <a href="#" class="nav-restaurants-page" v-on:click="navigateTo('restaurantsPage')">Restaurants</a>
        <a href="#" class="nav-pantry-page" v-on:click="navigateTo('pantryPage')">Pantry</a>
      </nav>
    </div>
    <router-view/>
  </div>
</template>

<script>
import Codenames from './Codenames'
import CurrentDocuments from './CurrentDocuments'
import HobbyTracker from './HobbyTracker'
import RecipesPage from './RecipesPage'
import RestaurantsPage from './RestaurantsPage'
import PantryPage from './PantryPage'
import { mapMutations } from 'vuex'

export default {
  name: 'Main',
  data () {
    return {
      loginUsername: '',
      navigationClass: ''
    }
  },
  created () {
    this.setUsername(this.$cookies.get('username'))
  },
  components: {
    CurrentDocuments, Codenames, HobbyTracker, RecipesPage, RestaurantsPage, PantryPage
  },
  methods: {
    ...mapMutations(['setUsername']),
    saveUsername () {
      this.setUsername(this.loginUsername)
      this.$cookies.set('username', this.loginUsername, '1y')
    },
    navigateTo (path) {
      switch (path) {
        case 'currentDocuments':
          this.navigationClass = 'nav-current-documents'
          break
        case 'hobbyTracker':
          this.navigationClass = 'nav-hobby-tracker'
          break
        case 'codenames':
          this.navigationClass = 'nav-codenames'
          break
        case 'recipesPage':
          this.navigationClass = 'nav-recipes-page'
          break
        case 'restaurantsPage':
          this.navigationClass = 'nav-restaurants-page'
          break
        case 'pantryPage':
          this.navigationClass = 'nav-pantry-page'
      }
      this.$router.push({ name: path })
    }
  }
}
</script>
