import re
import collections
import time

def validateOnLoad():
   mute()
   if table.isTwoSided(): information(":::WARNING::: This game is NOT designed to be played on a two-sided table. Things will not look right!! Please start a new game and unckeck the appropriate button.")
   for player in getPlayers():
      try: playerVersion = remoteCall(player, 'chkVersions', gameVersion)
      except: 
          playerVersion = "N/A"
      if playerVersion:
          information(":::ERROR::: Player {}'s game version {} is incompatible with your version {}. Make sure all players have compatible version before starting the play!".format(player.name, playerVersion, gameVersion))
   fetchCardScripts()

def chkVersions(version):
   versionNumbers = version.split(".")
   myVersionNumbers = gameVersion.split(".")
   if versionNumbers[0] != myVersionNumbers[0] or versionNumbers[1] != myVersionNumbers[1]: return gameVersion
   return None

def checkDeck(args):
   mute()
   player = args.player
   foundOutfit = False
   if player == me:
      #confirm(str([group.name for group in groups]))
      for group in args.groups:
         if group == me.piles['Play Hand']:
            for card in group:
               if card.Type == 'Outfit': 
                  notify("{} is playing {}".format(player,card.name))
                  foundOutfit = True
            if not foundOutfit: information(":::ERROR::: No outfit card found! Please put an outfit card in your deck before you try to use it in a game!")
         else:
            group.visibility = 'me'
            counts = collections.defaultdict(int)
            ok = True
            for card in group:
               if card.Type == 'Joker': 
                  counts['Jokers'] += 1
                  if counts['Jokers'] > 2:
                     ok = False
                     notify(":::ERROR::: More than 2 Jokers found in{}'s deck!".format(player))
               if card.name == 'Gunslinger' or card.name == 'Nature Spirit' or card.name == 'Ancestor Spirit':
                  ok = False
                  notify(":::ERROR::: Token card found in {}'s deck!".format(player))
               counts[card.name] += 1
               if counts[card.name] > 4: 
                  ok = False
                  notify(":::ERROR::: More than 4 cards of the same name ({}) found in {}'s deck!".format(card.name,player))
               counts[card.Rank + card.Suit] += 1
               if counts[card.Rank + card.Suit] > 4: 
                  ok = False
                  notify(":::ERROR::: More than 4 cards of the same suit and rank ({} of {}) found in {}'s deck!".format(card.Rank,card.Suit,player))
            deckLen = len(group) + len([c for c in me.piles['Play Hand'] if (c.Type != 'Outfit' and c.Type != 'Legend')]) - counts['Jokers']
            if deckLen != 52:
               ok = False
               notify(":::ERROR::: {}'s deck is not exactly 52 play cards ({})!".format(player,deckLen))
            group.visibility = 'None'
            if ok: notify("-> Deck of {} is OK!".format(player))
            else: 
               notify("-> Deck of {} is _NOT_ OK!".format(player))
               information("We have found illegal cards in your deck. Please load a legal deck!")
   # WiP Checking deck legality. 

def chkClickedCard(args):
   card = args.card
   mouseButton = args.mouseButton
   keysDown = args.keysDown
   debugNotify("card: {}, mouseButton: {}, keysDown: {}".format(card,mouseButton,keysDown))
   mute()
   if card.group != table: return
   if len(keysDown) == 1 and (keysDown[0] == "LeftAlt" or keysDown[0] == "RightAlt"):
       if card.model == "554d7494-0000-43fa-8a40-a960ec32a69e":
           # Putting here try catch blok in case update for card selection is not in this OCTGN client version 
           # TODO should be removed once the selection update is available
           try: clearSelection()
           except: debugNotify("::WARNING:: This version of OCTGN client does not support clearing of the selection!")
           card.select()
           ootDeeds = getCardsFromProperties(card, 'ootDeeds')
           for deed in ootDeeds:
               highlightLocation(deed, False)
       else: 
           highlightLocation(card)
   elif len(keysDown) == 2 and ("LeftAlt" in keysDown or "RightAlt" in keysDown) and ("LeftShift" in keysDown or "RightShift" in keysDown):
       if card == TownSquareToken or card.Type == 'Deed' or card.Type == 'Outfit':
           showAdjacentLocations(card)
   
