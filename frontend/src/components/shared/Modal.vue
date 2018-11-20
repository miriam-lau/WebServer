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
    show: Boolean
  },
  methods: {
    close () {
      this.$emit('close')
    }
  },
  mounted () {
    document.addEventListener('keydown', (e) => {
      if (this.show && e.keyCode === 27) {
        this.close()
      }
    })
  }
}
</script>
