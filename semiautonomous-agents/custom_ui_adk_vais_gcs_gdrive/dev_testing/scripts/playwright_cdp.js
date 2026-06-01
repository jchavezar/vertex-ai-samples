const { chromium } = require('playwright');

async function main() {
  console.log("Connecting to local Google Chrome on remote debugging port 9222...");
  const browser = await chromium.connectOverCDP('http://localhost:9222');
  const contexts = browser.contexts();
  console.log(`Found ${contexts.length} browser contexts.`);
  
  let page = null;
  for (const context of contexts) {
    const pages = context.pages();
    for (const p of pages) {
      const url = p.url();
      console.log(`Open tab URL: ${url}`);
      if (url.includes('localhost:3000')) {
        page = p;
        break;
      }
    }
    if (page) break;
  }

  if (!page) {
    console.error("❌ ERROR: Could not find any open tab to http://localhost:3000 in Chrome.");
    console.error("Please make sure you have the page open in Chrome.");
    await browser.close();
    return;
  }

  console.log(`\n✅ Connected to active tab: "${await page.title()}"`);
  
  // Bring the page to front focus
  await page.bringToFront();

  // Wait for the input box to be available and not disabled
  const inputSelector = 'form input';
  await page.waitForSelector(inputSelector);
  const placeholder = await page.getAttribute(inputSelector, 'placeholder');
  console.log(`Input placeholder: "${placeholder}"`);
  
  if (placeholder.includes("Awaiting secure credential")) {
    console.error("❌ ERROR: Google Drive integration is not connected/signed in on the UI yet.");
    await browser.close();
    return;
  }

  // Type the query
  const query = 'what was the first quarter revenue for Alphabet?';
  console.log(`Typing test query: "${query}"`);
  await page.fill(inputSelector, query);

  // Click SEND button
  console.log("Submitting message...");
  await page.click('form button[type="submit"]');

  // Wait for the response stream to complete
  console.log("Waiting 15 seconds for agent reasoning and search tool execution...");
  await page.waitForTimeout(15000);

  // Fetch all message text bubbles
  const assistantBubbles = await page.locator('div.rounded-bl-sm').allTextContents();
  console.log("\n💬 [Agent response]:");
  for (const txt of assistantBubbles) {
    console.log(`- ${txt.trim()}`);
  }

  // Take a clean screenshot of the result
  const screenshotPath = '/Users/jesusarguelles/IdeaProjects/vertex-ai-samples/semiautonomous-agents/custom_ui_adk_vais_gcs_gdrive/dev_testing/recordings/test_run.png';
  await page.screenshot({ path: screenshotPath });
  console.log(`\n📸 Screenshot saved to: ${screenshotPath}`);

  await browser.close();
  console.log("Finished browser automation test.");
}

main().catch(err => {
  console.error("Exception during browser testing:", err);
});
