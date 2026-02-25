import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        print("Connecting to [::1]:9222...")
        try:
            browser = await p.chromium.connect_over_cdp("http://[::1]:9222")
            print("Connected!")
            page = await browser.new_page()
            await page.goto("http://localhost:5173/")
            print(f"Page title at 5173: {await page.title()}")
            # Instead of just closing, let's try to shutdown the browser
            # await browser.close() # This closes the CDP session
            # If we want to kill the browser process via CDP
            # There isn't a direct 'kill' but close() on the browser instance usually works if it's the owner.
            await browser.close()
            print("Browser closed.")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(run())
