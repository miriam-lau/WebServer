<template>
  <div class="card-container">
    <div class="card-counter-container">{{cardArray.length}}</div>
    <img
        v-on:click="handleClick"
        v-on:mouseover="setCurrentCardSelection($parent, cardArray)"
        v-on:mouseout="clearCurrentCardSelection($parent)"
        :class="cardClass + ' card-in-container'"
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
     * Nullable. Represents the css class of the card to render. If none is specified, defaults to "card"
     */
    className: String,
    /**
     * Nullable. The pile to refresh the cardArray with when a card is moved.
     */
    reshufflePileArray: Array,
    /**
     * Nullable. Where to move the top card of the card stack to on left click.
     */
    defaultMoveArray: Array,
    cardArray: Array,
    /**
     * Nullable. If present, this is called with the current card which is moved.
     */
    callback: Function
  },
  computed: {
    cardClass () {
      if (this.className) {
        return this.className
      }
      return 'card'
    }
  },
  methods: {
    setCurrentCardSelection: setCurrentCardSelection,
    clearCurrentCardSelection: clearCurrentCardSelection,
    handleClick () {
      if (this.defaultMoveArray) {
        let card = moveCurrentCardSelection(this.$parent, this.defaultMoveArray, this.reshufflePileArray)
        if (card && this.callback) {
          this.callback(card)
        }
      }
    }
  }
}
</script>
