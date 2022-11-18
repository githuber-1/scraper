from pyppeteer import launch
import asyncio
import json
import csv
from itertools import zip_longest
import sys

# Use pyppeteer
# From https://www.scrapingbee.com/blog/pyppeteer/
# and https://dev.to/sonyarianto/practical-puppeteer-how-to-use-waitforxpath-and-evaluate-xpath-expression-15cp

# TODO: Delete these when everything is working
# LOGIN_URL = 'https://app.truecoach.co/login'
# WORKOUTS_URL = 'https://otgstrength.truecoach.co/client/workouts'

# UN = 'huberiah@gmail.com'
# PW = 'a5QrGdyrUwu6kLq'

# WORKOUTS = {}
# PREVIOUS_MONTH = ''
# YEAR = '2022'

class Scraper():
    def __init__(self, allPages):
        self.UN = 'huberiah@gmail.com'
        self.PW = 'a5QrGdyrUwu6kLq'
        self.LOGIN_URL = 'https://app.truecoach.co/login'
        self.WORKOUTS_URL = 'https://otgstrength.truecoach.co/client/workouts'
        self.workouts =  {}
        self.previous_month = ''
        self.previous_year = '2022'
        self.allPages = allPages
        
    def print_progress_bar(self, total, current):
        progress = int( (current / total) * 100 )
        progress_bar = "*" * progress
        empty_bar = ( (100 - progress) * "-")
        print('( ' + progress_bar + empty_bar + " )")

    async def expand_links(self, page):
        # get all past works on page if requested
        if self.allPages:
            cont = True
            while cont:
                print('*')
                loader = await page.querySelector('button[class="btn btn--a btn--s btn--wide"]')
                #print(f'loader: {loader}')
                if loader is not None:   
                    loader_text = await loader.getProperty('innerText)')
                    #print(loader_text)
                    await page.click('button[class="btn btn--a btn--s btn--wide"]')
                    await page.waitFor(500)
                else:
                    cont = False
                    print('-')

        # find all workout links
        workout_pages = await page.querySelectorAll('a[class="ember-view btn btn--base btn--s focus:underline')
        wk_links = []
        # TODO: turn this into expand_links function
        for w in workout_pages:
            wk_link = await w.getProperty('href')
            wk_link = await wk_link.jsonValue()
            wk_links.append(wk_link)
        print(f'Number of workouts to parse: {len(wk_links)}')
        # Visit each workout page
        iteration = 0
        for link in wk_links:
            iteration += 1
            #print(f'going to {link}')
            await page.goto(link)
            await page.waitFor(2000)
            workout_name = await page.querySelector('h3[class="prnt-title h2 split--cell"]') 
            if workout_name is not None:
                n = await workout_name.getProperty('innerText')
                #print(await n.jsonValue())
            else:
                workout_name = await page.querySelector('h3[class="prnt-title h2"]')
                n = await workout_name.getProperty('innerText')
                #print(await n.jsonValue())
            # get date
            date = await page.querySelector('h2[class="font-base font-semibold clientWorkoutHeader-title"]')
            n = await date.getProperty('innerText')
            n = await n.jsonValue()
            #print(f'date: {n}')
            date = n
            # get exercise names
            names = []
            exercise_names = await page.querySelectorAll('h4[class="whitespace-pre-line"]')
            for exercise_name in exercise_names:
                n = await exercise_name.getProperty('innerText')
                n = await n.jsonValue()
                #print('     ' + n)
                names.append(n)
            # get exercise info
            infos = []
            exercise_infos = await page.querySelectorAll('p[class="well well--xs whitespace-pre-line til"]')
            for exercise_info in exercise_infos:
                n = await exercise_info.getProperty('innerText')
                n = await n.jsonValue()
                #print('         ' + n)
                infos.append(n)
            # get exercise results
            results = []
            exercise_results = await page.querySelectorAll('textarea[class="ember-text-area ember-view workout-item-result"]')
            #print(f'results: {exercise_results}')
            for result in exercise_results:
                n = await result.getProperty('value')
                n = await n.jsonValue()
                #print(f'result: {n}')
                #print('         ' + n)
                results.append(n)

            overall_dict = ({"info": {"name": names, "info": infos, "results": results}})

            #print(json.dumps(overall_dict, indent=4))
            self.print_progress_bar(len(wk_links), iteration)
            self.workouts.update({date: overall_dict})


    def date_converter(self, datestr):
        date = datestr.split(',')[1]
        #print(f'date: {date}')
        # handle month
        month = date.split(' ')[1]
        #print(f'month: {month}')
        if month == 'Dec' and self.previous_month == 'Jan':
            self.previous_year = self.previous_year - 1

        day = date.split(' ')[2]
        numeric_filter = filter(str.isdigit, day)

        day_numeric_string = "".join(numeric_filter)
        self.previous_month = month

        date = day_numeric_string + "/" + month + "/" + self.previous_year

        #print(f'{month} / {day} / {year} ')

        return date

    def workouts_to_csv(self):
        csv_workouts = [['date', 'name', 'info', 'results']]

        for key, values in self.workouts.items():
            # each row begins with date which is the key of WORKOUTS
            csv_workout = []

            date = self.date_converter(key)
            csv_workout.append(date)

            names = values['info']['name']
            info = values['info']['info']
            results = values['info']['results']

            for n, i, r in zip_longest(names, info, results, fillvalue=''):
                if n is None:
                    n = 'Rest Day'
                i = i.replace("\n", '')
                r = r.replace("\n", '')
                csv_workout.append(n)
                csv_workout.append(i)
                csv_workout.append(r)

            csv_workouts.append(csv_workout)
        
        #print(csv_workouts)

        with open('workouts.csv', 'w', newline='') as file:
            writer = csv.writer(file, delimiter=',')
            for line in csv_workouts:
                writer.writerow(line)
            

