<template>
  <div contenteditable="true" @input="handleUpdate"></div>
</template>
<script>
export default {
  name: 'EditableDiv',
  props: {
    content: String,
    handleUpdate: Function
  },
  mounted () {
    this.$el.innerText = this.content
  }
}
</script>
