/**
 * Used with components that utilize shared/games/. See shared/games/README.md for usage.
 */

/**
 *
 * @param {Vue Object} component
 * @param {array} destinationPile
 * @param {array?} reshufflePile
 */
function moveCurrentCardSelection (component, destinationPile, reshufflePile) {
  if (!component.games_currentCardSelection.exists) {
    return
  }
  let success = component.moveCard(component.games_currentCardSelection['array'], component.games_currentCardSelection['index'], destinationPile, reshufflePile)
  if (!success) {
    return
  }
  if (component.games_currentCardSelection.index !== undefined) {
    if (component.games_currentCardSelection.array.length > component.games_currentCardSelection.index) {
      setCurrentCardSelection(component, component.games_currentCardSelection.array, component.games_currentCardSelection.index)
    } else {
      clearCurrentCardSelection(component)
    }
  }
}

/**
 *
 * @param {array} originalPile
 * @param {number} cardIndex
 * @param {array} destinationPile
 * @param {array?} reshufflePile if present, this deck will get emptied and reshuffled into the
 *     originalPile if the original pile is empty when the move is requested.
 */
function moveCard (originalPile, cardIndex, destinationPile, reshufflePile) {
  if (cardIndex !== undefined && (cardIndex < 0 || cardIndex >= originalPile.length)) {
    return false
  }
  if (cardIndex === undefined) {
    if (originalPile.length === 0 && reshufflePile && reshufflePile.length !== 0) {
      originalPile.push(...shuffle(reshufflePile))
      _emptyArray(reshufflePile)
    }
    cardIndex = originalPile.length - 1
  }
  if (cardIndex < 0 || cardIndex >= originalPile.length) {
    return false
  }
  let card = originalPile[cardIndex]
  destinationPile.push(card)
  originalPile.splice(cardIndex, 1)
  return true
}

function _emptyArray (arr) {
  for (let i = arr.length; i > 0; --i) {
    arr.pop()
  }
}

// Taken from https://gomakethings.com/how-to-shuffle-an-array-with-vanilla-js/
function shuffle (array) {
  var currentIndex = array.length
  var temporaryValue, randomIndex

  while (currentIndex !== 0) {
    randomIndex = Math.floor(Math.random() * currentIndex)
    currentIndex -= 1

    temporaryValue = array[currentIndex]
    array[currentIndex] = array[randomIndex]
    array[randomIndex] = temporaryValue
  }
  return array
}

/*
    if (originalPile === this.game.player['deck'] && this.game.player['deck'].length === 0 && this.game.player['discard'].length !== 0) {
      this.game.player['deck'].push(...this.shuffle(this.game.player['discard']))
      this.emptyArray(this.game.player['discard'])
    } else if (originalPile === this.game.boonsDeck && this.game.boonsDeck.length === 0 && this.game.boonsDiscard.length !== 0) {
      this.game.boonsDeck.push(...this.shuffle(this.game.boonsDiscard))
      this.emptyArray(this.game.boonsDiscard)
    } else if (originalPile === this.game.hexesDeck && this.game.hexesDeck.length === 0 && this.game.hexesDiscard.length !== 0) {
      this.game.hexesDeck.push(...this.shuffle(this.game.hexesDiscard))
      this.emptyArray(this.game.hexesDiscard)
    }
*/

/**
 * If index is undefined, then show the default card. i.e. the topmost card in most cases or a card back for the deck.
 */
function setCurrentCardSelection (component, cardArray, index) {
  if (index < 0 || index >= cardArray.length) {
    clearCurrentCardSelection(component)
    return
  }
  component.games_currentCardSelection = {
    array: cardArray,
    index: index,
    exists: true
  }
}

function clearCurrentCardSelection (component) {
  component.games_currentCardSelection = {}
}

export { shuffle, moveCard, moveCurrentCardSelection, setCurrentCardSelection, clearCurrentCardSelection }
