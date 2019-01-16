import { findPath, fetchFromPath } from './utils'
import { socket } from '../common/socketio'
import { callAxiosAndSetButterBar } from '../common/butterbar_component'

/**
 * This file defines utility functions for card games. It is used in conjunction with card_games.py. It relies on the
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
 * 3. A 'game' variable on the Vue component which holds all variables that need to be synced with the server.
 *     Any modification to any game variable must call a function from here and the function here must
 *     perform an action which is entirely consistent with what will occur on the server via setting the
 *     'games_mutations' field on the Vue component.
 * 4. A games_mutations field on the Vue component as described previously.
 * To use this, handleGameMount() must be called within mounted() on the Vue component.
 */

/**
 * Moves the card pointed to by games_currentCardSelection to the destination array. Re-sets what's pointed
 * to after the card is moved.
 * @param {Vue Object} component the Vue component which contains the games_currentCardSelection variable.
 * @param {array[Card]} destinationArray the destination array of cards to move the card to.
 * @param {array[Card]?} reshuffleArray if present, then if the original array is emptied, this pile of cards is
 *     reshuffled into the original array before the card is moved.
 * @param {map<string, anything>?} opts. Optional parameters. See moveCard.
 * @return {Card} the moved card if successful or null if not.
 */
function moveCurrentCard (component, destinationArray, reshuffleArray, opts) {
  let selection = component['games_currentCardSelection']
  if (!selection['exists']) {
    return null
  }
  let card = moveCard(component, selection['array'], selection['index'], destinationArray, reshuffleArray, opts)
  if (!card) {
    return null
  }
  if (selection['index'] !== undefined) {
    setCurrentCard(component, selection['array'], selection['index'])
  }
  return card
}

/**
 * Moves the card specified by the originalArray and cardIndex to the destination pile. Also adds the
 * games_mutations it performs to the Vue component.
 * TODO: There is a hack here which prevents a card from being moved if it has attached cards. Do
 *     something better to allow the card to still move.
 * @param {Vue Object} component the Vue component which contains the games_currentCardSelection variable.
 * @param {array} originalArray the original pile to move the card from.
 * @param {number} cardIndex the index of the card in the original pile.
 * @param {array[Card]} destinationArray the pile to move the card to.
 * @param {array[Card]?} reshuffleArray if present, this deck will get emptied and reshuffled into the
 *     originalArray if the original pile is empty when the move is requested.
 * @param {map<string, anything>?} opts. Optional parameters with keys:
 *     afterMoveCallback {Function(card, array<Card>, array<Card>)} this is called after the card is moved. Passed the
 *     moved card, the original array, and destination array.
 * @return {Card} the card that was moved or null if nothing if unsuccessful.
 */
function moveCard (component, originalArray, cardIndex, destinationArray, reshuffleArray, opts) {
  if (cardIndex === undefined) {
    if (originalArray.length === 0 && reshuffleArray && reshuffleArray.length !== 0) {
      moveAllCards(component, reshuffleArray, originalArray)
      shuffleCards(component, originalArray)
    }
  }
  let card = _getCardByArrayAndIndex(originalArray, cardIndex)
  if (card === null) {
    return null
  }
  let cardPath = findPath(component['game'], originalArray)
  let destinationCardPath = findPath(component['game'], destinationArray)
  destinationArray.push(card)
  originalArray.splice(originalArray.findIndex(c => c === card), 1)
  component['games_mutations'].push({
    type: 'moveCard',
    dataType: 'card',
    cardPath: cardPath,
    destinationCardPath: destinationCardPath,
    gameCardId: card['gameCardId']
  })
  if (opts && opts['afterMoveCallback']) {
    opts['afterMoveCallback'](card, originalArray, destinationArray)
  }
  return card
}

/**
 * Shuffles the given array of cards. Adds the games_mutations to the component.
 * component {Vue Object} the Vue coponent to add games_mutations to.
 * array {array<Card>} the array of cards to shuffle.
 */
