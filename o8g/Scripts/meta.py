    # Python Scripts for the Doomtown  CCG definition for OCTGN
    # Copyright (C) 2013  Konstantine Thoukydides

    # This python script is free software: you can redistribute it and/or modify
    # it under the terms of the GNU General Public License as published by
    # the Free Software Foundation, either version 3 of the License, or
    # (at your option) any later version.

    # This program is distributed in the hope that it will be useful,
    # but WITHOUT ANY WARRANTY; without even the implied warranty of
    # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    # GNU General Public License for more details.

    # You should have received a copy of the GNU General Public License
    # along with this script.  If not, see <http://www.gnu.org/licenses/>.


import re, time

debugVerbosity = -1 # At -1, means no debugging messages display

Automations = {'Play'                   : True, # If True, game will automatically trigger card effects when playing or double-clicking on cards. Requires specific preparation in the sets.
               'Triggers'               : True, # If True, game will search the table for triggers based on player's actions, such as installing a card, or discarding one.
               'WinForms'               : True, # If True, game will use the custom Windows Forms for displaying multiple-choice menus and information pop-ups
               'Placement'              : True, # If True, game will try to auto-place cards on the table after you paid for them.
               'Start/End-of-Turn/Phase': True # If True, game will automatically trigger effects happening at the start of the player's turn, from cards they control.                
              }                  
                  

CardsAA = {} # Dictionary holding all the AutoAction scripts for all cards
CardsAS = {} # Dictionary holding all the autoScript scripts for all cards
Stored_Keywords = {} # A Dictionary holding all the Keywords a card has.
costReducers = []
costIncreasers = []
               
#---------------------------------------------------------------------------
# Misc
#---------------------------------------------------------------------------
               
def resetAll(): # Clears all the global variables in order to start a new game.
   # Import all our global variables and reset them.
   global playerside, strikeCount, posSideCount, negSideCount, handsize
   global harrowedDudes, ValueMemory, debugVerbosity
   debugNotify(">>> resetAll()") #Debug   
   setGlobalVariable('Shootout','False')
   me.setGlobalVariable('playerOutfit','None')
   #playerside = None
   strikeCount = 0
   posSideCount = 0
   negSideCount = 0
   handsize = 5
   me.GhostRock = 0 # Wipe the counters
   me.Influence = 0
   me.Control = 0
   me.VictoryPoints = 0
   #me.HandRank = 0
   me.setGlobalVariable('Hand Rank','N/A')
   harrowedDudes.clear()
   ValueMemory.clear()
   hostCards = eval(getGlobalVariable('Host Cards'))
   hostCards.clear()
   setGlobalVariable('Host Cards',str(hostCards))
   setGlobalVariable('Mark','None')
   setGlobalVariable('Shootout','False')
   if debugVerbosity != -1 and confirm("Reset Debug Verbosity?"): debugVerbosity = -1
   debugNotify("<<< resetAll()") #Debug   

def chkHighNoon():
   if getGlobalVariable('Phase') != '3' and confirm(":::WARNING::: You are normally only allowed to take this action during High Noon.\n\nDo you want to jump to High Noon now?"): goToHighNoon()
   
def chkDummy(Autoscript, card): # Checks if a card's effect is only supposed to be triggered for a (non) Dummy card
   if debugVerbosity >= 4: notify(">>> chkDummy()") #Debug
   if re.search(r'onlyforDummy',Autoscript) and card.highlight != DummyColor: return False
   if re.search(r'excludeDummy', Autoscript) and card.highlight == DummyColor: return False
   return True

def storeSpecial(card): 
# Function stores into a shared variable some special cards that other players might look up.
   debugNotify(">>> storeSpecial(){}".format(extraASDebug())) #Debug
   specialCards = eval(me.getGlobalVariable('specialCards'))
   specialCards[card.Type] = card._id
   me.setGlobalVariable('specialCards', str(specialCards))
   
def getSpecial(cardType,player = me):
# Functions takes as argument the name of a special card, and the player to whom it belongs, and returns the card object.
   debugNotify(">>> getSpecial(){}".format(extraASDebug())) #Debug
   specialCards = eval(player.getGlobalVariable('specialCards'))
   debugNotify("<<< getSpecial() by returning: {}".format(Card(specialCards[cardType])))
   return Card(specialCards[cardType])

def ofwhom(Autoscript, controller = me, multiText = None): 
   debugNotify(">>> ofwhom(){}".format(extraASDebug(Autoscript))) #Debug
   targetPLs = []
   playerList = []
   if re.search(r'o[fn]Opponent', Autoscript) or re.search(r'o[fn]AllOpponents', Autoscript):
      if not multiText: multiText = "Choose which opponent you're targeting with this effect."
      if len(getPlayers()) > 1:
         for player in getPlayers():
            if len(player.Deck) == 0 and len(player.piles['Discard Pile']) == 0: 
               debugNotify("ofwhom() -- rejecting {} because they are a spectator".format(player))
               continue # This is a spectator 
            elif player != controller: 
               playerList.append(player) # Opponent needs to be not us, and of a different type. 
               debugNotify("ofwhom() -- appending {}".format(player),4)
            else: debugNotify("ofwhom() -- rejecting {} because they are the same as the controller ".format(player), 4)
         debugNotify("playerList = {}".format(playerList), 4)
         if len(playerList) == 1: targetPLs.append(playerList[0])
         elif len(playerList) == 0: 
            notify(":::Error::: No Valid Opponents found. Returning Myself as failsafe")
            targetPLs.append(me)
         else:
            if re.search(r'o[fn]AllOpponents', Autoscript): targetPLs = playerList
            else:
               choice = SingleChoice(multiText, [pl.name for pl in playerList])
               targetPLs.append(playerList[choice])
      else: 
         if debugVerbosity >= 1: whisper("There's no valid Opponents! Selecting myself.")
         targetPLs.append(me)
   else: targetPLs.append(controller) # If the script does not mention Opponent or Ally, then it's targeting the controller
   debugNotify("<<< ofwhom() returns {}".format([pl.name for pl in targetPLs]))
   return targetPLs
   
def compileCardStat(card, stat = 'Influence'):
   debugNotify(">>> compileCardStat(). card = {}, stat = {}".format(card.name,stat)) # Debug
   hostCards = eval(getGlobalVariable('Host Cards'))
   attachedCards = [Card(att_id) for att_id in hostCards if hostCards[att_id] == card._id]
   if stat == 'Influence':
      count = num(card.properties[stat])
      count += card.markers[mdict['PermInfluencePlus']] - card.markers[mdict['PermInfluenceMinus']] + card.markers[mdict['InfluencePlus']] - card.markers[mdict['InfluenceMinus']]
      for c in attachedCards: 
         count += num(c.Influence) # Attached cards which provide influence, effectively increase the influence of the card
         count += c.markers[mdict['PermInfluencePlus']] - c.markers[mdict['PermInfluenceMinus']] + c.markers[mdict['InfluencePlus']] - c.markers[mdict['InfluenceMinus']] # If any of the card's attachments have influence markers, then they affect their host as well.
   elif stat == 'Bullets':
      count = num(card.properties[stat])
      count += card.markers[mdict['PermBulletPlus']] - card.markers[mdict['PermBulletMinus']] + card.markers[mdict['BulletNoonPlus']] - card.markers[mdict['BulletNoonMinus']] + card.markers[mdict['BulletShootoutPlus']] - card.markers[mdict['BulletShootoutMinus']]
      for c in attachedCards: 
         count += num(c.properties['Bullet Bonus']) # Attached cards which provide bullets use a different field
         count += c.markers[mdict['PermBulletPlus']] - c.markers[mdict['PermBulletMinus']] + c.markers[mdict['BulletNoonPlus']] - c.markers[mdict['BulletNoonMinus']] + c.markers[mdict['BulletShootoutPlus']] - c.markers[mdict['BulletShootoutMinus']]
   elif stat == 'Control':
      count = num(card.properties[stat])
      count += card.markers[mdict['PermControlPlus']] - card.markers[mdict['PermControlMinus']] + card.markers[mdict['ControlPlus']] - card.markers[mdict['ControlMinus']]
   elif stat == 'Value': count = calcValue(card,'numeral')
   elif stat == 'Production':
      count = num(card.properties[stat])
      count += card.markers[mdict['ProdPlus']] - card.markers[mdict['ProdMinus']]
   elif stat == 'Upkeep':
      count = num(card.properties[stat])
      count += card.markers[mdict['ProdMinus']] - card.markers[mdict['ProdPlus']]
   elif stat == 'Grit':
      count = compileCardStat(card, 'Influence') + compileCardStat(card, 'Value') + compileCardStat(card, 'Bullets')
   else: count = 0
   if count < 0: 
      if stat == 'Value': count = 1
      else: count = 0
   elif count > 13 and stat == 'Value': count = 13
   debugNotify("<<< compileCardStat(). return = {} ".format(count)) # Debug
   return count

