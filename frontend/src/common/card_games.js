import { findPath, fetchFromPath } from './utils'
import { socket } from '../common/socketio'
import { callAxiosAndSetButterBar } from '../common/butterbar_component'

/**
 * This file defines utility functions for card games. It is used in conjunction with card_games.py. Only methods here
 * should be used to modify any data on the card games. Failure to do so will place the client and server out of sync.
 * Usage:
 *    handleComponentMounted() must be called within mounted() on the Vue component.
 *    handleComponentCreated() must be called within created() on the Vue component.
 *
 * This file relies on the following data being defined in the component:
 * games_currentCardSelection {Object{
 *     {boolean} exists whether there is any card selected or not.
 *     {array<Card>} array an array of card objects (representing a group of associated cards like a deck.)
 *     {number|null} index the index into the {@code array} of the currently selected card. If this is unset,
 *         the entire array is selected.
 *   }} This is the object on the Vue component representing the currently selected object by the user. This
 *       is normally set when the user mouses over a card or deck in a game. it relies on Card objects being
 *       used.
 * games_isInGame {boolean} represents whether the current user has a game for display or not.
 * games_numExpectedResponses {number} the number of expected responses from the server. This should usually be
 *      0 to represent that the client is in sync with the server. Each time the current user performs an update,
 *      the client will increment this by one and send a call to the backend. When the server updates itself and
 *      sends a response back to the client, this count will decrement by one. Only when the count is zero does the
 *      game refresh itself to sync with the server's version. This is to prevent temporary blips as the server is
 *      catching up to the client.
 * games_playerToInvite {string} a string representing the player to send a game invitation to. Rendered in an input box.
 * games_callbackForUpdateDisplayWithReceivedGameData {Function({Object} gameData)?} if defined, this is called after the game has updated
 *      its display with the received game data. Called with a param representing the gameData received.
 * games_mutations {Object} Keys must correspond to backend/src/card_games/card_games.py. See comment there.
 * game {Object} a nested variable that holds the game data. Can have any structure.
 *
 * Card objects:
 * Card {Object {
 *      gameCardId {number} a unique identifier for the specific card object. Eeven card objects with the same name will have
 *            different gameCardIds.
 *      image {string} the url to the image used to render a card.
 *      flippedImage {string?} Not needed in every game. if flipped is set, this must be also, otherwise not.
 *          It is the url of the image to render when the card is in a flipped state.
 *      flipped {boolean?} Not needed in every game. if set, whether a card is in the flipped state or not.
 *    }}
 */

const DATA_PLAYERS = 'players'
const DATA_UPDATE_TYPE = 'updateType'
const DATA_PLAYER_TRIGGERING_UPDATE = 'playerTriggeringUpdate'
const DATA_VALUE_CREATE = 'create'
const DATA_VALUE_UNDO = 'undo'
const DATA_VALUE_MUTATE = 'mutate'
const DATA_GAMEDATA = 'gameData'

const COMPONENT_USERNAME = 'username'

const GAMES_MUTATIONS = 'games_mutations'
const GAMES_NUM_EXPECTED_RESPONSES = 'games_numExpectedResponses'
const GAMES_PLAYER_TO_INVITE = 'games_playerToInvite'
const GAMES_IS_IN_GAME = 'games_isInGame'
const GAME = 'game'
const GAMES_CALLBACK_FOR_UPDATE_DISPLAY_WITH_RECEIVED_GAME_DATA = 'games_callbackForUpdateDisplayWithReceivedGameData'
const GAMES_CURRENT_CARD_SELECTION = 'games_currentCardSelection'
const GAMES_CURRENT_CARD_SELECTION_EXISTS = 'exists'
const GAMES_CURRENT_CARD_SELECTION_ARRAY = 'array'
const GAMES_CURRENT_CARD_SELECTION_INDEX = 'index'
const GAMES_GAME_ID = 'gameId'

const CARD_IMAGE = 'image'
const CARD_FLIPPED_IMAGE = 'flippedImage'
const CARD_GAME_CARD_ID = 'gameCardId'
const CARD_FLIPPED = 'flipped'

const BACKEND_KEY_DATA = 'data'
const BACKEND_KEY_USERNAME = 'username'

