    # generic.py
import re

def calcStringLabelSize(STRING): 
# A function which returns a slowly expansing size for a label. The more characters, the more the width expands to allow more characters on the same line.
   newlines = 0
   for char in STRING:
      if char == '\n': newlines += 1
   STRINGwidth = 200 + (len(STRING) / 4)
   STRINGheight = 30 + ((20 - newlines) * newlines) + (30 * (STRINGwidth / 100))
   return (STRINGwidth, STRINGheight)
 
def calcStringButtonHeight(STRING): 
# A function which returns a slowly expansing size for a label. The more characters, the more the width expands to allow more characters on the same line.
   newlines = 0
   for char in STRING:
      if char == '\n': newlines += 1
   STRINGheight = 30 + (8 * newlines) + (8 * (len(STRING) / 20))
   return STRINGheight
   
def formStringEscape(STRING): # A function to escape some characters that are not otherwise displayed by WinForms, like amperasands '&'
   slist = list(STRING)
   escapedString = ''
   for s in slist:
      if s == '&': char = '&&'
      else: char = s
      escapedString += char
   return escapedString

def information(Message):
   debugNotify(">>> information() with message: {}".format(Message))
   if Automations['WinForms']:
      Application.EnableVisualStyles()
      form = OKWindow(Message)
      form.BringToFront()
      showWinForm(form)
   else: 
      confirm(Message)
   
def SingleChoice(title, options, type = 'button', default = 0, cancelButton = True, cancelName = 'Cancel'):
   debugNotify(">>> SingleChoice() title={}".format(title))
   ### Old WinForms code is (hopefully) obsolete now
   # if Automations['WinForms']:
      # optChunks=[options[x:x+7] for x in xrange(0, len(options), 7)]
      # optCurrent = 0
      # choice = "New"
      # while choice == "New" or choice == "Next Page" or (not choice and not cancelButton):
         # Application.EnableVisualStyles()
         # form = SingleChoiceWindow(title, optChunks[optCurrent], type, default, pages = len(optChunks), cancelButtonBool = cancelButton, cancelName = cancelName)
         # form.BringToFront()
         # showWinForm(form)
         # choice = form.getIndex()
         # debugNotify("choice is: {}".format(choice), 2)
         # if choice == "Next Page": 
            # debugNotify("Going to next page", 3)
            # optCurrent += 1
            # if optCurrent >= len(optChunks): optCurrent = 0
         # elif choice != None: 
            # choice = num(form.getIndex()) + (optCurrent * 7) # if the choice is not a next page, then we convert it to an integer and give that back, adding 8 per number of page passed
   # else:
   choice = "New"
   if cancelButton: customButtonsList = [cancelName]
   else: customButtonsList = []
   while choice == "New" or (choice == None and not cancelButton):
      choice = askChoice(title, options, customButtons = customButtonsList)
      debugNotify("choice is: {}".format(choice), 2)
      if choice > 0: choice -= 1 # Reducing by 1 because askChoice() starts from 1 but my code expects to start from 0
      elif choice <= 0: choice = None
   debugNotify("<<< SingleChoice() with return {}".format(choice), 3)
   return choice
 
