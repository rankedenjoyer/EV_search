from scrape.scrape import Scrape

bot = Scrape()
bot.land_first_page()
bot.get_esports()
events = bot.get_event()
name = bot.get_name()
odds = bot.get_odds()
everything = dict()
i = 0
for event in events:
    everything[event] = dict()
    if name[i + 1] != 'Tie':
        everything[event][name[i]] = odds[i]
        everything[event][name[i + 1]] = odds[i + 1]
        i += 2
    else:
        everything[event][name[i]] = odds[i]
        everything[event][name[i + 1]] = odds[i + 1]
        everything[event][name[i + 2]] = odds[i + 2]
        i += 3
bot.land_calculator()
bot.choose_method()
for event in everything.keys():
    event_odd = list(everything[event].values())
    for key, value in everything[event].items():
        temp = list(event_odd)
        temp = [temp.pop(temp.index(value))] + temp
        bot.add_leg_odds(temp)
        bot.add_final_odds(value)
        bot.calculate()
        x = bot.get_EV()
        if x != 0:
            print(event + ' ' + key + ' ' + x)






