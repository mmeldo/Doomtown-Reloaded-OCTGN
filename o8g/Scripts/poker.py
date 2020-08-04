#---------------------------------------------------------------------------
# Poker Hand Evaluation scripts
#---------------------------------------------------------------------------
   
def PokerHand(rank,suit,type = shootout, result = 'normal'): # Evaluates 5 cards to find which poker hand they create.
   jokers = 0 # A counter to remember how many jokers we have in our hand
   for value in suit: 
      if value == 'Joker': jokers += 1 # Go through the hand and count the jokers available.
   numranks = [numrank(rank[0]), numrank(rank[1]), numrank(rank[2]), numrank(rank[3]), numrank(rank[4])] # Convert the hand into strict integers
   srank = sorted(numranks) # Sort the integers ascending. This is useful for checking for straights
   asuits = [asuit(suit[0]), asuit(suit[1]), asuit(suit[2]), asuit(suit[3]), asuit(suit[4])] # Convert suits
   ssuit = sorted(asuits) # Sort the suits ascending. This is useful for checking for flushes
   chkpairs = pairschk(rank,jokers,type) # So that we don't run the procedure 6 times unnecessarily.
   debugNotify("+++ PokerHand() pairs and high cards: {}".format(chkpairs))
# Look for Dead Man's Hand
   if checkDMH(rank,suit,jokers,type) == 1: 
      if result == 'comparison': 
          chkpairs[0] = 11
          return chkpairs
      else: return "11: Dead Man's Hand!"
# Look for five of a kind
   if chkpairs[0] == 5:  
      if result == 'comparison': 
          chkpairs[0] = 10
          return chkpairs
      else: return "10: Five of a Kind"
# Look for four of a kind
   elif chkpairs[0] == 4:  
      if result == 'comparison': 
          chkpairs[0] = 8
          return chkpairs
      else: return "8: Four of a Kind"
# Look for Full House
   elif chkpairs[0] == 32:  
      if result == 'comparison': 
          chkpairs[0] = 7
          return chkpairs
      else: return '7: Full House'
# Look for a Flush
   elif flushchk(ssuit,jokers,type) == 1: 
      if straightchk(srank,jokers,type) == 1:  
         if result == 'comparison': 
             chkpairs[0] = 9
             return chkpairs
         else: return "9: Straight Flush"
      else:  
         if result == 'comparison': 
             chkpairs[0] = 6
             return chkpairs
         else: return "6: Flush"
# Look for a straight
   elif straightchk(srank,jokers,type) == 1:  
      if result == 'comparison': 
          chkpairs[0] = 5
          return chkpairs
      else: return "5: Straight"
# Look for Three of a Kind
   elif chkpairs[0] == 3:  
      if result == 'comparison': 
          chkpairs[0] = 4
          return chkpairs
      else: return '4: Three of a kind'
# Look for Two Pairs
   elif chkpairs[0] == 2:  
      if result == 'comparison': 
          chkpairs[0] = 3
          return chkpairs
      else: return '3: Two Pairs'
# Look for One Pair
   elif chkpairs[0] == 1:  
      if result == 'comparison': 
          chkpairs[0] = 2
          return chkpairs
      else: return '2: One Pair'
# If none of the above is true, return a high card result.   
   else:  
      if result == 'comparison': 
          chkpairs[0] = 1
          return chkpairs
      else: return '1: High Card'

def numrank(rank, ask = False): # Convert card ranks into pure integers for comparison
   if rank == '*': 
      if ask: 
         failsafe = 0
         joker = askInteger("Please type a rank for the Joker (1-13)", 13)
         while joker > 13 or joker < 1: 
            joker = askInteger("Please type a rank for the Joker (1-13)", 13)
            failsafe += 1
            if failsafe == 4: break 
         if joker == 1 or joker > 10: notify(":>> {} sets the rank of the joker as {}".format(me,{1:'Ace',11:'Jack',12:'Queen',13:'King'}.get(joker)))
         else: notify(":>> {} sets the rank of the joker as {}".format(me,joker))
         return joker
      else: return 13
   elif rank == 'A': return 1
   elif rank == 'J': return 11
   elif rank == 'Q': return 12
   elif rank == 'K': return 13
   else: return num(rank)
   
def asuit(suit): # Convert card suits to single letters for sorting
   if suit == 'Joker':
      return '*'
   else:
      return suit[0]
   
def pairschk(rank,jokers = 0,type = shootout): 
# This function checks the hand for similar ranks and depending on how many it finds, it returns the appropriate hand code.
   i = 0
   j = 1
   valueMatch1 = 0
   valueMatch2 = 0
   valueSingles = []
   highCards = [0,[],[],0,0,0] # 6 items so the index represents the number of kind (e.g. index 3 contains 3oK), and 0 index for number of matching cards
   pairs = [0,0,0,0,0] 