def multiChoice(title, options): # This displays a choice where the player can select more than one ability to trigger serially one after the other
   debugNotify(">>> multiChoice() title={}".format(title))
   if Automations['WinForms']: # If the player has not disabled the custom WinForms, we use those
      optChunks=[options[x:x+7] for x in range(0, len(options), 7)]
      optCurrent = 0
      choices = "New"
      currChoices = []
      while choices == "New" or choices == "Next Page":
         Application.EnableVisualStyles() # To make the window look like all other windows in the user's system
         CPType = 'Control Panel'
         debugNotify("About to open form")
         if choices == "Next Page": nextPageBool = True
         else: nextPageBool = False
         form = MultiChoiceWindow(title, optChunks[optCurrent], CPType, pages = len(optChunks), currPage = optCurrent, existingChoices = currChoices) # We create an object called "form" which contains an instance of the MultiChoice windows form.
         showWinForm(form) # We bring the form to the front to allow the user to make their choices
         choices = form.getIndex() # Once the form is closed, we check an internal variable within the form object to grab what choices they made
         debugNotify("choices = {}".format(choices))
         if choices == "Next Page": 
            debugNotify("Going to next page", 4)
            optCurrent += 1
            if optCurrent >= len(optChunks): optCurrent = 0
            currChoices = form.getStoredChoices()
            debugNotify("currChoices = {}".format(currChoices))
   else: # If the user has disabled the windows forms, we use instead the OCTGN built-in askInteger function
      concatTXT = title + "\n\n(Tip: You can put multiple abilities one after the the other (e.g. '110'). Max 9 at once)\n\n" # We prepare the text of the window with a concat string
      for iter in range(len(options)): # We populate the concat string with the options
         concatTXT += '{}:--> {}\n'.format(iter,options[iter])
      choicesInteger = askInteger(concatTXT,0) # We now ask the user to put in an integer.
      if choicesInteger == None: choices = 'ABORT' # If the user just close the window, abort.
      else: 
         choices = list(str(choicesInteger)) # We convert our number into a list of numeric chars
         for iter in range(len(choices)): choices[iter] = int(choices[iter]) # we convert our list of chars into a list of integers      
   debugNotify("<<< multiChoice() with list: {}".format(choices), 3)
   return choices # We finally return a list of integers to the previous function. Those will in turn be iterated one-by-one serially.

def askCardsFromList(cards, text = None, title = None, min = 1, max = 1, bottomList = None, bottomLabel = None):
    dialog = cardDlg(cards, bottomList)
    dialog.min = min
    dialog.max = max
    if title: dialog.title = title
    if text: dialog.text = text
    if bottomLabel: dialog.text = text
    return dialog.show()

def askCardFromList(cards, text = None, title = None):
    dialog = cardDlg(cards)
    dialog.min = 1
    dialog.max = 1
    if title: dialog.title = title
    if text: dialog.text = text
    resultCards = dialog.show()
    if resultCards!= None and len(resultCards) > 0: return resultCards[0]
      
#---------------------------------------------------------------------------
# General functions
#---------------------------------------------------------------------------
            
def num (s): 
# This function reads the value of a card and returns an integer. For some reason integer values of cards are not processed correctly
# see bug 373 https://octgn.16bugs.com/projects/3602/bugs/188805
# This function will also return 0 if a non-integer or an empty value is provided to it as it is required to avoid crashing your functions.
#   if s == '+*' or s == '*': return 0
   if not s: return 0
   try:
      return int(s)
   except ValueError:
      return 0

def defPlayerColor(): # Obsolete in OCTGN 3 but leaving it here in case I find another use for it.
# Provide a random highlight colour for the player which we use to simulate ownership
   global PlayerColor
   if len(PlayerColor) == 7 : return
   RGB = ["0","1","2","3","4","5","6","7","8","9","a","b","c","d","e","f"]
   for i in range(6): PlayerColor += RGB[rnd(0,15)]

def debugNotify(msg = 'Debug Ping!', level = 1):
   if not re.search(r'<<<',msg) and not re.search(r'>>>',msg):
      hashes = '#' 
      for iter in range(level): hashes += '#' # We add extra hashes at the start of debug messages equal to the level of the debug+1, to make them stand out more
      msg = hashes + ' ' +  msg
   if re.search(r'<<<',msg): level = 3 # We always request level debug logs to display function exist notifications.
   if debugVerbosity >= level: notify(msg)

def barNotifyAll(color, msg, remote = False): # A function that takes care to send barNotifyAll() messages to all players
   mute()
   for player in getPlayers():
      if player != me and not remote: remoteCall(player,'barNotifyAll',[color,msg,True])
   notifyBar(color,msg)
      
def delayed_whisper(text): # Because whispers for some reason execute before notifys
   rnd(1,10)
   whisper(text)