def fetchDrawType(card): # We go through effects which change their draw value in order to priority
   drawType = card.properties['Draw Type']
   hostCards = eval(getGlobalVariable('Host Cards'))
   attachedCards = [Card(att_id) for att_id in hostCards if hostCards[att_id] == card._id]
   for c in attachedCards: 
      debugNotify("Checking {}'s {}".format(card.name,c.name))
      if re.search(r'This dude is a draw',c.Text) and not findMarker(c,'Unprepared'): drawType = 'Draw'
      if re.search(r'This dude is a stud',c.Text) and not findMarker(c,'Unprepared'): drawType = 'Stud'
   if findMarker(card,'High Noon:Draw'): drawType = 'Draw'
   elif findMarker(card,'High Noon:Stud'): drawType = 'Stud'
   if findMarker(card, 'Shootout:Draw'): drawType = 'Draw'
   elif findMarker(card, 'Shootout:Stud'): drawType = 'Stud'
   return drawType
   
def calcValue(card, type = 'poker'):
   numvalue = numrank(card.Rank) + card.markers[mdict['ValueNoonPlus']] - card.markers[mdict['ValueNoonMinus']] + card.markers[mdict['ValueShootoutPlus']] - card.markers[mdict['ValueShootoutMinus']] + card.markers[mdict['ValuePermPlus']] - card.markers[mdict['ValuePermMinus']]
   if card.group == table: numvalue += fetchKF(card)
   hostCards = eval(getGlobalVariable('Host Cards'))
   attachedCards = [Card(att_id) for att_id in hostCards if hostCards[att_id] == card._id]
   for c in attachedCards: 
      numvalue += c.markers[mdict['ValueNoonPlus']] - c.markers[mdict['ValueNoonMinus']] + c.markers[mdict['ValueShootoutPlus']] - c.markers[mdict['ValueShootoutMinus']] + c.markers[mdict['ValuePermPlus']] - c.markers[mdict['ValuePermMinus']]
      if c.Name == 'Tusk' and c.controller != me: numvalue += 5
   if type == 'raw': return numvalue
   if numvalue > 12 and type == 'numeral': return 13
   if numvalue > 12: return 'K'
   if numvalue == 12 and type == 'numeral': return 12
   if numvalue == 12: return 'Q'
   if numvalue == 11 and type == 'numeral': return 11
   if numvalue == 11: return 'J'
   if numvalue == 1 and type == 'numeral': return 1
   if numvalue == 1: return 'A'
   if numvalue < 1: return 0
   return numvalue

def chkTargeting(card):
   debugNotify(">>> chkTargeting(){}".format(extraASDebug())) #Debug
   for Autoscript in CardsAS.get(card.model,'').split('||'):
      if re.search(r'-onlyInShootouts',Autoscript) and getGlobalVariable('Shootout') != 'True': continue
      if re.search(r'-onlyInNoon',Autoscript) and getGlobalVariable('Shootout') == 'True': continue
      for autoS in Autoscript.split('$$'):
         if (re.search(r'on(Play)[^|]+(?<!Auto)Targeted', autoS)
               and len(findTarget(autoS)) == 0
               and not re.search(r'isOptional', autoS)
               and not confirm("This card requires a valid target for it to work correctly.\
                              \nIf you proceed without a target, strange things might happen.\
                            \n\nProceed anyway?")):
            return 'ABORT'
   if re.search(r'HandTarget', CardsAS.get(card.model,'')) or re.search(r'HandTarget', CardsAA.get(card.model,'')):
      hasTarget = False
      for c in me.hand:
         if c.targetedBy and c.targetedBy == me: hasTarget = True
      if not hasTarget:
         whisper(":::Warning::: This card effect requires that you have one of more cards targeted from your hand. Aborting!")
         return 'ABORT'

def participateDude(card, doNotBoot = False): # Marks a card as participating in a shootout.
   cardParticipated = False # If this value is left false, then the card wasn't modified in any way by this function.
   if card.Type == 'Dude' and not card.highlight:
      if getGlobalVariable('Shootout') == 'True':
         side = None
         for c in table:
            if c.highlight == AttackColor:
               if c.controller == me: side = 'Attack'
               elif len(getActivePlayers()) == 2: side = 'Defence' # If we found out opponent's dude as attacker and there's only 2 player in the game, we assume we're the defender.
            elif c.highlight == DefendColor:
               if c.controller == me: side = 'Defence'
               elif len(getActivePlayers()) == 2: side = 'Attack'               
         if not side: # If we still couldn't determine which side the player is on, we just ask directly.
            if confirm("Sorry, but I could not automatically determine if you're the attacking or defending player.\n\nIs this dude joining the attacking posse?"): side = 'Attack' 
            else: side = 'Defence'
         if side == 'Defence': joinDefence(card, doNotBoot = doNotBoot)
         else: joinAttack(card, doNotBoot = doNotBoot)         
         cardParticipated = True
      elif getGlobalVariable('Job Active') != 'False':
         for c in table: # If there is a job in progress and the leader participates with one of their own dudes, they join their posse.
            if c.highlight == InitiateColor and c.controller == me: 
               if moveToPosse(card, isJob = True, doNotBoot = doNotBoot):
                   card.highlight = InitiateColor
                   notify("{} is joining the leader's posse.".format(card))
                   executePlayScripts(card, 'PARTICIPATION')
               cardParticipated = True # need to mark as participated so no other smart action is performed
               break
   return cardParticipated

def moveToPosse(card, leader = None, mark = None, isJob = None, isAttacking = True, doNotBoot = False):
   scriptEffect = executePlayScripts(card, 'MOVETOPOSSE')
   if scriptEffect == 'ABORT': return
   performBoot = performMove = None
   if doNotBoot: performBoot = False
   if re.search(r'NOBOOT', scriptEffect): performBoot = False
   if re.search(r'NOMOVE', scriptEffect): performMove = False
   if not leader: leader = Card(eval(getGlobalVariable('Leader')))
   if not mark: mark = Card(eval(getGlobalVariable('Mark')))
   if isJob == None: isJob = getGlobalVariable('Job Active') != 'False'
   markLocation = determineCardLocation(mark)
   dudeLocation = determineCardLocation(card)
   if isAttacking and isJob:
       leaderLocation = Card(eval(leader.properties['beforeParticipation']))
   if performBoot == None: performBoot = True
   if performMove == None:
       performMove = True
       if dudeLocation == markLocation:
           performMove = False
           performBoot = False
       elif not areLocationsAdjacent(markLocation, dudeLocation):
           if not isJob or not isAttacking:
               if not confirm("{} is not in mark location, and is not adjacent to the mark location. Do you want to participate them anyway?".format(card.name)): return False
           elif not areLocationsAdjacent(leaderLocation, dudeLocation) and dudeLocation != leaderLocation:
               if not confirm("{} is not in mark or leader location, and is not adjacent to either mark nor leader. Do you want to participate them anyway?".format(card.name)): return False
   if performBoot and card.orientation == Rot90 and scriptEffect != 'ALLOWBOOTED':
       if isAttacking: posseType = "leader"
       else: posseType = "mark"
       if not confirm("{} requires to boot to join the {} posse, but they are already booted. Do you want to proceed anyway?".format(card.name, posseType)): return False
   saveProperty = ''
   if performMove:
      move(card, silent = True, targetCards = [markLocation], needToBoot = False)
      saveProperty = str(dudeLocation._id) + '|'
   if performBoot and card.orientation == Rot0 and scriptEffect != 'NOBOOT':
      card.orientation = Rot90
      saveProperty += "unbooted"
   if saveProperty != '': card.properties['beforeParticipation'] = saveProperty
   return True

