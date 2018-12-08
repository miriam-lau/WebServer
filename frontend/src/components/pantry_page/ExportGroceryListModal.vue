<template>
  <Modal :show="show" :close="close">
    <div class="modal-header">
     <h2>Exporting Grocery List</h2>
    </div>
    <div class="modal-body">
      <div :key="line" v-for="line in exportLines">
        {{ line }}
      </div>
    </div>
  </Modal>
</template>
<style>
  @import "../../assets/style/modal.css"
</style>
<script>
import Modal from '../shared/Modal'

export default {
  name: 'ExportGroceryListModal',
  props: {
    /** See Modal for explanation. */
    close: Function,
    /** See Modal for explanation. */
    show: Boolean,
    exportLines: Array
  },
  data () {
    return {
    }
  },
  components: {
    Modal
  }
}
</script>
