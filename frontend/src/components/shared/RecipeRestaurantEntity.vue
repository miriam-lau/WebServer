<template>
  <div>
    <span :key="backLink.id" v-for="(backLink, index) in backLinks">
      <a href="#" @click.prevent="backLink.handleClick">{{ backLink.name }}</a>
      <span v-if="index !== backLinks.length - 1">
        >
      </span>
    </span>
    <h1 class="recipe-restaurant-entity-title">
      {{ title }}
      <span v-if="hasInfo">
        <font-awesome-icon icon="pencil-alt" class="current-documents-icon" @click="showEditModal" />
        <font-awesome-icon icon="trash" class="current-documents-icon" @click="showDeleteModal" />
      </span>
    </h1>
    <div v-if="hasInfo">
      <div :key="infoImage" v-for="infoImage in infoImages">
        <img class="recipe-restaurant-entity-info-image" :src="infoImage" />
      </div>
      <div class="recipe-restaurant-entity-info">
        <table class="recipe-restaurant-entity-infotable">
          <tr v-for="info in infoDicts" :key="info.id">
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
              <a href="#" @click.prevent="childTableValue.handleClick">{{ colValue }}</a>
            </span>
            <span v-else>
              {{ colValue }}
            </span>
          </td>
        </tr>
      </table>
    </div>
    <FormModal :show="shouldShowEditModal" @close="shouldShowEditModal = false"
        :title="editModalTitle" :initialFormLines="editModalFormLines"
        :handleSave="closeModalAndHandleEditModalSave" buttonText="Save" />
    <FormModal :show="shouldShowDeleteModal" @close="shouldShowDeleteModal = false"
        :title="deleteModalTitle" :initialFormLines="[]" :handleSave="closeModalAndHandleDeleteModalSave"
        buttonText="Delete" />
  </div>
</template>
<style>
  @import "../../assets/style/recipe-restaurant-entity.css"
</style>
<script>
import FormModal from './FormModal'

// TODO: Possibly need to add more id annotations as keys in the v-fors.
export default {
  name: 'RecipeRestaurantEntity',
  props: {
    /** An array of objects with properties 'id' (a unique identifier), 'name' (what's displayed) and 'handleClick'
     * (the function that's called when the link is clicked.) This is used to navigate to the ancestors of this entity.
     */
    backLinks: Array,
    /** The title to be displayed for the page render of this entity. */
    title: String,
    /** Whether or not the entity being rendered has an info section to be rendered or not. */
    hasInfo: Boolean,
    /** An array of image urls to be displayed in the info section. */
    infoImages: Array,
    /** An array of objects with properties 'id' (a unique identifier), 'name' (for display), and 'value'
     * (also displayed) in the info section.
     */
    infoDicts: Array,
    /** Whether or not this entity has a child table to be rendered. */
    hasChildren: Boolean,
    /**
     * An array of strings corresponding to the headers of the child table.
     */
    childTableHeaders: Array,
    /**
     * An array of objects with the following properties:
     *   id: An app-wide identifier for the data row of this table.
     *   handleClick: A function to run when the first column of this row is clicked. (Used for navigation.)
     *   values: An array of primitive values to display in the table.
     */
    childTableValues: Array,
    /** The title to be displayed when the edit modal is brougt up. */
    deleteModalTitle: String,
    /** The title to be displayed when the edit modal is brougt up. */
    editModalTitle: String,
    /** See FormModal for a description. */
    editModalFormLines: Array,
    /** See FormModal for a description. */
    handleEditModalSave: Function,
    /** See FormModal for a description. */
    handleDeleteModalSave: Function
  },
  data () {
    return {
      shouldShowEditModal: false,
      shouldShowDeleteModal: false
    }
  },
  components: {
    FormModal
  },
  methods: {
    showDeleteModal () {
      this.shouldShowDeleteModal = true
    },
    showEditModal () {
      this.shouldShowEditModal = true
    },
    closeModalAndHandleEditModalSave (formLines) {
      this.shouldShowEditModal = false
      this.handleEditModalSave(formLines)
    },
    closeModalAndHandleDeleteModalSave (formLines) {
      this.shouldShowDeleteModal = false
      this.handleDeleteModalSave(formLines)
    }
  }
}
</script>
