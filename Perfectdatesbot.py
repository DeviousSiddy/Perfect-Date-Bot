import discord
import random
import dbf
from dbfread import DBF


client = discord.Client()
#states = ['IDLE','START','DEAL','MATCH','COUNTER','RESULTS']
states = ['IDLE','START/DEAL','MATCH','COUNTER','RESULTS']
state = states[0]

cards = DBF('db\CARDS.DBF')
lc = len(cards)
cardIDs = list(range(0,lc - 1))

flags = DBF('db\FLAGS.DBF')
lf = len(flags)
flagIDs = list(range(0,lf - 1))

players = []
playersID = []
maxplayers = 3
playercards = []
playerchoices = []
currplayer = 0
cardmaxperhand = 6
flagsmaxperhand = 4
contestantname = ''

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    global state, players, playersID, cardIDs, flagIDs, playercards, playerflags, maxplayers, currplayer,contestantname, playerchoices
    ##if message.channel.name=='perfect-date':
    if message.author == client.user:
        return

    if message.content.startswith('pd.hello'):
        await message.channel.send('Hello!')
        return
    
    if message.content.startswith('pd.emrestart'):
        reset()
        await message.channel.send('We had an emergency and needed to restart! \nMessage pd.start to begin again.')
        return

    
        

    if (state == states[0]):
        if message.content.startswith('pd.help'):
            await message.channel.send('pd.players <number>\nSets the number of max players. Minimal of 3 players possible.\n\npd.start\nStarts a game.\n\npd.emrestart\nResets the game.\n\npd.cadd <card description>\nAdd a custom card to the game.\n\npd.fadd <flag description>\nAdd a custom Red Flag to the game.')
            
        elif message.content.startswith('pd.cadd'):
            temp = message.content
            csugg = temp[8:]
            #csugg.replace(" ", "")
            if len(csugg) > 5: #needs more spam protection.
                authname = message.author.name
                #need to clean up... using 2 dbf classes.
                cards.load()
                camt = len(cards)
                

                cid = int(cards.records[camt-1]['ID'])+1
                cards.unload()
                cardsedit = dbf.Table('db\CARDS.DBF')
                cardsedit.open(mode=dbf.READ_WRITE)

                cardsedit.append((cid,csugg,authname))
                cardsedit.close()
                cards.load()
                lc = len(cards)
                cards.unload()
                cardIDs = list(range(0,lc - 1))
                await message.channel.send('Added card "' + csugg+'" by '+authname+'.')
            else:
                await message.channel.send('Error. Please try again')
                
            
            return
        elif message.content.startswith('pd.fadd'):
            temp = message.content
            csugg = temp[8:]
            #csugg.replace(" ", "")
            if len(csugg) > 5: #needs more spam protection.
                authname = message.author.name
                #need to clean up... using 2 dbf classes.
                flags.load()
                camt = len(flags)
                

                cid = int(flags.records[camt-1]['ID'])+1
                cards.unload()
                cardsedit = dbf.Table('db\FLAGS.DBF')
                cardsedit.open(mode=dbf.READ_WRITE)

                cardsedit.append((cid,csugg,authname))
                cardsedit.close()
                flags.load()
                lf = len(flags)
                flagIDs = list(range(0,lf - 1))
                flags.unload()
                await message.channel.send('Added Red Flag "' + csugg+'" by '+authname+'.')
            else:
                await message.channel.send('Error. Please try again')
                
            
            return
        elif message.content.startswith('pd.players'):#a way to change amount of players.
            temp = message.content
            choice = temp[10:]
            choice = choice.replace(" ", "")
            if len(choice) != 1:
                await message.channel.send('Error. Please try again')
            else:
                temp = int(choice)
                if temp < 3:
                    await message.channel.send('There cannot be less than 3 players.')
                else:
                    maxplayers = choice
                    await message.channel.send('Setting set. Now '+ maxplayers +' players can play.')         
            return
        elif message.content.startswith('pd.start'):#game start
            state = states[1]
            await message.channel.send('Hello! \nWelcome to a new game of Perfect Dates. \nThe game that is definitely NOT a card game. \nIn this game we can only have 4 contestants. So make sure to know who will join. \nCan the first contestant write pd.enter, please?')
            
            return
        

    if (state == states[1]): #Player register and card dealing
        if message.content.startswith('pd.enter'):
            a = message.author
            n = a.name
            if n in players:
                i = players.index(n)
                await message.channel.send('We already have registered ' + players[i] + ' as our player ' + format(i + 1))
            else:
                players.append(n)
                playersID.append(a)
                curplayer = len(players)
                await message.channel.send('We registered ' + players[curplayer - 1] + ' as our player ' + format(curplayer))

                if (maxplayers == curplayer):
                    state = states[2]
