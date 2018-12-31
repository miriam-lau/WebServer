import { Card, CardPile, PileManager } from './card_games'

function DominionGameManager (model) {
  this.model = model
  this.pileManager = new PileManager()

  // Takes in a map of pile names to array of card objects.
  this.initialize = function (data) {
    this.pileManager.reset()
    model.nonSupplyCards = this.convertCardObjectNestedArrayToCards(data['non_supply_cards'])
    model.kingdomCards = this.convertCardObjectNestedArrayToCards(data['kingdom_cards'])
    model.vpCards = this.convertCardObjectNestedArrayToCards(data['vp_cards'])
    model.treasureCards = this.convertCardObjectNestedArrayToCards(data['treasure_cards'])
    model.trash = this.convertCardObjectArrayToCards(data['trash'])
    model.player1Deck = this.convertCardObjectArrayToCards(data['player_1_deck'])
    model.player2Deck = this.convertCardObjectArrayToCards(data['player_2_deck'])
    model.bane = this.convertCardObjectArrayToCards(data['bane'])
    model.hexes = this.convertCardObjectArrayToCards(data['hexes'])
    model.boons = this.convertCardObjectArrayToCards(data['boons'])
    model.sidewaysCards = this.convertCardObjectArrayToCards(data['sideways_cards'])
    let pile = new CardPile()
    let card = new Card("asdf")
    /*
    for (let pileName in pileNamesToCardObjects) {
      let pile = new CardPile()
      let cardObjects = pileNamesToCardObjects[pileName]
      for (let cardIndex in cardObjects) {
        let card = new Card(this.getCardImageForCardObject(cardObjects[cardIndex]))
        pile.addCard(card)
      }
      this.pileManager.addPile(pileName, pile)
    }
    */
  }

  this.convertCardObjectNestedArrayToCards = function (cardArrs) {
    let ret = []
    for (let cardArr in cardArrs) {
      ret.push(this.convertCardObjectArrayToCards(cardArr))
    }
    return ret
  }

  this.convertCardObjectArrayToCards = function (cardObjs) {
    let ret = []
    for (let cardObj in cardObjs) {
      ret.push(this.convertCardObjectToCard(cardObj))
    }
    return ret
  }

  this.convertCardObjectToCard = function (cardObj) {
    return new Card(this.getCardImageForCardObject(cardObj))
  }

  // Static
  this.getCardImageForCardObject = function (card) {
    let imageName = card.set + '_'
    if (card.type !== 'card') {
      imageName += card.type + '_'
    }
    imageName += card.name
    imageName = imageName.toLowerCase()
    imageName = imageName.replace(/[-' /]/g, '')
    imageName = imageName.replace(/\(2nd\)/g, '2')
    imageName = '/static/dominion/card_images/' + imageName + '.jpg'
    return imageName
  }
}

export { DominionGameManager }
