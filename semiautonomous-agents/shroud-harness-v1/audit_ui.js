const puppeteer = require("puppeteer");
const fs = require("fs");

(async () => {
  const browser = await puppeteer.launch({ 
    args: ['--no-sandbox', '--disable-setuid-sandbox'] 
  });
  const page = await browser.newPage();
  
  try {
    console.log(">>> Navigating to http://localhost:3000...");
    await page.goto("http://localhost:3000", { waitUntil: "networkidle2" });
    
    // Give it a moment to render perfectly
    await new Promise(r => setTimeout(r, 1000));
    
    // 1. Take a screenshot
    console.log(">>> Capturing screenshot...");
    await page.screenshot({ path: "ui_snapshot.png", fullPage: true });

    // 2. Inspect CSS of specific elements
    console.log(">>> Inspecting Computed CSS...");
    
    const elementsToInspect = {
      "Body": "body",
      "Heading": "h1",
      "Input Capsule": "div.relative.max-w-2xl",
      "Flower": "svg.text-shroud-accent"
    };

    const auditData = {};

    for (const [name, selector] of Object.entries(elementsToInspect)) {
      try {
        const computed = await page.evaluate((sel) => {
          const el = document.querySelector(sel);
          if (!el) return null;
          const styles = window.getComputedStyle(el);
          return {
            fontFamily: styles.fontFamily,
            fontSize: styles.fontSize,
            backgroundColor: styles.backgroundColor,
            color: styles.color,
            borderRadius: styles.borderRadius,
            boxShadow: styles.boxShadow,
            padding: styles.padding,
            letterSpacing: styles.letterSpacing
          };
        }, selector);
        auditData[name] = computed;
      } catch (e) {
        auditData[name] = "Not found or error";
      }
    }

    fs.writeFileSync("ui_audit.json", JSON.stringify(auditData, null, 2));
    console.log(">>> UI Audit saved to ui_audit.json");

  } catch (error) {
    console.error("!!! Audit Failed:", error.message);
  } finally {
    await browser.close();
  }
})();