def chkGadgetCraft(card):
   success = True
   if re.search('Gadget', card.Keywords):
      if confirm("You are trying to create a gadget {}. Would you like to do a gadget skill check at this point?".format(card.Type)):
         myDudes = [dude for dude in table if dude.controller == me and dude.orientation == Rot0 and re.search(r'Mad Scientist',dude.Keywords)]
         if not len(myDudes):
            if confirm("You do not seem to have an available unbooted mad scientist to build this gadget. Abort the build?"):
               success = False
               return
            else:
               myDudes = [dude for dude in table if dude.controller == me and re.search(r'Mad Scientist',dude.Keywords)]
         MadScientist = None
         for dude in myDudes:
            if dude.targetedBy and dude.targetedBy == me: 
               MadScientist = dude
               break
         if not MadScientist:
            choice = SingleChoice('Choose one of your available Mad Scientists to build this gadget dude', makeChoiceListfromCardList(myDudes))
            if choice != None: MadScientist = myDudes[choice]
         if MadScientist:
            gadgetPull = pull(silent = True) # pull returns a tuple with the results of the pull
            MadScientist.orientation = Rot90
            notify("{} attempted to manufacture a {} and pulled a {} {}".format(MadScientist,card,fullrank(gadgetPull[0]), fullsuit(gadgetPull[1])))
         else: notify("{} has built a {} without a gadget skill check.".format(me, card))
      else: notify("{} has built a {} without a gadget skill check.".format(me, card))
   return success
   
def fetchSkills(card):
   #confirm("fetching skills for {}".format(card.name))
   skillList = []
   if card.Type == 'Dude': # only dudes have skills (for now at least)
      cardSubtypes = card.keywords.split('-') # And each individual Keyword. Keywords are separated by " - "
      for cardSubtype in cardSubtypes:
         strippedCS = cardSubtype.strip() # Remove any leading/trailing spaces between traits. We need to use a new variable, because we can't modify the loop iterator.
         #confirm("Checking {}".format(strippedCS))
         if strippedCS:
            skillRegex = re.search(r'(Huckster|Blessed|Shaman|Mad Scientist) ([0-9])',strippedCS)
            if skillRegex:
               skillRank = num(skillRegex.group(2))
               # We now look for effects that would modify that skill.
               debugNotify('Skill now {}'.format(skillRank))
               for marker in card.markers:
                  if re.search(r'Skill Bonus',marker[0]): skillRank += card.markers[marker]
                  if re.search(r'Skill Penalty',marker[0]): skillRank -= card.markers[marker]
               debugNotify('Skill now {}'.format(skillRank))
               if CardsAS.get(card.model,'') != '':
                  Autoscripts = CardsAS.get(card.model,'').split('||')
                  for autoS in Autoscripts:
                     skillBonusRegex = re.search(r'constantAbility:Skill Bonus:([0-9]+)',autoS)
                     if skillBonusRegex and checkSpecialRestrictions(autoS,card):
                        multiplier = per(autoS, card)
                        skillRank += multiplier * num(skillBonusRegex.group(1))
                        debugNotify('Skill now {}'.format(skillRank))
               # Finished checking effects on Dude themselves. Checking Attachments
               hostCards = eval(getGlobalVariable('Host Cards'))
               attachedCards = [Card(att_id) for att_id in hostCards if hostCards[att_id] == card._id]
               for attachment in attachedCards:
                  for marker in attachment.markers:
                     if re.search(r'Skill Bonus',marker[0]): skillRank += attachment.markers[marker]
                     if re.search(r'Skill Penalty',marker[0]): skillRank -= attachment.markers[marker]
                  debugNotify('Skill now {}'.format(skillRank))
                  if CardsAS.get(attachment.model,'') != '':
                     Autoscripts = CardsAS.get(attachment.model,'').split('||')
                     for autoS in Autoscripts:
                        skillBonusRegex = re.search(r'constantAbility:Skill Bonus:([0-9]+)',autoS)
                        if skillBonusRegex and checkSpecialRestrictions(autoS,attachment):
                           multiplier = per(autoS, attachment,targetCards = findTarget(autoS))
                           skillRank += multiplier * num(skillBonusRegex.group(1))
                           debugNotify('Skill now {}'.format(skillRank))                  
               skillList.append((skillRegex.group(1),skillRank)) # If we discover a skill, we add it in a tuple with the skill first, then its numerical value second.
   #confirm(str(skillList))        
   return skillList
      
def fetchKF(card):
   KFRank = 0
   if card.Type == 'Dude': # only dudes have Kung Fu
      cardSubtypes = card.keywords.split('-') # And each individual Keyword. Keywords are separated by " - "
      for cardSubtype in cardSubtypes:
         strippedCS = cardSubtype.strip() # Remove any leading/trailing spaces between traits. We need to use a new variable, because we can't modify the loop iterator.
         #confirm("Checking {}".format(strippedCS))
         if strippedCS:
            KFRegex = re.search(r'Kung Fu ([0-9])',strippedCS)
            if KFRegex:
               KFRank = num(KFRegex.group(1))
               # We now look for effects that would modify Kung Fu.
               debugNotify('KF now {}'.format(KFRank))
               for marker in card.markers:
                  if re.search(r'Kung Fu Bonus',marker[0]): KFRank += card.markers[marker]
                  if re.search(r'Kung Fu Penalty',marker[0]): KFRank -= card.markers[marker]
               debugNotify('KF now {}'.format(KFRank))
               if CardsAS.get(card.model,'') != '':
                  Autoscripts = CardsAS.get(card.model,'').split('||')
                  for autoS in Autoscripts:
                     KFBonusRegex = re.search(r'constantAbility:Kung Fu Bonus:([0-9]+)',autoS)
                     if KFBonusRegex and checkSpecialRestrictions(autoS,card):
                        multiplier = per(autoS, card)
                        KFRank += multiplier * num(KFBonusRegex.group(1))
                        debugNotify('KF now {}'.format(KFRank))
               # Finished checking effects on Dude themselves. Checking Attachments
               hostCards = eval(getGlobalVariable('Host Cards'))
               attachedCards = [Card(att_id) for att_id in hostCards if hostCards[att_id] == card._id]
               for attachment in attachedCards:
                  for marker in attachment.markers:
                     if re.search(r'Kung Fu Bonus',marker[0]): KFRank += attachment.markers[marker]
                     if re.search(r'Kung Fu Penalty',marker[0]): KFRank -= attachment.markers[marker]
                  debugNotify('KF now {}'.format(KFRank))
                  if CardsAS.get(attachment.model,'') != '':
                     Autoscripts = CardsAS.get(attachment.model,'').split('||')
                     for autoS in Autoscripts:
                        KFBonusRegex = re.search(r'constantAbility:Kung Fu Bonus:([0-9]+)',autoS)
                        if KFBonusRegex and checkSpecialRestrictions(autoS,attachment):
                           multiplier = per(autoS, attachment,targetCards = findTarget(autoS))
                           KFRank += multiplier * num(KFBonusRegex.group(1))
                           debugNotify('Skill now {}'.format(KFRank))  
   return KFRank
      
def sendToDrawHand(card):
   myDrawHand = [c for c in table if c.highlight == DrawHandColor and c.controller == me]
   maX = None
   y = 0
   for c in myDrawHand: # We're trying to figure out which is the last card in our current draw hand, to play the newly converted drawhand card in there.
      x,y = c.position
      if maX == None: maX = x
      elif x > maX: maX = x
   if maX == None: card.moveToTable(homeDistance(card) - cardDistance(card) * 3 * (cwidth(card) / 4), cheight(card) * 2) 
   else: card.moveToTable(maX + (cwidth(card) / 4), y)
   card.highlight = DrawHandColor
   clearAttachLinks(card) # When a card becomes a draw hand card, we discard all its attachments, if it had any.

def revealCards(cardList): # Moves all cards in a list to the table and reveals them to all players
   mute()
   notice = "{} reveals: ".format(me)
   for iter in range(len(cardList)):
      card = cardList[iter]
      card.moveToTable(iter * cwidth(card) - (len(cardList) * cwidth(card) / 2), 0, False)
      card.highlight = DrawHandColor
      update()
      if iter == len(cardList) - 1: notice += "{}.".format(card)
      else: notice += "{}, ".format(card)
   notify(notice)
   
def getKeywords(card): # A function which combines the existing card keywords, with markers which give it extra ones.
   debugNotify(">>> getKeywords(){}".format(extraASDebug())) #Debug
   global Stored_Keywords
   #confirm("getKeywords") # Debug
   keywordsList = []
   cKeywords = card.Keywords # First we try a normal grab, if the card properties cannot be read, then we flip face up.
   strippedKeywordsList = cKeywords.split('-')
   for cardKW in strippedKeywordsList:
      strippedKW = cardKW.strip() # Remove any leading/trailing spaces between traits. We need to use a new variable, because we can't modify the loop iterator.
      if strippedKW: keywordsList.append(strippedKW) # If there's anything left after the stip (i.e. it's not an empty string anymrore) add it to the list.   
   if card.markers:
      for key in card.markers:
         markerKeyword = re.search('Keyword:([\w ]+)',key[0])
         if markerKeyword:
            #confirm("marker found: {}\n key: {}".format(markerKeyword.groups(),key[0])) # Debug
            keywordsList.append(markerKeyword.group(1))
   keywords = ''
   for KW in keywordsList:
      keywords += '{}-'.format(KW)
   debugNotify("<<< getKeywords() by returning: {}.".format(keywords[:-1]), 3)
   return keywords[:-1] # We need to remove the trailing dash '-'

