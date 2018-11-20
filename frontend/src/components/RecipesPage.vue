<template>
  <div class="recipes-page">
    <RecipeRestaurantEntity
      :backLinks="backLinks"
      :title="title"
      :hasInfo="hasInfo"
      :hasInfoImage="hasInfoImage"
      :infoImageName="infoImageName"
      :infoDicts="infoDicts"
      :hasChildren="hasChildren"
      :childTableHeaders="childTableHeaders"
      :childTableValues="childTableValues" />
  </div>
</template>
<style>
  @import "../assets/style/recipes-page.css"
</style>
<script>
import RecipeRestaurantEntity from './shared/RecipeRestaurantEntity'
import { getFullBackendUrlForPath } from '../common/utils'
import axios from 'axios'

const ADD_COOKBOOK_URL = getFullBackendUrlForPath('/add/cookbook')
const ADD_RECIPE_URL = getFullBackendUrlForPath('/add/recipe')
const ADD_RECIPE_MEAL_URL = getFullBackendUrlForPath('/add/recipe_meal')

export default {
  name: 'RecipesPage',
  data () {
    return {
      backLinks: [{name: 'cookbooks', url: '/a'}, {name: 'joy of cooking', url: '/b'}],
      title: 'Cookbooks',
      hasInfo: true,
      hasInfoImage: true,
      infoImageName: '/asdf',
      infoDicts: [{name: 'Name', value: 'Joy of Cooking'}, {name: 'Category', value: 'American'}],
      hasChildren: true,
      childTableHeaders: ['Name', 'Rating', 'Date'],
      childTableValues: [
        {id: 0, url: '/123', values: ['1', '2', '3', '4']},
        {id: 1, url: '/1234', values: ['21', '22', '23', '24']},
        {id: 2, url: '/1235', values: ['31', '32', '33', '34']},
        {id: 3, url: '/1236', values: ['41', '42', '43', '44']}]
    }
  },
  components: {
    RecipeRestaurantEntity
  },
  methods: {
    addCookbook (name, notes) {
      axios.post(ADD_COOKBOOK_URL, {name: name, notes: notes})
    },
    addRecipe (cookbookId, name, priority, category, notes) {
      axios.post(
        ADD_RECIPE_URL,
        {cookbook_id: cookbookId, name: 'name', priority: priority, category: category, notes: notes})
    },
    addRecipeMeal (recipeId, date, user1Rating, user2Rating, user1Comments, user2Comments) {
      axios.post(
        ADD_RECIPE_MEAL_URL,
        {
          recipe_id: recipeId,
          date: date,
          user_1_rating: user1Rating,
          user_2_rating: user2Rating,
          user_1_comments: user1Comments,
          user_2_comments: user2Comments
        })
    }
  }
}
</script>
