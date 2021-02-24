import Vue from 'vue'
import Router from 'vue-router'
import RecipesPage from '@/components/RecipesPage'
import RestaurantsPage from '@/components/RestaurantsPage'
import PantryPage from '@/components/PantryPage'
import NotFound from '@/components/NotFound'

Vue.use(Router)

export default new Router({
  routes: [
    {
      path: '/recipes',
      name: 'recipesPage',
      component: RecipesPage,
      props: (route) => ({
        cookbookIdParam: route.query['cookbook'],
        recipeIdParam: route.query['recipe'],
        recipeMealIdParam: route.query['recipe-meal']
      })
    },
    {
      path: '/restaurants',
      name: 'restaurantsPage',
      component: RestaurantsPage,
      props: (route) => ({
        cityIdParam: route.query['city'],
        restaurantIdParam: route.query['restaurant'],
        dishIdParam: route.query['dish'],
        dishMealIdParam: route.query['dish-meal']
      })
    },
    {
      path: '/pantry',
      name: 'pantryPage',
      component: PantryPage,
      alias: '/pantry/*'
    },
    {
      path: '*',
      component: NotFound
    }
  ]
})