function shuffleCards (component, array) {
  var currentIndex = array.length
  var temporaryValue, randomIndex

  let randomNumbersUsed = []
  while (currentIndex !== 0) {
    randomIndex = Math.floor(Math.random() * currentIndex)
    randomNumbersUsed.push(randomIndex)
    currentIndex -= 1

    temporaryValue = array[currentIndex]
    array[currentIndex] = array[randomIndex]
    array[randomIndex] = temporaryValue
  }
  component['games_mutations'].push({
    type: 'shuffleCards',
    dataType: 'array',
    cardPath: findPath(component['game'], array),
    shuffleIndices: randomNumbersUsed
  })
  return randomNumbersUsed
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
function moveAllCards (component, originalArray, destinationArray) {
  while (originalArray.length > 0) {
    moveCard(component, originalArray, undefined, destinationArray)
  }
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
  component.games_currentCardSelection = { 'exists': false }
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

/**
 * This must be called in mounted() in the Vue component. It expects the following keys to be defined on data received
 * players {array<string>} the player names in this game.
 * update_type {string} 'create' for game creation or 'mutate' for game updates.
 * player_triggering_update {string} the name of the player performing the action causing this data to be received.
 * @param {Object} component the Vue component to act on.
 * @param {string} refreshName the name of the socketio channel to receive updates on.
 */
function handleComponentMount (component, refreshName) {
  socket.on(refreshName, (data) => {
    if (!data['players'].includes(component['username'])) {
      return
    }
    if (data['updateType'] === 'create') {
      component['games_numExpectedResponses'] = 0
    } else if (data['playerTriggeringUpdate'] === component['username']) {
      component['games_numExpectedResponses'] -= 1
    }
    if (component['games_numExpectedResponses'] < 0) {
      throw new Error('Unexpected response from server.')
    }
    if (component['games_numExpectedResponses'] === 0 || data['playerTriggeringUpdate'] !== component['username']) {
      updateDisplayWithReceivedGameData(component, data['gameData'])
    }
  })
}

/**
 * This must be called in mounted() in the Vue component. Handles setup.
 * @param {Object} component the Vue component to act on.
 */
function handleComponentCreated (component) {
  component['games_playerToInvite'] = defaultPlayerToInvite(component['username'])
}

/**
 * Modifies the given property.
 * @param {Object} component the Vue component to perform the modification on.
 * @param {Object} obj the object to modify the property on (the property is a key on this object). Must be a subelement of
 *     component['game']. May be nested.
 * @param {string} propertyName the name of the property to modify
 * @param {string} dataType the type data. Can be "property", "array", "card"
 * @param {string} mutationType the type of mutation to perform. Can be "incrementProperty", "decrementProperty", "set", or
 *     "invertProperty" (for booleans), or "appendElement".
 * @param {number|string|anything?} val the value to set the property to. Only used if mutationType is "set"
 */
function mutateProperty (component, obj, propertyName, dataType, mutationType, val) {
  let propertyPath = findPath(component['game'], obj)
  component['games_mutations'].push({
    type: mutationType,
    dataType: dataType,
    property: propertyName,
    propertyPath: propertyPath,
    value: val
  })
  if (mutationType === 'incrementProperty') {
    obj[propertyName]++
  } else if (mutationType === 'decrementProperty') {
    obj[propertyName]--
  } else if (mutationType === 'invertProperty') {
    obj[propertyName] = !obj[propertyName]
  } else if (mutationType === 'setProperty') {
    obj[propertyName] = val
  } else if (mutationType === 'appendElement') {
    obj[propertyName].push(val)
  } else {
    throw new Error('Unexpected mutation type.')
  }
}

/**
 * Modifies the given property.
 * @param {Object} component the Vue component to perform the modification on.
 * @param {string} propertyName the name of the property to modify
 * @param {string} mutationType the type of mutation to perform. Can be "incrementProperty", "decrementProperty", "setProperty", or
 *     "invertProperty" (for booleans), or "appendElement".
 * @param {number|string|anything?} val the value to set the property to. Only used if mutationType is "set"
 */
function mutateCurrentCard (component, propertyName, mutationType, val) {
  let card = getCurrentCard(component)
  mutateCard(component, card, propertyName, mutationType, val)
}

/**
* Modifies the given property.
* @param {Object} component the Vue component to perform the modification on.
* @param {string} propertyName the name of the property to modify
* @param {string} mutationType the type of mutation to perform. Can be "incrementProperty", "decrementProperty", "setProperty", or
*     "invertProperty" (for booleans), or "appendElement".
* @param {number|string|anything?} val the value to set the property to. Only used if mutationType is "set"
*/
function mutateCard (component, card, propertyName, mutationType, val) {
  if (!card) {
    return
  }
  let cardPath = findPath(component['game'], card)
  cardPath.pop()
  component['games_mutations'].push({
    type: mutationType,
    dataType: 'card',
    cardPath: cardPath,
    property: propertyName,
    gameCardId: card['gameCardId'],
    value: val
  })
  if (mutationType === 'incrementProperty') {
    card[propertyName]++
  } else if (mutationType === 'decrementProperty') {
    card[propertyName]--
  } else if (mutationType === 'invertProperty') {
    card[propertyName] = !card[propertyName]
  } else if (mutationType === 'setProperty') {
    card[propertyName] = val
  } else if (mutationType === 'appendElement') {
    card[propertyName].push(val)
  } else {
    throw new Error('Unexpected mutation type.')
  }
}

/**
 * Fetches the latest game for the currently logged in user and displays it if any exists.
 * component {Object} the Vue component to act on.
 * url {string} the url to fetch the latest game from.
 */
function updateDisplayWithLatestGame (component, url) {
  callAxiosAndSetButterBar(
    component,
    url,
    { username: component['username'] },
    null,
    'Failed to load game.',
    (response) => {
      if (response['data'] === null) {
        component['games_isInGame'] = false
        return
      }
      updateDisplayWithReceivedGameData(component, response['data']['data'])
    })
}

function updateDisplayWithReceivedGameData (component, gameData) {
  let currentCardSelectionArrayPath
  if (component['games_currentCardSelection']['exists']) {
    currentCardSelectionArrayPath = findPath(component['game'], component['games_currentCardSelection']['array'])
  }
  component['games_isInGame'] = true
  component['game'] = gameData
  if (currentCardSelectionArrayPath) {
    setCurrentCard(component, fetchFromPath(component['game'], currentCardSelectionArrayPath), component['games_currentCardSelection']['index'])
  }
  if (component['games_callbackForUpdateDisplayWithReceivedGameData'] !== undefined) {
    component['games_callbackForUpdateDisplayWithReceivedGameData'](gameData)
  }
}

/**
 * Calls the backend to generate a new game. Updates the game display once it is created.
 * component {Object} the Vue component to create the game on.
 * params {map<string, string|number|anything>} a map of the game data to pass in.
 * url {string} the url to call to create the game.
 */
function newGame (component, params, url) {
  callAxiosAndSetButterBar(
    component,
    url,
    params,
    'Generated Game',
    'Failed to generate game.',
    (response) => {
      let data = response.data
      updateDisplayWithReceivedGameData(component, data)
    })
}

/**
 * Saves the stored games_mutations to the backend.
 * @param {Object} component the Vue component to save the game on.
 * @param {*} url the url used to save the game.
 */
function saveGame (component, url) {
  if (component['games_mutations'].length === 0) {
    return
  }
  component['games_numExpectedResponses'] += 1
  callAxiosAndSetButterBar(
    component,
    url,
    {
      gameId: component['game']['gameId'],
      username: component['username'],
      mutations: component['games_mutations']
    },
    null,
    'Failed to save game.')
  component['games_mutations'] = []
}

export {
  shuffleCards, moveCard, moveAllCards, moveCurrentCard, setCurrentCard,
  clearCurrentCard, defaultPlayerToInvite, getImageForCard, getImageForCurrentCard,
  getCurrentCard, getImageForCardArray, handleComponentMount, handleComponentCreated, mutateProperty,
  updateDisplayWithLatestGame, newGame, saveGame, mutateCurrentCard, mutateCard
}