const UNDO_GAME_GAME_ID = 'gameId'
const SAVE_GAME_GAME_ID = 'gameId'
const SAVE_GAME_MUTATIONS = 'mutations'

const MUTATION_TYPE = 'type'
const MUTATION_DATA_TYPE = 'dataType'
const MUTATION_INCREMENT = 'increment'
const MUTATION_DECREMENT = 'decrement'
const MUTATION_INVERT = 'invert'
const MUTATION_SET = 'set'
const MUTATION_MOVE_CARD = 'moveCard'
const MUTATION_SHUFFLE = 'shuffle'
const MUTATION_APPEND = 'append'
const MUTATION_CARD = 'card'
const MUTATION_PROPERTY = 'property'
const MUTATION_GAME_CARD_ID = 'gameCardId'
const MUTATION_CARD_PATH = 'cardPath'
const MUTATION_DESTINATION_CARD_PATH = 'destinationCardPath'
const MUTATION_PROPERTY_PATH = 'propertyPath'
const MUTATION_VALUE = 'value'
const MUTATION_SHUFFLE_INDICES = 'shuffleIndices'

/**
 * This must be called in mounted() in the Vue component. It is to be used with card_games.py. It expects
 * 'players', 'updateType', 'playerTriggeringUpdate' to be defined on the response it receives from the server in its
 * socketio connection. See backend/src/app.py for more information.
 * @param {Object} component the Vue component to act on.
 * @param {string} refreshName the name of the socketio channel to receive updates on.
 */
function handleComponentMounted (component, refreshName) {
  socket.on(refreshName, (data) => {
    if (!data[DATA_PLAYERS].includes(component[COMPONENT_USERNAME])) {
      return
    }
    if (data[DATA_UPDATE_TYPE] === DATA_VALUE_CREATE) {
      component[GAMES_NUM_EXPECTED_RESPONSES] = 0
    } else if (data[DATA_UPDATE_TYPE] === DATA_VALUE_MUTATE) {
      if (data[DATA_PLAYER_TRIGGERING_UPDATE] === component[COMPONENT_USERNAME]) {
        component[GAMES_NUM_EXPECTED_RESPONSES] -= 1
      }
    }
    if (component[GAMES_NUM_EXPECTED_RESPONSES] < 0) {
      throw new Error('Unexpected response from server.')
    }
    if (data[DATA_UPDATE_TYPE] === DATA_VALUE_UNDO || component[GAMES_NUM_EXPECTED_RESPONSES] === 0 || data[DATA_PLAYER_TRIGGERING_UPDATE] !== component[COMPONENT_USERNAME]) {
      updateDisplayWithReceivedGameData(component, data[DATA_GAMEDATA])
    }
  })
}

/**
 * This must be called in created() in the Vue component. Handles setup.
 * @param {Object} component the Vue component to act on.
 */
function handleComponentCreated (component) {
  component[GAMES_PLAYER_TO_INVITE] = defaultPlayerToInvite(component)
}

/**
 * Updates the game display with the provided game data object. Calls GAMES_CALLBACK_FOR_UPDATE_DISPLAY_WITH_RECEIVED_GAME_DATA
 * upon success.
 * @param {Object} component the Vue component to refresh.
 * @param {Object} gameData the game data used to update the Vue component.
 */
function updateDisplayWithReceivedGameData (component, gameData) {
  let currentCardSelectionArrayPath = findPath(component[GAME], getCurrentCardArray(component))
  component[GAMES_IS_IN_GAME] = true
  component[GAME] = gameData
  if (currentCardSelectionArrayPath) {
    setCurrentCard(component, fetchFromPath(component[GAME], currentCardSelectionArrayPath), getCurrentCardIndex(component))
  }
  if (component[GAMES_CALLBACK_FOR_UPDATE_DISPLAY_WITH_RECEIVED_GAME_DATA] !== undefined) {
    component[GAMES_CALLBACK_FOR_UPDATE_DISPLAY_WITH_RECEIVED_GAME_DATA](gameData)
  }
}

/**
 * The default player name to invite to a game.
 * @param {Object} component the Vue component to act on.
 * @return {string} the default player to invite or the empty string is there is none.
 */
function defaultPlayerToInvite (component) {
  let username = component[COMPONENT_USERNAME]
  if (username === 'James') {
    return 'Miriam'
  } else if (username === 'Miriam') {
    return 'James'
  }
  return ''
}

