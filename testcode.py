import gspread
from oauth2client.service_account import ServiceAccountCredentials
import discord
from discord.ext import commands, tasks
import datetime
import asyncio
import re
import random
import json
import math

intents = discord.Intents().all()
intents.members = True 

discordClient = commands.Bot(command_prefix = ">", help_command=None, intents=intents, case_insensitive=True)

scope = ["https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
sheetsClient = gspread.authorize(creds)
sheet = sheetsClient.open("Evil Within").sheet1

#CHANNEL_ID = 
#BOT_TOKEN = ""#


with open('DowntimeResults1.json') as x:
  downtimeJobs = json.load(x)

validJobs = []
for id in downtimeJobs:
	for job in downtimeJobs[id]["aliases"]:
		validJobs.append(job.upper())

players = []
characters = []
downtime = []
credits = []
lore = []
contacts = []
blackmail = []
Milestone = []
Level = []


updating = False

def updateData():
	global characters
	global downtime
	global players
	global credits
	global lore
	global contacts
	global blackmail 
	global Milestone
	global Level
	players = sheet.col_values(1)
	del players[0]
	characters = sheet.col_values(2)
	del characters[0]
	downtime = sheet.col_values(3)
	del downtime[0]
	credits = sheet.col_values(4)
	del credits[0]
	lore = sheet.col_values(5)
	del lore[0]
	contacts = sheet.col_values(6)
	del contacts[0]
	blackmail = sheet.col_values(7)
	del blackmail[0]
	Milestone = sheet.col_values(8)
	del Milestone[0]
	Level = sheet.col_values(9)
	del Level[0]


@discordClient.event
async def on_ready():
	print("Bot is ready.")
	downtimeIncrease.start()

@discordClient.event
async def on_member_remove(member):
	global players
	await asyncio.sleep(1800)
	guild = discordClient.get_guild(1049430235453608006)
	if member not in guild.members:
		updateData()
		for x in range(len(players) - 1, -1, -1):
			if int(players[x]) == member.id:
				sheet.delete_row(x + 2)

@discordClient.command()
async def help(ctx):
	await ctx.message.add_reaction('\U0001F44D')
	await ctx.author.send("```>initialise [character] [DTD]\nThis command begins tracking the downtime and resources of a character. If you have a pre-existing character you have just decided to track, fill in the DTD section with their current DTD, otherwise ignore that prompt. \n\n>checkDTD [character]\nThis command allows you to check how much DTD a given character has.\n\n>spendDTD [character] [DTD] \nThis command allows you to Milestoneend downtime on a given character.\n\n>delete [character]\nThis command removes a character from the database. Please use it when a character becomes unavaliable to avoid bloating the database.\n\n>deposit [character] [credits] [lore] [contacts] [blackmail] [Milestone]\nThis command allows you to deposit resources into a character's account. Deposits will not take effect until either a DM or downtime roller approves them by reacting to your message with a: \U0001F44D\n\n>withdraw [character] [credits][lore] [contacts] [blackmail]\nThis command allows you to withdraw resources from a character's account.\n\n>balance [character]\nThis command allows you to check how many resources a character has.\n\n>transfer [credits] [lore] [contacts] [blackmail] to [transfer recipient] from [your character]\nThis command transfers resources between two characters.\n\n>checkCharacters\nThis command returns the name, downtime, and balance of each character you are currently tracking.\n\n>roll [DTD] [job] for [character] with [modifier]\nThis command rolls downtime jobs for a given character, automatically spending the days and adding any resources gained. Valid jobs include:\n- Bounty Hunting\n- Carousing (Lower, middle, or upper)\n- Crime\n- Espionage (Lower, middle or upper)\n- Racing (Rented racing if you don't have a speeder)\n- Research \n- Mercenary contracting\n- Pitfighting\n- Work\n\nPLEASE ENSURE THAT WHEN USING THESE COMMANDS YOU DO NOT INCORPORATE THE [] BRACKETS```")

@discordClient.command(aliases=["initialize"])
async def initialise(ctx, *, message):
	updateData()
	limitExceptions = [225428121145311232]
	global updating
	global players
	if not updating:
		if players.count(str(ctx.author.id)) < 3 or ctx.author.id in limitExceptions:
			inputs = message.split(" ")
			global characters

			if inputs[-1] == "DTD" or inputs[-1] == "dtd":
				del inputs[-1]
			if inputs[0].upper() in characters: 
				output = "There is an existing character with the name " + inputs[0] + "."
				await ctx.send(output)
			else:
				try:
					if abs(int(inputs[-1])) > -1 and len(inputs) > 1:
						if abs(int(inputs[-1])) <= 60:
							name = ""
							for x in range(len(inputs) - 1):
								name += inputs[x].upper()
								name += " "
							name = name[:-1]
							newRow = [str(ctx.author.id), name, abs(int(inputs[-1])), 0, 0, 0, 0, 0, ".",]
							await ctx.message.add_reaction('\U0001F44D')
						else:
							await ctx.send("You cannot initialise a character with over 60 DTD.")
					else:
						newRow = [str(ctx.author.id), message.upper(), 30, 0, 0, 0, 0, 0, ".",]
						await ctx.message.add_reaction('\U0001F44D')
				except:
					newRow = [str(ctx.author.id), message.upper(), 30, 0, 0, 0, 0, 0, ".",]
					await ctx.message.add_reaction('\U0001F44D')
				sheet.insert_row(newRow, 2)
		else:
			await ctx.send("You are already tracking the downtime of 1 character")
	else:
		await ctx.send("You cannot initialise a character whilst the current downtime period is being applied. Please try again later.")

@discordClient.command(aliases=["untrack"])
async def delete(ctx, *, character):
	global updating
	guild = discordClient.get_guild(1049430235453608006)
	if not updating:
		updateData()
		DM = discord.utils.get(ctx.guild.roles, name="DMs")
		try:
			if players[characters.index(character.upper())] == str(ctx.author.id) or DM in ctx.author.roles:
				sheet.delete_row(characters.index(character.upper()) + 2)
				await ctx.message.add_reaction('\U0001F44D')
				await ctx.message.add_reaction('\U0001F1EB')
			else:
				await ctx.send("Only the person who created a character can delete them.")
		except:
			output = "There is no recorded character by the name: " + character.title() + "."
			await ctx.send(output)
	else:
		await ctx.send("You cannot delete a character whilst the current downtime period is being applied. Please try again later.")

@discordClient.command(aliases=["CharacterList", "checkChars", "getCharacters", "cc", "getChars"])
async def checkCharacters(ctx):
	updateData()
	global characters
	global players
	global downtime
	global credits
	global lore
	global contacts
	global blackmail
	global Milestone

	if str(ctx.author.id) not in players:
		message = "You are not currently tracking any characters."
	else:
		message = "The characters you are currently tracking are:\n\n"
		for x in range (len(players) - 1):
			if players[x] == str(ctx.author.id):
				message += characters[x].title() + ", with " + str(min(60, int(downtime[x]))) + " DTD and "  + credits[x] + " cr, " + lore[x] + " lore, " + contacts[x] + " contacts, " + blackmail[x] + " blackmail, " + Milestone[x] + " Milestone \n"
	await ctx.send(message)

@discordClient.command()
async def check(ctx, *, message):
	await ctx.send("Please use either >checkDTD , >checkCr , >checklore , >checkct , >checkbm.")

@discordClient.command()
async def spend(ctx, *, message):
	await ctx.send("Please use  >spendDTD , >spendCr ,>spendlore , >spendct , >spendbm.")

@discordClient.command()
async def spendDTD(ctx, *, message):
	updateData()
	global characters
	global downtime
	global players
	global updating
	inputs = message.split(" ")
	name = message[:-(len(inputs[-1]) + 1)]

	if name.upper() in characters:
		try:	
			inputs[-1] = abs(int(inputs[-1]))
			if players[characters.index(name.upper())] == str(ctx.author.id):
				if int(downtime[characters.index(name.upper())]) < int(inputs[-1]):
					output = name + " only has " + str(downtime[characters.index(name.upper())]) + " DTD."
					if updating:
						output += "\n\nPlease be aware that the ongoing DTD period is currently being applied, and so downtime tracking accuracy may vary."
					await ctx.send(output)
				else:
					sheet.update_cell(characters.index(name.upper()) + 2, 3, int(downtime[characters.index(name.upper())]) - int(inputs[-1]))
					await ctx.message.add_reaction('\U0001F44D')
			else:
				await ctx.send("Only the person who created a character can spend their downtime.")
		except:
			await ctx.send("Command invalid.")
	else:
		output = "Could not find a character named " + name.title() + "."
		await ctx.send(output)

@tasks.loop(minutes=1)
async def downtimeIncrease():
    global downtime
    global updating
    dt = datetime.datetime.utcnow()
    if (dt.day == 1 or dt.day == 15) and dt.hour == 5 and dt.minute == 30:
        updateData()
        updating = True
        for x in range(len(downtime)):
            if int(downtime[x]) + 30 > 60:
                sheet.update_cell(x + 2, 3, 60)
            else:
                sheet.update_cell(x + 2, 3, int(downtime[x]) + 30)
            await asyncio.sleep(1)
        updating = False

@discordClient.command(aliases=["dep"])
async def deposit(ctx, *, message):
	updateData()
	global characters
	global credits

	inputs = message.split(" ")
	name = message[:-(len(inputs[-1]) + 1)]

	try:
		if name.upper() in characters:
			if int(inputs[-1].replace(',', '')) > 0:
				await ctx.message.add_reaction('\U0001F551')
			else:
				await ctx.send("Please enter a valid amount of credits.")
		else:
			output = "Could not find a character named " + name.title() + "."
			await ctx.send(output)
	except:
		await ctx.send("Command invalid.")

@discordClient.command(aliases=["depMilestone"])
async def depositMilestone(ctx, *, message):
	updateData()
	global characters
	global Milestone

	inputs = message.split(" ")
	name = message[:-(len(inputs[-1]) + 1)]

	try:
		if name.upper() in characters:
			if int(inputs[-1].replace(',', '')) > 0:
				await ctx.message.add_reaction('\U0001F551')
			else:
				await ctx.send("Please enter a valid amount of Milestone.")
		else:
			output = "Could not find a character named " + name.title() + "."
			await ctx.send(output)
	except:
		await ctx.send("Command invalid.")

@discordClient.event
async def on_raw_reaction_add(payload):
    global characters
    global credits
    global Milestone
    guild = discordClient.get_guild(1049430235453608006)
    channel = discordClient.get_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    user = guild.get_member(payload.user_id)

    inputs = message.content.split(" ")
    name = message.content[len(inputs[0]) + 1:-(len(inputs[-1]) + 1)]

    DM = discord.utils.get(message.guild.roles, name="Republic DM")
    MD = discord.utils.get(message.guild.roles, name="Moderator/Lore Keeper")
    ADM =discord.utils.get(message.guild.roles, name="Assistant DM")
	
	

    for reaction in message.reactions:
        if reaction.emoji == '\U0001F551' and reaction.me == True:
            if (MD in user.roles or DM in user.roles or ADM in user.roles) and payload.emoji.name == '\U0001F44D':
                updateData()
                await message.remove_reaction('\U0001F551', discordClient.get_user(1246533851761741977))
                sheet.update_cell(characters.index(name.upper()) + 2, 4, int(credits[characters.index(name.upper())]) + int(inputs[-1].replace(',', '')))
            elif (MD in user.roles or DM in user.roles or ADM in user.roles ) and payload.emoji.name == u"\U0001F44E":
                updateData()
                await message.remove_reaction('\U0001F551', discordClient.get_user(1246533851761741977))
                sheet.update_cell(characters.index(name.upper()) + 2, 8, int(Milestone[characters.index(name.upper())]) + int(inputs[-1].replace(',', '')))

@discordClient.command(aliases=["bal", "Checkcr"])
async def balance(ctx, *, character):
	updateData()
	global characters
	global credits
	
	if character.upper() in characters:
		output = character.title() + " has " + credits[characters.index(character.upper())] + "cr."
	else:
		output = "Could not find a character named " + character.title() + "."
	await ctx.send(output)
@discordClient.command(aliases=["ballore", "Checklore"])
async def balancelore(ctx, *, character):
	updateData()
	global characters
	global lore
	
	if character.upper() in characters:
		output = character.title() + " has " + lore[characters.index(character.upper())] + "lore."
	else:
		output = "Could not find a character named " + character.title() + "."
	await ctx.send(output)
@discordClient.command(aliases=["balct", "Checkcontacts"])
async def balancect(ctx, *, character):
	updateData()
	global characters
	global contacts
	
	if character.upper() in characters:
		output = character.title() + " has " + contacts[characters.index(character.upper())] + "contacts."
	else:
		output = "Could not find a character named " + character.title() + "."
	await ctx.send(output)
@discordClient.command(aliases=["balbm", "Checkblackmail"])
async def balancebm(ctx, *, character):
	updateData()
	global characters
	global blackmail
	
	if character.upper() in characters:
		output = character.title() + " has " + blackmail[characters.index(character.upper())] + "blackmail."
	else:
		output = "Could not find a character named " + character.title() + "."
	await ctx.send(output)
@discordClient.command(aliases=["balMilestone", "CheckMilestone"])
async def balanceMilestone(ctx, *, character):
	updateData()
	global characters
	global Milestone
	
	if character.upper() in characters:
		output = character.title() + " has " + Milestone[characters.index(character.upper())] + "Milestone."
	else:
		output = "Could not find a character named " + character.title() + "."
	await ctx.send(output)

@discordClient.command(aliases=["with", "Spendcr"])
async def withdraw(ctx, *, message):
	updateData()
	global characters
	global credits
	global players

	inputs = message.split(" ")
	name = message[:-(len(inputs[-1]) + 1)]
	if name.upper() in characters:
		try:	
			inputs[-1] = abs(int(inputs[-1].replace(',', '')))
			if players[characters.index(name.upper())] == str(ctx.author.id):
				if int(credits[characters.index(name.upper())]) < int(inputs[-1]):
					output = name.title() + " only has " + str(credits[characters.index(name.upper())]) + "cr."
					await ctx.send(output)
				else:
					sheet.update_cell(characters.index(name.upper()) + 2, 4, int(credits[characters.index(name.upper())]) - int(inputs[-1]))
					await ctx.message.add_reaction('\U0001F44D')
			else:
				await ctx.send("Only the person who created a character can spend their credits.")
		except:
			await ctx.send("Command invalid.")
	else:
		output = "Could not find a character named " + name.title() + "."
		await ctx.send(output)

@discordClient.command()
async def transfer(ctx, *, message):
	updateData()
	global characters
	global credits
	global players

	inputs = message.split(" ")
	transferValue = int(inputs[0].replace(',', ''))

	if (message.upper().find(" TO ") < message.upper().find(" FROM ")):
		recipient = message[message.upper().find(" TO ") + 4:message.upper().find(" FROM ")] 
	else:
		recipient = message[message.upper().find(" TO ") + 4:] 

	if (message.upper().find(" FROM ") < message.upper().find(" TO ")):
		name = message[message.upper().find(" FROM ") + 6:message.upper().find(" TO ")] 
	else:
		name = message[message.upper().find(" FROM ") + 6:] 

	try:
		if name.upper() in characters:
			if recipient.upper() in characters:
				if players[characters.index(name.upper())] == str(ctx.author.id):
					if players[characters.index(recipient.upper())] != str(ctx.author.id) or ctx.author.id == 225428121145311232:
						if int(transferValue) > 0:
							if int(credits[characters.index(name.upper())]) >= transferValue:
								sheet.update_cell(characters.index(name.upper()) + 2, 4, int(credits[characters.index(name.upper())]) - transferValue)
								sheet.update_cell(characters.index(recipient.upper()) + 2, 4, int(credits[characters.index(recipient.upper())]) + transferValue)
								await ctx.message.add_reaction('\U0001F44D')
							else:
								output = name.title() + " only has " + str(credits[characters.index(name.upper())]) + "cr."
								await ctx.send(output)
						else:
							await ctx.send("Cannot transfer credit value below 0.")
					else:
						await ctx.send("You cannot transfer credits between your own characters.")
				else:
					await ctx.send("Only the person who created a character can transfer their credits.")
			else:
				output = "Could not find a character named " + recipient.title() + "."
				await ctx.send(output)
		else:
			output = "Could not find a character named " + name.title() + "."
			await ctx.send(output)
	except:
		await ctx.send("Command invalid.")
@discordClient.command()
async def transferlore(ctx, *, message):
	updateData()
	global characters
	global lore
	global players

	inputs = message.split(" ")
	transferValue = int(inputs[0].replace(',', ''))

	if (message.upper().find(" TO ") < message.upper().find(" FROM ")):
		recipient = message[message.upper().find(" TO ") + 4:message.upper().find(" FROM ")] 
	else:
		recipient = message[message.upper().find(" TO ") + 4:] 

	if (message.upper().find(" FROM ") < message.upper().find(" TO ")):
		name = message[message.upper().find(" FROM ") + 6:message.upper().find(" TO ")] 
	else:
		name = message[message.upper().find(" FROM ") + 6:] 

	try:
		if name.upper() in characters:
			if recipient.upper() in characters:
				if players[characters.index(name.upper())] == str(ctx.author.id):
					if players[characters.index(recipient.upper())] != str(ctx.author.id) or ctx.author.id == 225428121145311232:
						if int(transferValue) > 0:
							if int(lore[characters.index(name.upper())]) >= transferValue:
								sheet.update_cell(characters.index(name.upper()) + 2, 5, int(lore[characters.index(name.upper())]) - transferValue)
								sheet.update_cell(characters.index(recipient.upper()) + 2, 5, int(lore[characters.index(recipient.upper())]) + transferValue)
								await ctx.message.add_reaction('\U0001F44D')
							else:
								output = name.title() + " only has " + str(lore[characters.index(name.upper())]) + " lore. "
								await ctx.send(output)
						else:
							await ctx.send("Cannot transfer Lore value below 0.")
					else:
						await ctx.send("You cannot transfer Lore between your own characters.")
				else:
					await ctx.send("Only the person who created a character can transfer their Lore.")
			else:
				output = "Could not find a character named " + recipient.title() + "."
				await ctx.send(output)
		else:
			output = "Could not find a character named " + name.title() + "."
			await ctx.send(output)
	except:
		await ctx.send("Command invalid.")
@discordClient.command()
async def transferct(ctx, *, message):
	updateData()
	global characters
	global contacts
	global players

	inputs = message.split(" ")
	transferValue = int(inputs[0].replace(',', ''))

	if (message.upper().find(" TO ") < message.upper().find(" FROM ")):
		recipient = message[message.upper().find(" TO ") + 4:message.upper().find(" FROM ")] 
	else:
		recipient = message[message.upper().find(" TO ") + 4:] 

	if (message.upper().find(" FROM ") < message.upper().find(" TO ")):
		name = message[message.upper().find(" FROM ") + 6:message.upper().find(" TO ")] 
	else:
		name = message[message.upper().find(" FROM ") + 6:] 

	try:
		if name.upper() in characters:
			if recipient.upper() in characters:
				if players[characters.index(name.upper())] == str(ctx.author.id):
					if players[characters.index(recipient.upper())] != str(ctx.author.id) or ctx.author.id == 225428121145311232:
						if int(transferValue) > 0:
							if int(contacts[characters.index(name.upper())]) >= transferValue:
								sheet.update_cell(characters.index(name.upper()) + 2, 6, int(contacts[characters.index(name.upper())]) - transferValue)
								sheet.update_cell(characters.index(recipient.upper()) + 2, 6, int(contacts[characters.index(recipient.upper())]) + transferValue)
								await ctx.message.add_reaction('\U0001F44D')
							else:
								output = name.title() + " only has " + str(contacts[characters.index(name.upper())]) + " contacts. "
								await ctx.send(output)
						else:
							await ctx.send("Cannot transfer contacts value below 0.")
					else:
						await ctx.send("You cannot transfer contacts between your own characters.")
				else:
					await ctx.send("Only the person who created a character can transfer their contacts.")
			else:
				output = "Could not find a character named " + recipient.title() + "."
				await ctx.send(output)
		else:
			output = "Could not find a character named " + name.title() + "."
			await ctx.send(output)
	except:
		await ctx.send("Command invalid.")
@discordClient.command()
async def transferbm(ctx, *, message):
	updateData()
	global characters
	global blackmail
	global players

	inputs = message.split(" ")
	transferValue = int(inputs[0].replace(',', ''))

	if (message.upper().find(" TO ") < message.upper().find(" FROM ")):
		recipient = message[message.upper().find(" TO ") + 4:message.upper().find(" FROM ")] 
	else:
		recipient = message[message.upper().find(" TO ") + 4:] 

	if (message.upper().find(" FROM ") < message.upper().find(" TO ")):
		name = message[message.upper().find(" FROM ") + 6:message.upper().find(" TO ")] 
	else:
		name = message[message.upper().find(" FROM ") + 6:] 

	try:
		if name.upper() in characters:
			if recipient.upper() in characters:
				if players[characters.index(name.upper())] == str(ctx.author.id):
					if players[characters.index(recipient.upper())] != str(ctx.author.id) or ctx.author.id == 225428121145311232:
						if int(transferValue) > 0:
							if int(blackmail[characters.index(name.upper())]) >= transferValue:
								sheet.update_cell(characters.index(name.upper()) + 2, 7, int(blackmail[characters.index(name.upper())]) - transferValue)
								sheet.update_cell(characters.index(recipient.upper()) + 2, 7, int(blackmail[characters.index(recipient.upper())]) + transferValue)
								await ctx.message.add_reaction('\U0001F44D')
							else:
								output = name.title() + " only has " + str(blackmail[characters.index(name.upper())]) + " blackmail. "
								await ctx.send(output)
						else:
							await ctx.send("Cannot transfer blackmail value below 0.")
					else:
						await ctx.send("You cannot transfer blackmail between your own characters.")
				else:
					await ctx.send("Only the person who created a character can transfer their blackmail.")
			else:
				output = "Could not find a character named " + recipient.title() + "."
				await ctx.send(output)
		else:
			output = "Could not find a character named " + name.title() + "."
			await ctx.send(output)
	except:
		await ctx.send("Command invalid.")

@discordClient.command()
async def checkDTD(ctx, *, character):
	updateData()
	global characters
	global downtime

	if character.upper() in characters:
		if int(downtime[characters.index(character.upper())]) > 60:
			output = character.title() + " has 60 DTD, and " + str(int(downtime[characters.index(character.upper())]) - 60) + " DTD to be claimed."
		else:
			output = character.title() + " has " + downtime[characters.index(character.upper())] + " DTD."
		if updating:
			output += "\n\nPlease be aware that the ongoing DTD period is currently being applied, and so downtime tracking accuracy may vary."
	else:
		output = "Could not find a character named " + character.title() + "."
	await ctx.send(output)

@discordClient.command()
async def roll(ctx, *, message):
	updateData()

	global characters
	global downtime
	global credits
	global players
	global lore
	global contacts
	global blackmail
	global disadv

	disadv = sheet.col_values(8)
	del disadv[0]

	inputs = message.split(" ")
	filler = ["DTD", "FOR", "OF", "AT", "WITH", "A", "DOING", "COMMITING"]

	x = 0
	while x < len(inputs):
		if inputs[x].upper() in filler:
			del inputs[x]
		else:
			x += 1

	commandValid = True
	foundCharacter = False

	try:
		days = abs(int(re.sub("[DTD]", "", inputs[0])))
		name = inputs[2].upper()
		nameLength = 1
		for x in range (len(players)):
			if players[x] == str(ctx.author.id):
				if message.upper().find(characters[x]) != -1:
					foundCharacter = True
					characterID = x
					nameLength = len(characters[x].split(" "))
					name = characters[x]
					if days > int(downtime[x]):
						commandValid = False
						output = name.title() + " only has " + downtime[x] + " DTD."
						await ctx.send(output)

		job = " ".join(inputs[1:len(inputs) - nameLength - 1]).upper()
		mod = int(re.sub("[+]", "", inputs[-1]))
	except:
		await ctx.send("Command invalid.")
		commandValid = False

	if not foundCharacter:
		output = "You are not currently tracking a character with that name."
		commandValid = False
		await ctx.send(output)

	if commandValid:
		if job not in validJobs:
			commandValid = False
			await ctx.send("Please select a valid job.")
		if days / 5 != round(days / 5):
			commandValid = False
			await ctx.send("Five downtime days make up a workweek, please spend downtime in full weeks to proceed.")

	if commandValid:
		weeks = round(days / 5)

		for id in downtimeJobs:
			if job in downtimeJobs[id]["aliases"]:
				jsonID = id
		
		if int(downtimeJobs[jsonID]["cost"]) * weeks > int(credits[characterID]):
			commandValid = False
			output = name.title() + " only has " + credits[characterID] + "cr. " + str(int(downtimeJobs[jsonID]["cost"]) * weeks) + "cr are needed for this roll."
			await ctx.send(output)

	if commandValid:
		disadvNextRoll = False
		if disadv[characterID] == "x":
			sheet.update_cell(characterID + 2, 5, ".")
			disadvNextRoll = True

		netblackmailChange = 0
		netloreChange = 0
		netcontactsChange = 0
		netCrChange = 0
		output = "DOWNTIME RESULTS:\n"

		sheet.update_cell(characterID + 2, 3, int(downtime[characterID]) - days)

		for i in range(int(weeks)):
			output += "\nWeek " + str(i + 1) + ":\n"
			d20 = random.randint(1, 20)
			d20Disadv = random.randint(1, 20)
			if disadvNextRoll:
				abilityCheck = min(d20, d20Disadv) + mod
				d20DisadvOutput = "~~" + str(max(d20Disadv, d20)) + "~~ "
				d20 = min(d20Disadv, d20)
			else:
				abilityCheck = d20 + mod
				d20DisadvOutput = ""
			output += "Ability check: " + str(abilityCheck) + " (" + d20DisadvOutput + str(d20) + " + " + str(mod) + ")\n"

			d100Mod = min(max(0, (5 * math.floor(abilityCheck / 5)) - 5), 25)
			d100 = random.randint(1, 100)
			
			
			
			d100Total = d100 + d100Mod
			d100Output = ""
			output += "Percentile total: " + str(d100Total) + " (" + d100Output + str(d100) + " + " + str(d100Mod) + ")\n"

			if d100Total > 110:
				output += "Result: " + downtimeJobs[jsonID]["111"]["output"] + "\n"
				netcontactsChange += int(downtimeJobs[jsonID]["111"]["contactsChange"])
				netblackmailChange += int(downtimeJobs[jsonID]["111"]["blackmailChange"])
				netloreChange += int(downtimeJobs[jsonID]["111"]["loreChange"])
				netCrChange += int(downtimeJobs[jsonID]["111"]["crChange"])
			elif d100Total > 100:
				output += "Result: " + downtimeJobs[jsonID]["101"]["output"] + "\n"
				netcontactsChange += int(downtimeJobs[jsonID]["101"]["contactsChange"])
				netblackmailChange += int(downtimeJobs[jsonID]["101"]["blackmailChange"])
				netloreChange += int(downtimeJobs[jsonID]["101"]["loreChange"])
				netCrChange += int(downtimeJobs[jsonID]["101"]["crChange"])
			elif d100Total > 70:
				output += "Result: " + downtimeJobs[jsonID]["71"]["output"] + "\n"
				netcontactsChange += int(downtimeJobs[jsonID]["71"]["contactsChange"])
				netblackmailChange += int(downtimeJobs[jsonID]["71"]["blackmailChange"])
				netloreChange += int(downtimeJobs[jsonID]["71"]["loreChange"])
				netCrChange += int(downtimeJobs[jsonID]["71"]["crChange"])
			elif d100Total > 30:
				output += "Result: " + downtimeJobs[jsonID]["31"]["output"] + "\n"
				netcontactsChange += int(downtimeJobs[jsonID]["31"]["contactsChange"])
				netblackmailChange += int(downtimeJobs[jsonID]["31"]["blackmailChange"])
				netloreChange += int(downtimeJobs[jsonID]["31"]["loreChange"])
				netCrChange += int(downtimeJobs[jsonID]["31"]["crChange"])
			else:
				output += "Result: " + downtimeJobs[jsonID]["1"]["output"] + "\n"
				netcontactsChange += int(downtimeJobs[jsonID]["1"]["contactsChange"])
				netblackmailChange += int(downtimeJobs[jsonID]["1"]["blackmailChange"])
				netloreChange += int(downtimeJobs[jsonID]["1"]["loreChange"])
				netCrChange += int(downtimeJobs[jsonID]["1"]["crChange"])
			disadvNextRoll = False
			if random.randint(1, 10) == 1:
				output += "DISADVANTAGE NEXT ROLL\n"
				disadvNextRoll = True

			output += "----------"
			await ctx.send(output)
			output = ""

		if disadvNextRoll:
			sheet.update_cell(characterID + 2, 5, "x")

		
		sheet.update_cell(characterID + 2, 5, int(lore[characterID]) + netloreChange)
		output = "NET lore CHANGE: " + str(netloreChange) + "lore"
		sheet.update_cell(characterID + 2, 7, int(blackmail[characterID]) + netblackmailChange)
		output = "NET blackmail CHANGE: " + str(netblackmailChange) + "blackmail"
		sheet.update_cell(characterID + 2, 6, int(contacts[characterID]) + netcontactsChange)
		output = "NET contacts CHANGE: " + str(netcontactsChange) + "contacts"
		sheet.update_cell(characterID + 2, 4, int(credits[characterID]) + netCrChange)
		output = "NET CR CHANGE: " + str(netCrChange) + "cr"
		await ctx.send(output)

discordClient.run("")