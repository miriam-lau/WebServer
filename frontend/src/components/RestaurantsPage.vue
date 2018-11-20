<template>
  <div class="restaurants-page">
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
  @import "../assets/style/restaurants-page.css"
</style>
<script>
import RecipeRestaurantEntity from './shared/RecipeRestaurantEntity'
import { getFullBackendUrlForPath } from '../common/utils'
import axios from 'axios'

const ADD_CITY_URL = getFullBackendUrlForPath('/add/city')
const ADD_RESTAURANT_URL = getFullBackendUrlForPath('/add/restaurant')
const ADD_DISH_URL = getFullBackendUrlForPath('/add/dish')
const ADD_DISH_MEAL_URL = getFullBackendUrlForPath('/add/dish_meal')

export default {
  name: 'RestaurantsPage',
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