def numOrder(num):
    """Return the ordinal for each place in a zero-indexed list.

    list[0] (the first item) returns '1st', list[1] return '2nd', etc.
    """
    def int_to_ordinal(i):
        """Return the ordinal for an integer."""
        # if i is a teen (e.g. 14, 113, 2517), append 'th'
        if 10 <= i % 100 < 20:
            return str(i) + 'th'
        # elseif i ends in 1, 2 or 3 append 'st', 'nd' or 'rd'
        # otherwise append 'th'
        else:
            return  str(i) + {1 : 'st', 2 : 'nd', 3 : 'rd'}.get(i % 10, "th")
    return int_to_ordinal(num + 1)

def findMarker(card, markerDesc): # Goes through the markers on the card and looks if one exist with a specific description
   if debugVerbosity >= 1: notify(">>> findMarker(){}".format(extraASDebug())) #Debug
   foundKey = None
   if markerDesc in mdict: markerDesc = mdict[markerDesc][0] # If the marker description is the code of a known marker, then we need to grab the actual name of that.
   for key in card.markers:
      debugNotify("### Key: {}\nmarkerDesc: {}".format(key[0],markerDesc)) # Debug
      if re.search(r'{}'.format(markerDesc.replace('+','\+')),key[0]) or markerDesc == key[0]: # We need to replace any '+' in the marker names to escaped \+ otherwise the regex statement gets confused
         foundKey = key
         if debugVerbosity >= 2: notify("### Found {} on {}".format(key[0],card))
         break
   if debugVerbosity >= 3: notify("<<< findMarker() by returning: {}".format(foundKey))
   return foundKey
      
def getActivePlayers():
   return [player for player in getPlayers() if len(player.Deck) > 0 or len(player.piles['Discard Pile']) > 0 or len(player.piles['Play Hand']) > 0]
   
def claimCard(card, player = me): # Requests the controller of a card to pass control to another player (script runner by default)
   debugNotify("Player {}({}) is claiming card {} from controller {}({}).".format(player, player._id, card, card.controller, card.controller._id)) 
   if card.controller == me:
       giveCard(card, player)
   elif card.controller != player: # If the card is already ours, we do not need to do anything.
      prevController = card.controller
      remoteCall(card.controller,'giveCard', [card,player])
      notify("Controller of card {} has been changed from {} to {}.".format(card, prevController, player))
   
def giveCard(card,player,pile = None): # Passes control of a card to a given player.
   mute()
   if card.group == table: 
      prevController = card.controller
      card.controller = player
      autoscriptOtherPlayers('{}:CardTakeover:{}'.format(player,prevController),card)
   else: 
      if pile: card.moveTo(pile) # If we pass a pile variable, it means we likely want to return the card to its original location (say after an aborted capture)
      else: card.moveTo(player.ScriptingPile)
      # If the card is in one of our piles, we cannot pass control to another player since we control the whole pile. We need to move it to their scripting pile. 
      # This should automatically also pass control to the controller of that pile
   update()

def passPileControl(pile,player):
   mute()
   update()
   pile.controller = player
   
def fetchHost(card):
   host = None
   hostCards = eval(getGlobalVariable('Host Cards'))
   hostID = hostCards.get(card._id,None)
   if hostID: host = Card(hostID) 
   return host

def fetchAttachments(card):
   hostCards = eval(getGlobalVariable('Host Cards'))
   return [Card(att_id) for att_id in hostCards if hostCards[att_id] == card._id]

def getCardsFromProperties(card, propertyName):
   propertyCardsStr = card.properties[propertyName]
   debugNotify("{} property for card {}: {}".format(propertyName, card, propertyCardsStr))
   if propertyCardsStr == None or propertyCardsStr == '': return []
   cardIds = propertyCardsStr.split('|')
   resultCards = [Card(eval(cardId)) for cardId in cardIds]   
   return resultCards

def getCardsControlledByMe(card, propertyName):
   cards = getCardsFromProperties(card, propertyName)
   mineCards = [card for card in cards if card.controller == me]
   return mineCards

