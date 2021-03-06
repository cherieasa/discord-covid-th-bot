import discord
from discord.ext import commands
from bs4 import BeautifulSoup
import requests
import nest_asyncio
import re
import pandas as pd

nest_asyncio.apply()

# Use client to hold the instance of bot
intents = discord.Intents(messages = True, guilds = True, reactions = True, members = True, presences = True)
client = commands.Bot(command_prefix = '.', intents = intents)

# Function when bot has got information it needs from discord -> READY state
@client.event
async def on_ready():
    print("Bot is ready")

@client.event
async def on_member_join(member):
    print(f'{member} has joined a server.')

@client.event
async def on_member_remove(member):
    print(f'{member} has left a server.')

@client.command(aliases = ['cases', 'covid19'])
async def covid(ctx):
    
    # Fetch html page
    url = 'https://covid19.th-stat.com/api/open/today'
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')
    
    info = str(soup).split(",")

    # Use RE to get numbers from data
    total_confirmed = re.findall(r'\d+', info[0])
    total_recovered = re.findall(r'\d+', info[1])
    current_hospitalised = re.findall(r'\d+', info[2])
    total_deaths = re.findall(r'\d+', info[3])
    new_confirmed = re.findall(r'\d+', info[4])
    new_recovered = re.findall(r'\d+', info[5])
    new_hospitalised = re.findall(r'\d+', info[6])
    new_deaths = re.findall(r'\d+', info[7])
    current_date = re.findall(r'\d+', info[8])
    current_date = str(current_date[0]) + "-" + str(current_date[1]) + "-" + str(current_date[2])
        
    await ctx.send("Thailand Daily Covid Cases of: " + f'{current_date}' + "\n" + f'New Cases: {new_confirmed[0]}' + "\n" + f'New Deaths: {new_deaths[0]}' )

@client.command(aliases = ['timeline'])
async def history(ctx, *, date):
    hist_url = 'https://covid19.th-stat.com/api/open/timeline'
    hist_page = requests.get(hist_url)
    hist_soup = BeautifulSoup(hist_page.text, 'html.parser')

    hist_info = re.findall(r'\[.+\]', str(hist_soup))
    hist_list = str(hist_info[0]).split("}")
    
    full_list = []
    
    for item in hist_list:
        
        each_date = item.split(",")
    
        # Get only value
        date_values = []
        value = ""
        for each_item in each_date:
            
            if "Date" in each_item:
                value = re.findall('[0-9]+', each_item)
                # Switch so date of month comes before month
                value = value[1] + value[0] +value [2]
                date_values.append(value)
            else:
                # Get only value after ":"
                value = re.findall('(?<=:).*$', each_item)
                date_values.extend(value)
            
        full_list.append(date_values)
    
    # Removes the last element (which is empty)
    full_list.pop()
        
    df = pd.DataFrame(data=full_list, columns = ['Date', 'New Confirmed', 'New Recovered', 'New Hospitalized', 'New Deaths', 'Confirmed', 'Recovered', 'Hospitalized', 'Deaths'])
        
    # Lookup of info via date
    lookup_date = re.findall('\d+',date)
    
    # Entered date with no separators eg. 01012020
    if len(lookup_date) == 1:
        lookup_date = str(lookup_date[0])
        
        # Entered date with year as 2 digits eg. 010120
        if len(lookup_date[4:]) == 2 :
            lookup_date = lookup_date[0:4] + "20" + lookup_date[4:]
    
    # Entered date with separators eg. 01-01-2020
    else:
        lookup_date = str(lookup_date[0]) + str(lookup_date[1]) + str(lookup_date[2])
        
        # Entered date with year as 2 digits eg. 010120
        if len(lookup_date[4:]) == 2 :
            lookup_date = lookup_date[0:4] + "20" + lookup_date[4:]
    
    lookup_values = df.loc[df['Date'] == lookup_date]
    
    # Get Date
    output_date = lookup_values['Date'].item()
    output_date = output_date[0:2] + "-" + output_date[2:4] + "-" + output_date[4:]
                                                                                
    # Get New Confirmed
    output_newconf = lookup_values['New Confirmed'].item()
    
    # Get New Recovered
    output_newrecov = lookup_values['New Recovered'].item()
    
    # Get New Hospitalized
    output_newhosp = lookup_values['New Hospitalized'].item()
    
    # Get New Deaths
    output_newdeaths = lookup_values['New Deaths'].item()
    
    # Get Confirmed
    output_conf = lookup_values['Confirmed'].item()
    
    # Get Recovered
    output_recov = lookup_values['Recovered'].item()

    # Get Hospitalized
    output_hosp = lookup_values['Hospitalized'].item()
    
    # Get Deaths
    output_deaths = lookup_values['Deaths'].item()
    
    await ctx.send("Information for Date: " + output_date + "\nNew Confirmed Cases: " + 
                    output_newconf + "\nNew Deaths: " + output_newdeaths + "\nNew Recovered: " 
                    + output_newrecov + "\nNew Hospitalized: " + output_newhosp + "\nTotal Confirmed Cases: " +
                    output_conf + "\nTotal Deaths: " + output_deaths + "\nTotal Recovered: " + output_recov +
                    "\nTotal Hospitalised: " + output_hosp)
    
    
# Bot Token as parameter
client.run('')
