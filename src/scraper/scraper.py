from pyppeteer import launch
import asyncio
import json


# Use pyppeteer
# From https://www.scrapingbee.com/blog/pyppeteer/
# and https://dev.to/sonyarianto/practical-puppeteer-how-to-use-waitforxpath-and-evaluate-xpath-expression-15cp

LOGIN_URL = 'https://app.truecoach.co/login'
WORKOUTS_URL = 'https://otgstrength.truecoach.co/client/workouts'

UN = 'huberiah@gmail.com'
PW = 'a5QrGdyrUwu6kLq'

WORKOUTS = {}

def expand_links():
    

async def main():
    # LOGIN -------------------------------------------------------------------------------
    # -------------------------------------------------------------------------------------
    # -------------------------------------------------------------------------------------

    # launch chromium browser in the background
    browser = await launch({"headless": False, "args": ["--start-maximized"]})     
    # open a new tab in the browser
    page = await browser.newPage()
    await page.setViewport({'width': 2560, 'height': 1440})
    # add URL to a new page and then open it
    await page.goto(LOGIN_URL)
    # wait for page to load
    await page.waitFor(1000)
    # get email form entry
    email = await page.querySelector('input[data-test="email"]')
    await email.type(UN)
    #print(f'email: {email}')
    # get password form entry
    password = await page.querySelector('input[data-test="password"]')
    await password.type(PW)
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
        
    await page.goto(WORKOUTS_URL)
    await page.waitFor(1000)

    # GET PAST WORKOUTS -------------------------------------------------------------------
    # -------------------------------------------------------------------------------------
    # -------------------------------------------------------------------------------------
    
    #go to past tab
    await page.click('button[class="clientHeader-tab ivy-tabs-tab ember-view"]')
    await page.waitFor(5000)
    print('past workouts')

    # get all past works on page
    # cont = True
    # while cont:

    #     loader = await page.querySelector('button[class="btn btn--a btn--s btn--wide"]')
    #     #print(f'loader: {loader}')
    #     if loader is not None:   
    #         loader_text = await loader.getProperty('innerText)')
    #         #print(loader_text)
    #         await page.click('button[class="btn btn--a btn--s btn--wide"]')
    #         await page.waitFor(500)
    #     else:
    #         cont = False

    workout_pages = await page.querySelectorAll('a[class="ember-view btn btn--base btn--s focus:underline')
    
    wk_links = []
    # TODO: turn this into expand_links function
    for w in workout_pages:
        wk_link = await w.getProperty('href')
        wk_link = await wk_link.jsonValue()
        wk_links.append(wk_link)
    print(f'number of workouts to parse: {len(wk_links)}')
    # Visit each workout page
    for link in wk_links:
        #print(f'going to {link}')
        await page.goto(link)
        await page.waitFor(2000)
        workout_name = await page.querySelector('h3[class="prnt-title h2 split--cell"]') 
        if workout_name is not None:
            n = await workout_name.getProperty('innerText')
            print(await n.jsonValue())
        else:
            workout_name = await page.querySelector('h3[class="prnt-title h2"]')
            n = await workout_name.getProperty('innerText')
            print(await n.jsonValue())
        # get date
        date = await page.querySelector('h2[class="font-base font-semibold clientWorkoutHeader-title"]')
        n = await date.getProperty('innerText')
        n = await n.jsonValue()
        print(f'date: {n}')
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
            print(f'result: {n}')
            #print('         ' + n)
            results.append(n)

        overall_dict = {}
        # for i, name in enumerate(names):
        #     if i < len(infos):
        #         info = infos[i]
        #     else:
        #         info = ''
        #     if i < len(results):  
        #         result = results[i]
        #     else:
        #         result = ''

        #     overall_dict.update({"info": {"name": name, "info": info, "results": result}})
        overall_dict.update({"info": {"name": names, "info": infos, "results": results}})

        #print(json.dumps(overall_dict, indent=4))
        print('')

        WORKOUTS.update({date: overall_dict})
    await browser.close() 

    print(json.dumps(WORKOUTS, indent=4))

if __name__ == "__main__":
    print("Starting...")
    asyncio.new_event_loop().run_until_complete(main())