def addIdToCardProperty(card, cardId, propertyName):
   propertyStr = card.properties[propertyName]
   if propertyStr == None or propertyStr == '':
      card.properties[propertyName] = str(cardId)
      return
   card.properties[propertyName] = "{}|{}".format(propertyStr, cardId)
   debugNotify("Card id {} added to property {} of card {}".format(cardId, propertyName, card))

def numOfCardIdsInProperty(card, propertyName):
   propertyStr = card.properties[propertyName]
   cardIds = propertyStr.split('|')
   return len(cardIds)

def removeIdFromCardProperty(card, cardId, propertyName):
   propertyStr = card.properties[propertyName]
   cardIds = propertyStr.split('|')
   if str(cardId) in cardIds: cardIds.remove(str(cardId))
   else: return
   if len(cardIds) == 0:
       card.properties[propertyName] = ""
       return
   newPropertyStr = cardIds[0]
   for newCardId in cardIds[1:]:
       newPropertyStr += "|{}".format(newCardId)
   card.properties[propertyName] = newPropertyStr
   debugNotify("Card id {} removed from property {} of card {}".format(cardId, propertyName, card))

def insertIdToCardProperty(card, cardId, cardIdToInsert, propertyName):
   propertyStr = card.properties[propertyName]
   cardIds = propertyStr.split('|')
   if str(cardId) in cardIds: 
       index = cardIds.index(str(cardId))
       if index == len(cardIds) - 1: cardIds.append(str(cardIdToInsert))
       else: cardIds.insert(index + 1, str(cardIdToInsert))
   else: return
   newPropertyStr = cardIds[0]
   for newCardId in cardIds[1:]:
       newPropertyStr += "|{}".format(newCardId)
   card.properties[propertyName] = newPropertyStr
   debugNotify("Card id {} inserted after id {} in property {} of card {}".format(cardIdToInsert, cardId, propertyName, card))

def posseBulletsTotal(player = None):
   totalBullets = 0
   for c in table:
      if (c.highlight == AttackColor or c.highlight == DefendColor) and (c.controller == player or (not player and c.controller != me)):
          totalBullets += compileCardStat(c, 'Bullets')
   return totalBullets
         
#---------------------------------------------------------------------------
# Card Placement functions
#---------------------------------------------------------------------------

def cwidth(card = None, divisor = 10):
#if debugVerbosity >= 1: notify(">>> cwidth(){}".format(extraASDebug())) #Debug
# This function is used to always return the width of the card plus an offset that is based on the percentage of the width of the card used.
# The smaller the number given, the less the card is divided into pieces and thus the larger the offset added.
# For example if a card is 80px wide, a divisor of 4 will means that we will offset the card's size by 80/4 = 20.
# In other words, we will return 1 + 1/4 of the card width. 
# Thus, no matter what the size of the table and cards becomes, the distances used will be relatively the same.
# The default is to return an offset equal to 1/10 of the card width. A divisor of 0 means no offset.
   if divisor == 0: offset = 0
   else: offset = CardWidth / divisor
   return (CardWidth + offset)

def cheight(card = None, divisor = 10):
   #if debugVerbosity >= 1: notify(">>> cheight(){}".format(extraASDebug())) #Debug
   if divisor == 0: offset = 0
   else: offset = CardHeight / divisor
   return (CardHeight + offset)

