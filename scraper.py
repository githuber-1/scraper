from pyppeteer import launch
import asyncio


# From https://www.scrapingbee.com/blog/pyppeteer/
# and https://dev.to/sonyarianto/practical-puppeteer-how-to-use-waitforxpath-and-evaluate-xpath-expression-15cp

LOGIN_URL = 'https://app.truecoach.co/login'
WORKOUTS_URL = 'https://otgstrength.truecoach.co/client/workouts'

UN = 'huberiah@gmail.com'
PW = 'a5QrGdyrUwu6kLq'

# Use pyppeteer

import asyncio
from pyppeteer import launch

async def main():
    # launch chromium browser in the background
    browser = await launch({"headless": False, "args": ["--start-maximized"]})     
    # open a new tab in the browser
    page = await browser.newPage()
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
    # log in
    await page.click('button[class="btn btn--a btn--m btn--wide mb-4"]')

    cont = True

    # get workouts
    await page.waitFor(3000)
    # get all headers from 1st page
    headers = await page.querySelectorAll('h4[class="h3"]')
    for header in headers:
        hd_text = await header.getProperty('innerText')
        #print(await hd_text.jsonValue()) 
    # get workout specifics from each workout page
    workouts = await page.querySelectorAll('a[class="ember-view btn btn--base btn--s focus:underline')
    wk_links = []
    for workout in workouts:
        print('workout: ')
        wk_link = await workout.getProperty('href')
        wk_link = await wk_link.jsonValue()
        wk_links.append(wk_link)
    for link in wk_links:
        print(f'going to {link}')
        await page.goto(link)
        print('waiting... ')
        await page.waitFor(500)
        await page.goBack()
        await page.waitFor(500)

    await browser.close() 

print("Starting...")
asyncio.new_event_loop().run_until_complete(main())