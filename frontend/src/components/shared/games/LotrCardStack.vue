<template>
  <div class="card-games-card-stack-outer-container" :style="outerContainerStyle">
    <div class="card-games-card-stack-count">{{cardArray.length}}</div>
    <div v-if="card() && card().resources" :style="'top:' + resourceVerticalPosition(card()) + '; left:' + getTokenLeftPosition()" class="lotr-card-list-token">{{card().resources}}R</div>
    <div v-if="card() && card().damage" :style="'top:' + damageVerticalPosition(card()) + '; left:' + getTokenLeftPosition()" class="lotr-card-list-token">{{card().damage}}D</div>
    <div v-if="card() && card().progress" :style="'top:' + progressVerticalPosition(card()) + '; left:' + getTokenLeftPosition()" class="lotr-card-list-token">{{card().progress}}P</div>
    <img
        v-on:click="handleClick"
        v-on:mouseover="setCurrentCard($parent, cardArray)"
        v-on:mouseout="clearCurrentCard($parent)"
        class="card-games-top-left-absolute-position"
        :style="cardImageStyle"
        :src="getImageForCardArray(cardArray)"/>
  </div>
</template>
<script>
import { moveCurrentCard, setCurrentCard, clearCurrentCard } from '../../../common/card_games'

/**
 * Renders the stack of cards represented by {@code cardArray}.
 *
 * When the card stack is hovered over, the currently selected card is set to this card array (not a specific card.)
 * See the README.md file in this directory for more information on the currently selected card and usage.
 *
 * When the card stack is no longer hovered over, the currently selected card is cleared.
 */
export default {
  name: 'LotrCardStack',
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
     * This is called with {@code cardArray} to get the image used to render the card stack.
     */
    getImageForCardArray: Function,
    /**
     * The img src used to render the card stack (represents the top card).
    */
    image: String,
    /**
     * Nullable. If {@code defaultMoveArray} is passed in, when the stack is clicked, the top card of this stack will
     * be moved to that array.
     */
    defaultMoveArray: Array,
    /**
     * Nullable. If {@code cardArray} is empty and {@code reshuffleArray} is passed in, {@code reshuffleArray} will
     * be shuffled into {@code cardArray} before moving the top card.
     */
    reshuffleArray: Array,
    /**
     * Nullable. If present, this is called with the top card which is moved.
     */
    callback: Function
  },
  computed: {
    outerContainerStyle () {
      return 'height: ' + this.cardHeight + '; width: ' + this.cardWidth + '; margin: ' + this.cardMargin
    },
    cardImageStyle () {
      let topCard = this.card()
      let style = 'height: ' + this.cardHeight + '; width: ' + this.cardWidth
      if (topCard && topCard['exhausted']) {
        style += ';filter: brightness(0.5)'
      }
      return style
    }
  },
  methods: {
    setCurrentCard: setCurrentCard,
    clearCurrentCard: clearCurrentCard,
    card () {
      if (this.cardArray.length === 0) {
        return null
      }
      return this.cardArray[this.cardArray.length - 1]
    },
    cardResources () {
      return this.card().resources
    },
    resourceVerticalPosition (card) {
      return 'calc(' + this.cardHeight + '/2 - 1.2vw)'
    },
    damageVerticalPosition (card) {
      return 'calc(' + this.cardHeight + '/2)'
    },
    progressVerticalPosition (card) {
      return 'calc(' + this.cardHeight + '/2 + 1.2vw)'
    },
    getTokenLeftPosition () {
      return 'calc(' + this.cardWidth + '/2 - 0.45vw)'
    },
    handleClick () {
      if (!this.defaultMoveArray) {
        return
      }
      moveCurrentCard(this.$parent, this.defaultMoveArray, this.reshuffleArray, { afterMoveCallback: this.callback })
    }
  }
}
</script>
