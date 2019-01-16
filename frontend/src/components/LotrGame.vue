<template>
  <div class="lotr-game">
    <ButterBar
      :message="butterBar_message"
      :css="butterBar_css"
    />
    <div class="card-games-new-game">
      <span class="card-games-text-on-background">Invite:</span>
      <input v-model="games_playerToInvite" class="card-games-player-to-invite"/>
      <span class="card-games-text-on-background">Scenario:</span>
      <select v-model="scenarioName">
        <option v-for="scenario in scenarioList" :key="scenario">
          {{ scenario }}
        </option>
      </select>
      <span class="card-games-text-on-background">Your Deck:</span> <textarea v-model="player1DeckXml"/>
      <span class="card-games-text-on-background">Partner's Deck:</span> <textarea v-model="player2DeckXml"/>
      <button v-on:click="newLotrGame">New Game</button>
    </div>
    <div v-if="games_isInGame">
      Debug sync: {{games_numExpectedResponses}}<br/>
      <button @click="shownPage = 'main'">Main</button>
      <button @click="shownPage = 'quest'">Quest Discard</button>
      <button v-if="game['hasSetup']" @click="shownPage = 'setup'">Setup</button>
      <button v-if="game['revealArea'].length > 0" @click="shownPage = 'revealArea'"><u>R</u>evealed</button>
      <button v-if="game['hasSecondQuest']" @click="shownPage = 'secondQuest'">Second Quest</button>
      <button @click="shownPage = 'encounterDeck'">Encounter Deck</button>
      <button @click="shownPage = 'encounterDiscard'">Encounter Discard</button>
      <button @click="shownPage = 'victory'">Victory</button>
      <button @click="shownPage = 'secondDeck'">Your Second Deck</button>
      <button v-if="game['hasSpecial']" @click="shownPage = 'special'">Special</button>
      <button v-if="game['hasSecondSpecial']" @click="shownPage = 'secondSpecial'">Second Special</button>
      <button @click="shownPage = 'deck'">Your Deck</button>
      <button @click="shownPage = 'discard'">Your D<u>i</u>scard</button>
      <button @click="shownPage = 'trash'"><u>T</u>rash</button>
      <button @click="shownPage = 'notes'">Notes</button>
      <img
          v-if="games_currentCardSelection['exists']"
          :class="getPreviewClassName()"
          :src="getImageForCurrentCardLotr()"/>
      <div class="lotr-cards-area-above-hand">
        <div v-if="shownPage === 'main'">
          <div class="lotr-staging-area">
            <span class="card-games-text-on-background">Sta<u>g</u>ing Area</span>
            <div class="lotr-single-cards-row">
              <LotrCardList
                  :cardArray="game['stagingArea']"
                  :getMoveArray="getMoveArrayFromStagingArea"
                  :callback="discardAttachmentsForCardListCallback"
                  :cardHeight="cardHeight"
                  :cardWidth="cardWidth"
                  :cardMargin="cardMargin"
                  :getImageForCard="getImageForCard" />
            </div>
          </div>
          <div class="lotr-active-location">
            <span class="card-games-text-on-background"><u>L</u>ocation</span>
            <div class="lotr-single-cards-row">
              <LotrCardList
                  :cardArray="game['activeLocation']"
                  :getMoveArray="getMoveArrayFromActiveLocation"
                  :callback="discardAttachmentsForCardListCallback"
                  :cardHeight="cardHeight"
                  :cardWidth="cardWidth"
                  :cardMargin="cardMargin"
                  :getImageForCard="getImageForCard" />
            </div>
          </div>
          <div class="lotr-quest">
            <span class="card-games-text-on-background">Quest</span>
            <div class="lotr-single-cards-row">
              <LotrCardStack
                :cardArray="game['questDeck']"
                :defaultMoveArray="game['questDiscard']"
                :cardHeight="cardHeight"
                :cardWidth="sidewaysCardWidth"
                :cardMargin="cardMargin"
                :getImageForCardArray="getImageForCardArrayLotr" />
              </div>
          </div>
          <div class="lotr-encounter">
            <span class="card-games-text-on-background">Encounter</span>
            <div class="lotr-single-cards-row">
              <LotrCardStack
                :cardArray="game['encounterDeck']"
                :defaultMoveArray="game['stagingArea']"
                :reshuffleArray="game['encounterDiscard']"
                :cardHeight="cardHeight"
                :cardWidth="cardWidth"
                :cardMargin="cardMargin"
                :getImageForCardArray="getImageForCardArrayLotr" />
            </div>
          </div>
          <div class="clearfix"/>
          <div class="lotr-player-play-area">
            <div>
              <span class="card-games-text-on-background">Your E<u>n</u>gaged Enemies</span>
              <div class="lotr-engaged-enemies">
                <LotrCardList
                    :cardArray="player['engagedEnemies']"
                    :getMoveArray="getMoveArrayFromEngagedArea"
                    :callback="discardAttachmentsForCardListCallback"
                    :cardHeight="cardHeight"
                    :cardWidth="cardWidth"
                    :cardMargin="cardMargin"
                    :getImageForCard="getImageForCard" />
              </div>
            </div>
            <div>
              <span class="card-games-text-on-background">Your <u>C</u>haracters</span>
              <div class="lotr-characters">
                <LotrCardList
                    :cardArray="player['characters']"
                    :defaultMoveArray="player['discard']"
                    :callback="discardAttachmentsForCardListCallback"
                    :cardHeight="cardHeight"
                    :cardWidth="cardWidth"
                    :cardMargin="cardMargin"
                    :getImageForCard="getImageForCard" />
              </div>
            </div>
          </div>
          <div class="lotr-attachment">
            <span class="card-games-text-on-background">Your Attachment</span>
            <div class="lotr-attachment-card-area">
              <LotrCardList
                  :cardArray="player['selectedAttachment']"
                  :cardHeight="cardHeight"
                  :cardWidth="cardWidth"
                  :cardMargin="cardMargin"
                  :getImageForCard="getImageForCard" />
            </div>
            <span class="card-games-text-on-background">Partner's Attachment</span>
            <div class="lotr-attachment-card-area">
              <LotrCardList
                  :cardArray="partner['selectedAttachment']"
                  :cardHeight="cardHeight"
                  :cardWidth="cardWidth"
                  :cardMargin="cardMargin"
                  :getImageForCard="getImageForCard" />
            </div>
          </div>
          <div class="lotr-player-play-area">
            <div>
              <span class="card-games-text-on-background">{{partner['name']}}'s Engaged Enemies</span>
              <div class="lotr-engaged-enemies">
                <LotrCardList
                    :cardArray="partner['engagedEnemies']"
                    :getMoveArray="getMoveArrayFromEngagedArea"
                    :cardHeight="cardHeight"
                    :cardWidth="cardWidth"
                    :cardMargin="cardMargin"
                    :getImageForCard="getImageForCard" />
              </div>
            </div>
            <div>
              <span class="card-games-text-on-background">{{partner['name']}}'s Characters</span>
              <div class="lotr-characters">
                <LotrCardList
                    :cardArray="partner['characters']"
                    :cardHeight="cardHeight"
                    :cardWidth="cardWidth"
                    :cardMargin="cardMargin"
                    :getImageForCard="getImageForCard" />
              </div>
            </div>
          </div>
        </div>
        <div v-else-if="shownPage === 'quest'">
          <LotrCardList
              :cardArray="game['questDiscard']"
              :cardHeight="cardHeight"
              :cardWidth="sidewaysCardWidth"
              :cardMargin="cardMargin"
              :getImageForCard="getImageForCard" />
        </div>
        <div v-else-if="shownPage === 'secondQuest'">
          <div class="lotr-quest-deck-and-discard">
            <LotrCardStack
              :cardArray="game['secondQuestDeck']"
              :defaultMoveArray="game['secondQuestReveal']"
              :cardHeight="cardHeight"
              :cardWidth="sidewaysCardWidth"
              :cardMargin="cardMargin"
              :getImageForCardArray="getImageForCardArrayLotr" />
            <LotrCardStack
              :cardArray="game['secondQuestDiscard']"
              :cardHeight="cardHeight"
              :cardWidth="sidewaysCardWidth"
              :cardMargin="cardMargin"
              :getImageForCardArray="getImageForCardArrayLotr" />
          </div>
          <LotrCardList
              :cardArray="game['secondQuestReveal']"
              :defaultMoveArray="game['secondQuestDiscard']"
              :cardHeight="cardHeight"
              :cardWidth="sidewaysCardWidth"
              :cardMargin="cardMargin"
              :getImageForCard="getImageForCard" />
        </div>
        <div v-else-if="shownPage === 'secondDeck'">
          <div class="lotr-deck-and-discard">
            <LotrCardStack
              :cardArray="player['secondaryDeck']"
              :defaultMoveArray="player['secondaryReveal']"
              :cardHeight="cardHeight"
              :cardWidth="sidewaysCardWidth"
              :cardMargin="cardMargin"
              :getImageForCardArray="getImageForCardArrayLotr" />
            <LotrCardStack
              :cardArray="player['secondaryDiscard']"
              :cardHeight="cardHeight"
              :cardWidth="sidewaysCardWidth"
              :cardMargin="cardMargin"
              :getImageForCardArray="getImageForCardArrayLotr" />
          </div>
          <LotrCardList
              :cardArray="game['secondaryReveal']"
              :defaultMoveArray="game['secondDiscard']"
              :cardHeight="cardHeight"
              :cardWidth="sidewaysCardWidth"
              :cardMargin="cardMargin"
              :getImageForCard="getImageForCard" />
        </div>
        <LotrCardList
            v-else-if="shownPage === 'setup'"
            :cardArray="game['setupArea']"
            :cardHeight="cardHeight"
            :cardWidth="cardWidth"
            :cardMargin="cardMargin"
            :getImageForCard="getImageForCard" />
        <LotrCardList
            v-else-if="shownPage === 'revealArea'"
            :cardArray="game['revealArea']"
            :cardHeight="cardHeight"
            :cardWidth="cardWidth"
            :cardMargin="cardMargin"
            :getImageForCard="getImageForCard" />
        <LotrCardList
            v-else-if="shownPage === 'encounterDiscard'"
            :cardArray="game['encounterDiscard']"
            :cardHeight="cardHeight"
            :cardWidth="cardWidth"
            :cardMargin="cardMargin"
            :getImageForCard="getImageForCard" />
        <LotrCardList
            v-else-if="shownPage === 'encounterDeck'"
            :cardArray="game['encounterDeck']"
            :cardHeight="cardHeight"
            :cardWidth="cardWidth"
            :cardMargin="cardMargin"
            :getImageForCard="getImageForCard" />
        <LotrCardList
            v-else-if="shownPage === 'victory'"
            :cardArray="game['victory']"
            :cardHeight="cardHeight"
            :cardWidth="cardWidth"
            :cardMargin="cardMargin"
            :getImageForCard="getImageForCard" />
        <div v-else-if="shownPage === 'special'">
          <div class="lotr-deck-and-discard">
            <LotrCardStack
              :cardArray="game['specialDeck']"
              :defaultMoveArray="game['specialReveal']"
              :cardHeight="cardHeight"
              :cardWidth="sidewaysCardWidth"
              :cardMargin="cardMargin"
              :getImageForCardArray="getImageForCardArrayLotr" />
            <LotrCardStack
              :cardArray="game['specialDiscard']"
              :cardHeight="cardHeight"
              :cardWidth="sidewaysCardWidth"
              :cardMargin="cardMargin"
              :getImageForCardArray="getImageForCardArrayLotr" />
          </div>
          <LotrCardList
              :cardArray="game['specialReveal']"
              :defaultMoveArray="game['specialDiscard']"
              :cardHeight="cardHeight"
              :cardWidth="sidewaysCardWidth"
              :cardMargin="cardMargin"
              :getImageForCard="getImageForCard" />
        </div>
        <div v-else-if="shownPage === 'secondSpecial'">
          <div class="lotr-deck-and-discard">
            <LotrCardStack
              :cardArray="game['secondSpecialDeck']"
              :defaultMoveArray="game['secondSpecialReveal']"
              :cardHeight="cardHeight"
              :cardWidth="sidewaysCardWidth"
              :cardMargin="cardMargin"
              :getImageForCardArray="getImageForCardArrayLotr" />
            <LotrCardStack
              :cardArray="game['secondSpecialDiscard']"
              :cardHeight="cardHeight"
              :cardWidth="sidewaysCardWidth"
              :cardMargin="cardMargin"
              :getImageForCardArray="getImageForCardArrayLotr" />
          </div>
          <LotrCardList
              :cardArray="game['secondSpecialReveal']"
              :defaultMoveArray="game['secondSpecialDiscard']"
              :cardHeight="cardHeight"
              :cardWidth="sidewaysCardWidth"
              :cardMargin="cardMargin"
              :getImageForCard="getImageForCard" />
        </div>
        <LotrCardList
            v-else-if="shownPage === 'trash'"
            :cardArray="game['trash']"
            :cardHeight="cardHeight"
            :cardWidth="cardWidth"
            :cardMargin="cardMargin"
            :getImageForCard="getImageForCard" />
        <LotrCardList
            v-else-if="shownPage === 'deck'"
            :cardArray="player['deck']"
            :cardHeight="cardHeight"
            :cardWidth="cardWidth"
            :cardMargin="cardMargin"
            :getImageForCard="getImageForCard" />
        <LotrCardList
            v-else-if="shownPage === 'discard'"
            :cardArray="player['discard']"
            :cardHeight="cardHeight"
            :cardWidth="cardWidth"
            :cardMargin="cardMargin"
            :getImageForCard="getImageForCard" />
        <textarea v-else-if="shownPage === 'notes'" class="lotr-note" v-model="notes"></textarea>
      </div>
      <div class="clearfix"/>
      <div class="lotr-player-area">
        <div class="card-games-stats-line">
          <span class="card-games-stat-item card-games-text-on-background">(1) Threat Points: {{player['threat']}}</span>
          <span class="card-games-stat-item card-games-text-on-background">Partner Threat Points: {{partner['threat']}}</span>
        </div>
        <div class="lotr-deck-and-hand">
          <div class="lotr-single-pile">
            <span class="card-games-text-on-background">Dec<u>k</u></span>
            <div class="lotr-single-pile-cards">
              <LotrCardStack
                  :cardArray="player['deck']"
                  :defaultMoveArray="player['hand']"
                  :cardHeight="cardHeight"
                  :cardWidth="cardWidth"
                  :cardMargin="cardMargin"
                  :getImageForCardArray="getImageForCardArrayLotr" />
            </div>
          </div>
          <div class="lotr-single-pile">
            <span class="card-games-text-on-background"><u>D</u>iscard</span>
            <div class="lotr-single-pile-cards">
              <LotrCardStack
                  :cardArray="player['discard']"
                  :cardHeight="cardHeight"
                  :cardWidth="cardWidth"
                  :cardMargin="cardMargin"
                  :getImageForCardArray="getImageForCardArrayLotr" />
            </div>
          </div>
          <div class="lotr-hand-area">
            <span class="card-games-text-on-background">Your <u>H</u>and</span>
            <div class="lotr-hand-cards-area">
              <LotrCardList
                  :cardArray="player['hand']"
                  :defaultMoveArray="player['characters']"
                  :cardHeight="cardHeight"
                  :cardWidth="cardWidth"
                  :cardMargin="cardMargin"
                  :getImageForCard="getImageForCard" />
            </div>
          </div>
        </div>
      </div>
    </div>
    <div class="clearfix"/>
  </div>
