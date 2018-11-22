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
      :handleDeleteModalSave="handleDeleteModalSave"
      :handleEditModalSave="handleEditModalSave"
      :editModalFormLines="editModalFormLines"
      :editModalTitle="editModalTitle"
      :handleAddModalSave="handleAddModalSave"
      :addModalFormLines="addModalFormLines"
      :addModalTitle="addModalTitle"
      :deleteModalTitle="deleteModalTitle"
      :entityType="entityType"
      :entityId="entityId" />
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
      recipesPageData: {},
      backLinks: [],
      /**
       * The type of entity currently being displayed. Possible values are 'cookbooks', 'cookbook', 'recipe',
       * 'recipe_meal'.
       */
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
      editModalFormLines: [],
      editModalTitle: '',
      /** See FormModal for a description. */
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
    getParentTypeOfCurrentEntity () {
      switch (this.entityType) {
        case 'cookbooks':
          return null
        case 'cookbook':
          return 'cookbooks'
        case 'recipe':
          return 'cookbook'
        case 'recipe_meal':
          return 'recipe'
      }
    },
    getChildTypeOfCurrentEntity () {
      switch (this.entityType) {
        case 'cookbooks':
          return 'cookbook'
        case 'cookbook':
          return 'recipe'
        case 'recipe':
          return 'recipe_meal'
        case 'recipe_meal':
          return null
      }
    },
    getCurrentEntity () {
      switch (this.entityType) {
        case 'cookbooks':
          return null
        case 'cookbook':
          return this.recipesPageData['cookbooks'][this.entityId]
        case 'recipe':
          return this.recipesPageData['recipes'][this.entityId]
        case 'recipe_meal':
          return this.recipesPageData['recipe_meals'][this.entityId]
      }
    },
    addChildArrayToEntity (entity, entityType) {
      switch (entityType) {
        case 'cookbook':
          entity['recipes'] = []
          break
        case 'recipe':
          entity['recipe_meals'] = []
      }
      return entity
    },
    getChildArrayForCurrentEntity () {
      let currentEntity = this.getCurrentEntity()
      switch (this.entityType) {
        case 'cookbooks':
          return this.recipesPageData['cookbooks_list']
        case 'cookbook':
          return currentEntity['recipes']
        case 'recipe':
          return currentEntity['recipe_meals']
        case 'recipe_meal':
          return null
      }
    },
    handleDeleteModalSave (unused) {
      let deleteUrl = DELETE_ENTITY_URL_PREFIX + this.entityType
      axios.post(deleteUrl, {id: this.entityId}).then(response => {
        let parentArray = this.getParentArrayFromEntity(this.entityType, this.entityId)
        let parentId = this.getParentIdForEntity(this.entityType, this.entityId)
        parentArray.splice(parentArray.indexOf(this.entityId), 1)
        delete this.recipesPageData[this.convertEntityTypeToMapName(this.entityType)][this.entityId]
        switch (this.entityType) {
          case 'cookbook':
            this.showCookbooks()
            return
          case 'recipe':
            this.showCookbook(parentId)
            return
          case 'recipe_meal':
            this.showRecipe(parentId)
        }
      })
    },
    handleEditModalSave (formSaveResponse) {
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
    handleAddModalSave (formSaveResponse) {
      switch (this.entityType) {
        case 'cookbook':
          formSaveResponse['cookbook_id'] = this.entityId
          break
        case 'recipe':
          formSaveResponse['recipe_id'] = this.entityId
      }
      let addUrl = ADD_ENTITY_URL_PREFIX + this.getChildTypeOfCurrentEntity()
      axios.post(addUrl, formSaveResponse).then(response => {
        let newEntity = response.data
        this.addChildArrayToEntity(newEntity, this.getChildTypeOfCurrentEntity())
        let id = newEntity['id']
        this.recipesPageData[this.convertEntityTypeToMapName(this.getChildTypeOfCurrentEntity())][id] = newEntity
        let childArrayForCurrentEntity = this.getChildArrayForCurrentEntity()
        if (childArrayForCurrentEntity) {
          childArrayForCurrentEntity.push(id)
        }
        this.showEntity(this.entityType, this.entityId)
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
    getParentArrayFromEntity (entityType, id) {
      switch (entityType) {
        case 'cookbook':
          return this.recipesPageData['cookbooks_list']
        case 'recipe':
          return this.recipesPageData['cookbooks'][this.recipesPageData['recipes'][id]['cookbook_id']]['recipes']
        case 'recipe_meal':
          return this.recipesPageData['recipes'][this.recipesPageData['recipe_meals'][id]['recipe_id']]['recipe_meals']
      }
    },
    getParentIdForEntity (entityType, id) {
      switch (entityType) {
        case 'recipe':
          return this.recipesPageData['recipes'][id]['cookbook_id']
        case 'recipe_meal':
          return this.recipesPageData['recipe_meals'][id]['recipe_id']
      }
    },
    showEntity (entityType, id) {
      switch (entityType) {
        case 'cookbooks':
          this.showCookbooks()
          return
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
      this.entityType = 'cookbooks'
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
      this.editModalTitle = 'Editing ' + this.title
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