def chooseSide(silent = False): # Called from many functions to check if the player has chosen a side for this game.
   mute()
   global playerside, playeraxis
   plCount = 0
   for player in sorted(getPlayers()):
      if len(player.Deck) == 0 and len(player.piles['Discard Pile']) == 0: continue # We ignore spectators
      plCount += 1
      if player != me: continue # We only set our own side
      if plCount == 1: # First player is on the right
         playeraxis = Xaxis
         playerside = 1
         if not silent: notify(":> {}'s gang arrives on the west side of town.".format(me))
      elif plCount == 2: # First player is on the left
         playeraxis = Xaxis
         playerside = -1
         if not silent: notify(":> {}' dudes scout warily from the east.".format(me))
      elif plCount == 3: # Third player is on the bottom
         playeraxis = Yaxis
         playerside = 1
         if not silent: notify(":> {}' outfit sets up on the south entrance.".format(me))
      elif plCount == 4: # Fourth player is on the top
         playeraxis = Yaxis
         playerside = -1
         if not silent: notify(":> {}'s posse claims the north entrance.".format(me))
      else:
         playeraxis = None  # Fifth and upward players are unaligned
         playerside = 0
         if not silent: notify(":> {}' arrive late to the party.".format(me))

def checkMovedCards(args):
   for iter in range(len(args.cards)):
      card = args.cards[iter]
      fromGroup = args.fromGroups[iter]
      toGroup = args.toGroups[iter]
      highlight = args.highlights[iter]
      #if isScriptMove: return # If the card move happened via a script, then all automations should have happened already.
      if fromGroup == me.piles['Play Hand'] and toGroup == table: 
         if card.Type == 'Outfit': 
            card.moveTo(me.piles['Play Hand'])
            update()
            setup(group = table)       
         else: playcard(card, retainPos = True)   
      elif fromGroup == me.Deck and toGroup == table and card.owner == me: # If the player moves a card into the table from their Deck we assume they are revealing it as a pull or draw hand replacement.
         card.highlight = DrawHandColor
         notify("{} reveals a {} of {}".format(me,fullrank(card.Rank), fullsuit(card.Suit)))
      elif fromGroup != table and toGroup == table and card.owner == me: # If the player moves a card into the table from Hand, or Trash, we assume they are installing it for free.
         reCalculate(notification = 'silent')
         if card.Type == 'Goods' or card.Type == 'Spell':
            hostCard = findHost(card)
            if hostCard: 
               attachCard(card,hostCard)
               notify(":> {} was attached to {}".format(card,hostCard))
      elif fromGroup == table and toGroup != table and card.owner == me: # If the player dragged a card manually from the table to their discard pile...
         clearAttachLinks(card) # If the card was manually removed from play then we simply take care of any attachments
         if card.type == 'Deed': clearDeedFromLocations(card)
         if card.type == 'Dude': removeDudeFromLocation(card, updateDude = True)
         reCalculate(notification = 'silent')
      elif fromGroup == table and toGroup == table and card.controller == me: # If the player dragged a card manually to a different location on the table, we want to re-arrange the attachments
         if card.Type == 'Dude':
             for c in table:
                 if c.Type == 'Deed' or c.Type == 'Outfit' or c == TownSquareToken:
                     cardx, cardy = card.position
                     if card.orientation == Rot90:
                         finaly = cardy + card.height - (card.width / 2)
                         finalx = cardx + (card.height / 2)
                     else:
                         finaly = cardy + (card.height / 2)
                         finalx = cardx + (card.width / 2)
                     cx, cy = c.position
                     if finalx > cx and finalx < cx + c.width and finaly > cy and finaly < cy + c.height:
                         if c == getDudeLocation(card): continue
                         if confirm("Do you want to move {} to location {}?".format(card.name, c.name)):
                             move(card, targetCards = [c])
                             break
                         else: card.moveToTable(args.xs[iter], args.ys[iter])
         if card.Type == 'Dude' or card.Type == 'Deed' or card.Type == 'Outfit': 
             update()
             orgAttachments(card) 