</template>
<style>
  @import "../assets/style/card-games.css"
</style>
<style>
  @import "../assets/style/lotr-game.css"
</style>
<script>

import ButterBar from './shared/ButterBar'
import CardStack from './shared/games/CardStack'
import CardList from './shared/games/CardList'
import LotrCardList from './shared/games/LotrCardList'
import LotrCardStack from './shared/games/LotrCardStack'
import { callAxiosAndSetButterBar } from '../common/butterbar_component'
import { getFullBackendUrlForPath } from '../common/utils'
import { store } from '../store/store'
import { moveCard, moveCurrentCard, handleComponentMount, handleComponentCreated,
  getImageForCard, getImageForCurrentCard, updateDisplayWithLatestGame, mutateProperty,
  mutateCurrentCard, mutateCard, shuffleCards,
  getCurrentCard, getImageForCardArray, newGame, saveGame } from '../common/card_games'

const LOTR_GET_SCENARIO_NAMES_URL = getFullBackendUrlForPath('/lotr_get_scenario_names')
const CREATE_LOTR_GAME_URL = getFullBackendUrlForPath('/create_lotr_game')
const LOTR_GET_LATEST_GAME_URL = getFullBackendUrlForPath('/lotr_get_latest_game')
const LOTR_MUTATE_GAME_URL = getFullBackendUrlForPath('/lotr_mutate_game')