/**
 * Given a Vue component get the array holding the selected card.
 * @param {Vue Object} component
 * @return {array<Cards>|null} the array holding the selected card or null if none exists.
 */
function getCurrentCardArray (component) {
  let selection = component[GAMES_CURRENT_CARD_SELECTION]
  if (!selection[GAMES_CURRENT_CARD_SELECTION_EXISTS] || !selection[GAMES_CURRENT_CARD_SELECTION_ARRAY]) {
    return null
  }
  return selection[GAMES_CURRENT_CARD_SELECTION_ARRAY]
}

/**
 * Given a Vue component get the index of the selected card within its containing array.
 * @param {Vue Object} component
 * @returns {number|null} the index of the selected card or null if there is none.
 */
function getCurrentCardIndex (component) {
  let selection = component[GAMES_CURRENT_CARD_SELECTION]
  if (!selection[GAMES_CURRENT_CARD_SELECTION_EXISTS] || !selection[GAMES_CURRENT_CARD_SELECTION_ARRAY] === null ||
    selection[GAMES_CURRENT_CARD_SELECTION_INDEX] === null) {
    return null
  }
  return selection[GAMES_CURRENT_CARD_SELECTION_INDEX]
}

/**
 * Moves the selected card to the destination array. Re-sets what's pointed to after the card is moved.
 * @param {Vue Object} component the Vue component.
 * @param {array[Card]|null} destinationArray the destination array of cards to move the card to. If null, then
 *      the card is unmoved.
 * @param {Object?} opt the optional parameters passed to moveCard. See that function for further details.
 * @returns {Card|null} the moved card if successful or null if not.
 */
function moveCurrentCard (component, destinationArray, opts) {
  if (!getCurrentCardExists(component)) {
    return null
  }
  let cardArray = getCurrentCardArray(component)
  let cardIndex = getCurrentCardIndex(component)
  let card = moveCard(component, cardArray, cardIndex, destinationArray, opts)
  if (!card) {
    return null
  }
  if (cardIndex !== null) {
    setCurrentCard(component, cardArray, cardIndex)
  }
  return card
}

/**
 * Given a Vue component get whether there is a selected card or not.
 * @param {Vue Object} component
 * @returns {boolean} whether there is a currently selected card or not.
 */
function getCurrentCardExists (component) {
  let selection = component[GAMES_CURRENT_CARD_SELECTION]
  return selection[GAMES_CURRENT_CARD_SELECTION_EXISTS]
}

/**
 * Gets the card represented by {@code array} and {@code index}. If no index is provided, it returns the last
 * card of the array.
 * @param {array[Card]|null} array the array containing the card. null would be an error and return null.
 * @param {number|null} index the index of the card or null.
 * @returns {Card|null} retuns the card or null if none exists.
 */
function _getCard (array, index) {
  if (array === null) {
    return null
  }
  if (index === null) {
    index = array.length - 1
  }
  if (index < 0 || index >= array.length) {
    return null
  }
  return array[index]
}

/**
 * Saves the stored GAMES_MUTATIONS to the backend.
 * @param {Object} component the Vue component to save the game on.
 * @param {string} url the url used to save the game.
 */
function saveGame (component, url) {
  if (component[GAMES_MUTATIONS].length === 0) {
    return
  }
  component[GAMES_NUM_EXPECTED_RESPONSES] += 1
  callAxiosAndSetButterBar(
    component,
    url,
    {
      [SAVE_GAME_GAME_ID]: component[GAME][GAMES_GAME_ID],
      [BACKEND_KEY_USERNAME]: component[COMPONENT_USERNAME],
      [SAVE_GAME_MUTATIONS]: component[GAMES_MUTATIONS]
    },
    null,
    'Failed to save game.')
  component[GAMES_MUTATIONS] = []
}

/**
 * Undoes the latest game move.
 * @param {Object} component the Vue component to save the game on.
 * @param {string} url the url used to save the game.
 */
function undo (component, url) {
  callAxiosAndSetButterBar(
    component,
    url,
    {
      [UNDO_GAME_GAME_ID]: component[GAME][GAMES_GAME_ID],
      [BACKEND_KEY_USERNAME]: component[COMPONENT_USERNAME]
    },
    null,
    'Failed to undo.')
}

