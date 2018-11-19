<template>
  <div class="recipes-page">
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
  @import "../assets/style/recipes-page.css"
</style>
<script>
import RecipeRestaurantEntity from './shared/RecipeRestaurantEntity'

export default {
  name: 'RecipesPage',
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
  }
}
</script>