export default {
  name: 'LotrGame',
  components: { ButterBar, CardStack, CardList, LotrCardList, LotrCardStack },
  computed: { username () { return store.state.username } },
  watch: {
    username () { updateDisplayWithLatestGame(this, LOTR_GET_LATEST_GAME_URL) },
    games_mutations: { handler (val) { saveGame(this, LOTR_MUTATE_GAME_URL) } }
  },
  created () {
    var style = getComputedStyle(document.body)
    this.cardHeight = style.getPropertyValue('--lotr-card-height')
    this.cardWidth = style.getPropertyValue('--lotr-card-width')
    this.cardMargin = style.getPropertyValue('--card-margin')
    this.sidewaysCardWidth = style.getPropertyValue('--lotr-sideways-card-width')
    this.updateLotrScenarios()
    updateDisplayWithLatestGame(this, LOTR_GET_LATEST_GAME_URL)
    window.addEventListener('keyup', this.handleKeyPress)
    handleComponentCreated(this)
  },
  mounted () {
    handleComponentMount(this, 'refreshLotr')
  },
  data () {
    return {
      /**
       * Needed for butter bar.
       */
      butterBar_message: '',
      /**
       * Needed for butter bar.
       */
      butterBar_css: '',
      /**
       * Num expected responses
       */
      games_numExpectedResponses: 0,
      /**
       * The game object represents all the data needed to render a game. It contains the following nested data:
       * playedCards {array[Card]} the cards played by either player.
       * stagingArea {array[Card]} the staging area.
       * activeLocation {array[Card]} the active location.
       * questReveal {array[Card]} the currently revealed quest. Should only have one card at a time.
       * questDeck {array[Card]} the quest deck.
       * questDiscard {array[Card]} the quest discard pile.
       * revealArea {array[Card]} the cards revealed by either player. Used to store cards temporarily while the
       *     characters look at them and move to another pile.
       * secondQuestDeck {array[Card]} the second quest deck in the game if one is available.
       * secondQuestDiscard {array[Card]} the discard pile for the second quest deck.
       * secondQuestReveal {array[Card]} the reveal pile for the second quest deck.
       * encounterDeck {array[Card]} the encounter deck.
       * encounterDiscard {array[Card]} the discard pile for the encounter deck.
       * victory {array[Card]} the victory pile of cards earned by players.
       * specialDeck {array[Card]} the special deck in the game if one is available.
       * specialDiscard {array[Card]} the discard pile for the special deck.
       * specialReveal {array[Card]} the reveal pile for the special deck.
       * secondSpecialDeck {array[Card]} the second special deck in the game if one is available.
       * secondSpecialDiscard {array[Card]} the discard pile for the second special deck.
       * secondSpecialReveal {array[Card]} the reveal pile for the second special deck.
       * setupArea {array[Card]} the special setup area for the game if one exists.
       * trash {array[Card]} the cards which have been put into the trash for any reason.
       * hasSetup {boolean} whether the game has a setup area or not.
       * hasSecondQuest {boolean} whether the game has a second quest deck or not.
       * hasSpecial {boolean} whether the game has a special deck or not.
       * hasSecondSpecial {boolean} whether the game has a second special deck or not.
       * gameId {number} the database id of the created game.
       * players {array[Player]} the array of the two players in the game.
       *
       * The objects referenced in game are Players and Cards.
       *
       * Player represents a player in the game. It contains the following keys:
       * name {string} the name of the player
       * characters {array[Card]} the characters in the player's play area.
       * deck {array[Card]} the deck of cards of the player.
       * hand {array[Card]} the hand of cards of the player.
       * discard {array[Card]} the discard pile of cards of the player.
       * engagedEnemies {array[Card]} the enemies engaged with the player.
       * secondaryDeck {array[Card]}: the secondary deck of the player if they are using it.
       * secondaryDiscard {array[Card]}: the discard pile of the secondary deck if they are using one.
       * secondaryReveal {array[Card]}: the reveal pile of the secondary deck if they are using one.
       * threat {number}: the current threat of the player.
       *
       * Card represents a card in the game. It contains many keys which can be found in the lotr.py file but
       * the relevant ones are the following:
       * image {string} the url used to render the card.
       * flippedImage {string} the url used to render the flipped side of the card.
       * attachments {array[Card]} the list of cards attached to this card.
       * resources {number} the number of resource tokens on this card.
       * progress {number} the number of progress tokens on this card.
       * damage {number} the number of damage tokens on this card.
       * flipped {boolean} whether the card is flipped or not.
       */
      game: {},
      /**
       * Needed for card-games.js.
       */
      games_currentCardSelection: {'exists': false},
      /**
       * The name of the player to invite when creating a new game.
       */
      games_playerToInvite: '',
      /**
       * Whether there is a game to display or not.
       */
      games_isInGame: false,
      /**
       * The pending mutations to be sent to the server.
       */
      games_mutations: [],
      /**
       * The deck the current player will use when creating a new game.
       */
      player1DeckXml: '',
      /**
       * The deck the partner player will use when creating a new game.
       */
      player2DeckXml: '',
      /**
       * The name of the scenario to create a new game with.
       */
      scenarioName: '',
      /**
       * The list of scenarios to choose from when creating a new game.
       */
      scenarioList: [],
      /**
       * The height of a card in the game. Read from the css as a string.
       */
      cardHeight: '',
      /**
       * The width of a card in the game. Read from the css as a string.
       */
      cardWidth: '',
      /**
       * The margin of a card in the game. Read from the css as a string.
       */
      cardMargin: '',
      /**
       * The width of a sideways card in the game. Read from the css as a string.
       */
      sidewaysCardWidth: '',
      /**
       * In-game notes the player can type to themselves.
       */
      notes: '',
      /**
       * Represents the current game page to display.
       */
      shownPage: 'main',
      /**
       * For convenience, this points to the object representing the player within game['players'].
       */
      player: {},
      /**
       * For convenience, this points to the object representing the player's partner within game['players'].
       */
      partner: {},
      /**
       * The index of the player within game['players'].
       */
      playerIndex: 0
    }
  },
  methods: {
    newLotrGame () {
      newGame(
        this, {
          scenario: this.scenarioName,
          player1: this.username,
          player2: this.games_playerToInvite,
          player1Deck: this.player1DeckXml,
          player2Deck: this.player2DeckXml,
          username: this.username
        },
        CREATE_LOTR_GAME_URL)
    },
    getImageForCard: getImageForCard,
    getImageForCurrentCardLotr () {
      return getImageForCurrentCard(
        this, {
          '/static/lotr/cards/card.jpg': [this.player['deck'], this.partner['deck']],
          '/static/lotr/cards/encounter.jpg': [this.game['encounterDeck']]
        })
    },
    getImageForCardArrayLotr (cardArray) {
      return getImageForCardArray(cardArray, {
        '/static/lotr/cards/card.jpg': [this.player['deck'], this.partner['deck']],
        '/static/lotr/cards/encounter.jpg': [this.game['encounterDeck']]
      })
    },
    getPreviewClassName () {
      if (!this.games_currentCardSelection['exists']) {
        return ''
      }
      let cardArray = this.games_currentCardSelection['array']
      return (
        cardArray === this.game['questDeck'] ||
        cardArray === this.game['questReveal'] ||
        cardArray === this.game['questDiscard'] ||
        cardArray === this.game['secondQuestDeck'] ||
        cardArray === this.game['secondQuestReveal'] ||
        cardArray === this.game['secondQuestDisard']) ? 'lotr-preview-sideways' : 'lotr-preview-normal'
    },
    moveCard: moveCard,
    getMoveArrayFromStagingArea (card, isAttachment) {
      if (card['Type'] === 'Location') {
        if (this.game['activeLocation'].length > 0) {
          return null
        }
        return this.game['activeLocation']
      }
      if (card['Type'] === 'Treachery') {
        return this.game['encounterDiscard']
      }
      if (card['Type'] === 'Enemy') {
        return this.player['engagedEnemies']
      }
      return null
    },
    getMoveArrayFromEngagedArea (card, isAttachment) {
      if (isAttachment) {
        return this.game['encounterDiscard']
      }
      if (card['Victory Points'] && card['Victory Points'] > 0) {
        return this.game['victory']
      }
      return this.game['encounterDiscard']
    },
    discardAttachmentsForCardListCallback (card, originalArray, destinationArray) {
      if (destinationArray === this.player['discard'] || destinationArray === this.partner['discard'] || destinationArray === this.game['encounterDiscard']) {
        for (let attachmentIndex = card['attachments'].length - 1; attachmentIndex >= 0; attachmentIndex--) {
          let attachment = card['attachments'][attachmentIndex]
          moveCard(this, card['attachments'], attachmentIndex, this.getDefaultDiscardForCard(attachment))
        }
      }
    },
    getMoveArrayFromActiveLocation (card, isAttachment) {
      if (isAttachment) {
        return this.game['encounterDiscard']
      }
      if (card['Victory Points'] && card['Victory Points'] > 0) {
        return this.game['victory']
      }
      return this.game['encounterDiscard']
    },
    updateLotrScenarios () {
      callAxiosAndSetButterBar(
        this,
        LOTR_GET_SCENARIO_NAMES_URL,
        {},
        null,
        'Failed to get scenarios.',
        (response) => {
          if (response.data === null) {
            return
          }
          this.scenarioList = response.data
          this.scenarioName = this.scenarioList[0]
        })
    },
    games_callbackForUpdateDisplayWithReceivedGameData (gameData) {
      this.playerIndex = gameData.players[0].name === this.username ? 0 : 1
      this.player = this.game.players[this.playerIndex]
      this.partner = this.game.players[1 - this.playerIndex] // Only supports a 2 player game.
    },
    handleKeyPress (event) {
      if (!this.games_isInGame) {
        return
      }
      switch (event.key) {
        case '1': this.incrementThreat(); return
        case '!': this.decrementThreat(); return
        case 'e': this.endRound(); return
      }
      let card = getCurrentCard(this)
      if (!card) {
        return
      }
      let destinationArray = null
      let reshuffleArray = null
      switch (event.key) {
        case 'l':
          if (this.game['activeLocation'].length > 0) {
            return
          }
          destinationArray = this.game['activeLocation']
          break
        case 'c': destinationArray = this.player.characters; break
        case 'n': destinationArray = this.player.engagedEnemies; break
        case 'o': destinationArray = this.game.encounterDiscard; break
        case 'y': destinationArray = this.game.encounterDeck; break
        case 'q': destinationArray = this.game.questDeck; break
        case 'i': destinationArray = this.getDefaultDiscardForCard(card); break
        case 'h': destinationArray = this.player.hand; break
        case 'k': destinationArray = this.player.deck; break
        case 'g': destinationArray = this.game.stagingArea; break
        case 't': destinationArray = this.game.trash; break
        case 'f': this.flipCurrentCard(); return
        case 'r': this.incrementResources(); return
        case 'd': this.incrementDamage(); return
        case 'p': this.incrementProgress(); return
        case 'R': this.decrementResources(); return
        case 'D': this.decrementDamage(); return
        case 'P': this.decrementProgress(); return
        case 'x': this.toggleExhaustCurrentCard(); return
        case 'a': this.handleAttachmentClick(); return
        case 's': this.dealShadowCard(); return
        case 'u': this.shuffleCards(); return
      }
      if (!destinationArray) {
        return
      }
      if (this.games_currentCardSelection.array === this.player.deck) {
        reshuffleArray = this.player.discard
      }
      moveCurrentCard(this, destinationArray, reshuffleArray)
    },
    getDefaultDiscardForCard (card) {
      if (card['owner'] && card['owner'] === 'player1') {
        return this.game['players'][0]['discard']
      }
      if (card['owner'] && card['owner'] === 'player2') {
        return this.game['players'][1]['discard']
      }
      return this.game['encounterDiscard']
    },
    incrementThreat () { mutateProperty(this, this.player, 'threat', 'property', 'incrementProperty') },
    decrementThreat () { mutateProperty(this, this.player, 'threat', 'property', 'decrementProperty') },
    incrementResources () {
      mutateCurrentCard(this, 'resources', 'incrementProperty')
    },
    decrementResources () {
      mutateCurrentCard(this, 'resources', 'decrementProperty')
    },
    incrementProgress () {
      mutateCurrentCard(this, 'progress', 'incrementProperty')
    },
    decrementProgress () {
      mutateCurrentCard(this, 'progress', 'decrementProperty')
    },
    incrementDamage () {
      mutateCurrentCard(this, 'damage', 'incrementProperty')
    },
    decrementDamage () {
      mutateCurrentCard(this, 'damage', 'decrementProperty')
    },
    toggleExhaustCurrentCard () {
      mutateCurrentCard(this, 'exhausted', 'invertProperty')
    },
    shuffleCards () {
      if (!this.games_currentCardSelection['exists']) {
        return
      }
      if (this.games_currentCardSelection['index'] !== undefined) {
        return
      }
      shuffleCards(this, this.games_currentCardSelection['array'])
    },
    dealShadowCard () {
      let card = getCurrentCard(this)
      if (card === null) {
        return
      }
      moveCard(this, this.game['encounterDeck'], undefined, card['attachments'], this.game['encounterDiscard'])
    },
    flipCurrentCard () {
      let card = getCurrentCard(this)
      if (!card) {
        return
      }
      if (!card.flippedImage) {
        return
      }
      mutateCurrentCard(this, 'flipped', 'invertProperty')
    },
    endRound () {
      for (let cardIndex in this.player['characters']) {
        let card = this.player['characters'][cardIndex]
        for (let attachmentIndex in card['attachments']) {
          let attachment = card['attachments'][attachmentIndex]
          mutateCard(this, attachment, 'exhausted', 'setProperty', false)
        }
        mutateCard(this, card, 'exhausted', 'setProperty', false)
        if (card['Type'] === 'Hero') {
          mutateCard(this, card, 'resources', 'incrementProperty')
        }
      }
      for (let cardIndex in this.partner['characters']) {
        let card = this.partner['characters'][cardIndex]
        for (let attachmentIndex in card['attachments']) {
          let attachment = card['attachments'][attachmentIndex]
          mutateCard(this, attachment, 'exhausted', 'setProperty', false)
        }
        mutateCard(this, card, 'exhausted', 'setProperty', false)
        if (card['Type'] === 'Hero') {
          mutateCard(this, card, 'resources', 'incrementProperty')
        }
      }
      moveCard(this, this.player['deck'], undefined, this.player['hand'], this.player['discard'])
      moveCard(this, this.partner['deck'], undefined, this.partner['hand'], this.partner['discard'])
      mutateProperty(this, this.player, 'threat', 'property', 'incrementProperty')
      mutateProperty(this, this.partner, 'threat', 'property', 'incrementProperty')
    },
    handleAttachmentClick () {
      if (this.player['selectedAttachment'].length > 1) {
        throw new Error('Too many selected attachments')
      }
      let card = getCurrentCard(this)
      if (this.player['selectedAttachment'].length === 1) {
        let selectionArray = this.games_currentCardSelection['array']
        if (selectionArray !== this.player['characters'] &&
            selectionArray !== this.player['engagedEnemies'] &&
            selectionArray !== this.partner['characters'] &&
            selectionArray !== this.partner['engagedEnemies'] &&
            selectionArray !== this.partner['engagedEnemies'] &&
            selectionArray !== this.game['stagingArea'] &&
            selectionArray !== this.game['activeLocation']) {
          return
        }
        moveCard(this, this.player['selectedAttachment'], 0, card['attachments'])
      } else {
        if (card['attachments'].length > 0) {
          return
        }
        moveCurrentCard(this, this.player['selectedAttachment'])
      }
    }
  }
}
</script>
