import Vue from 'vue'
import Router from 'vue-router'
import CurrentDocuments from '@/components/CurrentDocuments'
import HobbyTracker from '@/components/HobbyTracker'
import InventoryTracker from '@/components/InventoryTracker'
import Codenames from '@/components/Codenames'
import RecipesPage from '@/components/RecipesPage'
import RestaurantsPage from '@/components/RestaurantsPage'
import PantryPage from '@/components/PantryPage'
import NotesPage from '@/components/NotesPage'
import NotFound from '@/components/NotFound'
import Dominion from '@/components/Dominion'
import DominionGame from '@/components/DominionGame'

Vue.use(Router)

export default new Router({
  routes: [
    {
      path: '/current-documents',
      name: 'currentDocuments',
      component: CurrentDocuments
    },
    {
      path: '/hobby-tracker',
      name: 'hobbyTracker',
      component: HobbyTracker
    },
    {
      path: '/codenames',
      name: 'codenames',
      component: Codenames
    },
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
      path: '/notes',
      name: 'notesPage',
      component: NotesPage
    },
    {
      path: '/inventory-tracker',
      name: 'inventoryTracker',
      component: InventoryTracker
    },
    {
      path: '/dominion',
      name: 'dominion',
      component: Dominion
    },
    {
      path: '/dominion-game',
      name: 'dominionGame',
      component: DominionGame
    },
    {
      path: '*',
      component: NotFound
    }
  ]
})
