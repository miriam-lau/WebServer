<template>
  <div :class="'butter-bar ' + css">
    {{ message }}&nbsp;
  </div>
</template>
<style>
  @import "../../assets/style/butter-bar.css"
</style>
<script>
/**
 * To use this component, see the associated helper functions for it defined in common/butterbar_component.js.
 */
export default {
  name: 'ButterBar',
  props: {
    message: String,
    css: String
  }
}
</script>
