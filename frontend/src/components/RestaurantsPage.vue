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
      :handleEditModalSave="handleEditModalSave"
      :handleDeleteModalSave="handleDeleteModalSave"
      :editModalFormLines="editModalFormLines"
      :editModalTitle="editModalTitle"
      :deleteModalTitle="deleteModalTitle"
      :entityType="entityType"
      :entityId="entityId" />
  </div>
</template>
<script>
import RecipeRestaurantEntity from './shared/RecipeRestaurantEntity'
import { getFullBackendUrlForPath, isEqual, getDisplayDate } from '../common/utils'
import axios from 'axios'

const ADD_CITY_URL = getFullBackendUrlForPath('/add/city')
const ADD_RESTAURANT_URL = getFullBackendUrlForPath('/add/restaurant')
const ADD_DISH_URL = getFullBackendUrlForPath('/add/dish')
const ADD_DISH_MEAL_URL = getFullBackendUrlForPath('/add/dish_meal')
const GET_RESTAURANTS_PAGE_DATA_URL = getFullBackendUrlForPath('/get_restaurants_page_data')
const EDIT_ENTITY_URL_PREFIX = getFullBackendUrlForPath('/edit/')
const DELETE_ENTITY_URL_PREFIX = getFullBackendUrlForPath('/delete/')

