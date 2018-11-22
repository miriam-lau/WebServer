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
    this.getRestaurantsPageDataAndRender()
  },
  methods: {
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
    handleDeleteModalSave (unused) {
      let entityType = this.entity['entity_type']
      let entityId = this.entity['id']
      let deleteUrl = DELETE_ENTITY_URL_PREFIX + entityType
      axios.post(deleteUrl, {id: entityId}).then(response => {
        let parent = this.getParentEntityFor(this.entity)
        parent['children'].splice(parent['children'].indexOf(entityId), 1)
        delete this.restaurantsPageData[entityType][entityId]
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
        this.restaurantsPageData[newEntity['entity_type']][newEntity['id']] = newEntity
        this.showEntity(this.entity)
      })
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
        let handleClick = this.showCity.bind(this, city)
        return {
          id: cityId,
          handleClick: handleClick,
          values: [city['name'], city['state'], city['country'], city['notes']]
        }
      })
      this.addModalTitle = 'Adding city'
      this.addModalFormLines = [
        {
          id: 'add-city-modal-name',
          name: 'name',
          displayName: 'Name:',
          value: ''
        },
        {
          id: 'add-city-modal-state',
          name: 'state',
          displayName: 'State:',
          value: ''
        },
        {
          id: 'add-city-modal-country',
          name: 'country',
          displayName: 'Country:',
          value: ''
        },
        {
          id: 'add-city-modal-notes',
          name: 'notes',
          displayName: 'Notes:',
          value: ''
        }
      ]
    },
    showCity (city) {
      let id = city['id']
      this.entity = city
      this.backLinks =
          [{id: 'cities', name: 'Cities', handleClick: this.showCities.bind(this)}]
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
        let handleClick = this.showRestaurant.bind(this, restaurant)
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
      this.addModalTitle = 'Adding restaurant'
      this.editModalTitle = 'Editing ' + this.title
      this.deleteModalTitle = 'Deleting ' + this.title
      this.editModalFormLines = [
        {
          id: 'city-modal-name-' + city['id'],
          name: 'name',
          displayName: 'Name:',
          value: city['name']
        },
        {
          id: 'city-modal-state-' + city['state'],
          name: 'state',
          displayName: 'State:',
          value: city['state']
        },
        {
          id: 'city-modal-country-' + city['country'],
          name: 'country',
          displayName: 'Country:',
          value: city['country']
        },
        {
          id: 'city-modal-notes-' + city['id'],
          name: 'notes',
          displayName: 'Notes:',
          value: city['notes']
        }
      ]
      this.addModalFormLines = [
        {
          id: 'add-restaurant-modal-name',
          name: 'name',
          displayName: 'Name:',
          value: ''
        },
        {
          id: 'add-restaurant-modal-address',
          name: 'address',
          displayName: 'Address:',
          value: ''
        },
        {
          id: 'add-restaurant-modal-category',
          name: 'category',
          displayName: 'Category:',
          value: ''
        },
        {
          id: 'add-restaurant-modal-notes',
          name: 'notes',
          displayName: 'Notes:',
          value: ''
        }
      ]
    },
    showRestaurant (restaurant) {
      let id = restaurant['id']
      let city = this.restaurantsPageData['city'][restaurant['parent_id']]
      this.entity = restaurant
      this.backLinks =
          [
            { id: 'cities', name: 'Cities', handleClick: this.showCities.bind(this) },
            { id: 'city-' + city['id'], name: city['name'], handleClick: this.showCity.bind(this, city) }
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
        let handleClick = this.showDish.bind(this, dish)
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
      this.addModalTitle = 'Adding dish'
      this.editModalTitle = 'Editing ' + this.title
      this.deleteModalTitle = 'Deleting ' + this.title
      this.editModalFormLines = [
        {
          id: 'restaurant-modal-name-' + restaurant['id'],
          name: 'name',
          displayName: 'Name:',
          value: restaurant['name']
        },
        {
          id: 'restaurant-modal-address-' + restaurant['address'],
          name: 'address',
          displayName: 'Address:',
          value: restaurant['address']
        },
        {
          id: 'restaurant-modal-category-' + restaurant['category'],
          name: 'category',
          displayName: 'Category:',
          value: restaurant['category']
        },
        {
          id: 'restaurant-modal-notes-' + restaurant['id'],
          name: 'notes',
          displayName: 'Notes:',
          value: restaurant['notes']
        }
      ]
      this.addModalFormLines = [
        {
          id: 'add-dish-modal-name',
          name: 'name',
          displayName: 'Name:',
          value: ''
        },
        {
          id: 'add-dish-modal-category',
          name: 'category',
          displayName: 'Category:',
          value: ''
        },
        {
          id: 'add-dish-modal-notes',
          name: 'notes',
          displayName: 'Notes:',
          value: ''
        }
      ]
    },
    showDish (dish) {
      let id = dish['id']
      let restaurant = this.restaurantsPageData['restaurant'][dish['parent_id']]
      let city = this.restaurantsPageData['city'][restaurant['parent_id']]
      this.entity = dish
      this.backLinks =
          [
            { id: 'cities', name: 'Cities', handleClick: this.showCities.bind(this) },
            { id: 'city-' + city['id'], name: city['name'], handleClick: this.showCity.bind(this, city) },
            {
              id: 'restaurant-' + restaurant['id'],
              name: restaurant['name'],
              handleClick: this.showRestaurant.bind(this, restaurant)
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
        let handleClick = this.showDishMeal.bind(this, dishMeal)
        return {
          id: dishMealId,
          handleClick: handleClick,
          values: [getDisplayDate(dishMeal['date']), this.getOverallRatingForDishMeal(dishMeal).toFixed(1),
            dishMeal['user_1_rating'].toFixed(1), dishMeal['user_1_comments'], dishMeal['user_2_rating'].toFixed(1),
            dishMeal['user_2_comments']]
        }
      })
      this.addModalTitle = 'Adding dish meal'
      this.editModalTitle = 'Editing ' + this.title
      this.deleteModalTitle = 'Deleting ' + this.title
      this.editModalFormLines = [
        {
          id: 'dish-modal-name-' + dish['id'],
          name: 'name',
          displayName: 'Name:',
          value: dish['name']
        },
        {
          id: 'dish-modal-category-' + dish['id'],
          name: 'category',
          displayName: 'Category:',
          value: dish['category']
        },
        {
          id: 'dish-modal-notes-' + dish['id'],
          name: 'notes',
          displayName: 'Notes:',
          value: dish['notes']
        }
      ]
      this.addModalFormLines = [
        {
          id: 'add-dishmeal-modal-date',
          name: 'date',
          displayName: 'Date:',
          value: ''
        },
        {
          id: 'add-dishmeal-modal-miriam-rating',
          name: 'user_1_rating',
          displayName: 'Miriam\'s Rating:',
          value: ''
        },
        {
          id: 'add-dishmeal-modal-james-rating',
          name: 'user_2_rating',
          displayName: 'James\' Rating:',
          value: ''
        },
        {
          id: 'add-dishmeal-modal-miriam-comments',
          name: 'user_1_comments',
          displayName: 'Miriam\'s Comments:',
          value: ''
        },
        {
          id: 'add-dishmeal-modal-james-comments',
          name: 'user_2_comments',
          displayName: 'James\' Comments:',
          value: ''
        }
      ]
    },
    showDishMeal (dishMeal) {
      let id = dishMeal['id']
      let dish = this.restaurantsPageData['dish'][dishMeal['parent_id']]
      let restaurant = this.restaurantsPageData['restaurant'][dish['parent_id']]
      let city = this.restaurantsPageData['city'][restaurant['parent_id']]
      this.entity = dishMeal
      this.backLinks =
          [
            { id: 'cities', name: 'Cities', handleClick: this.showCities.bind(this) },
            { id: 'city-' + city['id'], name: city['name'], handleClick: this.showCity.bind(this, city) },
            {
              id: 'restaurant-' + restaurant['id'],
              name: restaurant['name'],
              handleClick: this.showRestaurant.bind(this, restaurant)
            },
            { id: 'dish-' + dish['id'], name: dish['name'], handleClick: this.showDish.bind(this, dish) }
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
      this.editModalTitle = 'Editing ' + this.title
      this.deleteModalTitle = 'Deleting ' + this.title
      this.editModalFormLines = [
        {
          id: 'dishmeal-modal-date-' + dishMeal['id'],
          name: 'date',
          displayName: 'Date:',
          value: dishMeal['date']
        },
        {
          id: 'dishmeal-modal-miriam-rating-' + dishMeal['id'],
          name: 'user_1_rating',
          displayName: 'Miriam\'s Rating:',
          value: dishMeal['user_1_rating']
        },
        {
          id: 'dishmeal-modal-james-rating-' + dishMeal['id'],
          name: 'user_2_rating',
          displayName: 'James\' Rating:',
          value: dishMeal['user_2_rating']
        },
        {
          id: 'dishmeal-modal-miriam-comments-' + dishMeal['id'],
          name: 'user_1_comments',
          displayName: 'Miriam\'s Comments:',
          value: dishMeal['user_1_comments']
        },
        {
          id: 'dishmeal-modal-james-comments-' + dishMeal['id'],
          name: 'user_2_comments',
          displayName: 'James\' Comments:',
          value: dishMeal['user_2_comments']
        }
      ]
    },
    getRestaurantsPageDataAndRender () {
      axios.post(GET_RESTAURANTS_PAGE_DATA_URL).then(
        response => {
          this.restaurantsPageData = response.data
          this.showCities()
        }
      )
    }
  }
}
</script>
