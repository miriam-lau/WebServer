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

      :showEditModal="showEditModal"
      :showDeleteModal="showDeleteModal"
      :showAddModal="showAddModal"
      :formModal_show="formModal_show"
      :formModal_close="formModal_close"
      :formModal_title="formModal_title"
      :formModal_formLines="formModal_formLines"
      :formModal_errorText="formModal_errorText"
      :formModal_callback="formModal_callback"
      :formModal_passThroughProps="formModal_passThroughProps"
      :formModal_buttonText="formModal_buttonText"
      :formModal_shouldShowError="formModal_shouldShowError"

      :butterBar_message="butterBar_message"
      :butterBar_css="butterBar_css"
    />
  </div>
</template>
<script>
import { setButterBarMessage, ButterBarType } from '../common/butterbar_component'
import { showModal, createFormModalEntry, generateAxiosModalCallback } from '../common/form_modal_component'

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
      infoImages: [],
      infoDicts: [],
      hasChildren: false,
      childTableHeaders: [],
      childTableValues: [],

      formModal_show: false,
      formModal_title: '',
      formModal_formLines: [],
      formModal_errorText: '',
      formModal_callback: Function,
      formModal_passThroughProps: {},
      formModal_buttonText: '',
      formModal_shouldShowError: false,

      butterBar_message: '',
      butterBar_css: ''
    }
  },
  components: {
    RecipeRestaurantEntity
  },
  props: {
    cookbookIdParam: String,
    recipeIdParam: String,
    recipeMealIdParam: String
  },
  watch: {
    cookbookIdParam: function (oldValue, newValue) {
      this.renderPageFromProps()
    },
    recipeIdParam: function (oldValue, newValue) {
      this.renderPageFromProps()
    },
    recipeMealIdParam: function (oldValue, newValue) {
      this.renderPageFromProps()
    }
  },
  created () {
    this.getRecipesPageDataAndRender()
  },
  methods: {
    formModal_close () {
      this.formModal_show = false
    },
    showEditModal () {
      let modalFormLines = []
      switch (this.entity['entity_type']) {
        case 'cookbook':
          let cookbook = this.entity
          modalFormLines = [
            createFormModalEntry('cookbook-modal-name-' + cookbook['id'], 'name', 'Name:', cookbook['name']),
            createFormModalEntry('cookbook-modal-notes-' + cookbook['id'], 'notes', 'Notes:', cookbook['notes'])
          ]
          break
        case 'recipe':
          let recipe = this.entity
          modalFormLines = [
            createFormModalEntry('recipe-modal-name-' + recipe['id'], 'name', 'Name:', recipe['name']),
            createFormModalEntry(
              'recipe-modal-category-' + recipe['id'], 'category', 'Category:', recipe['category']),
            createFormModalEntry(
              'recipe-modal-priority-' + recipe['id'], 'priority', 'Priority:', recipe['priority']),
            createFormModalEntry('recipe-modal-notes-' + recipe['id'], 'notes', 'Notes:', recipe['notes'])
          ]
          break
        case 'recipe_meal':
          let recipeMeal = this.entity
          modalFormLines = [
            createFormModalEntry('recipemeal-modal-date-' + recipeMeal['id'], 'date', 'Date:', recipeMeal['date']),
            createFormModalEntry(
              'recipemeal-modal-miriam-rating-' + recipeMeal['id'], 'user_1_rating', 'Miriam\'s Rating:',
              recipeMeal['user_1_rating']),
            createFormModalEntry(
              'recipemeal-modal-james-rating-' + recipeMeal['id'], 'user_2_rating', 'James\' Rating:',
              recipeMeal['user_2_rating']),
            createFormModalEntry(
              'recipemeal-modal-miriam-comments-' + recipeMeal['id'], 'user_1_comments', 'Miriam\'s Comments:',
              recipeMeal['user_1_comments']),
            createFormModalEntry(
              'recipemeal-modal-james-comments-' + recipeMeal['id'], 'user_2_comments', 'James\' Comments:',
              recipeMeal['user_2_comments'])
          ]
      }
      let editUrl = EDIT_ENTITY_URL_PREFIX + this.entity['entity_type']
      showModal(
        this,
        'Editing ' + this.title,
        modalFormLines,
        this.entity,
        generateAxiosModalCallback(this, editUrl, this.editEntity),
        'Save',
        'Error editing ' + this.title)
    },
    showAddModal () {
      let modalTitle = ''
      let modalFormLines = []
      switch (this.entity['entity_type']) {
        case 'cookbooks':
          modalTitle = 'Adding cookbook'
          modalFormLines = [
            createFormModalEntry('add-cookbook-modal-name', 'name', 'Name:', ''),
            createFormModalEntry('add-cookbook-modal-notes', 'notes', 'Notes:', '')
          ]
          break
        case 'cookbook':
          modalTitle = 'Adding recipe'
          modalFormLines = [
            createFormModalEntry('add-recipe-modal-name', 'name', 'Name:', ''),
            createFormModalEntry('add-recipe-modal-category', 'category', 'Category:', ''),
            createFormModalEntry('add-recipe-modal-priority', 'priority', 'Priority:', ''),
            createFormModalEntry('add-recipe-modal-notes', 'notes', 'Notes:', '')
          ]
          break
        case 'recipe':
          modalTitle = 'Adding recipe meal'
          modalFormLines = [
            createFormModalEntry('add-recipemeal-modal-date', 'date', 'Date:', ''),
            createFormModalEntry('add-recipemeal-modal-miriam-rating', 'user_1_rating', 'Miriam\'s Rating:', ''),
            createFormModalEntry('add-recipemeal-modal-james-rating', 'user_2_rating', 'James\' Rating:', ''),
            createFormModalEntry('add-recipemeal-modal-miriam-comments', 'user_1_comments', 'Miriam\'s Comments:', ''),
            createFormModalEntry('add-recipemeal-modal-james-comments', 'user_2_comments', 'James\' Comments:', '')
          ]
          break
      }
      let addUrl = ADD_ENTITY_URL_PREFIX + this.getChildEntityTypeFor(this.entity)
      showModal(
        this,
        modalTitle,
        modalFormLines,
        { parent_id: this.entity['id'], entity_type: this.getChildEntityTypeFor(this.entity) },
        generateAxiosModalCallback(this, addUrl, this.addEntity),
        'Add',
        'Error adding item')
    },
    showDeleteModal () {
      this.deleteModalTitle = 'Deleting ' + this.title
      let deleteUrl = DELETE_ENTITY_URL_PREFIX + this.entity['entity_type']
      showModal(
        this,
        'Deleting ' + this.title,
        [],
        this.entity,
        generateAxiosModalCallback(this, deleteUrl, this.deleteEntity),
        'Delete',
        'Error deleting ' + this.title)
    },
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
    deleteEntity (response) {
      let entity = response['data']
      let entityType = entity['entity_type']
      let entityId = entity['id']
      let title = entity['entity_type'] === 'recipe_meal' ? 'Meal' : entity['name']
      let parent = this.getParentEntityFor(entity)
      parent['children'].splice(parent['children'].indexOf(entityId), 1)
      delete this.recipesPageData[entityType][entityId]
      this.showEntity(parent)
      setButterBarMessage(this, 'Deleted ' + title, ButterBarType.INFO)
    },
    editEntity (response) {
      let newEntity = response['data']
      let entityId = newEntity['id']
      let entityType = newEntity['entity_type']
      let title = newEntity['entity_type'] === 'recipe_meal' ? 'Meal' : newEntity['name']
      for (let prop in newEntity) {
        this.recipesPageData[entityType][entityId][prop] = newEntity[prop]
      }
      this.showEntity(this.entity)
      setButterBarMessage(this, 'Saved ' + title, ButterBarType.INFO)
    },
    addEntity (response) {
      let newEntity = response.data
      let title = newEntity['entity_type'] === 'recipe_meal' ? 'Meal' : newEntity['name']
      this.recipesPageData[newEntity['entity_type']][newEntity['id']] = newEntity
      this.entity['children'].push(newEntity['id'])
      this.showEntity(this.entity)
      setButterBarMessage(this, 'Added ' + title, ButterBarType.INFO)
    },
    getNumRecipesMadeFromCookbook (cookbook) {
      return cookbook['children'].reduce((acc, recipeId) => {
        let recipe = this.recipesPageData['recipe'][recipeId]
        if (this.getNumTimesRecipeMade(recipe) > 0) {
          return acc + 1
        }
        return acc
      }, 0)
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
        let handleClick = this.navigateTo.bind(this, 'recipesPage', { cookbook: '' + cookbook['id'] })
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
    navigateTo (name, queryParams) {
      this.$router.push({ name: name, query: queryParams })
    },
    showCookbook (cookbook) {
      let id = cookbook['id']
      this.entity = cookbook
      this.backLinks =
          [{id: 'cookbooks', name: 'Cookbooks', handleClick: this.navigateTo.bind(this, 'recipesPage', {})}]
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
        let handleClick = this.navigateTo.bind(this, 'recipesPage', { recipe: '' + recipeId })
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
    showRecipe (recipe) {
      let id = recipe['id']
      let cookbook = this.recipesPageData['cookbook'][recipe['parent_id']]
      this.entity = recipe
      this.backLinks =
          [
            { id: 'cookbooks', name: 'Cookbooks', handleClick: this.navigateTo.bind(this, 'recipesPage', {}) },
            {
              id: 'cookbook-' + cookbook['id'],
              name: cookbook['name'],
              handleClick: this.navigateTo.bind(this, 'recipesPage', { cookbook: '' + cookbook['id'] })
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
        let handleClick = this.navigateTo.bind(this, 'recipesPage', { 'recipe-meal': '' + recipeMeal['id'] })
        return {
          id: recipeMealId,
          handleClick: handleClick,
          values: [getDisplayDate(recipeMeal['date']), this.getOverallRatingForRecipeMeal(recipeMeal).toFixed(1),
            recipeMeal['user_1_rating'].toFixed(1), recipeMeal['user_1_comments'],
            recipeMeal['user_2_rating'].toFixed(1), recipeMeal['user_2_comments']]
        }
      })
    },
    showRecipeMeal (recipeMeal) {
      let id = recipeMeal['id']
      let recipe = this.recipesPageData['recipe'][recipeMeal['parent_id']]
      let cookbook = this.recipesPageData['cookbook'][recipe['parent_id']]
      this.entity = recipeMeal
      this.backLinks =
          [
            { id: 'cookbooks', name: 'Cookbooks', handleClick: this.navigateTo.bind(this, 'recipesPage', {}) },
            {
              id: 'cookbook-' + cookbook['id'],
              name: cookbook['name'],
              handleClick: this.navigateTo.bind(this, 'recipesPage', { cookbook: '' + cookbook['id'] })
            },
            {
              id: 'recipe-' + recipe['id'],
              name: recipe['name'],
              handleClick: this.navigateTo.bind(this, 'recipesPage', { recipe: '' + recipe['id'] })
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
    },
    getRecipesPageDataAndRender () {
      axios.post(GET_RECIPES_PAGE_DATA_URL).then(
        response => {
          this.recipesPageData = response.data
          this.renderPageFromProps()
        }
      )
    },
    renderPageFromProps () {
      if (!this.cookbookIdParam && !this.recipeIdParam && !this.recipeMealIdParam) {
        this.showCookbooks()
        return
      }

      let entity = null
      if (this.cookbookIdParam) {
        entity = this.recipesPageData['cookbook'][parseInt(this.cookbookIdParam)]
      } else if (this.recipeIdParam) {
        entity = this.recipesPageData['recipe'][parseInt(this.recipeIdParam)]
      } else if (this.recipeMealIdParam) {
        entity = this.recipesPageData['recipe_meal'][parseInt(this.recipeMealIdParam)]
      }
      if (entity) {
        this.showEntity(entity)
        return
      }
      setButterBarMessage(this, 'Unable to perform navigation.', ButterBarType.ERROR)
    }
  }
}
</script>
