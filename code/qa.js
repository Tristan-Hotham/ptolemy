// QA: open index.html at desktop and phone widths, log console errors, take screenshots to qa/.
// Run from the study root with a static server (python3 -m http.server PORT; set PORT). MapLibre comes from a local npm
// copy (the CDN is not reachable from the build container); tiles and fonts are blocked here, so the screenshots show
// the offline base map. NOML=1 blocks MapLibre too, to check that the page degrades gracefully.
const { chromium } = require("playwright");
const fs = require("fs");
const ML = process.env.MAPLIBRE_DIST || "/tmp/ml/node_modules/maplibre-gl/dist";
(async () => {
  fs.mkdirSync("qa", { recursive: true });
  const b = await chromium.launch({ args: ["--use-gl=swiftshader", "--enable-webgl", "--ignore-gpu-blocklist"] });
  const errs = [];
  const sizes = process.env.ONLY ? [[process.env.ONLY, process.env.ONLY === "phone" ? 390 : 1280, 860]] : [["desktop", 1280, 900], ["phone", 390, 844]];
  for (const [nm, vw, vh] of sizes) {
    const p = await b.newPage({ viewport: { width: vw, height: vh }, deviceScaleFactor: nm === "phone" ? 2 : 1 });
    await p.route(/arcgisonline|googleapis|gstatic/, r => r.abort());
    if (process.env.NOML) await p.route(/maplibre-gl/, r => r.abort());
    else {
      await p.route(/maplibre-gl@[\d.]+\/dist\/maplibre-gl\.js/, r => r.fulfill({ path: ML + "/maplibre-gl.js", contentType: "application/javascript" }));
      await p.route(/maplibre-gl@[\d.]+\/dist\/maplibre-gl\.css/, r => r.fulfill({ path: ML + "/maplibre-gl.css", contentType: "text/css" }));
    }
    p.on("console", m => { if (m.type() === "error" && !/ERR_FAILED|net::|Failed to load resource|AJAXError|tile/i.test(m.text())) errs.push(nm + ": " + m.text()); });
    p.on("pageerror", e => errs.push(nm + " pageerror: " + e.message));
    await p.goto("http://localhost:" + process.env.PORT + "/index.html", { waitUntil: "load" });
    await p.waitForTimeout(4000);
    const tag = process.env.NOML ? "noml_" : "";
    const jpg = f => `qa/${tag}${nm}_${f}.jpg`;
    await p.screenshot({ path: jpg("top"), type: "jpeg", quality: 70 });
    const shot = async (sel, f) => { await p.locator(sel).scrollIntoViewIfNeeded(); await p.waitForTimeout(1200); await p.locator(sel).screenshot({ path: jpg(f), type: "jpeg", quality: 70 }); };
    await shot("#atlas", "atlas");
    await p.fill("#q", "Londinium"); await p.waitForTimeout(400); await p.keyboard.press("Enter"); await p.waitForTimeout(2500); await shot("#atlas", "london");
    if (!process.env.NOML) {
      await p.click('#focusRow .btn:nth-child(4)'); await p.waitForTimeout(1800); await shot("#atlas", "britain");
      await p.click('#colRow .btn[data-c="cont"]'); await p.waitForTimeout(600);
      await p.click('#focusRow .btn:nth-child(7)'); await p.waitForTimeout(1800); await shot("#atlas", "taprobane");
      await p.click('#colRow .btn[data-c="err"]');
      await p.click('#focusRow .btn:nth-child(2)'); await p.waitForTimeout(1500);
      await p.locator("#wmap .lyrBtn").click(); await p.waitForTimeout(300);
      await p.locator('#wmap input[data-l="ptolw"]').check(); await p.locator('#wmap input[data-l="arrows"]').check(); await p.waitForTimeout(1200); await shot("#atlas", "layers_world");
      await p.locator('#wmap input[data-l="ptolw"]').uncheck(); await p.locator('#wmap input[data-l="arrows"]').uncheck(); await p.locator("#wmap .lyrBtn").click();
      await p.locator("#pmap .lyrBtn").click(); await p.waitForTimeout(300);
      await p.locator('#pmap input[data-l="realp"]').check(); await p.locator('#pmap input[data-l="xi"]').check(); await p.locator('#pmap input[data-l="other"]').check(); await p.waitForTimeout(1200); await shot("#atlas", "layers_ptol");
      await p.locator('#pmap input[data-l="realp"]').uncheck(); await p.locator('#pmap input[data-l="xi"]').uncheck(); await p.locator('#pmap input[data-l="other"]').uncheck(); await p.locator("#pmap .lyrBtn").click();
      await p.click('#regTable tr[data-k="AS10"]'); await p.waitForTimeout(2000); await shot("#atlas", "india");
    }
    for (const c of ["stretchChart", "alexChart", "britChart", "indiaChart", "caspChart", "regChart", "regTable", "recChart"]) await shot("#" + c, c);
    if (nm === "phone" && !process.env.NOML) {
      await p.click("#theme"); await p.waitForTimeout(1500); await shot("#atlas", "dark_atlas"); await shot("#britChart", "dark_brit");
      await p.locator("#wmap").scrollIntoViewIfNeeded(); await p.locator("#wmap .mfs-btn").click(); await p.waitForTimeout(1500); await p.screenshot({ path: `qa/${nm}_fullscreen.jpg`, type: "jpeg", quality: 70 });
    }
    const ov = await p.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
    console.log(nm, "horizontal overflow px:", ov);
    await p.close();
  }
  console.log("errors:", errs.length ? errs : "none");
  await b.close();
})();