/**
 * Moves all cards from the original pile to the destination pile.
 * @param {array[Card]} originalArray the original pile to move the cards from.
 * @param {array[Card]} destinationArray the destination pile.
 */
function moveAllCards (component, originalArray, destinationArray) {
  while (originalArray.length > 0) {
    moveCard(component, originalArray, null, destinationArray)
  }
}

/**
 * Sets the GAMES_CURRENT_CARD_SELECTION variable in the Vue component. If the index is invalid, it
 * clears the current selection.
 * @param {Object} component the Vue component to set the card on.
 * @param {array[Card]} cardArray the card array to set the current selected card from.
 * @param {number|null} index the index of the card to set.
 */
function setCurrentCard (component, cardArray, index) {
  if (index !== null && (index < 0 || index >= cardArray.length)) {
    clearCurrentCard(component)
    return
  }
  component[GAMES_CURRENT_CARD_SELECTION] = {
    [GAMES_CURRENT_CARD_SELECTION_EXISTS]: true,
    [GAMES_CURRENT_CARD_SELECTION_ARRAY]: cardArray,
    [GAMES_CURRENT_CARD_SELECTION_INDEX]: index
  }
}

/**
 * Clears the current selection from the Vue component.
 * @param {Object} component the Vue component to clear the card on.
 */
function clearCurrentCard (component) {
  component[GAMES_CURRENT_CARD_SELECTION] = {
    [GAMES_CURRENT_CARD_SELECTION_EXISTS]: false
  }
}

/**
 * Given a card object, returns the image associated with the card.
 * @param {Card} card
 * @return {string} the url used to render the card.
 */
function getImageForCard (card) {
  return card[CARD_FLIPPED] ? card[CARD_FLIPPED_IMAGE] : card[CARD_IMAGE]
}

/**
 * Given a Vue component get the image used to render the selected card.
 * @param {Object} component the Vue component to render the card on.
 * @param Map<String, Array[Array[card]]>} cardImageToCardArrayArray a map of card image url to array of array[Card].
 *     If the selection array matches any arrays listed, the card image url will be what's rendered. This is typically
 *     used to render decks which have their card backs face down to the user.
 * @return {string} the url to render the card or the empty string if there is no card selected.
 */
