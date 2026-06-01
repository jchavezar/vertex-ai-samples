const { chromium } = require('playwright');
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

async function main() {
  const tempDir = path.join(__dirname, '../scratch/temp_frames');
  if (!fs.existsSync(tempDir)) {
    fs.mkdirSync(tempDir, { recursive: true });
  }

  console.log("Connecting to local Google Chrome on remote debugging port 9222...");
  const browser = await chromium.connectOverCDP('http://localhost:9222');
  const contexts = browser.contexts();
  
  let page = null;
  for (const context of contexts) {
    const pages = context.pages();
    for (const p of pages) {
      const url = p.url();
      if (url.includes('localhost:3000')) {
        page = p;
        break;
      }
    }
    if (page) break;
  }

  if (!page) {
    console.error("❌ ERROR: Could not find any open tab to http://localhost:3000 in Chrome.");
    await browser.close();
    return;
  }

  console.log(`✅ Connected to tab: "${await page.title()}"`);
  await page.bringToFront();

  // Step 1: Initial state
  console.log("Capturing frame 1: Initial state...");
  await page.screenshot({ path: path.join(tempDir, 'frame_01.png') });
  await page.waitForTimeout(500);

  // Step 2: Typing query (part 1)
  console.log("Typing query part 1...");
  const inputSelector = 'form input';
  await page.fill(inputSelector, "what was the first quarter");
  await page.screenshot({ path: path.join(tempDir, 'frame_02.png') });
  await page.waitForTimeout(500);

  // Step 3: Typing query (part 2)
  console.log("Typing query part 2...");
  const query = 'what was the first quarter revenue for Alphabet?';
  await page.fill(inputSelector, query);
  await page.screenshot({ path: path.join(tempDir, 'frame_03.png') });
  await page.waitForTimeout(500);

  // Step 4: Click send button
  console.log("Clicking submit button...");
  await page.click('form button[type="submit"]');
  await page.screenshot({ path: path.join(tempDir, 'frame_04.png') });
  await page.waitForTimeout(2000);

  // Step 5: Loading / thinking state
  console.log("Capturing frame 5: Loading state...");
  await page.screenshot({ path: path.join(tempDir, 'frame_05.png') });
  await page.waitForTimeout(4000);

  // Step 6: Mid-loading state
  console.log("Capturing frame 6: Mid-loading state...");
  await page.screenshot({ path: path.join(tempDir, 'frame_06.png') });
  await page.waitForTimeout(4000);

  // Step 7: Response rendering
  console.log("Capturing frame 7: Response rendering...");
  await page.screenshot({ path: path.join(tempDir, 'frame_07.png') });
  await page.waitForTimeout(4000);

  // Step 8: Final response state
  console.log("Capturing frame 8: Final state...");
  await page.screenshot({ path: path.join(tempDir, 'frame_08.png') });

  await browser.close();
  console.log("Browser interaction complete. Creating GIF...");

  // Compile with ffmpeg
  const outputGif = path.join(__dirname, '../recordings/adk_drive_demo_walkthrough.gif');
  const recordingsDir = path.dirname(outputGif);
  if (!fs.existsSync(recordingsDir)) {
    fs.mkdirSync(recordingsDir, { recursive: true });
  }

  // Build high quality palette and compile GIF using ffmpeg
  const ffmpegCmd = `/opt/homebrew/bin/ffmpeg -framerate 1 -i "${tempDir}/frame_%02d.png" -vf "scale=1200:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse" -y "${outputGif}"`;
  console.log(`Executing ffmpeg: ${ffmpegCmd}`);
  try {
    execSync(ffmpegCmd);
    console.log(`✅ GIF successfully created and saved to: ${outputGif}`);
  } catch (err) {
    console.error("❌ Failed to compile GIF using ffmpeg:", err.message);
  }
}

main().catch(err => {
  console.error("Error:", err);
});
