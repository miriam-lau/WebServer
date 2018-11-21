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
      :childTableValues="childTableValues" />
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

export default {
  name: 'RestaurantsPage',
  data () {
    return {
      restaurantsPageData: {},
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
    this.getRestaurantsPageDataAndRender()
  },
  methods: {
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
      this.backLinks =
          [{name: 'Cities', handleClick: this.showCities.bind(this)}]
      this.title = city['name']
      this.hasInfo = true
      this.infoImages = []
      // TODO: Populate this with more info.
      this.infoDicts = [
        {name: 'State', value: city['state']},
        {name: 'Country', value: city['country']},
        {name: 'Notes', value: city['notes']}
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
    },
    showRestaurant (id) {
      let restaurant = this.restaurantsPageData['restaurants'][id]
      let city = this.restaurantsPageData['cities'][restaurant['city_id']]
      this.backLinks =
          [
            {name: 'Cities', handleClick: this.showCities.bind(this)},
            {name: city['name'], handleClick: this.showCity.bind(this, city['id'])}
          ]
      this.title = restaurant['name']
      this.hasInfo = true
      this.infoImages = []
      // TODO: Populate this with more info.
      this.infoDicts = [
        {name: 'Best Rating', value: this.getBestRatingForRestaurant(restaurant).toFixed(1)},
        {name: 'Address', value: restaurant['address']},
        {name: 'Category', value: restaurant['category']},
        {name: 'Notes', value: restaurant['notes']}
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
    },
    showDish (id) {
      let dish = this.restaurantsPageData['dishes'][id]
      let restaurant = this.restaurantsPageData['restaurants'][dish['restaurant_id']]
      let city = this.restaurantsPageData['cities'][restaurant['city_id']]
      this.backLinks =
          [
            {name: 'Cities', handleClick: this.showCities.bind(this)},
            {name: city['name'], handleClick: this.showCity.bind(this, city['id'])},
            {name: restaurant['name'], handleClick: this.showRestaurant.bind(this, restaurant['id'])}
          ]
      this.title = restaurant['name'] + ': ' + dish['name']
      this.hasInfo = true
      this.infoImages = []
      // TODO: Populate this with more info.
      this.infoDicts = [
        {name: 'Best Rating', value: this.getBestRatingForDish(dish).toFixed(1)},
        {name: 'Latest Rating', value: this.getLatestRatingForDish(dish).toFixed(1)},
        {name: 'Num Times Tried', value: this.getNumTimesDishTried(dish)},
        {name: 'Category', value: dish['category']},
        {name: 'Notes', value: dish['notes']}
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
    },
    showDishMeal (id) {
      let dishMeal = this.restaurantsPageData['dish_meals'][id]
      let dish = this.restaurantsPageData['dishes'][dishMeal['dish_id']]
      let restaurant = this.restaurantsPageData['restaurants'][dish['restaurant_id']]
      let city = this.restaurantsPageData['cities'][restaurant['city_id']]
      this.backLinks =
          [
            {name: 'Cities', handleClick: this.showCities.bind(this)},
            {name: city['name'], handleClick: this.showCity.bind(this, city['id'])},
            {name: restaurant['name'], handleClick: this.showRestaurant.bind(this, restaurant['id'])},
            {name: dish['name'], handleClick: this.showDish.bind(this, dish['id'])}
          ]
      this.title = 'Meal for ' + restaurant['name'] + ': ' + dish['name']
      this.hasInfo = true
      this.infoImages = []
      this.infoDicts = [
        {name: 'Date', value: getDisplayDate(dishMeal['date'])},
        {name: 'Miriam\'s Rating', value: dishMeal['user_1_rating'].toFixed(1)},
        {name: 'James\'s Rating', value: dishMeal['user_2_rating'].toFixed(1)},
        {name: 'Miriam\'s Comments', value: dishMeal['user_1_comments']},
        {name: 'James\' Comments', value: dishMeal['user_2_comments']}
      ]
      this.hasChildren = false
      this.childTableHeaders = []
      this.childTableValues = []
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