#---------------------------------------------------------------------------
# Location Functions
#---------------------------------------------------------------------------
def getDudeLocation(dude):
   locationId = dude.properties['Occupying']
   if locationId and locationId != "":
       return Card(eval(locationId))

def addDudeToLocation(card, dude):
   dude.properties['Occupying'] = "{}".format(card._id)
   addIdToCardProperty(card, dude._id, 'Occupants')

def removeDudeFromLocation(dude, location = None, updateDude = False):
   if location == None: location = getDudeLocation(dude)
   if location == None: return
   if updateDude: dude.properties['Occupying'] = ""
   removeIdFromCardProperty(location, dude._id, 'Occupants')

def getDudesAtLocation(card):
   occupants = getCardsFromProperties(card, 'Occupants');
   return occupants

# This is not exactly index in the list, but position above or below the outfit
def getDeedPositionOnStreet(card):
   if card.Type != 'Deed' and card.Type != 'Outfit': return
   if card.Type == 'Outfit':
       return 0
   locationOutfitCard = Card(eval(card.owner.getGlobalVariable('playerOutfit')))
   deedsAbove = getCardsFromProperties(locationOutfitCard, 'Above')
   if card in deedsAbove: return deedsAbove.index(card) + 1
   deedsBelow = getCardsFromProperties(locationOutfitCard, 'Below')
   if card in deedsBelow: return (deedsBelow.index(card) + 1) * -1
   debugNotify("Deed {} was not found on the street!")

def areLocationsAdjacent(location1, location2):
   debugNotify(">>> Adjacent locations - location1: {}, location2: {}".format(location1, location2))
   if not location1 or not location2: return False
   hostCards = eval(getGlobalVariable('Host Cards'))
   attachmentsList1 = [cID for cID in hostCards if hostCards[cID] == location1._id and Card(cID).name == "Spirit Trail"]
   if len(attachmentsList1) > 0:
       attachmentsList2 = [cID for cID in hostCards if hostCards[cID] == location2._id and Card(cID).name == "Spirit Trail"]
       if len(attachmentsList2) > 0: return True
   if (re.search(r'Out of Town', location1.Keywords) or re.search(r'Out of Town', location2.Keywords)):
       if location1.name == 'Surveyor\'s Office' or location2.name == 'Surveyor\'s Office':
           return True;
       return False;
   if location1.name == 'Town Square' or location2.name == 'Town Square':
       if location1.name == 'Maza Gang Hideout' or location2.name == 'Maza Gang Hideout':
           return False;
       return True;
   if (location1.Type != 'Deed' and location1.Type != 'Outfit') or (location2.Type != 'Deed' and location2.Type != 'Outfit'): return False
   if location1.name == '\"Open Wound\"' and location2.name == '\"Open Wound\"': return True
   # Special cases needs to go before this if ^
   if location1.owner == location2.owner:
       position1 = getDeedPositionOnStreet(location1)
       position2 = getDeedPositionOnStreet(location2)
       if position1 + 1 == position2 or position1 - 1 == position2:
           return True;
       return False;

def findDeedOnStreet(card, direction = 'Above'):
   if card.Type != 'Deed' and card.Type != 'Outfit' and re.search('Out of Town', card.Keywords): return
   deedsInDirection = getCardsFromProperties(OutfitCard, direction)
   if not deedsInDirection or len(deedsInDirection) == 0: return
   if not card in deedsInDirection: return
   return deedsInDirection.index(card)

def highlightLocationUsingFilter(card, removeHighlight = False):
   debugNotify("Deed {} with type {} has filter: {}".format(card, card.Type, card.filter))
   if card.Type != 'Deed' and card.Type != 'Outfit': return
   transparency = "44"
   deedfilterString = "#{}00ff00"
   dudefilterString = "#{}ff0000"
   if removeHighlight or card.filter == deedfilterString.format(''): 
      deedfilterString = "#00000000"
      dudefilterString = "#00000000"
   card.filter = deedfilterString.format(transparency)
   dudesHere = getDudesAtLocation(card)
   for dude in dudesHere:
      dude.filter = dudefilterString.format(transparency)

def highlightLocation(card, clear = True):
   if card.Type != 'Deed' and card.Type != 'Outfit': return
   if clear:
       # Putting here try catch blok in case update for card selection is not in this OCTGN client version 
       # TODO should be removed once the selection update is available
       try: clearSelection()
       except: notifyDebug("::DEBUG:: This version of OCTGN client does not support clearing of the selection!")
   card.select()
   dudesHere = getDudesAtLocation(card)
   for dude in dudesHere:
       dude.select()

def clearDeedFromLocations(card):
   if card == None: return
   for dude in getDudesAtLocation(card):
       moveHome(dude, False)
   removeIdFromCardProperty(OutOfTownToken, card._id, 'ootDeeds')
   removeIdFromCardProperty(OutfitCard, card._id, 'Above')
   removeIdFromCardProperty(OutfitCard, card._id, 'Below')

def determineCardLocation(targetCard):
   if not targetCard: return
   if targetCard.Type == 'Dude': return getDudeLocation(targetCard)
   elif targetCard.Type == 'Deed' or targetCard.Type == 'Outfit' or targetCard.name == 'Town Square': return targetCard
   elif targetCard.Type == 'Action': return
   else:
      host = fetchHost(targetCard)
      if host:
          if host.Type == 'Dude': return getDudeLocation(host)
          elif host.Type == 'Deed' or host.Type == 'Outfit' or host.Name == 'Town Square': return host

def determineControl(card): 
    if not card or card.Type == 'Outfit' or card.Type == 'Token': return
    playersStats = {}
    originalController = card.controller
    playerWithMost = card.owner
    controllingPlayer = card.owner
    defaultDeterminator = 'Influence'
    ikeRowdy = card.markers['Rowdy Ike', '00000000-0000-0000-0000-000000000002']
    if ikeRowdy or re.search(r'Rowdy', card.Keywords) or card.name == "Dead Dog Tavern" or card.name == "The Oriental Saloon": defaultDeterminator = 'Bullets'
    for dude in getDudesAtLocation(card):
        determinator = defaultDeterminator
        if len(dude.markers):
            for marker in dude.markers:
                if re.search(r'Rowdy Dude', marker[0]): determinator = 'Bullets'
        amount = compileCardStat(dude, stat = determinator)
        if (amount < 1) : continue
        if playersStats.has_key(dude.controller._id): playersStats[dude.controller._id] += amount
        else: playersStats[dude.controller._id] = amount
        debugNotify("Dude controller inf: {}, Player with most Inf: {}".format(playersStats.get(dude.controller._id), playersStats.get(playerWithMost._id)))
        if dude.controller == playerWithMost:
            controllingPlayer = dude.controller
        elif playersStats.get(dude.controller._id) > playersStats.get(playerWithMost._id): 
            playerWithMost = dude.controller
            controllingPlayer = dude.controller
        elif playersStats.get(dude.controller._id) == playersStats.get(playerWithMost._id): 
            controllingPlayer = card.owner
        debugNotify("{} {}: {} | Overall: {}".format(dude, amount, determinator, playersStats))
    if controllingPlayer != originalController: 
        if controllingPlayer != card.owner: notify("{} broke into {} and has taken control from the {}.".format(controllingPlayer, card, originalController))
        else: notify("{} has wrestled control of {} back from {}.".format(controllingPlayer, card, originalController))
        card.controller = controllingPlayer
   
#---------------------------------------------------------------------------
# Counter Manipulation
#---------------------------------------------------------------------------
   
def modInfluence(count = 1, notification = silent): # A function to modify the players influence counter. Can also notify.
   count = num(count) # We need to make sure we get an integer or we will fail horribly. OCTGN doesn't seem to respect its own definitions.
   me.Influence += count # Now increase the influence by the amount passed to us.
   if notification == 'loud' and count > 0: notify("{}'s influence has increased by {}. New total is {}".format(me, count, me.Influence))  
   # We only notify if the function is called as "loud" and we actually modify anything.

