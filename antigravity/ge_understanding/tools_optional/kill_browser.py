import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        print("Starting playwright...")
        try:
            # Try IPv6 first since curl worked there
            browser = await p.chromium.connect_over_cdp("http://[::1]:9222")
            print("Connected via IPv6!")
            await browser.close()
            print("Closed via IPv6!")
        except Exception as e:
            print(f"IPv6 failed: {e}")
            try:
                # Try IPv4
                browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
                print("Connected via IPv4!")
                await browser.close()
                print("Closed via IPv4!")
            except Exception as e2:
                print(f"IPv4 failed: {e2}")

if __name__ == "__main__":
    asyncio.run(run())