def placeCard(card,type = None, dudecount = 0, destination = None):
# This function automatically places a card on the table according to what type of card is being placed
# It is called by one of the various custom types and each type has a different value depending on if the player is on the X or Y axis.
   global posSideCount, negSideCount, OutOfTownToken
   if playeraxis == Xaxis:
      if type == 'HireDude' or (type == None and card.Type == 'Dude'):
         # TODO M2 check other dudes that can go to other locations (or use script?)
         dudecount = len(getDudesAtLocation(OutfitCard))
         # Move the dude next to where we expect the player's home card to be.
         card.moveToTable(homeDistance(card) + cardDistance(card) + playerside * (dudecount * cwidth(card)), 0)
         addDudeToLocation(OutfitCard, card)
      if type == 'PlaceDeed' or type == 'OrganizeDeed' or (type == None and card.Type == 'Deed'):
         if re.search('Out of Town', card.Keywords): # Check if we're bringing out an out of town deed
            ootDeeds = getCardsFromProperties(OutOfTownToken, 'ootDeeds')
            if ootDeeds: numOotDeeds = len(ootDeeds)
            else: numOotDeeds = 0
            if not card in ootDeeds: addIdToCardProperty(OutOfTownToken, card._id, 'ootDeeds')
            ootX, ootY = OutOfTownToken.position
            card.moveToTable(ootX + 10 + (5 + cwidth(card) * numOotDeeds), ootY + 10 * playerside)
         else:
            if type == 'OrganizeDeed':
                if findDeedOnStreet(card, 'Above') != None: choice = 1
                elif findDeedOnStreet(card, 'Below') != None: choice = 2
            else:
                # If it's a city deed, then ask the player where they want it.
                choice = askChoice("Where do you want to place deed {}?".format(card.name), choices = ["Above","Below"])
            if choice == 2: 
               negSideCount += 1 #If it's on the bottom, increment the counter...
               if type != 'OrganizeDeed': addIdToCardProperty(OutfitCard, card._id, 'Below')
               card.moveToTable(homeDistance(card), negSideCount * cheight(card)) # ...and put the deed below all other deeds already there.
            else:
               posSideCount += 1 # Same as above but going upwards from home.
               if type != 'OrganizeDeed': addIdToCardProperty(OutfitCard, card._id, 'Above')
               card.moveToTable(homeDistance(card), -1 * (posSideCount * cheight(card)))     
         if type == "OrganizeDeed": organizeLocation(card)
      if type == 'SetupHome':
         card.moveToTable(homeDistance(card), 0) # We move it to one side depending on what side the player chose.
      if type == 'SetupDude':
         card.moveToTable(homeDistance(card) + cardDistance(card) + playerside * (dudecount * cwidth(card)), 0) 
         addDudeToLocation(OutfitCard, card)
         # We move them behind the house
      if type == 'SetupOther':
         card.moveToTable(playerside * (cwidth(card,4) * 3), playerside * -1 * cheight(card)) # We move the card around the player's area.      
      if type == 'MoveDude':
         destX, destY = destination.position
         if re.search('Out of Town', destination.Keywords):
             card.moveToTable(destX, destY - playerside * (5 - destination.height) * (dudecount + 1)) # Place your dudes below out of town deeds
         elif destination.model == "ac0b08ed-8f78-4cff-a63b-fa1010878af9":
             tsCards = getCardsControlledByMe(destination, 'Occupants')
             if tsCards and len(tsCards) > 0:
                 botX, botY = tsCards[0].position
                 for tsCard in tsCards[1:]:
                     x, y = tsCard.position
                     if y > botY: 
                         botX = x
                         botY = y
                 botY += cheight(card) + 2
             else:
                 botX = destX + 2
                 botY = destY + 2
                 if playerside == 1: botX = destX + destination.width - cwidth(card) - 2
             card.moveToTable(botX, botY) # Place your dudes below out of town deeds
         else:
             card.moveToTable(destX + playerside * ((dudecount + 1) * cwidth(card) + 2), destY) # We move the card around the player's area. 

   elif playeraxis == Yaxis:
      # TODO M2 The Y player axis placement should be updated
      if type == 'HireDude' or (type == None and card.Type == 'Dude'):# Hire dudes on your home + one card height - 20% of a card height
         card.moveToTable(0,homeDistance(card) + (playerside * cheight(card,-4)))
      if type == 'PlaceDeed' or (type == None and card.Type == 'Deed'): 
         if re.search('Out of Town', card.Keywords): # Check if we're bringing out an out of town deed
            ootDeeds = getCardsFromProperties(OutOfTownToken, 'ootDeeds')
            if ootDeeds: numOotDeeds = len(ootDeeds)
            else: numOotDeeds = 0
            if not card in ootDeeds: addIdToCardProperty(OutOfTownToken, card._id, 'ootDeeds')
            ootX, ootY = OutOfTownToken.position
            card.moveToTable((playerside * cwidth(card,4) * 5) + numOotDeeds * cwidth(card) * playerside, homeDistance(card) + cardDistance(card))
         else:
            if confirm("Do you want to place this deed on the right side of your street?"): # If it's a city deed, then ask the player where they want it.
               negSideCount += 1 #If it's on the right, increment the counter...
               card.moveToTable(negSideCount * cwidth(card),homeDistance(card)) # ...and put the deed below all other deeds already there.
            else:
               posSideCount += 1 # Same as above but going leftwards from home.
               card.moveToTable(-1 * (posSideCount * cwidth(card)),homeDistance(card))       
      if type == 'SetupHome':
         card.moveToTable(0,homeDistance(card)) 
      if type == 'SetupDude': # Setup your dudes one card height behind your home and in a horizontal line
         card.moveToTable(-cwidth(card) + (dudecount * cwidth(card)),homeDistance(card) + cardDistance(card)) 
      if type == 'SetupOther':
         card.moveToTable(playerside * -3 * cwidth(card), playerside * (cheight(card,4) * 3)) 
   else: card.moveToTable(0,0)
   