def modControl(count = 1, notification = silent): # Same as above but for Control Points
   count = num(count)
   me.Control += count
   if notification == 'loud' and count > 0: notify("{}'s control points have increased by {}. New total is {}".format(me, count, me.Control))         

def modVP(count = 1, notification = silent): # Same as above but for Control Points
   count = num(count)
   me.VictoryPoints += count
   if notification == 'loud' and count > 0: notify("{}'s victory points have increased by {}. New total is {}".format(me, count, me.VictoryPoints))         

def payCost(count = 1, notification = silent, MSG = None): # Same as above for Ghost Rock. However we also check if the cost can actually be paid.
   count = num(count)
   if not MSG: MSG = "You do not seem to have enough Ghost Rock in your bank to play this card. Are you sure you want to proceed? \
                    \n(If you do, your GR will go to the negative. You will need to increase it manually as required.)"
   if count == 0 : return # If the card has 0 cost, there's nothing to do.
   if me.GhostRock < count: # If we don't have enough Ghost Rock in the bank, we assume card effects or mistake and notify the player that they need to do things manually.
      if notification == loud: 
         if not confirm(MSG): return 'ABORT'
         notify("{} was supposed to pay {} Ghost Rock but only has {} in their bank. They'll need to reduce the cost by {} with card effects.".format(me, count, me.GhostRock, count - me.GhostRock))   
         me.GhostRock -= num(count)
      else: me.GhostRock -= num(count) 
   else: # Otherwise, just take the money out and inform that we did if we're "loud".
      me.GhostRock -= num(count)
      if notification == 'loud': notify("{} has paid {} Ghost Rock. {} is left in their stash".format(me, count, me.GhostRock))  

def cardRMsync(card, notification = 'loud'): # a function which removes influence and CP when a card which had them leaves play.
   if card.Type != 'Dude' and card.Type != 'Deed': return
   influence = 0
   control = 0
   count = num(card.Influence) + card.markers[mdict['InfluencePlus']] - card.markers[mdict['InfluenceMinus']]
   if count > 0: 
      modInfluence(-1 * count)
      if notification == 'loud': notify("{}'s influence is reduced by {}".format(me,count))
   count = num(card.Control) + card.markers[mdict['ControlPlus']] - card.markers[mdict['ControlMinus']]
   if count > 0: 
      modControl(-1 * count)
      if notification == 'loud': notify("{}'s control points are reduced by {}".format(me,count))

def fetchAllOpponents(targetPL = me):
   debugNotify(">>> fetchAllOpponents()") #Debug
   opponentList = []
   if len(getPlayers()) > 1:
      for player in getPlayers():
         if player.getGlobalVariable('playerOutfit') == 'None': continue # This is a spectator 
         if player != targetPL: opponentList.append(player) # Opponents in Doomtown is everyone else.
   else: opponentList = [me] # For debug purposes
   debugNotify("<<< fetchAllOpponents() returning size {} ".format(len(opponentList))) #Debug
   return opponentList   
   
def fetchAllAllies(targetPL = me):
   debugNotify(">>> fetchAllAllies()") #Debug
   alliesList = [me] # There's no team-games in Doomtown (yet)
   # if len(getPlayers()) > 1:
      # for player in getPlayers():
         # if player.getGlobalVariable('Side') == '': continue # This is a spectator 
         # if player == targetPL or player.getGlobalVariable('Side') == targetPL.getGlobalVariable('Side'): alliesList.append(player) # Opponent needs to be not us, and of a different type. 
   # else: alliesList = [me] # For debug purposes
   debugNotify("<<< fetchAllAllies() returning size {} ".format(len(alliesList))) #Debug
   return alliesList   
   
      
#---------------------------------------------------------------------------
# Shootout/Lowball Scripts
#---------------------------------------------------------------------------

def findLowballWinner():
# This is a function which evaluates the lowball poker hand ranks of all players on the table and determines the winner
# This works for an indefinite number of players and it works as follows
# It checks if all players have revealed a lowball hand. If they haven't then it aborts. 
# This means that the slowest player is always the one who will do the hand comparison
# Once all hands are on the table, it compares hand ranks one by one until it finds the highest 
# then passes the winning player's object to the function that called it (usually revealLowballHand)
   debugNotify(">>> lowballWinner()")
   i = 0
   j = 1
   handtie = False
   if len(getActivePlayers()) == 1: winner = me # Code to allow me debug with just one player in the match
   tied = [] # A list which holds the player objects of players who are tied. Not used atm.
             # We will pass it later to a variable to determine high card winners.
   for player in getActivePlayers():
      #notify("Checking Player {} handrank == {}".format(player.name,player.getGlobalVariable('Hand Rank'))) # Debug
      if player.getGlobalVariable('Hand Rank') == 'N/A': 
         debugNotify("<<< lowballWinner(). ABORTED")
         return 'aborted' # If one player hasn't revealed their hand yet, abort this function
   activePlayers = getActivePlayers()
   handRanks = []
   for PL in activePlayers: handRanks.append(num(PL.getGlobalVariable('Hand Rank')))
   while i < len(activePlayers) - 1: # Go once through all the players except the last
      while j < len(activePlayers): # Then go through all the players except the starting one in the previous for loop.
         debugNotify("comp {} to {}. handtie {}.".format(activePlayers[i].name,activePlayers[j].name,handtie),4)
         if handRanks[i] < handRanks[j]: # If the player we're checking has a lower hand than the next player...
            if handtie: # If we have recorded a tie...
               if handRanks[i] >= num(tied[0].getGlobalVariable('Hand Rank')): pass # ...and if the tie is lower/equal than the current player. Then do nothing
               else: 
                  handtie = False # If the tie is higher than the current player, then there's no more a tie.
                  winner = activePlayers[i]
            else: winner = activePlayers[i] # Else record the current player as the winner
         elif handRanks[i] > handRanks[j]: # If the primary player (activePlayers[i])has lost a hand comparison, 
                                                         # then we take him completely off the comparison and move to the next one.
            if handtie: # but if there is a tie...
               if handRanks[j] >= num(tied[0].getGlobalVariable('Hand Rank')): pass # ...and if the winning player is not lower/equal than the tie. Then do nothing
               else: 
                  handtie = False # If the tie is higher than the current player, then there's no more a tie.               
                  winner = activePlayers[j]
            else: winner = activePlayers[j] # And the winner is the player who won the current player
            j += 1
            break # No more need to check this player anymore as he's lost.
         else: 
            handtie = True # If none of the player's won, it's a tie
            if len(tied) == 0: # If our list isn't populated yet, then add the first two tied players
               tied = [activePlayers[i], activePlayers[j]]
            else: # If we have some players in the list, only add the compared ones if they're not already in the list.
               if activePlayers[i] not in tied: tied.append(activePlayers[i])
               if activePlayers[j] not in tied: tied.append(activePlayers[j])
         j += 1
         if not handtie: 
            if winner ==  activePlayers[i] and j == len(activePlayers): # If the player we're currently comparing has won all other hands,
               #clearHandRanks()                                         # and there's no more players to compare with then there' no reason to compare more.
               debugNotify("<<< lowballWinner() with Winner = {}.".format(winner))
               return winner                                
      i += 1
      j = i + 1
   #clearHandRanks()
   if handtie: 
      debugNotify("<<< lowballWinner() with a Hand Tie")
      return 'tie'
   else: 
      debugNotify("<<< lowballWinner() with Winner = {}.".format(winner))
      return winner # If the loop manages to finish and it's not a tie, then the winner is always the last player in the list.

def getPotCard(chkOnly = False): # Checks if the Lowball Pot Card is on the table and creates it if it isn't.
   mute()
   potCard = None
   for c in table:
      if c.model == "c421c742-c920-4cad-9f72-032c3378191e": 
         potCard = c
         break
   if not potCard and getGlobalVariable('Phase') == '1' and not chkOnly:
      if me._id == 1: 
         potCard = table.create("c421c742-c920-4cad-9f72-032c3378191e",cwidth() / -2,-20, 1, False)
         potCard.orientation = Rot90
      else: 
         for player in getPlayers():
            if player._id == 1: remoteCall(player,'getPotCard',[])
   #notify("returning {}".format(potCard)) # Debug
   return potCard # We return the card to the function that called us, so that it can use it.

def incrPotCard(count = 1):
   if me._id == 1:
      potCard = getPotCard()
      potCard.markers[mdict['Ghost Rock']] += 1
   else: 
      for player in getPlayers():
         if player._id == 1: remoteCall(player,'incrPotCard',[count])
   
def clearPotCard():
   potCard = getPotCard(True)
   if potCard: delCard(potCard,True)
   
