const express = require("express");
const cors = require("cors");
const puppeteer = require("puppeteer-extra");
const StealthPlugin = require("puppeteer-extra-plugin-stealth");

puppeteer.use(StealthPlugin());

const BASE_URL = "https://brainly.in";
const app = express();
app.use(cors());

async function getWithRetries(url, retries = 3, delay = 2000) {
  let browser;
  for (let attempt = 1; attempt <= retries; attempt++) {
    try {
      browser = await puppeteer.launch({
        headless: true,
        args: [
          "--no-sandbox",
          "--disable-setuid-sandbox",
          "--disable-dev-shm-usage",
          "--disable-accelerated-2d-canvas",
          "--no-first-run",
          "--no-zygote",
          "--disable-gpu",
        ],
      });

      const page = await browser.newPage();
      await page.setUserAgent(
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) " +
          "AppleWebKit/537.36 (KHTML, like Gecko) " +
          "Chrome/116.0 Safari/537.36"
      );

      await page.goto(url, { waitUntil: "domcontentloaded", timeout: 15000 });

      const content = await page.content();
      const bodyText = await page.evaluate(() => document.body.innerText);

      await browser.close();

      try {
        return JSON.parse(bodyText);
      } catch {
        return { html: content };
      }
    } catch (err) {
      console.error(`Attempt ${attempt} failed: ${err.message}`);
      if (browser) await browser.close();
      if (attempt < retries) {
        await new Promise((r) => setTimeout(r, delay));
      }
    }
  }
  throw new Error(`Failed to fetch ${url} after ${retries} attempts`);
}

app.get("/*", async (req, res) => {
  const fullPath = req.params[0] || "";
  let targetUrl = `${BASE_URL}/${fullPath}`;
  if (req.url.includes("?")) {
    targetUrl = `${BASE_URL}/${req.url}`;
  }

  try {
    const data = await getWithRetries(targetUrl);
    res.json(data);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`🚀 Server running at http://localhost:${PORT}`));
