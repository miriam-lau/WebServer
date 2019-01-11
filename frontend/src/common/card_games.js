import { emptyArray, transferContents } from './utils'
/**
 * Used with components that utilize shared/games/. See shared/games/README.md for usage.
 */

/**
 * Moves the games_currentCardSelection from the given Vue component to the destination array passed in.
 * @param {Vue Object} component the Vue component which contains the games_currentCardSelection variable.
 * @param {array[Card]} destinationPile the destination array of cards to move the card to.
 * @param {array[Card]?} reshufflePile if present, then if the original array is emptied, this pile of cards is
 *     reshuffled into the original array before the card is moved.
 * @return the moved card if successful or null if not.
 */
function moveCurrentCardSelection (component, destinationPile, reshufflePile) {
  if (!component.games_currentCardSelection.exists) {
    return null
  }
  let card = component.moveCard(component.games_currentCardSelection['array'], component.games_currentCardSelection['index'], destinationPile, reshufflePile)
  if (!card) {
    return null
  }
  if (component.games_currentCardSelection.index !== undefined) {
    if (component.games_currentCardSelection.array.length > component.games_currentCardSelection.index) {
      setCurrentCardSelection(component, component.games_currentCardSelection.array, component.games_currentCardSelection.index)
    } else {
      clearCurrentCardSelection(component)
    }
  }
  return card
}

/**
 * Moves the card specified by the originalPile and cardIndex to the destination pile.
 * TODO: Do something better than just preventing the card from moving if it has attachments.
 * @param {array} originalPile the original pile to move the card from.
 * @param {number} cardIndex the index of the card in the original pile.
 * @param {array[Card]} destinationPile the pile to move the card to.
 * @param {array[Card]?} reshufflePile if present, this deck will get emptied and reshuffled into the
 *     originalPile if the original pile is empty when the move is requested.
 * @return the card that was moved or null if nothing if unsuccessful.
 */
function moveCard (originalPile, cardIndex, destinationPile, reshufflePile) {
  if (cardIndex !== undefined && (cardIndex < 0 || cardIndex >= originalPile.length)) {
    return null
  }
  if (cardIndex === undefined) {
    if (originalPile.length === 0 && reshufflePile && reshufflePile.length !== 0) {
      originalPile.push(...shuffle(reshufflePile))
      emptyArray(reshufflePile)
    }
    cardIndex = originalPile.length - 1
  }
  if (cardIndex < 0 || cardIndex >= originalPile.length) {
    return null
  }
  let card = originalPile[cardIndex]
  if (card['attachments'] && card['attachments'].length > 0) {
    return null
  }
  destinationPile.push(card)
  originalPile.splice(cardIndex, 1)
  return card
}

/**
 * Moves all cards from the origianl pile to the destination pile.
 * @param {array[Card]} originalPile the original pile to move the cards from.
 * @param {array[Card]} destinationPile the destination pile.
 */
function moveAllCards (originalPile, destinationPile) {
  transferContents(originalPile, destinationPile)
}

/**
 * Shuffles the array. Returns it.
 * Taken from https://gomakethings.com/how-to-shuffle-an-array-with-vanilla-js/
 * @param {array} array an array (of anything) to shuffle.
 */
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
 * Sets the games_currentCardSelection variable in the Vue component.
 * @param {*} component the Vue component to set the card on.
 * @param {array[Card]} cardArray the card array to set the current selected card from.
 * @param {number} index the index of the card to set.
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

/**
 * Clears the current selection from the Vue component.
 * @param {*} component
 */
function clearCurrentCardSelection (component) {
  component.games_currentCardSelection = {'exists': false}
}

/**
 * The default player name to invite to a game.
 * @param {*} username the name of the current player.
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
 * card is an object that has the key 'image' and may optionally have the keys 'flipped' and 'flippedImage'.
 * @param {Card} card
 */
function getImageForCard (card) {
  if (card.flipped) {
    return card['flippedImage']
  }
  return card['image']
}

/**
 * Given a games_currentCardSelection variable (See LotrGame.vue for a description), get the image used to render it.
 * The {@code cardImageToCardArrayArray} is a map of card image to array of card arrays such that if the array of the currently
 * selected card matches the key, it will return that image.
 * @param {Object} gamesCurrentCardSelection
 * @param Map<String, Array[Array[card]]>} cardImageToCardArrayArray
 */
function getImageForGamesCurrentCardSelection (gamesCurrentCardSelection, cardImageToCardArrayArray) {
  if (!gamesCurrentCardSelection.exists) {
    return
  }
  for (let cardImage in cardImageToCardArrayArray) {
    let cardArrayArrays = cardImageToCardArrayArray[cardImage]
    for (let index in cardArrayArrays) {
      if (cardArrayArrays[index] === gamesCurrentCardSelection['array']) {
        return cardImage
      }
    }
  }
  let index = gamesCurrentCardSelection.index
  if (index === undefined) {
    index = gamesCurrentCardSelection.array.length - 1
  }
  if (index < 0) {
    return '/static/blank-card.jpg'
  } else if (gamesCurrentCardSelection.array.length <= index) {
    return ''
  } else {
    return getImageForCard(gamesCurrentCardSelection.array[index])
  }
}

/**
 * Given a games_currentCardSelection variable (See LotrGame.vue for a description), get the currently selected
 * card if any is available.
 * @param {Object} gamesCurrentCardSelection
 * @return {Card?}
 */
function getGamesCurrentCardSelection (gamesCurrentCardSelection) {
  if (!gamesCurrentCardSelection.exists || !gamesCurrentCardSelection.array) {
    return null
  }
  let cardIndex = gamesCurrentCardSelection.index
  let cardArray = gamesCurrentCardSelection.array
  if (cardIndex !== undefined && (cardIndex < 0 || cardIndex >= cardArray.length)) {
    return null
  }
  if (cardIndex === undefined) {
    cardIndex = cardArray.length - 1
  }
  return cardArray[cardIndex]
}

/**
 * Given an array of Card objects, get the image used to render that array (usually renders the top card.)
 * The {@code cardImageToCardArrayArray} is a map of card image to array of card arrays such that if the array of the currently
 * selected card matches the key, it will return that image.
 * @param {Array[Card]} cardArray
 * @param Map<String, Array[Array[card]]>} cardImageToCardArrayArray
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
  return getImageForCard(cardArray[cardArray.length - 1])
}

export { shuffle, moveCard, moveAllCards, moveCurrentCardSelection, setCurrentCardSelection,
  clearCurrentCardSelection, defaultPlayerToInvite, getImageForCard, getImageForGamesCurrentCardSelection,
  getGamesCurrentCardSelection, getImageForCardArray }