def clearDrawHandonTable():
   for card in table:
      if card.controller == me:
         if card.highlight == DrawHandColor:
            discard(card)  
            card.highlight = None
         if card.model == 'cd31eabe-e2d8-49f7-b4de-16ee4fedf3c1': # The cheatin' icon
            delCard(card)

def clearRemainingActions(all = False): # all is set to true when finishing a shootout, so that it then clears jobs and BH actions cards etc.
   for card in table:
      if (card.controller == me 
          and card.Type == 'Action' 
          and not re.search('Condition', card.Keywords) 
          and not re.search('Noon Job[:,]', card.Text) # Noon Jobs are discarded only at the end of the shootout.
          and card.Name != 'Bounty Hunter' # BH cards are discarded only at the end of the shootout
          and card.highlight != DrawHandColor 
          and card.highlight != DummyColor): discard(card)  

def makeChoiceListfromCardList(cardList,includeText = False, includeGroup = False):
# A function that returns a list of strings suitable for a choice menu, out of a list of cards
# Each member of the list includes a card's name, traits, resources, markers and, if applicable, combat icons
   debugNotify(">>> makeChoiceListfromCardList()")
   debugNotify("cardList: {}".format([c.name for c in cardList]), 2)
   targetChoices = []
   debugNotify("About to prepare choices list.", 2)# Debug
   for T in cardList:
      debugNotify("Checking {}".format(T), 4)# Debug
      markers = 'Counters:'
      if T.markers[mdict['Bounty']] and T.markers[mdict['Bounty']] >= 1: markers += "{} Bounty,".format(T.markers[mdict['Bounty']])
      if T.markers[mdict['Harrowed']] and T.markers[mdict['Harrowed']] >= 1: markers += "Harrowed,"
      if T.markers[mdict['PermInfluencePlus']] and T.markers[mdict['PermInfluencePlus']] >= 1: markers += " +{} Permanent Influence,".format(T.markers[mdict['PermInfluencePlus']])
      if T.markers[mdict['PermInfluenceMinus']] and T.markers[mdict['PermInfluenceMinus']] >= 1: markers += " +{} Permanent Influence,".format(T.markers[mdict['PermInfluenceMinus']])
      if T.markers[mdict['InfluencePlus']] and T.markers[mdict['InfluencePlus']] >= 1: markers += " +{} Influence,".format(T.markers[mdict['InfluencePlus']])
      if T.markers[mdict['InfluenceMinus']] and T.markers[mdict['InfluenceMinus']] >= 1: markers += " -{} Influence,".format(T.markers[mdict['InfluenceMinus']])
      if T.markers[mdict['PermControlPlus']] and T.markers[mdict['PermControlPlus']] >= 1: markers += " +{} Permanent Control,".format(T.markers[mdict['PermControlPlus']])
      if T.markers[mdict['PermControlMinus']] and T.markers[mdict['PermControlMinus']] >= 1: markers += " +{} Permanent Control,".format(T.markers[mdict['PermControlMinus']])
      if T.markers[mdict['ControlPlus']] and T.markers[mdict['ControlPlus']] >= 1: markers += " +{} Control,".format(T.markers[mdict['ControlPlus']])
      if T.markers[mdict['ControlMinus']] and T.markers[mdict['ControlMinus']] >= 1: markers += " -{} Control,".format(T.markers[mdict['ControlMinus']])
      if T.markers[mdict['ProdPlus']] and T.markers[mdict['ProdPlus']] >= 1: markers += " +{} Production,".format(T.markers[mdict['ProdPlus']])
      if T.markers[mdict['ProdMinus']] and T.markers[mdict['ProdMinus']] >= 1: markers += " +{} Upkeep,".format(T.markers[mdict['ProdMinus']])
      if T.markers[mdict['ValueNoonPlus']] and T.markers[mdict['ValueNoonPlus']] >= 1: markers += " +{} Value,".format(T.markers[mdict['ValueNoonPlus']])
      if T.markers[mdict['ValueNoonMinus']] and T.markers[mdict['ValueNoonMinus']] >= 1: markers += " -{} Value,".format(T.markers[mdict['ValueNoonMinus']])
      if T.markers[mdict['BulletNoonPlus']] and T.markers[mdict['BulletNoonPlus']] >= 1: markers += " +{} Noon Bullets,".format(T.markers[mdict['BulletNoonPlus']])
      if T.markers[mdict['BulletShootoutPlus']] and T.markers[mdict['BulletShootoutPlus']] >= 1: markers += " +{} Shootout Bullets,".format(T.markers[mdict['BulletShootoutPlus']])
      if T.markers[mdict['PermBulletPlus']] and T.markers[mdict['PermBulletPlus']] >= 1: markers += " +{} Permanent Bullets,".format(T.markers[mdict['PermBulletPlus']])
      if T.markers[mdict['PermBulletMinus']] and T.markers[mdict['PermBulletMinus']] >= 1: markers += " -{} Permanent Bullets,".format(T.markers[mdict['PermBulletMinus']])
      if T.markers[mdict['BulletNoonMinus']] and T.markers[mdict['BulletNoonMinus']] >= 1: markers += " -{} Noon Bullets,".format(T.markers[mdict['BulletNoonMinus']])
      if T.markers[mdict['BulletShootoutMinus']] and T.markers[mdict['BulletShootoutMinus']] >= 1: markers += " -{} Shootout Bullets,".format(T.markers[mdict['BulletShootoutMinus']])
      if T.markers[mdict['Ghost Rock']] and T.markers[mdict['Ghost Rock']] >= 1: markers += "{} GR,".format(T.markers[mdict['Ghost Rock']])
      if markers != 'Counters:': markers += '\n'
      else: markers = ''
      if T.markers[mdict['Traded']] and T.markers[mdict['Traded']] >= 1: traded = "\n(Already Traded)"
      else: traded = ''
      debugNotify("Finished Adding Markers. Adding stats...", 4)# Debug               
      stats = ''
      stats += "Value: {} of {}.\nCost: {}".format(fullrank(calcValue(T)),fullsuit(T.Suit),T.Cost)
      if T.Influence != '': stats += "\nInfluence: {}. ".format(T.Influence)
      if T.Control != '': stats += "\nControl: {}. ".format(T.Control)
      if T.Type == 'Dude': stats += "\nBullets: {} {}. ".format(T.Bullets, T.properties['Draw Type'])
      if T.Production != '' and T.Production != '0': stats += "\nProduction: {}. ".format(T.Production)
      if T.Upkeep != '' and T.Upkeep != '0': stats += "\nUpkeep: {}. ".format(T.Upkeep)
      if includeText: cText = '\n' + T.Text
      else: cText = ''
      hostCards = eval(getGlobalVariable('Host Cards'))
      attachmentsList = [Card(cID).name for cID in hostCards if hostCards[cID] == T._id]
      cAttachments = ''
      if len(attachmentsList) >= 1: cAttachments = '\nAttachments:' + str(attachmentsList)
      elif T.Type == 'Goods' or T.Type == 'Spell': 
          host = fetchHost(T)
          if host: cAttachments = '\nAttached To:' + host.name + "(" + host.owner.name + ")"
      if includeGroup: cGroup = '\n' + T.group.name # Include group is used to inform the player where the card resides in cases where they're selecting cards from multiple groups.
      else: cGroup = ''
      debugNotify("Finished Adding Stats. Going to choice...", 4)# Debug               
      choiceTXT = "{}\n{}\n{}{}\n{}{}{}{}{}".format(T.name,T.Type,T.Keywords,traded,markers,stats,cAttachments,cText,cGroup)
      targetChoices.append(choiceTXT)
   return targetChoices
   debugNotify("<<< makeChoiceListfromCardList()", 3)
   
      
#------------------------------------------------------------------------------
# Card Attachments scripts
#------------------------------------------------------------------------------

