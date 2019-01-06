<template>
  <div class="card-container">
    <div class="card-counter-container">{{cardArray.length}}</div>
      <img
          v-on:click="handleClick"
          v-on:mouseover="setCurrentCardSelection($parent, cardArray)"
          v-on:mouseout="clearCurrentCardSelection($parent)"
          class="card card-in-container"
          :src="$parent.getImageForCardArrayOrBlank(cardArray)"/>
  </div>
</template>
<script>
import { moveCurrentCardSelection, setCurrentCardSelection, clearCurrentCardSelection } from '../../../common/card_games'

/**
 * Renders the stack of cards represented by {@code cardArray}.
 */
export default {
  name: 'CardStack',
  props: {
    /**
     * Nullable. The pile to refresh the cardArray with when a card is moved.
     */
    reshufflePileArray: Array,
    /**
     * Nullable. Where to move the top card of the card stack to on left click.
     */
    defaultMoveArray: Array,
    cardArray: Array
  },
  methods: {
    setCurrentCardSelection: setCurrentCardSelection,
    clearCurrentCardSelection: clearCurrentCardSelection,
    handleClick () {
      if (this.defaultMoveArray) {
        moveCurrentCardSelection(this.$parent, this.defaultMoveArray, this.reshufflePileArray)
      }
    }
  }
}
</script>
