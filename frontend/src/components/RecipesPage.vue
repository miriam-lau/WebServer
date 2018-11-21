<template>
  <div class="recipes-page">
    <RecipeRestaurantEntity
      :backLinks="backLinks"
      :title="title"
      :hasInfo="hasInfo"
      :infoDicts="infoDicts"
      :infoImages="infoImages"
      :hasChildren="hasChildren"
      :childTableHeaders="childTableHeaders"
      :childTableValues="childTableValues" />
  </div>
</template>
<script>
import RecipeRestaurantEntity from './shared/RecipeRestaurantEntity'
import { getFullBackendUrlForPath, isEqual, getDisplayDate } from '../common/utils'
import axios from 'axios'

const ADD_COOKBOOK_URL = getFullBackendUrlForPath('/add/cookbook')
const ADD_RECIPE_URL = getFullBackendUrlForPath('/add/recipe')
const ADD_RECIPE_MEAL_URL = getFullBackendUrlForPath('/add/recipe_meal')
const GET_RECIPES_PAGE_DATA_URL = getFullBackendUrlForPath('/get_recipes_page_data')

export default {
  name: 'RecipesPage',
  data () {
    return {
      recipesPageData: {},
      backLinks: [],
      title: '',
      hasInfo: false,
      infoDicts: [],
      infoImages: [],
      hasChildren: false,
      childTableHeaders: [],
      childTableValues: []
    }
  },
  components: {
    RecipeRestaurantEntity
  },
  created () {
    this.getRecipesPageDataAndRender()
  },
  methods: {
    getNumRecipesMadeFromCookbook (cookbook) {
      return cookbook['recipes'].length
    },
    getNumRecipesWeWantToMakeForCookbook (cookbook) {
      return cookbook['recipes'].reduce((acc, recipeId) => {
        let recipe = this.recipesPageData['recipes'][recipeId]
        if (recipe['priority'] > 0) {
          return acc + 1
        }
        return acc
      }, 0)
    },
    getSuccessRatePercentageForCookbook (cookbook) {
      let numRecipesMade = this.getNumRecipesMadeFromCookbook(cookbook)
      if (numRecipesMade === 0) {
        return 0
      }
      let numSuccesses = cookbook['recipes'].map(recipeId => {
        let recipe = this.recipesPageData['recipes'][recipeId]
        return this.getBestRatingForRecipe(recipe)
      }).reduce((acc, rating) => {
        if (isEqual(rating, 7) || (rating > 7)) {
          return acc + 1
        }
        return acc
      }, 0)
      return (100.0 * numSuccesses / numRecipesMade)
    },
    getBestRatingForRecipe (recipe) {
      if (recipe['recipe_meals'].length === 0) {
        return 0
      }
      return recipe['recipe_meals'].map(recipeMealId => {
        let recipeMeal = this.recipesPageData['recipe_meals'][recipeMealId]
        return this.getOverallRatingForRecipeMeal(recipeMeal)
      }).reduce((max, x) => x > max ? x : max, 0)
    },
    getLatestRatingForRecipe (recipe) {
      if (recipe['recipe_meals'].length === 0) {
        return 0
      }
      let recipeMeals = recipe['recipe_meals'].map(recipeMealId => this.recipesPageData['recipe_meals'][recipeMealId])
      return this.getOverallRatingForRecipeMeal(
        recipeMeals.reduce((currentRecipeMeal, nextRecipeMeal) => {
          return Date.parse(currentRecipeMeal['date']) > Date.parse(nextRecipeMeal['date'])
            ? currentRecipeMeal : nextRecipeMeal
        }, []))
    },
    getNumTimesRecipeMade (recipe) {
      return recipe['recipe_meals'].length
    },
    getOverallRatingForRecipeMeal (recipeMeal) {
      let rating1 = recipeMeal['user_1_rating']
      let rating2 = recipeMeal['user_2_rating']
      if (isEqual(rating1, 0) && isEqual(rating2, 0)) {
        return 0
      } else if (isEqual(rating1, 0)) {
        return rating2
      } else if (isEqual(rating2, 0)) {
        return rating1
      }
      return (rating1 + rating2) / 2
    },
    showCookbooks () {
      this.backLinks = []
      this.title = 'Cookbooks'
      this.hasInfo = false
      this.infoImages = []
      this.infoDicts = []
      this.hasChildren = true
      this.childTableHeaders = ['Name', 'Num Recipes Made', 'Success Rate', 'Num Recipes We Want To Make']
      this.childTableValues = this.recipesPageData['cookbooks_list'].map(cookbookId => {
        let cookbook = this.recipesPageData['cookbooks'][cookbookId]
        let handleClick = this.showCookbook.bind(this, cookbookId)
        let numRecipesMade = this.getNumRecipesMadeFromCookbook(cookbook)
        let numRecipesWeWantToMake = this.getNumRecipesWeWantToMakeForCookbook(cookbook)
        let successRate = this.getSuccessRatePercentageForCookbook(cookbook).toFixed(0) + '%'
        return {
          id: cookbookId,
          handleClick: handleClick,
          values: [cookbook['name'], numRecipesMade, successRate, numRecipesWeWantToMake]
        }
      })
    },
    showCookbook (id) {
      let cookbook = this.recipesPageData['cookbooks'][id]
      this.backLinks =
          [{name: 'Cookbooks', handleClick: this.showCookbooks.bind(this)}]
      this.title = cookbook['name']
      this.hasInfo = true
      this.infoImages = []
      // TODO: Populate this with more info.
      this.infoDicts = [
        {name: 'Num Recipes Made', value: this.getNumRecipesMadeFromCookbook(cookbook)},
        {name: 'Success Rate', value: this.getSuccessRatePercentageForCookbook(cookbook).toFixed(0) + '%'},
        {name: 'Num Recipes We Want To Make', value: this.getNumRecipesWeWantToMakeForCookbook(cookbook)},
        {name: 'Notes', value: cookbook['notes']}
      ]
      this.hasChildren = true
      this.childTableHeaders = ['Name', 'Num Times Made', 'Best Rating', 'Latest Rating', 'Priority', 'Category']
      this.childTableValues = cookbook['recipes'].map(recipeId => {
        let recipe = this.recipesPageData['recipes'][recipeId]
        let handleClick = this.showRecipe.bind(this, recipeId)
        return {
          id: recipeId,
          handleClick: handleClick,
          values: [
            recipe['name'],
            this.getNumTimesRecipeMade(recipe),
            this.getBestRatingForRecipe(recipe).toFixed(1),
            this.getLatestRatingForRecipe(recipe).toFixed(1),
            recipe['priority'],
            recipe['category']]
        }
      })
    },
    showRecipe (id) {
      let recipe = this.recipesPageData['recipes'][id]
      let cookbook = this.recipesPageData['cookbooks'][recipe['cookbook_id']]
      this.backLinks =
          [
            {name: 'Cookbooks', handleClick: this.showCookbooks.bind(this)},
            {name: cookbook['name'], handleClick: this.showCookbook.bind(this, cookbook['id'])}
          ]
      this.title = cookbook['name'] + ': ' + recipe['name']
      this.hasInfo = true
      this.infoImages = []
      // TODO: Populate this with more info.
      this.infoDicts = [
        {name: 'Best Rating', value: this.getBestRatingForRecipe(recipe).toFixed(1)},
        {name: 'Latest Rating', value: this.getLatestRatingForRecipe(recipe).toFixed(1)},
        {name: 'Num Times Made', value: this.getNumTimesRecipeMade(recipe)},
        {name: 'Category', value: recipe['category']},
        {name: 'Priority', value: recipe['priority']},
        {name: 'Notes', value: recipe['notes']}
      ]
      this.hasChildren = true
      this.childTableHeaders = ['Date', 'Overall Rating', 'Miriam\'s Rating', 'Miriam\'s Comments',
        'James\' Rating', 'James\' Comments']
      this.childTableValues = recipe['recipe_meals'].map(recipeMealId => {
        let recipeMeal = this.recipesPageData['recipe_meals'][recipeMealId]
        let handleClick = this.showRecipeMeal.bind(this, recipeMealId)
        return {
          id: recipeMealId,
          handleClick: handleClick,
          values: [getDisplayDate(recipeMeal['date']), this.getOverallRatingForRecipeMeal(recipeMeal).toFixed(1),
            recipeMeal['user_1_rating'].toFixed(1), recipeMeal['user_1_comments'],
            recipeMeal['user_2_rating'].toFixed(1), recipeMeal['user_2_comments']]
        }
      })
    },
    showRecipeMeal (id) {
      let recipeMeal = this.recipesPageData['recipe_meals'][id]
      let recipe = this.recipesPageData['recipes'][recipeMeal['recipe_id']]
      let cookbook = this.recipesPageData['cookbooks'][recipe['cookbook_id']]
      this.backLinks =
          [
            {name: 'Cookbooks', handleClick: this.showCookbooks.bind(this)},
            {name: cookbook['name'], handleClick: this.showCookbook.bind(this, cookbook['id'])},
            {name: recipe['name'], handleClick: this.showRecipe.bind(this, recipe['id'])}
          ]
      this.title = 'Meal for ' + cookbook['name'] + ': ' + recipe['name']
      this.hasInfo = true
      this.infoImages = []
      this.infoDicts = [
        {name: 'Date', value: getDisplayDate(recipeMeal['date'])},
        {name: 'Miriam\'s Rating', value: recipeMeal['user_1_rating'].toFixed(1)},
        {name: 'James\'s Rating', value: recipeMeal['user_2_rating'].toFixed(1)},
        {name: 'Miriam\'s Comments', value: recipeMeal['user_1_comments']},
        {name: 'James\' Comments', value: recipeMeal['user_2_comments']}
      ]
      this.hasChildren = false
      this.childTableHeaders = []
      this.childTableValues = []
    },
    getRecipesPageDataAndRender () {
      axios.post(GET_RECIPES_PAGE_DATA_URL).then(
        response => {
          this.recipesPageData = response.data
          this.showCookbooks()
        }
      )
    },
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