def findHost(card, Autoscript = ''):
   debugNotify(">>> findHost() for {}".format(card)) #Debug
   # Tries to find a host to attach the gear
   hostCards = eval(getGlobalVariable('Host Cards'))
   if re.search(r'Targeted',Autoscript): potentialHosts = findTarget(Autoscript)
   elif re.search(r'Improvement',card.Keywords): potentialHosts = findTarget('Targeted-atDeed-isUnbooted-targetMine') # First we try to do a limited search, in case they forgot too many cards targeted
   elif re.search(r'Totem',card.Keywords): potentialHosts = findTarget('Targeted-atDeed_or_Town Square_or_Outfit-targetMine') 
   elif re.search(r'Condition',card.Keywords): potentialHosts = findTarget('Targeted') 
   elif card.Type == 'Legend': potentialHosts = findTarget('AutoTargeted-atOutfit-targetMine') 
   elif card.type == 'Spell':
      if re.search(r'Hex',card.Keywords): potentialHosts = findTarget('Targeted-atDude_and_Huckster-isUnbooted-targetMine',choiceTitle = "Choose one of your dudes to learn this Hex") 
      elif re.search(r'Miracle',card.Keywords): potentialHosts = findTarget('Targeted-atDude_and_Blessed-isUnbooted-targetMine',choiceTitle = "Choose one of your dudes to get this inspired with this Miracle") 
      elif re.search(r'Shaman',card.Keywords): potentialHosts = findTarget('Targeted-atDude_and_Shaman-isUnbooted-targetMine',choiceTitle = "Choose one of your dudes to communicate with this Spirit") 
      else: potentialHosts = findTarget('Targeted-atDude-isUnbooted-targetMine',choiceTitle = "Choose one of your dudes to learn this Spell") 
   elif card.Name == 'Blight Serum': # Blight Serum is a special case and it attaches to both Dudes and Deeds.
      potentialHosts = findTarget('Targeted-atDude_or_Deed-isUnbooted-targetMine',choiceTitle = "Choose one of your dudes to receive these goods") 
   else: potentialHosts = findTarget('Targeted-atDude-isUnbooted-targetMine',choiceTitle = "Choose one of your dudes to receive these goods") 
   if len(potentialHosts) == 0: # If they haven't targeted a normally valid card, we try to discover one they've just targeted anyway
      potentialHosts = findTarget('Targeted-atDeed_or_Dude_or_Outfit',choiceTitle = "Choose one of your dudes to attach this {}".format(card.Type)) # If they manually targeted a card, we let them go through with it, in case they know something we don't
   if len(potentialHosts) == 0: # If they haven't targeted a card, we try to discover one
      if re.search(r'Improvement',card.Keywords): potentialHosts = findTarget('DemiAutoTargeted-atDeed-choose1') 
      elif re.search(r'Condition',card.Keywords): potentialHosts = findTarget('DemiAutoTargeted-choose1',choiceTitle = "Choose one of your cards attach this condition") 
      elif card.type == 'Spell':
         if re.search(r'Hex',card.Keywords): potentialHosts = findTarget('DemiAutoTargeted-atDude_and_Huckster-choose1-targetMine',choiceTitle = "Choose one of your dudes to learn this Hex") 
         elif re.search(r'Miracle',card.Keywords): potentialHosts = findTarget('DemiAutoTargeted-atDude_and_Blessed-choose1-targetMine',choiceTitle = "Choose one of your dudes to get inspired with this Miracle") 
         elif re.search(r'Shaman',card.Keywords): potentialHosts = findTarget('DemiAutoTargeted-atDude_and_Shaman-choose1-targetMine',choiceTitle = "Choose one of your dudes to communicate with this Spirit") 
         else: potentialHosts = findTarget('DemiAutoTargeted-atDude-choose1-targetMine',choiceTitle = "Choose one of your dudes to learn this Spell") 
      else: potentialHosts = findTarget('DemiAutoTargeted-atDude-choose1',choiceTitle = "Choose one of your dudes to receive these goods") 
   debugNotify("Finished gatherting potential hosts",2)
   if len(potentialHosts) == 0: # If they still didn't select a target, we abort.
      delayed_whisper(":::ERROR::: Please Target a valid dude for these goods")
      result = None
   else: result = potentialHosts[0] # If a propert host is targeted, then we return it to the calling function. We always return just the first result.
   debugNotify("<<< findHost() with result {}".format(result), 3)
   return result

def attachCard(attachment,host,facing = 'Same'):
   debugNotify(">>> attachCard(){}".format(extraASDebug())) #Debug
   hostCards = eval(getGlobalVariable('Host Cards'))
   hostCards[attachment._id] = host._id
   setGlobalVariable('Host Cards',str(hostCards))
   if host.controller != me:
      attachment.moveToTable(0,0)
      giveCard(attachment,host.controller)
      remoteCall(host.controller,'orgAttachments',[host,facing])
   else: orgAttachments(host,facing)
   debugNotify("<<< attachCard()", 3)
   
def clearAttachLinks(card,type = 'Discard'):
# This function takes care to discard any attachments of a card that left play
# It also clear the card from the host dictionary, if it was itself attached to another card
   debugNotify(">>> clearAttachLinks()") #Debug
   hostCards = eval(getGlobalVariable('Host Cards'))
   cardAttachementsNR = len([att_id for att_id in hostCards if hostCards[att_id] == card._id])
   if cardAttachementsNR >= 1:
      hostCardSnapshot = dict(hostCards)
      for attachmentID in hostCardSnapshot:
         if hostCardSnapshot[attachmentID] == card._id:
            if Card(attachmentID) in table: 
               debugNotify("Attachment exists. Trying to remove.", 2)      
               discard(Card(attachmentID)) # We always just discard attachments 
            del hostCards[attachmentID]
   debugNotify("Checking if the card is attached to unlink.", 2)      
   if hostCards.has_key(card._id):
      hostCard = Card(hostCards[card._id])
      del hostCards[card._id] # If the card was an attachment, delete the link
      setGlobalVariable('Host Cards',str(hostCards)) # We store it before calling orgAttachments, so that it has the updated list of hostCards.
      orgAttachments(hostCard) 
   else: setGlobalVariable('Host Cards',str(hostCards))
   debugNotify("<<< clearAttachLinks()", 3) #Debug   

def unlinkHosts(card): #Checking if the card is attached to unlink.
   debugNotify(">>> returnHostTokens()") #Debug
   hostCards = eval(getGlobalVariable('Host Cards'))
   if hostCards.has_key(card._id):
      hostCard = Card(hostCards[card._id])
      del hostCards[card._id] # If the card was an attachment, delete the link
      setGlobalVariable('Host Cards',str(hostCards)) # We need to store again before orgAttachments takes over
      orgAttachments(hostCard) # Reorganize the attachments if the parent is not a daemon-type card.
   debugNotify("<<< returnHostTokens()", 3) #Debug   
   

def orgAttachments(card,facing = 'Same'):
# This function takes all the cards attached to the current card and re-places them so that they are all visible
# xAlg, yAlg are the algorithsm which decide how the card is placed relative to its host and the other hosted cards. They are always multiplied by attNR
   global TownSquareToken
   if card.controller != me: 
      remoteCall(card.controller,'orgAttachments',[card,facing])
      return
   debugNotify(">>> orgAttachments()") #Debug
   attNR = 1
   debugNotify(" Card Name : {}".format(card.name), 4)
   if specialHostPlacementAlgs.has_key(card.name):
      debugNotify("Found specialHostPlacementAlgs", 3)
      xAlg = specialHostPlacementAlgs[card.name][0]
      yAlg = specialHostPlacementAlgs[card.name][1]
      debugNotify("Found Special Placement Algs. xAlg = {}, yAlg = {}".format(xAlg,yAlg), 2)
   else: 
      debugNotify("No specialHostPlacementAlgs", 3)
      xAlg = 0 # The Default placement on the X axis, is to place the attachments at the same X as their parent
      yAlg = -(cwidth() / 4)
   hostCards = eval(getGlobalVariable('Host Cards'))
   cardAttachements = [Card(att_id) for att_id in hostCards if hostCards[att_id] == card._id]
   x,y = card.position
   for attachment in cardAttachements:
      if facing == 'Faceup': FaceDown = False
      elif facing == 'Facedown': FaceDown = True
      else: # else is the default of 'Same' and means the facing stays the same as before.
         if attachment.isFaceUp: FaceDown = False
         else: FaceDown = True
      if attachment.controller != me: remoteCall(attachment.controller,'giveCard',[attachment,me])
      attachment.moveToTable(x + (xAlg * attNR), y + (yAlg * attNR),FaceDown)
      if FaceDown: attachment.peek()
      attachment.index = len(cardAttachements) - attNR # This whole thing has become unnecessary complicated because sendToBack() does not work reliably
      debugNotify("{} index = {}".format(attachment,attachment.index), 4) # Debug
      attNR += 1
      debugNotify("Moving {}, Iter = {}".format(attachment,attNR), 4)
   card.sendToFront() # Because things don't work as they should :(
   sendBack(TownSquareToken)
   remoteCall(card.controller,'sendBackOoTToken',[])
   if debugVerbosity >= 4: # Checking Final Indices
      for attachment in cardAttachements: notify("{} index = {}".format(attachment,attachment.index)) # Debug
   debugNotify("<<< orgAttachments()", 3) #Debug      

