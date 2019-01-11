import { emptyArray, transferContents, shuffle } from './utils'

/**
 * This file defines utility functions for card games. It relies on the
 * following data being defined in the component:
 * 1. games_currentCardSelection {Object{
 *     array {array[Card]} an array of card objects (representing a group of associated cards like a deck.)
 *     exists {boolean} whether a currently selected card exists or not
 *     index {number?} the index into the {@code array} of the currently selected card. If this is unset,
 *         the entire array is selected.
 *   }} This is the object on the Vue component representing the currently selected object by the user. This
 *       is normally set when the user mouses over a card or deck in a game. it relies on Card objects being
 *       used.
 * 2. Card {Object {
 *      image {string} the url to the image used to render a card.
 *      flippedImage {string?} Not needed in every game. if flipped is set, this must be also, otherwise not.
 *          It is the url of the image to render when the card is in a flipped state.
 *      flipped {boolean?} Not needed in every game. if set, whether a card is in the flipped state or not.
 *      attachments {array[Card]?} Not needed in every game. If set, it is the list of cards attached to this one
 *          such as weapons in LOTR.
 *    }}
 */

/**
 * Moves the card pointed to by games_currentCardSelection to the destination array. Re-sets what's pointed
 * to after the card is moved.
 * @param {Vue Object} component the Vue component which contains the games_currentCardSelection variable.
 * @param {array[Card]} destinationArray the destination array of cards to move the card to.
 * @param {array[Card]?} reshuffleArray if present, then if the original array is emptied, this pile of cards is
 *     reshuffled into the original array before the card is moved.
 * @return {Card} the moved card if successful or null if not.
 */
function moveCurrentCard (component, destinationArray, reshuffleArray) {
  let selection = component['games_currentCardSelection']
  if (!selection['exists']) {
    return null
  }
  let card = component.moveCard(selection['array'], selection['index'], destinationArray, reshuffleArray)
  if (!card) {
    return null
  }
  if (selection['index'] !== undefined) {
    setCurrentCard(component, selection['array'], selection['index'])
  }
  return card
}

/**
 * Moves the card specified by the originalArray and cardIndex to the destination pile.
 * TODO: There is a hack here which prevents a card from being moved if it has attached cards. Do
 *     something better to allow the card to still move.
 * @param {array} originalArray the original pile to move the card from.
 * @param {number} cardIndex the index of the card in the original pile.
 * @param {array[Card]} destinationArray the pile to move the card to.
 * @param {array[Card]?} reshuffleArray if present, this deck will get emptied and reshuffled into the
 *     originalArray if the original pile is empty when the move is requested.
 * @return {Card} the card that was moved or null if nothing if unsuccessful.
 */
function moveCard (originalArray, cardIndex, destinationArray, reshuffleArray) {
  if (cardIndex === undefined) {
    if (originalArray.length === 0 && reshuffleArray && reshuffleArray.length !== 0) {
      originalArray.push(...shuffle(reshuffleArray))
      emptyArray(reshuffleArray)
    }
  }
  let card = _getCardByArrayAndIndex(originalArray, cardIndex)
  if (card['attachments'] && card['attachments'].length > 0) {
    return null
  }
  destinationArray.push(card)
  originalArray.splice(cardIndex, 1)
  return card
}

/**
 * Given an array of cards and optionally an index for the card, return the represented card.
 * (Either the card at the index or the last card of the array.)
 * @param {array[Card]} array
 * @param {number?} index
 */
function _getCardByArrayAndIndex (array, index) {
  if (index === undefined) {
    index = array.length - 1
  }
  if (index < 0 || index >= array.length) {
    return null
  }
  return array[index]
}

/**
 * Moves all cards from the origianl pile to the destination pile.
 * @param {array[Card]} originalArray the original pile to move the cards from.
 * @param {array[Card]} destinationArray the destination pile.
 */
function moveAllCards (originalArray, destinationArray) {
  transferContents(originalArray, destinationArray)
}

