<template>
  <div>
    <img
        v-for="(card, index) in cardArray"
        :key="index"
        v-on:click="handleClick()"
        v-on:mouseover="handleMouseOver(cardArray, index)"
        v-on:mouseout="handleMouseOut()"
        :style="cardImageStyle"
        :src="getImageForCard(card)"/>
  </div>
</template>
<script>
import { moveCurrentCard, setCurrentCard, clearCurrentCard } from '../../../common/card_games'

/**
 * Renders the cards represented by {@code cardArray} as a list.
 * When a card is hovered over, the currently selected card is set to this card array and index of the card within it.
 * See the README.md file in this directory for more information on the currently selected card and usage.
 *
 * When the card is no longer hovered over, the currently selected card is cleared.
  */
export default {
  name: 'CardList',
  props: {
    /**
     * The array of cards to render.
     */
    cardArray: Array,
    /**
     * The css width of the card.
     */
    cardWidth: String,
    /**
     * The css height of the card.
     */
    cardHeight: String,
    /**
     * The css margin of the outer container surrounding the card.
     */
    cardMargin: String,
    /**
     * This is called with a card from {@code cardArray} to get the image used to render the card.
     */
    getImageForCard: Function,
    /**
     * Nullable. If {@code defaultMoveArray} is passed in, when a card is clicked, it will be moved to that array.
     */
    defaultMoveArray: Array,
    /**
     * Nullable. Whether or not to populate the currently selected card on mouseover.
     */
    shouldNotPopulateCurrentCard: Boolean,
    /**
     * Nullable. If present, this is called with the top card which is moved.
     */
    callback: Function
  },
  computed: {
    cardImageStyle () {
      return 'height: ' + this.cardHeight + '; width: ' + this.cardWidth + '; margin: ' + this.cardMargin
    }
  },
  methods: {
    handleClick () {
      if (!this.defaultMoveArray) {
        return
      }
      moveCurrentCard(this.$parent, this.defaultMoveArray, undefined, { afterMoveCallback: this.callback })
    },
    handleMouseOver (cardArray, index) {
      if (this.shouldNotPopulateCurrentCard) {
        return
      }
      setCurrentCard(this.$parent, cardArray, index)
    },
    handleMouseOut () {
      if (this.shouldNotPopulateCurrentCard) {
        return
      }
      clearCurrentCard(this.$parent)
    }
  }
}
</script>