# The above variable is where we'll be storing the matches we find for each hand. 
# The first pair we find will be labeled 1 and the second 2 as long as it's not the same rank as 1.
# This is for prevent us from counting the same pairing more than once. 
# In the end, we'll have a list where each digit is either 0, 1 or 2. 0 means this card's rank matches no other card in the hand
# 1 and 2 means that this card's rank is the same as all the others which are labeled with the same number
# So for example [1,0,1,2,2] is two pairs and [1,1,2,1,2] is full house.
   match1 = 0 # These will count in the end how many matches per rank we have. 
   match2 = 0
   op1 = 5 # These are used to point which was the first card where we found a match of this number.
   op2 = 5
   while i < 4: 
      while j < 5: # We start a nested while. First we check the first card with all the others. 
                   # Then the second one with the 3rd, 4th and 5th.
                   # Then 3rd with 4th and 5th and finally 4th and 5th.
                   # Always excluding jokers.
         if rank[i] == rank[j] and rank[i] != '*': # If we find a match (but we don't care about matching jokers)
#            notify("comparing rank[{}] = {} with rank[{}] = {}".format(i,rank[i],j,rank[j])) # Used for testing
            if op1 == 5: # If our first pointer has not been set
               op1 = i # Put our pointer on the first card of the match
               pairs[i] = 1 # Set the position of those cards to belong to the first matching.
               pairs[j] = 1
            elif rank[op1] == rank[j]: #If the pointer shows that the match belongs to the first group.
               pairs[j] = 1 # set the currently checked card's position to belong to the first group.
            elif op2 == 5: # If there is no match with the first pointer, then use the second one
               op2 = i
               pairs[i] = 2
               pairs[j] = 2
            elif rank[op2] == rank[j]: # Same process
               pairs[j]=2
#            notify("pairs[{},{},{},{},{}]".format(pairs[0],pairs[1],pairs[2],pairs[3],pairs[4])) # Used for testing
         j += 1 
      i += 1 # here we increment the parent loop by one
      j = i+1 # And we set the second loop's iterator to start at one position further.
   pairingIndex = 0
   for pair in pairs: # Now we count how many matching cards we have for each group
      if pair == 1: 
          match1 += 1
          valueMatch1 = numrank(rank[pairingIndex])
      elif pair == 2: 
          match2 += 1
          valueMatch2 = numrank(rank[pairingIndex])
      else:
          if rank[pairingIndex] != '*': valueSingles.append(numrank(rank[pairingIndex]))
      pairingIndex += 1
   debugNotify("match1 = {}, match2 = {}, valueSingles = {}, type == {}".format(match1, match2, valueSingles, type)) # Used for testing
   if jokers:
      valueSingles.sort()
      workList = list(valueSingles)
      if valueMatch1: workList.append(valueMatch1)
      if valueMatch2: workList.append(valueMatch2)
      workList.sort()
      jokerValues = []
      jokerIndex = 0
      while jokerIndex < jokers:
         jokerValue = 1
         valueIndex = 0
         for singleValue in workList:
            if singleValue == jokerValue: 
               jokerValue += 1
            else: break
            valueIndex += 1
         jokerValues.append(jokerValue)
         workList.insert(valueIndex, jokerValue)
         jokerIndex += 1 
      valueSingles += jokerValues
   valueSingles.sort(reverse = True)
   if match1 == 5 or (match1 + jokers == 5 and type == shootout): # Finally we check for hand ranks. 5 sames are Five of a Kind
      highCards[5] = valueMatch1                                  # (Jokers count only in non-lowball hands)
      highCards[0] = 5
      return highCards
   if match1 == 4 or (match1 + jokers == 4 and type == shootout): # 4 Sames are Four of a Kind.
      highCards[4] = valueMatch1
      highCards[1] = valueSingles
      highCards[0] = 4
      return highCards
   if (match1 == 3 and match2 == 2) or (match1 + jokers == 3 and match2 == 2 and type == shootout): # Thee of a kind plus one pair is a Full House
      highCards[3] = valueMatch1
      highCards[2] = valueMatch2
      highCards[0] = 32
      return highCards
   if (match1 == 2 and match2 == 3) or (match1 == 2 and match2 + jokers == 3 and type == shootout): # Thee of a kind plus one pair is a Full House
      highCards[2] = valueMatch1
      highCards[3] = valueMatch2
      highCards[0] = 32
      return highCards
   if (match1 == 3 or # 3 sames is a Thee of a Kind
      (match1 + jokers == 3 and type == shootout) or # 1 pair and one joker is also a Three of a Kind
      (jokers == 2 and type == shootout)): # Also 2 jokers and nothing else is always at the least a Three of a Kind
      if jokers == 2 and type == shootout: 
         maxValue = valueSingles[len(valueSingles) - 1]
         highCards[3] = maxValue
         valueSingles.remove(maxValue)
      else: highCards[3] = valueMatch1
      highCards[1] = valueSingles
      highCards[0] = 3
      return highCards
   if match1 == 2 and match2 == 2: # 2 of each is Two Pairs 
      if valueMatch1 > valueMatch2:
         highCards[2].append(valueMatch1)
         highCards[2].append(valueMatch2)
      else:
         highCards[2].append(valueMatch2)
         highCards[2].append(valueMatch1)
      highCards[1] = valueSingles
      highCards[0] = 2
      return highCards
   if match1 == 2 or (jokers == 1 and type == shootout): # 2 matching cards is One Pair
      if jokers == 1 and type == shootout:               # And one joker with nothing else is always at least a pair.
         maxValue = valueSingles[len(valueSingles) - 1]
         highCards[2] = [maxValue]
         valueSingles.remove(maxValue)
      else: highCards[2] = [valueMatch1]
      highCards[1] = valueSingles
      highCards[0] = 1
      return highCards
   else: 
      highCards[1] = valueSingles
      return highCards
   
