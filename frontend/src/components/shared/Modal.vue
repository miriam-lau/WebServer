<template>
  <transition name="modal">
    <div class="modal-mask" @click="close" v-show="show">
      <div class="modal-container" @click.stop>
        <slot></slot>
      </div>
    </div>
  </transition>
</template>
<style>
  @import "../../assets/style/modal.css"
</style>
<script>
// Code from https://adamwathan.me/2016/01/04/composing-reusable-modal-dialogs-with-vuejs/

export default {
  name: 'Modal',
  data () {
    return {
    }
  },
  props: {
    /** Whether this modal is shown or not. */
    show: Boolean,
    /** Called when the modal is closed. Done by clicking outside of the modal or pressing escape. */
    close: Function
  },
  mounted () {
    // Closes the modal if 'escape' is pressed.
    document.addEventListener('keydown', (e) => {
      if (this.show && e.keyCode === 27) {
        this.close()
      }
    })
  }
}
</script>