export default {
  name: 'RestaurantsPage',
  data () {
    return {
      restaurantsPageData: {},
      /** The type of entity currently being displayed. */
      entityType: '',
      /** The id of the entity currently being displayed. */
      entityId: 0,
      backLinks: [],
      title: '',
      hasInfo: false,
      infoDicts: [],
      infoImages: [],
      hasChildren: false,
      childTableHeaders: [],
      childTableValues: [],
      /** See FormModal for a description. */
      editModalFormLines: [],
      editModalTitle: '',
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
    handleDeleteModalSave (unused) {
      let deleteUrl = DELETE_ENTITY_URL_PREFIX + this.entityType
      axios.post(deleteUrl, {id: this.entityId}).then(response => {
        let parentArray = this.getParentArrayFromEntity(this.entityType, this.entityId)
        let parentId = this.getParentIdForEntity(this.entityType, this.entityId)
        parentArray.splice(parentArray.indexOf(this.entityId), 1)
        delete this.restaurantsPageData[this.convertEntityTypeToMapName(this.entityType)][this.entityId]
        switch (this.entityType) {
          case 'city':
            this.showCities()
            return
          case 'restaurant':
            this.showCity(parentId)
            return
          case 'dish':
            this.showRestaurant(parentId)
            return
          case 'dish_meal':
            this.showDish(parentId)
        }
      })
    },
    handleEditModalSave (formSaveResponse) {
      formSaveResponse['id'] = this.entityId
      let editUrl = EDIT_ENTITY_URL_PREFIX + this.entityType
      axios.post(editUrl, formSaveResponse).then(response => {
        let newEntity = response.data
        let id = newEntity['id']
        let currentEntity = this.restaurantsPageData[this.convertEntityTypeToMapName(this.entityType)][id]
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
        case 'city':
          return 'cities'
        case 'restaurant':
          return 'restaurants'
        case 'dish':
          return 'dishes'
        case 'dish_meal':
          return 'dish_meals'
      }
    },
    getParentArrayFromEntity (entityType, id) {
      switch (entityType) {
        case 'city':
          return this.restaurantsPageData['cities_list']
        case 'restaurant':
          return this.restaurantsPageData['cities'][this.restaurantsPageData['restaurants'][id]['city_id']]['restaurants']
        case 'dish':
          return this.restaurantsPageData['restaurants'][this.restaurantsPageData['dishes'][id]['restaurant_id']]['dishes']
        case 'dish_meal':
          return this.restaurantsPageData['dishes'][this.restaurantsPageData['dish_meals'][id]['dish_id']]['dish_meals']
      }
    },
    getParentIdForEntity (entityType, id) {
      switch (entityType) {
        case 'restaurant':
          return this.restaurantsPageData['restaurants'][id]['city_id']
        case 'dish':
          return this.restaurantsPageData['dishes'][id]['restaurant_id']
        case 'dish_meal':
          return this.restaurantsPageData['dish_meals'][id]['dish_id']
      }
    },
    showEntity (entityType, id) {
      switch (entityType) {
        case 'city':
          this.showCity(id)
          return
        case 'restaurant':
          this.showRestaurant(id)
          return
        case 'dish':
          this.showDish(id)
          return
        case 'dish_meal':
          this.showDishMeal(id)
      }
    },
    getNumDishesTriedAtRestaurant (restaurant) {
      return restaurant['dishes'].length
    },
    getBestRatingForRestaurant (restaurant) {
      if (restaurant['dishes'].length === 0) {
        return 0
      }
      return restaurant['dishes'].map(dishId => {
        let dish = this.restaurantsPageData['dishes'][dishId]
        return this.getBestRatingForDish(dish)
      }).reduce((max, x) => x > max ? x : max, 0)
    },
    getBestRatingForDish (dish) {
      if (dish['dish_meals'].length === 0) {
        return 0
      }
      return dish['dish_meals'].map(dishMealId => {
        let dishMeal = this.restaurantsPageData['dish_meals'][dishMealId]
        return this.getOverallRatingForDishMeal(dishMeal)
      }).reduce((max, x) => x > max ? x : max, 0)
    },
    getLatestRatingForDish (dish) {
      if (dish['dish_meals'].length === 0) {
        return 0
      }
      let dishMeals = dish['dish_meals'].map(dishMealId => this.restaurantsPageData['dish_meals'][dishMealId])
      return this.getOverallRatingForDishMeal(
        dishMeals.reduce((currentDishMeal, nextDishMeal) => {
          return Date.parse(currentDishMeal['date']) > Date.parse(nextDishMeal['date'])
            ? currentDishMeal : nextDishMeal
        }, []))
    },
    getNumTimesDishTried (dish) {
      return dish['dish_meals'].length
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
      this.hasInfo = false
      this.infoImages = []
      this.infoDicts = []
      this.hasChildren = true
      this.childTableHeaders = ['Name', 'State', 'Country', 'Notes']
      this.childTableValues = this.restaurantsPageData['cities_list'].map(cityId => {
        let city = this.restaurantsPageData['cities'][cityId]
        let handleClick = this.showCity.bind(this, cityId)
        return {
          id: cityId,
          handleClick: handleClick,
          values: [city['name'], city['state'], city['country'], city['notes']]
        }
      })
    },
    showCity (id) {
      let city = this.restaurantsPageData['cities'][id]
      this.entityType = 'city'
      this.entityId = id
      this.backLinks =
          [{id: 'cities', name: 'Cities', handleClick: this.showCities.bind(this)}]
      this.title = city['name']
      this.hasInfo = true
      this.infoImages = []
      // TODO: Populate this with more info.
      this.infoDicts = [
        {id: 'city-state-' + id, name: 'State', value: city['state']},
        {id: 'city-country-' + id, name: 'Country', value: city['country']},
        {id: 'city-notes-' + id, name: 'Notes', value: city['notes']}
      ]
      this.hasChildren = true
      this.childTableHeaders = ['Name', 'Num Dishes Tried', 'Best Rating', 'Category']
      this.childTableValues = city['restaurants'].map(restaurantId => {
        let restaurant = this.restaurantsPageData['restaurants'][restaurantId]
        let handleClick = this.showRestaurant.bind(this, restaurantId)
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
    },
    showRestaurant (id) {
      let restaurant = this.restaurantsPageData['restaurants'][id]
      let city = this.restaurantsPageData['cities'][restaurant['city_id']]
      this.entityType = 'restaurant'
      this.entityId = id
      this.backLinks =
          [
            {id: 'cities', name: 'Cities', handleClick: this.showCities.bind(this)},
            {id: 'city-' + city['id'], name: city['name'], handleClick: this.showCity.bind(this, city['id'])}
          ]
      this.title = restaurant['name']
      this.hasInfo = true
      this.infoImages = []
      // TODO: Populate this with more info.
      this.infoDicts = [
        {id: 'restaurant-best-rating-' + id, name: 'Best Rating', value: this.getBestRatingForRestaurant(restaurant).toFixed(1)},
        {id: 'restaurant-address-' + id, name: 'Address', value: restaurant['address']},
        {id: 'restaurant-category-' + id, name: 'Category', value: restaurant['category']},
        {id: 'restaurant-notes-' + id, name: 'Notes', value: restaurant['notes']}
      ]
      this.hasChildren = true
      this.childTableHeaders = ['Name', 'Num Times Tried', 'Best Rating', 'Category']
      this.childTableValues = restaurant['dishes'].map(dishId => {
        let dish = this.restaurantsPageData['dishes'][dishId]
        let handleClick = this.showDish.bind(this, dishId)
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
    },
    showDish (id) {
      let dish = this.restaurantsPageData['dishes'][id]
      let restaurant = this.restaurantsPageData['restaurants'][dish['restaurant_id']]
      let city = this.restaurantsPageData['cities'][restaurant['city_id']]
      this.entityType = 'dish'
      this.entityId = id
      this.backLinks =
          [
            {id: 'cities', name: 'Cities', handleClick: this.showCities.bind(this)},
            {id: 'city-' + city['id'], name: city['name'], handleClick: this.showCity.bind(this, city['id'])},
            {
              id: 'restaurant-' + restaurant['id'],
              name: restaurant['name'],
              handleClick: this.showRestaurant.bind(this, restaurant['id'])
            }
          ]
      this.title = restaurant['name'] + ': ' + dish['name']
      this.hasInfo = true
      this.infoImages = []
      // TODO: Populate this with more info.
      this.infoDicts = [
        {id: 'dish-best-rating-' + id, name: 'Best Rating', value: this.getBestRatingForDish(dish).toFixed(1)},
        {id: 'dish-latest-rating-' + id, name: 'Latest Rating', value: this.getLatestRatingForDish(dish).toFixed(1)},
        {id: 'dish-num-times-tried-' + id, name: 'Num Times Tried', value: this.getNumTimesDishTried(dish)},
        {id: 'dish-category-' + id, name: 'Category', value: dish['category']},
        {id: 'dish-notes-' + id, name: 'Notes', value: dish['notes']}
      ]
      this.hasChildren = true
      this.childTableHeaders = ['Date', 'Overall Rating', 'Miriam\'s Rating', 'Miriam\'s Comments',
        'James\' Rating', 'James\' Comments']
      this.childTableValues = dish['dish_meals'].map(dishMealId => {
        let dishMeal = this.restaurantsPageData['dish_meals'][dishMealId]
        let handleClick = this.showDishMeal.bind(this, dishMealId)
        return {
          id: dishMealId,
          handleClick: handleClick,
          values: [getDisplayDate(dishMeal['date']), this.getOverallRatingForDishMeal(dishMeal).toFixed(1),
            dishMeal['user_1_rating'].toFixed(1), dishMeal['user_1_comments'], dishMeal['user_2_rating'].toFixed(1),
            dishMeal['user_2_comments']]
        }
      })
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
    },
    showDishMeal (id) {
      let dishMeal = this.restaurantsPageData['dish_meals'][id]
      let dish = this.restaurantsPageData['dishes'][dishMeal['dish_id']]
      let restaurant = this.restaurantsPageData['restaurants'][dish['restaurant_id']]
      let city = this.restaurantsPageData['cities'][restaurant['city_id']]
      this.entityType = 'dish_meal'
      this.entityId = id
      this.backLinks =
          [
            {id: 'cities', name: 'Cities', handleClick: this.showCities.bind(this)},
            {id: 'city-' + city['id'], name: city['name'], handleClick: this.showCity.bind(this, city['id'])},
            {id: 'restaurant-' + restaurant['id'], name: restaurant['name'], handleClick: this.showRestaurant.bind(this, restaurant['id'])},
            {id: 'dish-' + dish['id'], name: dish['name'], handleClick: this.showDish.bind(this, dish['id'])}
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
    },
    addCity (name, state, country, notes) {
      axios.post(ADD_CITY_URL, {name: name, state: state, country: country, notes: notes})
    },
    addRestaurant (cityId, name, category, address, notes) {
      axios.post(ADD_RESTAURANT_URL, {city_id: cityId, name: name, category: category, address: address, notes: notes})
    },
    addDish (restaurantId, name, category, notes) {
      axios.post(ADD_DISH_URL, {restaurant_id: restaurantId, name: name, category: category, notes: notes})
    },
    addDishMeal (dishId, date, user1Rating, user2Rating, user1Comments, user2Comments) {
      axios.post(
        ADD_DISH_MEAL_URL,
        {
          dish_id: dishId,
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