async def main():
    # INIT --------------------------------------------------------------------------------
    # -------------------------------------------------------------------------------------
    # -------------------------------------------------------------------------------------
    try:
        if sys.argv[1].capitalize() == 'True':
            print('Parsing all old workouts')
            allPages = True
        else:
            print('test')
            allPages = False
    except(IndexError):
        allPages = True
    
    scraper = Scraper(allPages)

    # LOGIN -------------------------------------------------------------------------------
    # -------------------------------------------------------------------------------------
    # -------------------------------------------------------------------------------------

    # launch chromium browser in the background
    browser = await launch({"headless": True, "args": ["--start-maximized"]})     
    # open a new tab in the browser
    page = await browser.newPage()
    await page.setViewport({'width': 2560, 'height': 1440})
    # add URL to a new page and then open it
    await page.goto(scraper.LOGIN_URL)
    # wait for page to load
    await page.waitFor(1000)
    # get email form entry
    email = await page.querySelector('input[data-test="email"]')
    await email.type(scraper.UN)
    #print(f'email: {email}')
    # get password form entry
    password = await page.querySelector('input[data-test="password"]')
    await password.type(scraper.PW)
    #print(f'password: {password}')
    # log in, this takes us to workouts page
    await page.click('button[class="btn btn--a btn--m btn--wide mb-4"]')
    await page.waitFor(3000)

    # GET FUTURE WORKOUTS -----------------------------------------------------------------
    # -------------------------------------------------------------------------------------
    # -------------------------------------------------------------------------------------

    # loader = await page.querySelector('button[class="btn btn--a btn--s btn--wide"]')
    # if loader is not None:
    #     await page.click('button[class="btn btn--a btn--s btn--wide"]')
    #     await page.waitFor(1000)

    # # TODO: Delete this headers section? Can get info from workout below?
    # headers = await page.querySelectorAll('h4[class="h3"]')
    # for header in headers:
    #     hd_text = await header.getProperty('innerText')
    #     #print(await hd_text.jsonValue()) 
    # # grab main page first, and then go to 'Past' workouts and iterate through entire list
    # # get workout specifics from each workout page
    # workouts = await page.querySelectorAll('a[class="ember-view btn btn--base btn--s focus:underline')
    # wk_links = []
    # print('future workouts')
    # # TODO: turn this into expand_links function
    # for workout in workouts:
    #     wk_link = await workout.getProperty('href')
    #     wk_link = await wk_link.jsonValue()
    #     wk_links.append(wk_link)
    # for link in wk_links:
    #     #print(f'going to {link}')
    #     await page.goto(link)
    #     await page.waitFor(2000)
    #     # get workout name
    #     workout_name = await page.querySelector('h3[class="prnt-title h2 split--cell"]') 
    #     if workout_name is not None:
    #         n = await workout_name.getProperty('innerText')
    #         print(await n.jsonValue())
    #     else:
    #         workout_name = await page.querySelector('h3[class="prnt-title h2"]')
    #         n = await workout_name.getProperty('innerText')
    #         #print(await n.jsonValue())
    #     # get exercise names
    #     names = []
    #     exercise_names = await page.querySelectorAll('h4[class="whitespace-pre-line"]')
    #     for exercise_name in exercise_names:
    #         n = await exercise_name.getProperty('innerText')
    #         n = await n.jsonValue()
    #         #print('     ' + n)
    #         names.append(n)
    #     # get exercise info
    #     infos = []
    #     exercise_infos = await page.querySelectorAll('p[class="well well--xs whitespace-pre-line til"]')
    #     for exercise_info in exercise_infos:
    #         n = await exercise_info.getProperty('innerText')
    #         n = await n.jsonValue()
    #         #print('         ' + n)
    #         infos.append(n)
    #     # get exercise results
    #     results = []
    #     exercise_results = await page.querySelectorAll('textarea[placeholder="Enter Results"]')
    #     for result in exercise_results:
    #         n = await result.getProperty('innerText')
    #         n = await n.jsonValue()
    #         print('         ' + n)
    #         results.append(n)

    #     overall_dict = {}
    #     for i, name in enumerate(names):
    #         if i < len(infos):
    #             info = infos[i]
    #         else:
    #             info = ''
    #         if i < len(results):
    #             results = results[i]
    #         else:
    #             results = ''

    #         overall_dict.update({name: {"info": info, "results": results}})

    #     print(f'overall_dict: {overall_dict}')
        
    await page.goto(scraper.WORKOUTS_URL)
    await page.waitFor(1000)

    # GET PAST WORKOUTS -------------------------------------------------------------------
    # -------------------------------------------------------------------------------------
    # -------------------------------------------------------------------------------------
    
    #go to past tab
    await page.click('button[class="clientHeader-tab ivy-tabs-tab ember-view"]')
    await page.waitFor(5000)

    await scraper.expand_links(page)

    await browser.close() 

    #print(json.dumps(WORKOUTS, indent=4))

    scraper.workouts_to_csv()

if __name__ == "__main__":
    print("Parsing old workouts...")
    asyncio.new_event_loop().run_until_complete(main())