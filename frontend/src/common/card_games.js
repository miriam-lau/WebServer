import { emptyArray, transferContents } from './utils'
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
      emptyArray(reshufflePile)
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

function moveAllCards (originalPile, destinationPile) {
  transferContents(originalPile, destinationPile)
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

export { shuffle, moveCard, moveAllCards, moveCurrentCardSelection, setCurrentCardSelection, clearCurrentCardSelection }