/**
 * Sets the games_currentCardSelection variable in the Vue component. If the index is invalid, it
 * clears the current selection.
 * @param {Object} component the Vue component to set the card on.
 * @param {array[Card]} cardArray the card array to set the current selected card from.
 * @param {number} index the index of the card to set.
 */
function setCurrentCard (component, cardArray, index) {
  if (index < 0 || index >= cardArray.length) {
    clearCurrentCard(component)
    return
  }
  component.games_currentCardSelection = {
    array: cardArray,
    index: index,
    exists: true
  }
}

/**
 * Clears the current selection from the Vue component.
 * @param {Object} component
 */
function clearCurrentCard (component) {
  component.games_currentCardSelection = {'exists': false}
}

/**
 * The default player name to invite to a game.
 * @param {string} username the name of the currently logged in player.
 * @return {string} the default player to invite.
 */
function defaultPlayerToInvite (username) {
  if (username === 'James') {
    return 'Miriam'
  } else if (username === 'Miriam') {
    return 'James'
  } else if (username === 'Angeline') {
    return 'Sujinda'
  } else if (username === 'Sujinda') {
    return 'Angeline'
  }
  return ''
}

/**
 * Given a card object, returns the image associated with the card.
 * @param {Card} card
 * @return {string} the url to render the card.
 */
function getImageForCard (card) {
  return card['flipped'] ? card['flippedImage'] : card['image']
}

/**
 * Given a Vue component get the image used to render the selected card.
 * The {@code cardImageToCardArrayArray} is
 * @param {Object} component
 * @param Map<String, Array[Array[card]]>} cardImageToCardArrayArray a map of card image url to array of array[Card].
 *     If the selection array matches any arrays listed, the card image url will be what's rendered. This is typically
 *     used to render decks which have their card backs face down to the user.
 * @return {string} the url to render the card or the empty string on failure.
 */
function getImageForCurrentCard (component, cardImageToCardArrayArray) {
  let selection = component['games_currentCardSelection']
  if (!selection['exists']) {
    return ''
  }
  for (let cardImage in cardImageToCardArrayArray) {
    let cardArrayArrays = cardImageToCardArrayArray[cardImage]
    for (let index in cardArrayArrays) {
      if (cardArrayArrays[index] === selection['array']) {
        return cardImage
      }
    }
  }
  let card = getCurrentCard(component)
  if (!card) {
    return '/static/blank-card.jpg'
  }
  return getImageForCard(card)
}

/**
 * Given a Vue component get the selected card.
 * @param {Vue Object} component
 * @return {Card?}
 */
function getCurrentCard (component) {
  let selection = component['games_currentCardSelection']
  if (!selection['exists'] || !selection['array']) {
    return null
  }
  return _getCardByArrayAndIndex(selection['array'], selection['index'])
}

/**
 * Given an array of Card objects, get the image used to render that array (usually renders the top card.)
 * The {@code cardImageToCardArrayArray} is a map of card image to array of card arrays such that if the array of the currently
 * selected card matches the key, it will return that image.
 * @param {Array[Card]} cardArray
 * @param Map<String, Array[Array[card]]>} cardImageToCardArrayArray
 * @return {string} the url used to render the array.
 */
function getImageForCardArray (cardArray, cardImageToCardArrayArray) {
  if (cardArray.length === 0) {
    return '/static/blank-card.jpg'
  }
  for (let cardImage in cardImageToCardArrayArray) {
    let cardArrayArrays = cardImageToCardArrayArray[cardImage]
    for (let index in cardArrayArrays) {
      if (cardArrayArrays[index] === cardArray) {
        return cardImage
      }
    }
  }
  return getImageForCard(_getCardByArrayAndIndex(cardArray))
}

export { shuffle, moveCard, moveAllCards, moveCurrentCard, setCurrentCard,
  clearCurrentCard, defaultPlayerToInvite, getImageForCard, getImageForCurrentCard,
  getCurrentCard, getImageForCardArray }