#                    await message.channel.send('We seem to have enough players
#                    now!  Welcome our special contestants: \nPlayer 1: ' +
#                    players[0] + '\nPlayer 2: ' + players[1])
                    m = 'We seem to have enough players now! Welcome our special contestants: \n'
                    for p in players:
                        m = m + "Player " + str(players.index(p)+1) + ': ' + p + '\n'
                    await message.channel.send(m)
                    #amtcards = 0:2
                    #amtflags = 0:1

                    contestantID = random.randint(0,len(players) - 1)
                    contestantname = players[contestantID]

                    for p in players:
                        #card dealing
                        cards.load()
                        flags.load()
                        if p == contestantname: #contestant gets no cards
                            for iter in range(0,(cardmaxperhand+flagsmaxperhand)):
                                playercards.append('null')
                            
                        else:
                            #card displaying
                            playerindex = players.index(p)
                            dealmessage = 'Here are your cards: \n'
                            
                            cardi = 1
                            for c in range(0,cardmaxperhand):
                                if len(cardIDs) < (cardmaxperhand * (maxplayers - 1)): #reset cards when deck contains less cards than needed for round
                                    cardIDs = list(range(0,lc - 1))
                                cardID = cardIDs[random.randint(0,(len(cardIDs) - 1))]
                                cardIDs.remove(cardID)
                                playercards.append(cardID)
                                
                                dealmessage = dealmessage + str(cardi) + '. ' + cards.records[cardID]['DESC'] + '\n'
                                cardi = cardi + 1

                            dealmessage = dealmessage + '\n\nHere are your flags: \n'
                            for c in range(0,flagsmaxperhand):                                
                                if len(flagIDs) < (flagsmaxperhand * (maxplayers - 1)): #reset flags when deck contains less flags than needed for round
                                    flagIDs = list(range(0,lf - 1))
                                flagID = flagIDs[random.randint(0,(len(flagIDs) - 1))]
                                flagIDs.remove(flagID)
                                playercards.append(flagID)
                                dealmessage = dealmessage + str(cardi) + '. ' + flags.records[flagID]['DESC'] + '\n'
                                cardi = cardi + 1

                            #playercards filled with cardsIDs.  Now send cards
                            #to players.
                            await playersID[playerindex].send(dealmessage)
                        cards.unload()
                        flags.unload()

                                
                    await message.channel.send('Cards are dealt. Your cards are in your DMs. Please look at them there. \nI will call out your name, after wich you can select a card to describe the Perfect Date for the contestant.')
                    
                    
                    await message.channel.send('\n\n' + contestantname + ' will be the first contestant.')
                    
                    currplayer = 0 #start with Player 1
                    if players[0] == contestantname:
                        currplayer = 1 #else with Player 2
                        playerchoices.append(100000)
                        playerchoices.append(100000)
                                               
                    await message.channel.send('\n\n' + players[currplayer] + ', choose two cards to describe the Perfect Date for ' + contestantname + ' with pd.select <cardnumber>, <cardnumber>')
                    

                    state = states[2]
                    return
                    
                    
                
    if (state == states[2]): # Matching phase
        if message.content.startswith('pd.select'):
            if message.author.name == contestantname:
                playerchoices.append(100000)
                playerchoices.append(100000)
            elif message.author.name == players[currplayer] and message.author.name != contestantname:
                
                temp = message.content
                choice = temp[10:]
                choice.replace(" ", "")
                if choice.count(',') != 1:
                    await message.channel.send('Error. Did you not use a comma (,) or too many? Remember that you can only choose 2 cards. Please try again.')
                elif len(choice) != 3:
                    await message.channel.send('Error. Remember that you can only choose 2 cards. So "pd.select <cardnumber>, <cardnumber>". Please try again')
                else:
                    choice1 = int(choice[0])
                    choice2 = int(choice[2])
                    if (choice1 > cardmaxperhand) or (choice2 > cardmaxperhand) or (choice1 < 1) or (choice2 < 1):
                        await message.channel.send('Error. You chose flags. Or an impossible card number. Either way, please try again')
                    else:
                        choice1 = choice1 - 1 + currplayer * (cardmaxperhand + flagsmaxperhand)
                        choice2 = choice2 - 1 + currplayer * (cardmaxperhand + flagsmaxperhand)
                        
                        #handle card choice
                        playerchoices.append(playercards[choice1])
                        playerchoices.append(playercards[choice2])

                        cards.load()
                        m = 'Player ' + players[currplayer] + ', present your choices:\nThe traits ' + contestantname + '\'s Date has is: \n1. ' + cards.records[playercards[choice1]]['DESC'] + '\n2. ' + cards.records[playercards[choice2]]['DESC']
                        cards.unload()
                        
                        

                        #move to next player
                        currplayer = currplayer + 1
                        if currplayer<maxplayers: 
                            if players[currplayer]==contestantname:#if contestant then move 1
                                currplayer = currplayer + 1
               
                
                        #move state when all players went.
                        if currplayer >= maxplayers:
                            state = states[3]
                            if players[0] == contestantname:
                                currplayer = 1                        
                            else:
                                currplayer = 0

                            nextplayer = nextplayercheck()
                            #nextplayer = currplayer + 1
                            #if players[nextplayer] == contestantname:
                            #    nextplayer = currplayer + 2
                            #if nextplayer >= maxplayers:
                            #    nextplayer = 0
                            #    if players[nextplayer] == contestantname:
                            #        nextplayer = 1                     
                            
                            await message.channel.send(m+'\n\n' + players[currplayer] + ', choose a Red Flag to describe ' + players[nextplayer] + '\'s Date for ' + contestantname + ' with pd.select <cardnumber>')
                            return
                        else:
                            await message.channel.send(m+'\n\n' + players[currplayer] + ', choose two card to describe the Perfect Date for ' + contestantname + ' with pd.select <cardnumber>, <cardnumber>')
                            return

    if (state == states[3]): #Flag phase
        if message.content.startswith('pd.select'):
            if message.author.name == players[currplayer] and message.author.name != contestantname:
                
                temp = message.content
                choice = temp[10:]
                choice.replace(" ", "")
                if choice.count(',') != 0:
                    await message.channel.send('Error. Did you use a comma (,)? Remember that you can only choose 1 card. Please try again.')
                elif len(choice) > 2:
                    await message.channel.send('Error. Remember that you can only choose 1 Red Flag. So "pd.select <cardnumber>". Please try again')
                else:
                    choice1 = int(choice)
                   
                    if (choice1 <= cardmaxperhand) or (choice1 >= cardmaxperhand + flagsmaxperhand):
                        await message.channel.send('Error. You chose Trait Cards. Or an impossible card number. Either way, please try again')
                    else:
                        choice1 = choice1 - 1 + currplayer * (cardmaxperhand + flagsmaxperhand)
                        targplaychoices = nextplayercheck()
                        #targplaychoices = currplayer + 1
                        #if players[targplaychoices] == contestantname:
                        #    targplaychoices = currplayer + 2
                        #if targplaychoices >= maxplayers:
                        #    targplaychoices = 0
                        #    if players[targplaychoices] == contestantname:
                        #        targplaychoices = 1

                        oldchoice1 = playerchoices[targplaychoices * 2]
                        oldchoice2 = playerchoices[(targplaychoices * 2) + 1]
                        #handle card choice
                        cards.load()
                        flags.load()
                        m = 'Player ' + players[currplayer] + ', present your case against ' + players[targplaychoices] + ':\nThe traits ' + contestantname + '\'s Date has was: \n1. ' + cards.records[oldchoice1]['DESC'] + '\n2. ' + cards.records[oldchoice2]['DESC'] + '\n\nBUT the Date also:\n' + flags.records[playercards[choice1]]['DESC']
                        cards.unload()
                        flags.unload()
                        
                        

                        #move to next player
                        currplayer = currplayer + 1
                        if currplayer<maxplayers: 
                            if players[currplayer]==contestantname:#if contestant then move 1
                                currplayer = currplayer + 1
                
                        #move state when all players went.
                        if currplayer >= maxplayers:
                            state = states[4]
                            m = m+'\n\nOK! ' + contestantname + ', You have heard about all your Dates.\nIt is time to choose your Perfect Date!\nWHO described your Perfect Date? (Please write pd.select <playernumber>)\n'
                            for p in players:
                                if p!=contestantname:
                                    m = m + "Player " + str(players.index(p)+1) + ': ' + p + '\n'
                            
                            await message.channel.send(m)
                            return
                        else:
                            nextplayer = nextplayercheck()
                            #nextplayer = currplayer + 1
                            #if players[nextplayer] == contestantname:
                            #    nextplayer = currplayer + 2
                            #if nextplayer >= maxplayers:
                            #    nextplayer = 0
                            #    if players[nextplayer] == contestantname:
                            #        nextplayer = 1

                            await message.channel.send(m+'\n\n' + players[currplayer] + ', choose a Red Flag to describe ' + players[nextplayer] + '\'s Date for ' + contestantname + ' with pd.select <cardnumber>')
                            return
                
    if (state == states[4]):            #Result phase and reset
        if message.content.startswith('pd.select'):
            if message.author.name == contestantname:
                temp = message.content
                choice = temp[10:]
                choice.replace(" ", "")
                if choice.count(',') != 0:
                    await message.channel.send('Error. Did you use a comma (,)? Remember that you can only choose 1 winner. Please try again.')
                elif len(choice) != 1:
                    await message.channel.send('Error. Remember that you can only choose 1 winner. So "pd.select <playernumber>". Please try again')
                else:
                    choice1 = int(choice)
                   
                    if (choice1 >= maxplayers) or (choice1 < 1):
                        await message.channel.send('Error. You did not choose a player. Either way, please try again')
                        return
                    else:
                        choice1 = choice1 - 1
                        await message.channel.send('Congratulations, ' + players[choice1] + '!!\nYou\'re Date is the Perfect Date for ' + contestantname + '!!\nCongratulations to the contestant for being less of a loner. Or condolences?\nAnyway, thanks for playing! At the moment you can only play 1 round at a time so if you want to play again, please type "pd.start".\nTill next time!')
                        reset()
                        return
 
def reset():
    global state, players, playersID, playercards, playerchoices, currplayer
    state = states[0]
    players = []
    playersID = []
    playercards = []
    playerchoices = []
    currplayer = 0

def nextplayercheck(): #check who next player is and return player #.
    global currplayer, contestantname, players, maxplayers
    nextplayer = currplayer + 1
    if players[nextplayer] == contestantname:
        nextplayer = currplayer + 2
    if nextplayer >= maxplayers:
        nextplayer = 0
        if players[nextplayer] == contestantname:
            nextplayer = 1
    return nextplayer




client.run('Njk5MzIxOTU0MDc0ODg2MjI1.XpUP8Q.Pyu1JLYdRPBqTfyrnPx4jQrejd8')