function getImageForCurrentCard (component, cardImageToCardArrays) {
  let currentCardArray = getCurrentCardArray(component)
  if (currentCardArray === null) {
    return ''
  }
  for (let cardImage in cardImageToCardArrays) {
    let cardArrays = cardImageToCardArrays[cardImage]
    for (let index in cardArrays) {
      if (cardArrays[index] === currentCardArray) {
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
  let selection = component[GAMES_CURRENT_CARD_SELECTION]
  if (!selection[GAMES_CURRENT_CARD_SELECTION_EXISTS] || !selection[GAMES_CURRENT_CARD_SELECTION_ARRAY]) {
    return null
  }
  return _getCard(selection[GAMES_CURRENT_CARD_SELECTION_ARRAY], selection[GAMES_CURRENT_CARD_SELECTION_INDEX])
}

/**
 * Given an array of Card objects, get the image used to render that array (usually renders the top card.)
 * The {@code cardImageToCardArrays} is a map of card image to array of array<Card> such that if the array of {@code cardArray}
 * matches the key, it will return that image.
 * @param {array[Card]} cardArray the array of cards to render.
 * @param map<String, array[array[Card]]>} cardImageToCardArrays
 * @return {string} the url used to render the array.
 */
function getImageForCardArray (cardArray, cardImageToCardArrays) {
  if (cardArray.length === 0) {
    return '/static/blank-card.jpg'
  }
  for (let cardImage in cardImageToCardArrays) {
    let cardArrays = cardImageToCardArrays[cardImage]
    for (let index in cardArrays) {
      if (cardArrays[index] === cardArray) {
        return cardImage
      }
    }
  }
  return getImageForCard(_getCard(cardArray, null))
}

/**
 * Fetches the latest game for the currently logged in user and displays it if any exists.
 * @param {Object} component the Vue component to act on.
 * @param {string} url the url to fetch the latest game from.
 */
function updateDisplayWithLatestGame (component, url) {
  callAxiosAndSetButterBar(
    component,
    url,
    { [BACKEND_KEY_USERNAME]: component[COMPONENT_USERNAME] },
    null,
    'Failed to load game.',
    (response) => {
      if (response[BACKEND_KEY_DATA] === null) {
        component[GAMES_IS_IN_GAME] = false
        return
      }
      updateDisplayWithReceivedGameData(component, response[BACKEND_KEY_DATA][BACKEND_KEY_DATA])
    })
}

/**
 * Calls the backend to generate a new game. Updates the game display once it is created.
 * component {Object} the Vue component to create the game on.
 * @param {map<string, any>} params a map of the game data to pass in.
 * @param {string} url the url to call to create the game.
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
 * Shuffles the given array of cards.
 * @param {Vue Object} component the Vue coponent.
 * @param {array<Card>} array the array of cards to shuffle.
 * @returns {array<number>} the numbers used in the algorithm to shuffle the cards.
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
  component[GAMES_MUTATIONS].push({
    [MUTATION_TYPE]: MUTATION_SHUFFLE,
    [MUTATION_DATA_TYPE]: MUTATION_PROPERTY,
    [MUTATION_PROPERTY_PATH]: findPath(component[GAME], array),
    [MUTATION_SHUFFLE_INDICES]: randomNumbersUsed
  })
  return randomNumbersUsed
}

/**
 * Moves the card specified by the originalArray and cardIndex to the destination pile.
 * @param {Vue Object} component the Vue component which contains the GAMES_CURRENT_CARD_SELECTION variable.
 * @param {array<Card>} originalArray the original pile to move the card from.
 * @param {number|null} cardIndex the index of the card in the original pile. Can be null in which case it moves the top
 *      card.
 * @param {array[Card]} destinationArray the pile to move the card to.
 * @param {Object?} opts the optional parameters used to perform various tasks. If it exists, it can take any of the following
 *      keys:
 *      beforeMoveCallback {Function(card {Card}, originalArray {array<Card>}, destinationArray {array<Card>})} -> boolean the
 *          function to call before a card is moved. If it does not return true, the move card is canceled.
 *      afterMoveCallback {Function(card {Card}, originalArray {array<Card>}, destinationArray {array<Card>})} the function
 *          to call after a card is moved.
 * @returns {Card|null} the card that was moved or null if nothing if unsuccessful.
 */
function moveCard (component, originalArray, cardIndex, destinationArray, opts) {
  let beforeMoveCallback
  let afterMoveCallback
  if (opts) {
    beforeMoveCallback = opts['beforeMoveCallback']
    afterMoveCallback = opts['afterMoveCallback']
  }
  let card = _getCard(originalArray, cardIndex)
  if (beforeMoveCallback) {
    let success = beforeMoveCallback(card, originalArray, destinationArray)
    if (!success) {
      return null
    }
  }
  card = _getCard(originalArray, cardIndex)
  if (card === null) {
    return null
  }
  let cardPath = findPath(component[GAME], originalArray)
  let destinationCardPath = findPath(component[GAME], destinationArray)
  destinationArray.push(card)
  originalArray.splice(originalArray.findIndex(c => c === card), 1)
  component[GAMES_MUTATIONS].push({
    [MUTATION_TYPE]: MUTATION_MOVE_CARD,
    [MUTATION_DATA_TYPE]: MUTATION_CARD,
    [MUTATION_CARD_PATH]: cardPath,
    [MUTATION_DESTINATION_CARD_PATH]: destinationCardPath,
    [MUTATION_GAME_CARD_ID]: card[CARD_GAME_CARD_ID]
  })
  if (afterMoveCallback) {
    afterMoveCallback(card, originalArray, destinationArray)
  }
  return card
}

/**
 * Performs a mutation with data type property. See card_games.py for more explanation.
 * @param {Object} component the Vue component to perform the modification on.
 * @param {Object} obj the object containing the property to modify.
 * @param {string} type the type of mutation to perform.
 * @param {Object?} opt the optional parameters used. If populated, allows the following keys:
 *    value {anything}: The value to set or append.
 *    propertyName {string}: The name of the property to modify.
 */
function mutateProperty (component, obj, type, opt) {
  let propertyPath = findPath(component[GAME], obj)
  component[GAMES_MUTATIONS].push({
    [MUTATION_TYPE]: type,
    [MUTATION_DATA_TYPE]: MUTATION_PROPERTY,
    [MUTATION_PROPERTY_PATH]: propertyPath,
    [MUTATION_PROPERTY]: opt ? opt[MUTATION_PROPERTY] : null,
    [MUTATION_VALUE]: opt ? opt[MUTATION_VALUE] : null
  })
  if (type === MUTATION_INCREMENT) {
    obj[opt[MUTATION_PROPERTY]]++
  } else if (type === MUTATION_DECREMENT) {
    obj[opt[MUTATION_PROPERTY]]--
  } else if (type === MUTATION_INVERT) {
    obj[opt[MUTATION_PROPERTY]] = !obj[opt[MUTATION_PROPERTY]]
  } else if (type === MUTATION_SET) {
    obj[opt[MUTATION_PROPERTY]] = opt[MUTATION_VALUE]
  } else if (type === MUTATION_APPEND) {
    obj.push(opt[MUTATION_VALUE])
  } else {
    throw new Error('Unexpected mutation type.')
  }
}

/**
 * Performs a mutation with data type card. See card_games.py for more explanation.
 * @param {Object} component the Vue component to perform the modification on.
 * @param {Card} card the card containing the property to modify.
 * @param {string} type the type of mutation to perform.
 * @param {array} propertyPath the property path array to the object containing the property being modified.
 * @param {Object?} opt the optional parameters used. If populated, allows the following keys:
 *    value {anything}: The value to set or append.
 *    propertyName {string}: The name of the property to modify.
*/
function mutateCard (component, card, type, propertyPath, opt) {
  if (!card) {
    return
  }
  let cardPath = findPath(component[GAME], card)
  cardPath.pop()
  let propertyObj = fetchFromPath(card, propertyPath)
  component[GAMES_MUTATIONS].push({
    [MUTATION_TYPE]: type,
    [MUTATION_DATA_TYPE]: MUTATION_CARD,
    [MUTATION_CARD_PATH]: cardPath,
    [MUTATION_PROPERTY_PATH]: propertyPath,
    [MUTATION_GAME_CARD_ID]: card[CARD_GAME_CARD_ID],
    [MUTATION_PROPERTY]: opt ? opt[MUTATION_PROPERTY] : null,
    [MUTATION_VALUE]: opt ? opt[MUTATION_VALUE] : null
  })
  if (type === MUTATION_INCREMENT) {
    propertyObj[opt[MUTATION_PROPERTY]]++
  } else if (type === MUTATION_DECREMENT) {
    propertyObj[opt[MUTATION_PROPERTY]]--
  } else if (type === MUTATION_INVERT) {
    propertyObj[opt[MUTATION_PROPERTY]] = !card[opt[MUTATION_PROPERTY]]
  } else if (type === MUTATION_SET) {
    propertyObj[opt[MUTATION_PROPERTY]] = opt[MUTATION_VALUE]
  } else if (type === MUTATION_APPEND) {
    propertyObj[opt[MUTATION_PROPERTY]].push(opt[MUTATION_VALUE])
  } else {
    throw new Error('Unexpected mutation type.')
  }
}

/**
 * Performs a mutation on the current card. See card_games.py for more explanation.
 * @param {Object} component the Vue component to perform the modification on.
 * @param {string} type the type of mutation to perform.
 * @param {array} propertyPath the property path array to the object containing the property being modified.
 * @param {Object?} opt the optional parameters used. If populated, allows the following keys:
 *    value {anything}: The value to set or append.
 *    propertyName {string}: The name of the property to modify.
*/
function mutateCurrentCard (component, type, propertyPath, opt) {
  let card = getCurrentCard(component)
  mutateCard(component, card, type, propertyPath, opt)
}

export {
  shuffleCards, moveCard, moveAllCards, moveCurrentCard, setCurrentCard,
  clearCurrentCard, defaultPlayerToInvite, getImageForCard, getImageForCurrentCard, getCurrentCardArray,
  getCurrentCard, getImageForCardArray, handleComponentMounted, handleComponentCreated, mutateProperty, undo,
  updateDisplayWithLatestGame, newGame, saveGame, mutateCurrentCard, mutateCard, MUTATION_VALUE, MUTATION_PROPERTY
}
