<template>
  <div>
    <img
        v-for="(card, index) in cardArray"
        :key="index"
        v-on:click="handleClick()"
        v-on:mouseover="setCurrentCardSelection($parent, cardArray, index)"
        v-on:mouseout="clearCurrentCardSelection($parent)"
        class="card"
        :src="$parent.getImageForCard(card)"/>
  </div>
</template>
<script>
import { moveCurrentCardSelection, setCurrentCardSelection, clearCurrentCardSelection } from '../../../common/card_games'

/**
 * Renders the cards represented by {@code card}.
 */
export default {
  name: 'CardList',
  props: {
    /**
     * Nullable. Where to move the top card of the card stack to on left click.
     */
    defaultMoveArray: Array,
    /**
     * The card array the current card belongs to.
     */
    cardArray: Array
  },
  methods: {
    setCurrentCardSelection: setCurrentCardSelection,
    clearCurrentCardSelection: clearCurrentCardSelection,
    handleClick () {
      if (this.defaultMoveArray) {
        moveCurrentCardSelection(this.$parent, this.defaultMoveArray)
      }
    }
  }
}
</script>