def chkControllerChanged(args):
    if args.card.Type == 'Deed' or args.card.Type == 'Dude':
        reCalculate(notification = 'silent', checkDeeds = False)

def chkMarkerChanges(args):
   mute()
   #notify(markerName) #debug
   #return # Not in use yet
   if args.scripted: return # If the marker change happened via a script, then all automations should have happened already.
   reCalculate(notification = 'silent')
   #if markerName == "+1 Influence": modInfluence(-1)
   #if markerName == "-1 Influence" and num(card.Influence) > card.markers[mdict['InfluenceMinus']]: modInfluence()
   #if markerName == "+1 Control": modControl(-1)
   #if markerName == "-1 Control" and num(card.Influence) > card.markers[mdict['ControlMinus']]: modControl()   
     
def checkPlayerGlobalVars(args):
   mute()
   if args.name == 'RevealReady' and me._id == 1 and args.value != 'False': checkHandReveal(args.player) # Only the hosting player reveals hands
   if args.name == 'Hand Rank' and me._id == 1 and args.value != 'N/A': compareHandRanks() # Only the hosting player reveals hands

def checkHandReveal(playerVar):           
   playersReady = []
   if getGlobalVariable('Shootout') == 'True': # If it's a shootout, we only care to see if that player's opponent is ready.
      for player in getActivePlayers():
         if player.getGlobalVariable('RevealReady') == 'Shootout': playersReady.append(player)
         if len(playersReady) == 2: break
      if len(playersReady) < 2 and len(getPlayers()) != 1:
         notify("{} is ready to reveal their shootout hand. Waiting for their opponent...".format(playerVar))
      else:
         for player in playersReady:
            remoteCall(player,'revealShootoutHand',[player.piles['Draw Hand'],True,False])
   else:
      for player in getActivePlayers():
         if player.getGlobalVariable('RevealReady') != 'False': playersReady.append(player)
      if len(playersReady) < len(getActivePlayers()):
         notify("{} is ready to reveal their lowball hand. Waiting for everyone else...".format(playerVar))
      else:
         for player in playersReady:
            remoteCall(player,'revealLowballHand',[player.piles['Draw Hand'],True,False])
   
def compareHandRanks():
   if getGlobalVariable('Shootout') == 'True': 
      competingPlayers = []
      for player in getActivePlayers():
         if player.getGlobalVariable('Hand Rank') != 'N/A': competingPlayers.append(player)
         if len(competingPlayers) == 2: break
      if len(competingPlayers) == 2: 
         handRankDiff = num(competingPlayers[0].getGlobalVariable('Hand Rank')) - num(competingPlayers[1].getGlobalVariable('Hand Rank'))
         if handRankDiff < 0: 
            notify("\n-- The winner is {} by {} ranks and {} must absorb as many casualties in this round.".format(competingPlayers[1], abs(handRankDiff), competingPlayers[0]))
         elif handRankDiff > 0: 
            notify("\n-- The winner is {} by {} ranks and {} must absorb as many casualties in this round.".format(competingPlayers[0], abs(handRankDiff), competingPlayers[1]))
         else: 
            notify ("\n-- The Shootout is a tie. Both player suffer one casualty")
         if competingPlayers[1] == me: autoscriptOtherPlayers('HandRevealed', count = handRankDiff * -1)
         else: autoscriptOtherPlayers('HandRevealed', count = handRankDiff)
         clearHandRanks()
   else:
      winner = findLowballWinner()
      if winner == 'tie': notify ("\n-- It's a tie! Y'all need to compare high cards to determine the lucky bastard. (Winner needs to press Ctrl+W)")
      else: # Otherwise the evuation will fail which means that the winner variable holds is a player class.
         notify ("\n-- The winner is {}. (They need to press Ctrl+W once the resolution phase has ended.)".format(winner)) # Thus we can just announce them.
   
def reconnect(group = table, x=0, y=0):
   global OutfitCard
   chooseSide(True)
   for card in table:
      if card.owner == me and card.Type == 'Outfit': 
         OutfitCard = card
   fetchCardScripts()
   barNotifyAll('#990000','{} has reconnected to the game'.format(me.name))