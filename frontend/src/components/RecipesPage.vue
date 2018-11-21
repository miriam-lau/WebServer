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
      :childTableValues="childTableValues"
      :handleModalSave="handleModalSave"
      :modalFormLines="modalFormLines"
      :modalTitle="modalTitle"
      :entityType="entityType"
      :entityId="entityId" />
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
const EDIT_ENTITY_URL_PREFIX = getFullBackendUrlForPath('/edit/')

export default {
  name: 'RecipesPage',
  data () {
    return {
      recipesPageData: {},
      backLinks: [],
      /** The type of entity currently being displayed. */
      entityType: '',
      /** The id of the entity currently being displayed. */
      entityId: 0,
      title: '',
      hasInfo: false,
      /** An array of objects with properties 'name', and 'value' to be displayed in the info section. */
      infoDicts: [],
      /** An array of image urls to be displayed in the info section. */
      infoImages: [],
      hasChildren: false,
      /** See RecipeRestaurantEntity for a description. */
      childTableHeaders: [],
      /** See RecipeRestaurantEntity for a description. */
      childTableValues: [],
      /** See FormModal for a description. */
      modalFormLines: [],
      modalTitle: ''
    }
  },
  components: {
    RecipeRestaurantEntity
  },
  created () {
    this.getRecipesPageDataAndRender()
  },
  methods: {
    handleModalSave (formSaveResponse) {
      formSaveResponse['id'] = this.entityId
      let editUrl = EDIT_ENTITY_URL_PREFIX + this.entityType
      axios.post(editUrl, formSaveResponse).then(response => {
        let newEntity = response.data
        let id = newEntity['id']
        let currentEntity = this.recipesPageData[this.convertEntityTypeToMapName(this.entityType)][id]
        for (let prop in newEntity) {
          if (prop === 'id') {
            continue
          }
          currentEntity[prop] = newEntity[prop]
        }
        this.showEntity(this.entityType, id)
      })
    },
    convertEntityTypeToMapName (entityType) {
      switch (entityType) {
        case 'cookbook':
          return 'cookbooks'
        case 'recipe':
          return 'recipes'
        case 'recipe_meal':
          return 'recipe_meals'
      }
    },
    showEntity (entityType, id) {
      switch (entityType) {
        case 'cookbook':
          this.showCookbook(id)
          return
        case 'recipe':
          this.showRecipe(id)
          return
        case 'recipe_meal':
          this.showRecipeMeal(id)
      }
    },
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
      this.entityType = 'cookbook'
      this.entityId = id
      this.backLinks =
          [{id: 'cookbooks', name: 'Cookbooks', handleClick: this.showCookbooks.bind(this)}]
      this.title = cookbook['name']
      this.hasInfo = true
      this.infoImages = []
      // TODO: Populate this with more info.
      this.infoDicts = [
        {id: 'cookbook-num-recipes-made-' + id, name: 'Num Recipes Made', value: this.getNumRecipesMadeFromCookbook(cookbook)},
        {id: 'cookbook-success-rate-' + id, name: 'Success Rate', value: this.getSuccessRatePercentageForCookbook(cookbook).toFixed(0) + '%'},
        {id: 'cookbook-num-recipes-we-want-to-make-' + id, name: 'Num Recipes We Want To Make', value: this.getNumRecipesWeWantToMakeForCookbook(cookbook)},
        {id: 'cookbook-notes-' + id, name: 'Notes', value: cookbook['notes']}
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
      this.modalTitle = 'Editing ' + this.title
      this.modalFormLines = [
        {
          id: 'cookbook-modal-name-' + cookbook['id'],
          name: 'name',
          displayName: 'Name:',
          value: cookbook['name']
        },
        {
          id: 'cookbook-modal-notes-' + cookbook['id'],
          name: 'notes',
          displayName: 'Notes:',
          value: cookbook['notes']
        }
      ]
    },
    showRecipe (id) {
      let recipe = this.recipesPageData['recipes'][id]
      let cookbook = this.recipesPageData['cookbooks'][recipe['cookbook_id']]
      this.entityType = 'recipe'
      this.entityId = id
      this.backLinks =
          [
            {id: 'cookbooks', name: 'Cookbooks', handleClick: this.showCookbooks.bind(this)},
            {
              id: 'cookbook-' + cookbook['id'],
              name: cookbook['name'],
              handleClick: this.showCookbook.bind(this, cookbook['id'])
            }
          ]
      this.title = cookbook['name'] + ': ' + recipe['name']
      this.hasInfo = true
      this.infoImages = []
      // TODO: Populate this with more info.
      this.infoDicts = [
        {id: 'recipe-best-rating-' + id, name: 'Best Rating', value: this.getBestRatingForRecipe(recipe).toFixed(1)},
        {id: 'recipe-latest-rating-' + id, name: 'Latest Rating', value: this.getLatestRatingForRecipe(recipe).toFixed(1)},
        {id: 'recipe-num-times-made-' + id, name: 'Num Times Made', value: this.getNumTimesRecipeMade(recipe)},
        {id: 'recipe-category-' + id, name: 'Category', value: recipe['category']},
        {id: 'recipe-priority-' + id, name: 'Priority', value: recipe['priority']},
        {id: 'recipe-notes-' + id, name: 'Notes', value: recipe['notes']}
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
      this.modalTitle = 'Editing ' + this.title
      this.modalFormLines = [
        {
          id: 'recipe-modal-name-' + recipe['id'],
          name: 'name',
          displayName: 'Name:',
          value: recipe['name']
        },
        {
          id: 'recipe-modal-category-' + recipe['id'],
          name: 'category',
          displayName: 'Category:',
          value: recipe['category']
        },
        {
          id: 'recipe-modal-priority-' + recipe['id'],
          name: 'priority',
          displayName: 'Priority:',
          value: recipe['priority']
        },
        {
          id: 'recipe-modal-notes-' + recipe['id'],
          name: 'notes',
          displayName: 'Notes:',
          value: recipe['notes']
        }
      ]
    },
    showRecipeMeal (id) {
      let recipeMeal = this.recipesPageData['recipe_meals'][id]
      let recipe = this.recipesPageData['recipes'][recipeMeal['recipe_id']]
      let cookbook = this.recipesPageData['cookbooks'][recipe['cookbook_id']]
      this.entityType = 'recipe_meal'
      this.entityId = id
      this.backLinks =
          [
            {id: 'cookbooks', name: 'Cookbooks', handleClick: this.showCookbooks.bind(this)},
            {
              id: 'cookbook-' + cookbook['id'],
              name: cookbook['name'],
              handleClick: this.showCookbook.bind(this, cookbook['id'])
            },
            {
              id: 'recipe-' + recipe['id'],
              name: recipe['name'],
              handleClick: this.showRecipe.bind(this, recipe['id'])
            }
          ]
      this.title = 'Meal for ' + cookbook['name'] + ': ' + recipe['name']
      this.hasInfo = true
      this.infoImages = []
      this.infoDicts = [
        {id: 'recipemeal-date-' + id, name: 'Date', value: getDisplayDate(recipeMeal['date'])},
        {id: 'recipemeal-miriam-rating-' + id, name: 'Miriam\'s Rating', value: recipeMeal['user_1_rating'].toFixed(1)},
        {id: 'recipemeal-james-rating-' + id, name: 'James\'s Rating', value: recipeMeal['user_2_rating'].toFixed(1)},
        {id: 'recipemeal-miriam-comments' + id, name: 'Miriam\'s Comments', value: recipeMeal['user_1_comments']},
        {id: 'recipemeal-james-comments' + id, name: 'James\' Comments', value: recipeMeal['user_2_comments']}
      ]
      this.hasChildren = false
      this.childTableHeaders = []
      this.childTableValues = []
      this.modalTitle = 'Editing ' + this.title
      this.modalFormLines = [
        {
          id: 'recipemeal-modal-date-' + recipeMeal['id'],
          name: 'date',
          displayName: 'Date:',
          value: recipeMeal['date']
        },
        {
          id: 'recipemeal-modal-miriam-rating-' + recipeMeal['id'],
          name: 'user_1_rating',
          displayName: 'Miriam\'s Rating:',
          value: recipeMeal['user_1_rating']
        },
        {
          id: 'recipemeal-modal-james-rating-' + recipeMeal['id'],
          name: 'user_2_rating',
          displayName: 'James\' Rating:',
          value: recipeMeal['user_2_rating']
        },
        {
          id: 'recipemeal-modal-miriam-comments-' + recipeMeal['id'],
          name: 'user_1_comments',
          displayName: 'Miriam\'s Comments:',
          value: recipeMeal['user_1_comments']
        },
        {
          id: 'recipemeal-modal-james-comments-' + recipeMeal['id'],
          name: 'user_2_comments',
          displayName: 'James\' Comments:',
          value: recipeMeal['user_2_comments']
        }
      ]
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