def homeDistance(card = None):
# This function retusn the distance from the middle each player's home will be setup towards their playerSide. 
# This makes the code more readable and allows me to tweak these values from one place
   if playeraxis == Xaxis:
      return (playerside * cwidth() * 5) # players on the X axis, are placed 5 times a card's width towards their side (left or right)
   elif playeraxis == Yaxis:
      return (playerside * cheight() * 3) # players on the Y axis, are placed 3 times a card's height towards their side (top or bottom)

def cardDistance(card = None):
# This function returns the size of the card towards a player's side. 
# This is useful when playing cards on the table, as you can always manipulate the location
#   by multiples of the card distance towards your side
# So for example, if a player is playing on the bottom side. This function will always return a positive cardheight.
#   Thus by adding this in a moveToTable's y integer, the card being placed will be moved towards your side by one multiple of card height
#   While if you remove it from the y integer, the card being placed will be moved towards the centre of the table by one multiple of card height.
   if playeraxis == Yaxis:
      return (playerside * cheight())
   else:
      return (playerside * cwidth())

#------------------------------------------------------------------------------
# Remote Calls
#------------------------------------------------------------------------------
      
def delCard(card,wait = False):
   mute()
   if card.controller == me:
      removeDudeFromLocation(card)
      card.delete()
   else: 
      remoteCall(card.controller,"delCard",[card])
      if wait:
         count = 0
         try: # We need to do a try/except, because if the card has been deleted, then it won't have a group class to check.
            while card.group == table: # This is then only way to check if the card has been deleted yet.
               rnd(1,10)
               count += 1
               if count == 10: break
         except: pass # This means the card has been deleted.
      
def setPlayerVariable(var,value):
   mute()
   me.setGlobalVariable(var,value)

def areDeedsOrOutfit(card, x = 0, y = 0, silent = False, forced =  None):
    for checkCard in card:
        if checkCard.type != 'Deed' and checkCard.type != 'Outfit': return False
    return True

def areDudes(card, x = 0, y = 0, silent = False, forced =  None):
    for checkCard in card:
        if checkCard.type != 'Dude': return False
    return True

def isPlayable(card, x = 0, y = 0, silent = False, forced =  None):
    for checkCard in card:
        if checkCard.type == 'Token': return False
    return True

def isOrganizable(card, x = 0, y = 0, silent = False, forced =  None):
    for checkCard in card:
        if checkCard.type != 'Deed' and checkCard.type != 'Outfit' and checkCard != OutOfTownToken: return False
    return True

def checkSmartAction(card, x = 0, y = 0, silent = False, forced =  None):
    for checkCard in card:
        if checkCard.type == 'Token' and checkCard.model != 'c421c742-c920-4cad-9f72-032c3378191e': # If the player has double-clicked the Town Square card or other token, we assume it's a mistake
            return False
    return True