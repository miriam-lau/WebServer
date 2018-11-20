<template>
  <div>
    <span :key="backLink.name" v-for="(backLink, index) in backLinks">
      <a :href="backLink.url">{{ backLink.name }}</a>
      <span v-if="index !== backLinks.length - 1">
        >
      </span>
    </span>
    <h1>
      {{ title }}
      <font-awesome-icon icon="pencil-alt" class="current-documents-icon" />
    </h1>
    <div v-if="hasInfo">
      <div v-if="hasInfoImage">
        <img class="recipe-restaurant-entity-info-image" :src="infoImageName" />
      </div>
      <div class="recipe-restaurant-entity-info">
        <table class="recipe-restaurant-entity-infotable">
          <tr v-for="info in infoDicts" :key="info.name">
            <td>{{ info.name }}:</td><td>{{ info.value }}</td>
          </tr>
        </table>
      </div>
    </div>
    <div v-if="hasChildren" class="recipe-restaurant-entity-children-list">
      <table class="recipe-restaurant-entity-table">
        <tr>
          <th v-for="header in childTableHeaders" :key="header">{{ header }}</th>
        </tr>
        <tr v-for="childTableValue in childTableValues" :key="childTableValue.id">
          <td v-for="(colValue, index) in childTableValue.values" :key="index">
            <span v-if="index === 0">
              <a :href="childTableValue.url">{{ colValue }}</a>
            </span>
            <span v-else>
              {{ colValue }}
            </span>
          </td>
        </tr>
      </table>
    </div>
  </div>
</template>
<style>
  @import "../../assets/style/recipe-restaurant-entity.css"
</style>
<script>
export default {
  name: 'RecipeRestaurantEntity',
  data () {
    return {
    }
  },
  props: {
    backLinks: Array,
    title: String,
    hasInfo: Boolean,
    hasInfoImage: Boolean,
    infoImageName: String,
    infoDicts: Array,
    hasChildren: Boolean,
    childTableHeaders: Array,
    childTableValues: Array
  },
  created () {
  }
}
</script>
