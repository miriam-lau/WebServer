<template>
  <div class="restaurants-page">
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

const GET_RESTAURANTS_PAGE_DATA_URL = getFullBackendUrlForPath('/get_restaurants_page_data')
const EDIT_ENTITY_URL_PREFIX = getFullBackendUrlForPath('/edit/')
const DELETE_ENTITY_URL_PREFIX = getFullBackendUrlForPath('/delete/')
const ADD_ENTITY_URL_PREFIX = getFullBackendUrlForPath('/add/')

export default {
  name: 'RestaurantsPage',
  data () {
    return {
      /**
       * This is the restaurants page data that comes from the python backend. See restaurants_page.py for a description.
       */
      restaurantsPageData: {},
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
    cityIdParam: String,
    restaurantIdParam: String,
    dishIdParam: String,
    dishMealIdParam: String
  },
  watch: {
    cityIdParam: function (oldValue, newValue) {
      this.renderPageFromProps()
    },
    restaurantIdParam: function (oldValue, newValue) {
      this.renderPageFromProps()
    },
    dishIdParam: function (oldValue, newValue) {
      this.renderPageFromProps()
    },
    dishMealIdParam: function (oldValue, newValue) {
      this.renderPageFromProps()
    }
  },
  created () {
    this.getRestaurantsPageDataAndRender()
  },
  methods: {
    formModal_close () {
      this.formModal_show = false
    },
    showEditModal () {
      let modalFormLines = null
      switch (this.entity['entity_type']) {
        case 'city':
          let city = this.entity
          modalFormLines = [
            createFormModalEntry('city-modal-name-' + city['id'], 'name', 'Name:', city['name']),
            createFormModalEntry('city-modal-state-' + city['id'], 'state', 'State:', city['state']),
            createFormModalEntry('city-modal-country-' + city['id'], 'country', 'Country:', city['country']),
            createFormModalEntry('city-modal-notes-' + city['id'], 'notes', 'Notes:', city['notes'])
          ]
          break
        case 'restaurant':
          let restaurant = this.entity
          modalFormLines = [
            createFormModalEntry('restaurant-modal-name-' + restaurant['id'], 'name', 'Name:', restaurant['name']),
            createFormModalEntry(
              'restaurant-modal-address-' + restaurant['id'], 'address', 'Address:', restaurant['address']),
            createFormModalEntry(
              'restaurant-modal-category-' + restaurant['id'], 'category', 'Category:', restaurant['category']),
            createFormModalEntry('restaurant-modal-notes-' + restaurant['id'], 'notes', 'Notes:', restaurant['notes'])
          ]
          break
        case 'dish':
          let dish = this.entity
          modalFormLines = [
            createFormModalEntry('dish-modal-name-' + dish['id'], 'name', 'Name:', dish['name']),
            createFormModalEntry('dish-modal-category-' + dish['id'], 'category', 'Category:', dish['category']),
            createFormModalEntry('dish-modal-notes-' + dish['id'], 'notes', 'Notes:', dish['notes'])
          ]
          break
        case 'dish_meal':
          let dishMeal = this.entity
          modalFormLines = [
            createFormModalEntry('dishmeal-modal-date-' + dishMeal['id'], 'date', 'Date:', dishMeal['date']),
            createFormModalEntry(
              'dishmeal-modal-miriam-rating-' + dishMeal['id'], 'user_1_rating', 'Miriam\'s Rating:',
              dishMeal['user_1_rating']),
            createFormModalEntry(
              'dishmeal-modal-james-rating-' + dishMeal['id'], 'user_2_rating', 'James\' Rating:',
              dishMeal['user_2_rating']),
            createFormModalEntry(
              'dishmeal-modal-miriam-comments-' + dishMeal['id'], 'user_1_comments', 'Miriam\'s Comments:',
              dishMeal['user_1_comments']),
            createFormModalEntry(
              'dishmeal-modal-james-comments-' + dishMeal['id'], 'user_2_comments', 'James\' Comments:',
              dishMeal['user_2_comments'])
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
      let modalFormLines = null
      switch (this.entity['entity_type']) {
        case 'cities':
          modalTitle = 'Adding city'
          modalFormLines = [
            createFormModalEntry('add-city-modal-name', 'name', 'Name:', ''),
            createFormModalEntry('add-city-modal-state', 'state', 'State:', ''),
            createFormModalEntry('add-city-modal-country', 'country', 'Country:', ''),
            createFormModalEntry('add-city-modal-notes', 'notes', 'Notes:', '')
          ]
          break
        case 'city':
          modalTitle = 'Adding restaurant'
          modalFormLines = [
            createFormModalEntry('add-restaurant-modal-name', 'name', 'Name:', ''),
            createFormModalEntry('add-restaurant-modal-address', 'address', 'Address:', ''),
            createFormModalEntry('add-restaurant-modal-category', 'category', 'Category:', ''),
            createFormModalEntry('add-restaurant-modal-notes', 'notes', 'Notes:', '')
          ]
          break
        case 'restaurant':
          modalTitle = 'Adding dish'
          modalFormLines = [
            createFormModalEntry('add-dish-modal-name', 'name', 'Name:', ''),
            createFormModalEntry('add-dish-modal-category', 'category', 'Category:', ''),
            createFormModalEntry('add-dish-modal-notes', 'notes', 'Notes:', '')
          ]
          break
        case 'dish':
          modalTitle = 'Adding dish meal'
          modalFormLines = [
            createFormModalEntry('add-dishmeal-modal-date', 'date', 'Date:', ''),
            createFormModalEntry('add-dishmeal-modal-miriam-rating', 'user_1_rating', 'Miriam\'s Rating:', ''),
            createFormModalEntry('add-dishmeal-modal-james-rating', 'user_2_rating', 'James\' Rating:', ''),
            createFormModalEntry('add-dishmeal-modal-miriam-comments', 'user_1_comments', 'Miriam\'s Comments:', ''),
            createFormModalEntry('add-dishmeal-modal-james-comments', 'user_2_comments', 'James\' Comments:', '')
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
      return this.restaurantsPageData[parentEntityType][entity['parent_id']]
    },
    getParentEntityTypeFor (entity) {
      switch (entity['entity_type']) {
        case 'city':
          return 'cities'
        case 'restaurant':
          return 'city'
        case 'dish':
          return 'restaurant'
        case 'dish_meal':
          return 'dish'
      }
      return null
    },
    getChildEntityTypeFor (entity) {
      switch (entity['entity_type']) {
        case 'cities':
          return 'city'
        case 'city':
          return 'restaurant'
        case 'restaurant':
          return 'dish'
        case 'dish':
          return 'dish_meal'
      }
      return null
    },
    showEntity (entity) {
      switch (entity['entity_type']) {
        case 'cities':
          this.showCities()
          return
        case 'city':
          this.showCity(entity)
          return
        case 'restaurant':
          this.showRestaurant(entity)
          return
        case 'dish':
          this.showDish(entity)
          return
        case 'dish_meal':
          this.showDishMeal(entity)
      }
    },
    deleteEntity (response) {
      let entity = response['data']
      let entityType = entity['entity_type']
      let entityId = entity['id']
      let title = entity['entity_type'] === 'dish_meal' ? 'Meal' : entity['name']
      let parent = this.getParentEntityFor(entity)
      parent['children'].splice(parent['children'].indexOf(entityId), 1)
      delete this.restaurantsPageData[entityType][entityId]
      this.showEntity(parent)
      setButterBarMessage(this, 'Deleted ' + title, ButterBarType.INFO)
    },
    editEntity (response) {
      let newEntity = response['data']
      let entityId = newEntity['id']
      let entityType = newEntity['entity_type']
      let title = newEntity['entity_type'] === 'dish_meal' ? 'Meal' : newEntity['name']
      for (let prop in newEntity) {
        this.restaurantsPageData[entityType][entityId][prop] = newEntity[prop]
      }
      this.showEntity(this.entity)
      setButterBarMessage(this, 'Saved ' + title, ButterBarType.INFO)
    },
    addEntity (response) {
      let newEntity = response.data
      let title = newEntity['entity_type'] === 'dish_meal' ? 'Meal' : newEntity['name']
      this.restaurantsPageData[newEntity['entity_type']][newEntity['id']] = newEntity
      this.entity['children'].push(newEntity['id'])
      this.showEntity(this.entity)
      setButterBarMessage(this, 'Added ' + title, ButterBarType.INFO)
    },
    getNumDishesTriedAtRestaurant (restaurant) {
      return restaurant['children'].length
    },
    getBestRatingForRestaurant (restaurant) {
      if (restaurant['children'].length === 0) {
        return 0
      }
      return restaurant['children'].map(dishId => {
        let dish = this.restaurantsPageData['dish'][dishId]
        return this.getBestRatingForDish(dish)
      }).reduce((max, x) => x > max ? x : max, 0)
    },
    getBestRatingForDish (dish) {
      if (dish['children'].length === 0) {
        return 0
      }
      return dish['children'].map(dishMealId => {
        let dishMeal = this.restaurantsPageData['dish_meal'][dishMealId]
        return this.getOverallRatingForDishMeal(dishMeal)
      }).reduce((max, x) => x > max ? x : max, 0)
    },
    getLatestRatingForDish (dish) {
      if (dish['children'].length === 0) {
        return 0
      }
      let dishMeals = dish['children'].map(dishMealId => this.restaurantsPageData['dish_meal'][dishMealId])
      return this.getOverallRatingForDishMeal(
        dishMeals.reduce((currentDishMeal, nextDishMeal) => {
          return Date.parse(currentDishMeal['date']) > Date.parse(nextDishMeal['date'])
            ? currentDishMeal : nextDishMeal
        }, []))
    },
    getNumTimesDishTried (dish) {
      return dish['children'].length
    },
    getOverallRatingForDishMeal (dishMeal) {
      let rating1 = dishMeal['user_1_rating']
      let rating2 = dishMeal['user_2_rating']
      if (isEqual(rating1, 0) && isEqual(rating2, 0)) {
        return 0
      } else if (isEqual(rating1, 0)) {
        return rating2
      } else if (isEqual(rating2, 0)) {
        return rating1
      }
      return (rating1 + rating2) / 2
    },
    showCities () {
      this.backLinks = []
      this.title = 'Cities'
      this.entity = this.restaurantsPageData['cities'][0]
      this.hasInfo = false
      this.infoImages = []
      this.infoDicts = []
      this.hasChildren = true
      this.childTableHeaders = ['Name', 'State', 'Country', 'Notes']
      this.childTableValues = this.entity['children'].map(cityId => {
        let city = this.restaurantsPageData['city'][cityId]
        let handleClick = this.navigateTo.bind(this, 'restaurantsPage', { city: '' + cityId })
        return {
          id: cityId,
          handleClick: handleClick,
          values: [city['name'], city['state'], city['country'], city['notes']]
        }
      })
    },
    navigateTo (name, queryParams) {
      this.$router.push({ name: name, query: queryParams })
    },
    showCity (city) {
      let id = city['id']
      this.entity = city
      this.backLinks =
          [{
            id: 'cities',
            name: 'Cities',
            handleClick: this.navigateTo.bind(this, 'restaurantsPage', {})}]
      this.title = city['name']
      this.hasInfo = true
      this.infoImages = []
      this.infoDicts = [
        { id: 'city-state-' + id, name: 'State', value: city['state'] },
        { id: 'city-country-' + id, name: 'Country', value: city['country'] },
        { id: 'city-notes-' + id, name: 'Notes', value: city['notes'] }
      ]
      this.hasChildren = true
      this.childTableHeaders = ['Name', 'Num Dishes Tried', 'Best Rating', 'Category']
      this.childTableValues = city['children'].map(restaurantId => {
        let restaurant = this.restaurantsPageData['restaurant'][restaurantId]
        let handleClick = this.navigateTo.bind(this, 'restaurantsPage', { restaurant: '' + restaurant['id'] })
        return {
          id: restaurantId,
          handleClick: handleClick,
          values: [
            restaurant['name'],
            this.getNumDishesTriedAtRestaurant(restaurant),
            this.getBestRatingForRestaurant(restaurant).toFixed(1),
            restaurant['category']]
        }
      })
    },
    showRestaurant (restaurant) {
      let id = restaurant['id']
      let city = this.restaurantsPageData['city'][restaurant['parent_id']]
      this.entity = restaurant
      this.backLinks =
          [
            { id: 'cities', name: 'Cities', handleClick: this.navigateTo.bind(this, 'restaurantsPage', {}) },
            { id: 'city-' + city['id'],
              name: city['name'],
              handleClick: this.navigateTo.bind(this, 'restaurantsPage', { city: '' + city['id'] }) }
          ]
      this.title = restaurant['name']
      this.hasInfo = true
      this.infoImages = []
      this.infoDicts = [
        {
          id: 'restaurant-best-rating-' + id,
          name: 'Best Rating',
          value: this.getBestRatingForRestaurant(restaurant).toFixed(1)
        },
        { id: 'restaurant-address-' + id, name: 'Address', value: restaurant['address'] },
        { id: 'restaurant-category-' + id, name: 'Category', value: restaurant['category'] },
        { id: 'restaurant-notes-' + id, name: 'Notes', value: restaurant['notes'] }
      ]
      this.hasChildren = true
      this.childTableHeaders = ['Name', 'Num Times Tried', 'Best Rating', 'Category']
      this.childTableValues = restaurant['children'].map(dishId => {
        let dish = this.restaurantsPageData['dish'][dishId]
        let handleClick = this.navigateTo.bind(this, 'restaurantsPage', { dish: '' + dish['id'] })
        return {
          id: dishId,
          handleClick: handleClick,
          values: [
            dish['name'],
            this.getNumTimesDishTried(dish),
            this.getBestRatingForDish(dish).toFixed(1),
            dish['category']]
        }
      })
    },
    showDish (dish) {
      let id = dish['id']
      let restaurant = this.restaurantsPageData['restaurant'][dish['parent_id']]
      let city = this.restaurantsPageData['city'][restaurant['parent_id']]
      this.entity = dish
      this.backLinks =
          [
            { id: 'cities', name: 'Cities', handleClick: this.navigateTo.bind(this, 'restaurantsPage', {}) },
            {
              id: 'city-' + city['id'],
              name: city['name'],
              handleClick: this.navigateTo.bind(this, 'restaurantsPage', { city: '' + city['id'] }) },
            {
              id: 'restaurant-' + restaurant['id'],
              name: restaurant['name'],
              handleClick: this.navigateTo.bind(this, 'restaurantsPage', { restaurant: '' + restaurant['id'] })
            }
          ]
      this.title = restaurant['name'] + ': ' + dish['name']
      this.hasInfo = true
      this.infoImages = []
      this.infoDicts = [
        { id: 'dish-best-rating-' + id, name: 'Best Rating', value: this.getBestRatingForDish(dish).toFixed(1) },
        { id: 'dish-latest-rating-' + id, name: 'Latest Rating', value: this.getLatestRatingForDish(dish).toFixed(1) },
        { id: 'dish-num-times-tried-' + id, name: 'Num Times Tried', value: this.getNumTimesDishTried(dish) },
        { id: 'dish-category-' + id, name: 'Category', value: dish['category'] },
        { id: 'dish-notes-' + id, name: 'Notes', value: dish['notes'] }
      ]
      this.hasChildren = true
      this.childTableHeaders = ['Date', 'Overall Rating', 'Miriam\'s Rating', 'Miriam\'s Comments',
        'James\' Rating', 'James\' Comments']
      this.childTableValues = dish['children'].map(dishMealId => {
        let dishMeal = this.restaurantsPageData['dish_meal'][dishMealId]
        let handleClick = this.navigateTo.bind(this, 'restaurantsPage', { 'dish-meal': '' + dishMeal['id'] })
        return {
          id: dishMealId,
          handleClick: handleClick,
          values: [getDisplayDate(dishMeal['date']), this.getOverallRatingForDishMeal(dishMeal).toFixed(1),
            dishMeal['user_1_rating'].toFixed(1), dishMeal['user_1_comments'], dishMeal['user_2_rating'].toFixed(1),
            dishMeal['user_2_comments']]
        }
      })
    },
    showDishMeal (dishMeal) {
      let id = dishMeal['id']
      let dish = this.restaurantsPageData['dish'][dishMeal['parent_id']]
      let restaurant = this.restaurantsPageData['restaurant'][dish['parent_id']]
      let city = this.restaurantsPageData['city'][restaurant['parent_id']]
      this.entity = dishMeal
      this.backLinks =
          [
            { id: 'cities', name: 'Cities', handleClick: this.navigateTo.bind(this, 'restaurantsPage', {}) },
            {
              id: 'city-' + city['id'],
              name: city['name'],
              handleClick: this.navigateTo.bind(this, 'restaurantsPage', { city: '' + city['id'] }) },
            {
              id: 'restaurant-' + restaurant['id'],
              name: restaurant['name'],
              handleClick: this.navigateTo.bind(this, 'restaurantsPage', { restaurant: '' + restaurant['id'] })
            },
            {
              id: 'dish-' + dish['id'],
              name: dish['name'],
              handleClick: this.navigateTo.bind(this, 'restaurantsPage', { dish: '' + dish['id'] })
            }
          ]
      this.title = 'Meal for ' + restaurant['name'] + ': ' + dish['name']
      this.hasInfo = true
      this.infoImages = []
      this.infoDicts = [
        {id: 'dishmeal-date-' + id, name: 'Date', value: getDisplayDate(dishMeal['date'])},
        {id: 'dishmeal-miriam-rating-' + id, name: 'Miriam\'s Rating', value: dishMeal['user_1_rating'].toFixed(1)},
        {id: 'dishmeal-james-rating-' + id, name: 'James\'s Rating', value: dishMeal['user_2_rating'].toFixed(1)},
        {id: 'dishmeal-miriam-comments-' + id, name: 'Miriam\'s Comments', value: dishMeal['user_1_comments']},
        {id: 'dishmeal-james-comments-' + id, name: 'James\' Comments', value: dishMeal['user_2_comments']}
      ]
      this.hasChildren = false
      this.childTableHeaders = []
      this.childTableValues = []
    },
    getRestaurantsPageDataAndRender () {
      axios.post(GET_RESTAURANTS_PAGE_DATA_URL).then(
        response => {
          this.restaurantsPageData = response.data
          this.renderPageFromProps()
        }
      )
    },
    renderPageFromProps () {
      if (!this.cityIdParam && !this.restaurantIdParam && !this.dishIdParam && !this.dishMealIdParam) {
        this.showCities()
        return
      }

      let entity = null
      if (this.cityIdParam) {
        entity = this.restaurantsPageData['city'][parseInt(this.cityIdParam)]
      } else if (this.restaurantIdParam) {
        entity = this.restaurantsPageData['restaurant'][parseInt(this.restaurantIdParam)]
      } else if (this.dishIdParam) {
        entity = this.restaurantsPageData['dish'][parseInt(this.dishIdParam)]
      } else if (this.dishMealIdParam) {
        entity = this.restaurantsPageData['dish_meal'][parseInt(this.dishMealIdParam)]
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