def sendBack(card): # Function which asks the current card controller to send it to the background (to avoid OCTGN complaining)
   mute()
   if card.controller == me: card.sendToBack()
   else: remoteCall(card.controller,'sendBack',[card])

def sendBackOoTToken():
   global OutOfTownToken
   sendBack(OutOfTownToken)

def reduceCost(card, action = 'PLAY', fullCost = 0, dryRun = False, reversePlayer = False): 
   # reversePlayer is a variable that holds if we're looking for cost reducing effects affecting our opponent, rather than the one running the script.
   global costReducers,costIncreasers
   type = action.capitalize()
   #if fullCost == 0: return 0 # Not used as we now have actions which also increase costs
   fullCost = abs(fullCost)
   reduction = 0
   ### First we check if the card has an innate reduction.
   Autoscripts = CardsAS.get(card.model,'').split('||')
   if len(Autoscripts):
      debugNotify("Checking for onPay reductions")
      for autoS in Autoscripts:
         if not re.search(r'onPay', autoS):
            debugNotify("No onPay trigger found in {}!".format(autoS), 2)
            continue
         reductionSearch = re.search(r'Reduce([0-9S]+)Cost({}|All)'.format(type), autoS)
         oppponent = ofwhom('-ofOpponent')
         if reductionSearch.group(1) == 'S': # S is for Special reductions, like Ivor Howley
            if card.model == 'e1d93d5b-222d-4a82-b18f-62728f7791c0': # Ivor Howley xp
               count = len([c for c in table if re.search(r'Abomination',c.Keywords)])
               for pl in getActivePlayers(): count += len([c for c in pl.piles['Boot Hill'] if re.search(r'Abomination',c.Keywords)])
               multiplier = 1
            elif card.model == '711deb54-4548-4206-81af-77d5dcc8793a': #Morgan Lash
                wantedDudes = findTarget("AutoTargeted-atDude-hasMarker{Bounty}-targetMine")
                print(len(wantedDudes))
                maxBounty = 0
                
                for dude in wantedDudes:
                    if dude.markers[mdict['Bounty']] > maxBounty:
                        maxBounty = int(dude.markers[mdict['Bounty']])
                print(maxBounty)
                print(wantedDudes)
                print(dude.markers[mdict['Bounty']])
                count = maxBounty
                multiplier = 1 
                
            elif card.name == "Wyatt Earp":
               count = len([c for c in pl.piles['Boot Hill'] if c.Type == 'Dude' and c.Outfit == 'Law Dogs'])
               multiplier = 2
            elif card.name == 'Dr. Gregory Tremane':            
               count = len([c for c in table if re.search(r'Gadget',c.Keywords) and c.controller == me])
               multiplayer = 1
         else:
            count = num(reductionSearch.group(1))
            targetCards = findTarget(autoS,card = card)
            multiplier = per(autoS, card, 0, targetCards)
         reduction += (count * multiplier)
         if reduction > fullCost: reduction = fullCost
         fullCost -= (count * multiplier)
         if reduction > 0 and not dryRun: notify("-- {}'s full cost is reduced by {}".format(card,reduction))
   return reduction
   
#------------------------------------------------------------------------------
#  Online Functions
#------------------------------------------------------------------------------
      
def fetchCardScripts(group = table, x=0, y=0, silent = False): # Creates 2 dictionaries with all scripts for all cards stored, based on a web URL or the local version if that doesn't exist.
   debugNotify(">>> fetchCardScripts()") #Debug
   ### Note to self. Switching on Debug Verbosity here tends to crash the game.probably because of bug #596
   global CardsAA, CardsAS # Global dictionaries holding Card AutoActions and Card autoScripts for all cards.
   if not silent: whisper("+++ Fetching fresh scripts. Please Wait...")
   if len(getPlayers()) > 1 and debugVerbosity < 0: # Skipping this always for now.
      try: (ScriptsDownload, code) = webRead('https://raw.github.com/db0/Doomtown-Reloaded-OCTGN/master/o8g/Scripts/CardScripts.py',5000)
      except: 
         if debugVerbosity >= 0: notify("Timeout Error when trying to download scripts")
         code = ScriptsDownload = None
   else: # If we have only one player, we assume it's a debug game and load scripts from local to save time.
      if debugVerbosity >= 0: notify("Skipping Scripts Download for faster debug")
      code = 0
      ScriptsDownload = None
   debugNotify("code: {}, text: {}".format(code, ScriptsDownload)) #Debug
   if code != 200 or not ScriptsDownload or (ScriptsDownload and not re.search(r'ANR CARD SCRIPTS', ScriptsDownload)): 
      #whisper(":::WARNING::: Cannot download card scripts at the moment. Will use locally stored ones.")
      Split_Main = ScriptsLocal.split('=====') # Split_Main is separating the file description from the rest of the code
   else: 
      #WHAT THE FUUUUUCK? Why does it gives me a "value cannot be null" when it doesn't even come into this path with a broken connection?!
      #WHY DOES IT WORK IF I COMMENT THE NEXT LINE. THIS MAKES NO SENSE AAAARGH!
      #ScriptsLocal = ScriptsDownload #If we found the scripts online, then we use those for our scripts
      Split_Main = ScriptsDownload.split('=====')
   if debugVerbosity >= 5:  #Debug
      notify(Split_Main[1])
      notify('=====')
   Split_Cards = Split_Main[1].split('.....') # Split Cards is making a list of a different cards
   if debugVerbosity >= 5: #Debug
      notify(Split_Cards[0]) 
      notify('.....')
   for Full_Card_String in Split_Cards:
      if re.search(r'ENDSCRIPTS',Full_Card_String): break # If we have this string in the Card Details, it means we have no more scripts to load.
      Split_Details = Full_Card_String.split('-----') # Split Details is splitting the card name from its scripts
      if debugVerbosity >= 5:  #Debug
         notify(Split_Details[0])
         notify('-----')
      # A split from the Full_Card_String always should result in a list with 2 entries.
      if debugVerbosity >= 5: notify(Split_Details[0].strip()) # If it's the card name, notify us of it.
      Split_Scripts = Split_Details[2].split('+++++') # List item [1] always holds the two scripts. autoScripts and AutoActions.
      CardsAS[Split_Details[1].strip()] = Split_Scripts[0].strip()
      CardsAA[Split_Details[1].strip()] = Split_Scripts[1].strip()
      if debugVerbosity >= 5: notify(Split_Details[0].strip() + "-- STORED")
   if debugVerbosity >= 5: # Debug
      notify("CardsAS Dict:\n{}".format(str(CardsAS)))
      notify("CardsAA Dict:\n{}".format(str(CardsAA))) 
   debugNotify("<<< fetchCardScripts()") #Debug
   
      
#------------------------------------------------------------------------------
# Debugging
#------------------------------------------------------------------------------
   
def TrialError(group, x=0, y=0): # Debugging
   global debugVerbosity
   mute()
   ######## Testing Corner ########
   #findTarget('Targeted-atVehicle_and_Fighter_or_Character_and_nonWookie')
   #BotD.moveToTable(0,0) 
   ###### End Testing Corner ######
   #notify("### Setting Debug Verbosity")
   if debugVerbosity >=0: 
      if debugVerbosity == 0: 
         debugVerbosity = 1
         #ImAProAtThis() # At debug level 1, we also disable all warnings
      elif debugVerbosity == 1: debugVerbosity = 2
      elif debugVerbosity == 2: debugVerbosity = 3
      elif debugVerbosity == 3: debugVerbosity = 4
      else: debugVerbosity = 0
      notify("Debug verbosity is now: {}".format(debugVerbosity))
      return
   notify("### Checking Players")
   for player in players:
      if player.name == 'db0' or player.name == 'dbzer0' or player.name == 'null': debugVerbosity = 0
   notify("### Checking Debug Validity")
   if not (len(players) == 1 or debugVerbosity >= 0): 
      whisper("This function is only for development purposes")
      return
   notify("### Setting Table Side")
   if not playerside:  # If we've already run this command once, don't recreate the cards.
      chooseSide()

def extraASDebug(Autoscript = None):
   if Autoscript and debugVerbosity >= 3: return ". Autoscript:{}".format(Autoscript)
   else: return ''

def addC(cardModel,count = 1): # Quick function to add custom cards on the table depending on their GUID
# Use the following to spawn a card
# remoteCall(me,'addC',['<cardGUID>'])
   card = table.create(cardModel, 0,0, count, True)
   
   