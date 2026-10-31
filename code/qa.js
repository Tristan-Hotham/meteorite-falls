// QA: open index.html at desktop and phone widths, log console errors, take screenshots to qa/.
// Run from the study root with a static server (python3 -m http.server 8793; set PORT to change).
const { chromium } = require("playwright");
// Leaflet from a local npm copy (the CDN is not reachable from the build container); tiles and fonts are blocked here.
const LEAF = process.env.LEAFLET_DIST || "/dev/shm/football/npm/node_modules/leaflet/dist";
(async () => {
  const b = await chromium.launch();
  const errs = [];
  for (const [nm, vw, vh] of (process.env.ONLY ? [["phone", 390, 844]] : [["desktop", 1280, 900], ["phone", 390, 844]])) {
    const p = await b.newPage({ viewport: { width: vw, height: vh }, deviceScaleFactor: nm === "phone" ? 2 : 1 });
    await p.route(/arcgisonline|googleapis|gstatic/, r => r.abort());
    await p.route(/leaflet.min.js/, r => r.fulfill({ path: LEAF + "/leaflet.js" }));
    await p.route(/leaflet.min.css/, r => r.fulfill({ path: LEAF + "/leaflet.css" }));
    p.on("console", m => { if (m.type() === "error" && !/ERR_FAILED|net::/.test(m.text())) errs.push(nm + ": " + m.text()); });
    p.on("pageerror", e => errs.push(nm + " pageerror: " + e.message));
    await p.goto("http://localhost:" + (process.env.PORT || 8793) + "/index.html", { waitUntil: "networkidle" });
    await p.waitForTimeout(2500);
    await p.screenshot({ path: `qa/${nm}_top.png` });
    const shot = async (sel, f) => { console.log(nm, f, new Date().toISOString().slice(11,19)); await p.locator(sel).scrollIntoViewIfNeeded(); await p.waitForTimeout(700); await p.locator(sel).screenshot({ path: `qa/${nm}_${f}.png` }); };
    await shot("#atlas", "map");
    await p.click('#fallRow [data-f="fell"]'); await p.click("#focusRow .btn:nth-child(5)"); await p.waitForTimeout(1500); await shot("#atlas", "falls_europe");
    await p.click('#fallRow [data-f="all"]'); await p.click('#viewRow [data-v="heat"]'); await p.click("#focusRow .btn:last-child"); await p.waitForTimeout(1500); await shot("#atlas", "density");
    await p.click('#viewRow [data-v="dots"]'); await p.click('#colRow [data-c="group"]'); await p.click("#focusRow .btn:nth-child(2)"); await p.waitForTimeout(1500); await shot("#atlas", "antarctica_class");
    await p.click('#colRow [data-c="region"]');
    await p.fill("#q", "Hoba"); await p.waitForTimeout(500); await p.keyboard.press("Enter"); await p.waitForTimeout(2000); await shot("#atlas", "search_hoba");
    await p.fill("#q", "Japan"); await p.waitForTimeout(500); await p.keyboard.press("Enter"); await p.waitForTimeout(2000); await shot("#atlas", "country_japan");
    await p.evaluate(() => { const i = document.querySelector('.lyrPanel [data-k="ratio"]'); i.checked = true; i.dispatchEvent(new Event("change")); const b = document.querySelector('.lyrPanel [data-k="boxes"]'); b.checked = true; b.dispatchEvent(new Event("change")); });
    await p.click("#focusRow .btn:last-child"); await p.waitForTimeout(1500); await shot("#atlas", "ratio_layer");
    await p.click(".lyrBtn"); await p.waitForTimeout(300); await shot("#map", "layers_panel"); await p.click(".lyrBtn");
    for (const c of ["regChart", "areaTable", "decChart", "contChart", "ratioChart", "popChart", "heavyTable", "clsChart"]) await shot("#" + c, c);
    if (nm === "phone") {
      await p.click("#theme"); await p.waitForTimeout(1500); await shot("#atlas", "dark_map"); await shot("#decChart", "dark_dec");
      await p.locator("#atlas").scrollIntoViewIfNeeded(); await p.click(".mfs-btn"); await p.waitForTimeout(1500); await p.screenshot({ path: `qa/${nm}_fullscreen.png` });
    }
    const ov = await p.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
    console.log(nm, "horizontal overflow px:", ov);
    await p.close();
  }
  console.log("errors:", errs.length ? errs : "none");
  await b.close();
})();
