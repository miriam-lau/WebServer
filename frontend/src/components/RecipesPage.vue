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
      :addModalFormLines="addModalFormLines"
      :addModalTitle="addModalTitle"
      :handleAddModalSave="handleAddModalSave"
      :editModalFormLines="editModalFormLines"
      :editModalTitle="editModalTitle"
      :handleEditModalSave="handleEditModalSave"
      :deleteModalTitle="deleteModalTitle"
      :handleDeleteModalSave="handleDeleteModalSave" />
  </div>
</template>
<script>
import RecipeRestaurantEntity from './shared/RecipeRestaurantEntity'
import { getFullBackendUrlForPath, isEqual, getDisplayDate } from '../common/utils'
import axios from 'axios'

const GET_RECIPES_PAGE_DATA_URL = getFullBackendUrlForPath('/get_recipes_page_data')
const EDIT_ENTITY_URL_PREFIX = getFullBackendUrlForPath('/edit/')
const DELETE_ENTITY_URL_PREFIX = getFullBackendUrlForPath('/delete/')
const ADD_ENTITY_URL_PREFIX = getFullBackendUrlForPath('/add/')

export default {
  name: 'RecipesPage',
  data () {
    return {
      /**
       * This is the recipes page data that comes from the python backend. See recipes_page.py for a description.
       */
      recipesPageData: {},
      /**
       * The entity currently being displayed.
       */
      entity: {},
      /** See FormModal for a description of the following data. */
      backLinks: [],
      title: '',
      hasInfo: false,
      infoDicts: [],
      infoImages: [],
      hasChildren: false,
      childTableHeaders: [],
      childTableValues: [],
      editModalFormLines: [],
      editModalTitle: '',
      addModalFormLines: [],
      addModalTitle: '',
      deleteModalTitle: ''
    }
  },
  components: {
    RecipeRestaurantEntity
  },
  created () {
    this.getRecipesPageDataAndRender()
  },
  methods: {
    getParentEntityFor (entity) {
      let parentEntityType = this.getParentEntityTypeFor(entity)
      return this.recipesPageData[parentEntityType][entity['parent_id']]
    },
    getParentEntityTypeFor (entity) {
      switch (entity['entity_type']) {
        case 'cookbook':
          return 'cookbooks'
        case 'recipe':
          return 'cookbook'
        case 'recipe_meal':
          return 'recipe'
      }
      return null
    },
    getChildEntityTypeFor (entity) {
      switch (entity['entity_type']) {
        case 'cookbooks':
          return 'cookbook'
        case 'cookbook':
          return 'recipe'
        case 'recipe':
          return 'recipe_meal'
      }
      return null
    },
    showEntity (entity) {
      switch (entity['entity_type']) {
        case 'cookbooks':
          this.showCookbooks()
          return
        case 'cookbook':
          this.showCookbook(entity)
          return
        case 'recipe':
          this.showRecipe(entity)
          return
        case 'recipe_meal':
          this.showRecipeMeal(entity)
      }
    },
    handleDeleteModalSave (unused) {
      let entityType = this.entity['entity_type']
      let entityId = this.entity['id']
      let deleteUrl = DELETE_ENTITY_URL_PREFIX + entityType
      axios.post(deleteUrl, {id: entityId}).then(response => {
        let parent = this.getParentEntityFor(this.entity)
        parent['children'].splice(parent['children'].indexOf(entityId), 1)
        delete this.recipesPageData[entityType][entityId]
        this.showEntity(parent)
      })
    },
    handleEditModalSave (formSaveResponse) {
      let entityId = this.entity['id']
      formSaveResponse['id'] = entityId

      let editUrl = EDIT_ENTITY_URL_PREFIX + this.entity['entity_type']
      axios.post(editUrl, formSaveResponse).then(response => {
        let newEntity = response.data
        for (let prop in newEntity) {
          this.entity[prop] = newEntity[prop]
        }
        this.showEntity(this.entity)
      })
    },
    handleAddModalSave (formSaveResponse) {
      formSaveResponse['parent_id'] = this.entity['id']
      let addUrl = ADD_ENTITY_URL_PREFIX + this.getChildEntityTypeFor(this.entity)
      axios.post(addUrl, formSaveResponse).then(response => {
        let newEntity = response.data
        this.entity['children'].push(newEntity['id'])
        this.recipesPageData[newEntity['entity_type']][newEntity['id']] = newEntity
        this.showEntity(this.entity)
      })
    },
    getNumRecipesMadeFromCookbook (cookbook) {
      return cookbook['children'].length
    },
    getNumRecipesWeWantToMakeForCookbook (cookbook) {
      return cookbook['children'].reduce((acc, recipeId) => {
        let recipe = this.recipesPageData['recipe'][recipeId]
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
      let numSuccesses = cookbook['children'].map(recipeId => {
        let recipe = this.recipesPageData['recipe'][recipeId]
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
      if (recipe['children'].length === 0) {
        return 0
      }
      return recipe['children'].map(recipeMealId => {
        let recipeMeal = this.recipesPageData['recipe_meal'][recipeMealId]
        return this.getOverallRatingForRecipeMeal(recipeMeal)
      }).reduce((max, x) => x > max ? x : max, 0)
    },
    getLatestRatingForRecipe (recipe) {
      if (recipe['children'].length === 0) {
        return 0
      }
      let recipeMeals = recipe['children'].map(recipeMealId => this.recipesPageData['recipe_meal'][recipeMealId])
      return this.getOverallRatingForRecipeMeal(
        recipeMeals.reduce((currentRecipeMeal, nextRecipeMeal) => {
          return Date.parse(currentRecipeMeal['date']) > Date.parse(nextRecipeMeal['date'])
            ? currentRecipeMeal : nextRecipeMeal
        }, []))
    },
    getNumTimesRecipeMade (recipe) {
      return recipe['children'].length
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
      this.entity = this.recipesPageData['cookbooks'][0]
      this.hasInfo = false
      this.infoImages = []
      this.infoDicts = []
      this.hasChildren = true
      this.childTableHeaders = ['Name', 'Num Recipes Made', 'Success Rate', 'Num Recipes We Want To Make']
      this.childTableValues = this.entity['children'].map(cookbookId => {
        let cookbook = this.recipesPageData['cookbook'][cookbookId]
        let handleClick = this.showCookbook.bind(this, cookbook)
        let numRecipesMade = this.getNumRecipesMadeFromCookbook(cookbook)
        let numRecipesWeWantToMake = this.getNumRecipesWeWantToMakeForCookbook(cookbook)
        let successRate = this.getSuccessRatePercentageForCookbook(cookbook).toFixed(0) + '%'
        return {
          id: cookbookId,
          handleClick: handleClick,
          values: [cookbook['name'], numRecipesMade, successRate, numRecipesWeWantToMake]
        }
      })
      this.addModalTitle = 'Adding cookbook'
      this.addModalFormLines = [
        {
          id: 'add-cookbook-modal-name',
          name: 'name',
          displayName: 'Name:',
          value: ''
        },
        {
          id: 'add-cookbook-modal-notes',
          name: 'notes',
          displayName: 'Notes:',
          value: ''
        }
      ]
    },
    showCookbook (cookbook) {
      let id = cookbook['id']
      this.entity = cookbook
      this.backLinks =
          [{id: 'cookbooks', name: 'Cookbooks', handleClick: this.showCookbooks.bind(this)}]
      this.title = cookbook['name']
      this.hasInfo = true
      this.infoImages = []
      this.infoDicts = [
        {
          id: 'cookbook-num-recipes-made-' + id,
          name: 'Num Recipes Made',
          value: this.getNumRecipesMadeFromCookbook(cookbook)},
        {
          id: 'cookbook-success-rate-' + id,
          name: 'Success Rate',
          value: this.getSuccessRatePercentageForCookbook(cookbook).toFixed(0) + '%'
        },
        {
          id: 'cookbook-num-recipes-we-want-to-make-' + id,
          name: 'Num Recipes We Want To Make',
          value: this.getNumRecipesWeWantToMakeForCookbook(cookbook)
        },
        { id: 'cookbook-notes-' + id, name: 'Notes', value: cookbook['notes'] }
      ]
      this.hasChildren = true
      this.childTableHeaders = ['Name', 'Num Times Made', 'Best Rating', 'Latest Rating', 'Priority', 'Category']
      this.childTableValues = cookbook['children'].map(recipeId => {
        let recipe = this.recipesPageData['recipe'][recipeId]
        let handleClick = this.showRecipe.bind(this, recipe)
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
      this.editModalTitle = 'Editing ' + this.title
      this.deleteModalTitle = 'Deleting ' + this.title
      this.addModalTitle = 'Adding recipe'
      this.editModalFormLines = [
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
      this.addModalFormLines = [
        {
          id: 'add-recipe-modal-name',
          name: 'name',
          displayName: 'Name:',
          value: ''
        },
        {
          id: 'add-recipe-modal-category',
          name: 'category',
          displayName: 'Category:',
          value: ''
        },
        {
          id: 'add-recipe-modal-priority',
          name: 'priority',
          displayName: 'Priority:',
          value: ''
        },
        {
          id: 'add-recipe-modal-notes',
          name: 'notes',
          displayName: 'Notes:',
          value: ''
        }
      ]
    },
    showRecipe (recipe) {
      let id = recipe['id']
      let cookbook = this.recipesPageData['cookbook'][recipe['parent_id']]
      this.entity = recipe
      this.backLinks =
          [
            { id: 'cookbooks', name: 'Cookbooks', handleClick: this.showCookbooks.bind(this) },
            {
              id: 'cookbook-' + cookbook['id'],
              name: cookbook['name'],
              handleClick: this.showCookbook.bind(this, cookbook)
            }
          ]
      this.title = cookbook['name'] + ': ' + recipe['name']
      this.hasInfo = true
      this.infoImages = []
      this.infoDicts = [
        {
          id: 'recipe-best-rating-' + id,
          name: 'Best Rating',
          value: this.getBestRatingForRecipe(recipe).toFixed(1)
        },
        {
          id: 'recipe-latest-rating-' + id,
          name: 'Latest Rating',
          value: this.getLatestRatingForRecipe(recipe).toFixed(1)
        },
        { id: 'recipe-num-times-made-' + id, name: 'Num Times Made', value: this.getNumTimesRecipeMade(recipe) },
        { id: 'recipe-category-' + id, name: 'Category', value: recipe['category'] },
        { id: 'recipe-priority-' + id, name: 'Priority', value: recipe['priority'] },
        { id: 'recipe-notes-' + id, name: 'Notes', value: recipe['notes'] }
      ]
      this.hasChildren = true
      this.childTableHeaders = ['Date', 'Overall Rating', 'Miriam\'s Rating', 'Miriam\'s Comments',
        'James\' Rating', 'James\' Comments']
      this.childTableValues = recipe['children'].map(recipeMealId => {
        let recipeMeal = this.recipesPageData['recipe_meal'][recipeMealId]
        let handleClick = this.showRecipeMeal.bind(this, recipeMeal)
        return {
          id: recipeMealId,
          handleClick: handleClick,
          values: [getDisplayDate(recipeMeal['date']), this.getOverallRatingForRecipeMeal(recipeMeal).toFixed(1),
            recipeMeal['user_1_rating'].toFixed(1), recipeMeal['user_1_comments'],
            recipeMeal['user_2_rating'].toFixed(1), recipeMeal['user_2_comments']]
        }
      })
      this.editModalTitle = 'Editing ' + this.title
      this.addModalTitle = 'Adding recipe meal'
      this.deleteModalTitle = 'Deleting ' + this.title
      this.editModalFormLines = [
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
      this.addModalFormLines = [
        {
          id: 'add-recipemeal-modal-date',
          name: 'date',
          displayName: 'Date:',
          value: ''
        },
        {
          id: 'add-recipemeal-modal-miriam-rating',
          name: 'user_1_rating',
          displayName: 'Miriam\'s Rating:',
          value: ''
        },
        {
          id: 'add-recipemeal-modal-james-rating',
          name: 'user_2_rating',
          displayName: 'James\' Rating:',
          value: ''
        },
        {
          id: 'add-recipemeal-modal-miriam-comments',
          name: 'user_1_comments',
          displayName: 'Miriam\'s Comments:',
          value: ''
        },
        {
          id: 'add-recipemeal-modal-james-comments',
          name: 'user_2_comments',
          displayName: 'James\' Comments:',
          value: ''
        }
      ]
    },
    showRecipeMeal (recipeMeal) {
      let id = recipeMeal['id']
      let recipe = this.recipesPageData['recipe'][recipeMeal['parent_id']]
      let cookbook = this.recipesPageData['cookbook'][recipe['parent_id']]
      this.entity = recipeMeal
      this.backLinks =
          [
            { id: 'cookbooks', name: 'Cookbooks', handleClick: this.showCookbooks.bind(this) },
            {
              id: 'cookbook-' + cookbook['id'],
              name: cookbook['name'],
              handleClick: this.showCookbook.bind(this, cookbook)
            },
            {
              id: 'recipe-' + recipe['id'],
              name: recipe['name'],
              handleClick: this.showRecipe.bind(this, recipe)
            }
          ]
      this.title = 'Meal for ' + cookbook['name'] + ': ' + recipe['name']
      this.hasInfo = true
      this.infoImages = []
      this.infoDicts = [
        { id: 'recipemeal-date-' + id, name: 'Date', value: getDisplayDate(recipeMeal['date']) },
        {
          id: 'recipemeal-miriam-rating-' + id,
          name: 'Miriam\'s Rating',
          value: recipeMeal['user_1_rating'].toFixed(1)
        },
        { id: 'recipemeal-james-rating-' + id, name: 'James\'s Rating', value: recipeMeal['user_2_rating'].toFixed(1) },
        { id: 'recipemeal-miriam-comments' + id, name: 'Miriam\'s Comments', value: recipeMeal['user_1_comments'] },
        { id: 'recipemeal-james-comments' + id, name: 'James\' Comments', value: recipeMeal['user_2_comments'] }
      ]
      this.hasChildren = false
      this.childTableHeaders = []
      this.childTableValues = []
      this.editModalTitle = 'Editing ' + this.title
      this.deleteModalTitle = 'Deleting ' + this.title
      this.editModalTitle = 'Adding Recipe Meal'
      this.editModalFormLines = [
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
    }
  }
}
</script>