def checkDMH(rank,suit,jokers,type = shootout): # This function checks whether the player has a Dead Man's Hand
# A DMH is 2 black Aces (clubs & spades), 2 black eights (clubs & spades) and one Diamond Jack.
   i = 0
   count = 0
   DMH = [0,0,0,0,0] # Create a list. Each digit will become 1 if the corresponding card has been found for DMH.
   while i < 5:
      if rank[i] == '8' and suit[i] == 'Spades': DMH[0] = 1
      if rank[i] == '8' and suit[i] == 'Clubs': DMH[1] = 1
      if rank[i] == 'A' and suit[i] == 'Spades': DMH[2] = 1
      if rank[i] == 'A' and suit[i] == 'Clubs': DMH[3] = 1
      if rank[i] == 'J' and suit[i] == 'Diamonds': DMH[4] = 1
      i += 1
   for card in DMH:
      if card == 1: count += 1
   if count == 5 or (count + jokers == 5 and type == shootout): return 1
   else: return 0

def flushchk(suit,jokers,type = shootout): # Check if the player's hand is a flush.
   # suits are sorted, so we just have to compare the first and last
   if type == shootout:
      return suit[jokers] == suit[4] # jokers come first
   else:
      return suit[0] == suit[4]

def straightchk(rank,jokers,type = shootout): # Check if the player's hand is a straight.
   i = 0
   avjokers = jokers # count jokers being used up to prevent hands like Q 8 7 Joker Joker from being detected as straights
   straight = 0 # A counter to see how many serial numbers the player has
   while i < 4 - jokers: 
      if (rank[i] + 1 == rank[i+1] or # We increment our counter if the pair is serial or...
         (rank[i] + 2 == rank[i+1] and avjokers >= 1 and type == shootout) or # If the pair is two numbers away 
                                                                            # and the player has at least 1 joker to cover the gap
                                                                            # and this is a non-lowball hand or...
                                                                            # (because in lowball you don't want the jokers to be helping you get a higher hand)
         (rank[i] + 3 == rank[i+1] and avjokers == 2 and type == shootout)):  # If the pair is three numbers away 
                                                                            # and the player has 2 jokers to cover the gap
                                                                            # and this is not a lowball hand...
         straight +=1 # Then increase the counter marking how many straight pairs we have by 1.
         avjokers -= rank[i+1] - rank[i] - 1 # Decrease the count of available jokers
      i += 1
   if straight == 4 or (straight + jokers == 4 and type == shootout): return 1 # If we have 4 straight pairs (including the jokers), then it's a straight.
   else: return 0

def cheatinchk(rank,suit): # Check if the player is cheating (i.e. has 2 or more cards of the same suit & rank)
   i = 0
   j = 1
   while i < 4:
      while j < 5:
         if rank[i] == rank[j] and suit[i] == suit[j] and suit[i] != 'Joker': return " (Cheatin'!)"
         j += 1
      i += 1
      j = i + 1
   return ''
   
def fullsuit(suit): # This function simply returns the full suit of the various cards so that notifications read easily.
   if suit == "C": return "Clubs"
   elif suit == "S": return "Spades"
   elif suit == "D": return "Diamonds"
   elif suit == "H": return "Hearts"
   else: return suit
   
def fullrank(rank): # This function simply returns the full rank of non-numeral cards so that notifications read easily
   if rank == "Q": return "Queen of"
   elif rank == "J": return "Jack of"
   elif rank == "K": return "King of"
   elif rank == "A": return "Ace of"
   elif rank == "*": return "" # The Joker is announced from the Suit
   else: return "{} of".format(rank)
 
def clearHandRanks(): # Cleas player hand ranks so that comparisons can start anew
   debugNotify(">>> clearHandRanks().")
   for player in getActivePlayers():
      #player.HandRank = 0 # Make sure that all shootout handrank counters are cleared.
      if player != me: remoteCall(player,'clearMyHandRank',[])
      else: clearMyHandRank()
   debugNotify("<<< clearHandRanks().")
      
def clearMyHandRank():
   mute()
   #notify("====> clearing my handrank") # Debug
   me.setGlobalVariable('Hand Rank','N/A')
