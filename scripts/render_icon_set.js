#!/usr/bin/env node
/* Render a shared icon set (FontAwesome 6 via react-icons) to real PNG
 * files, white-on-transparent, so every deck/doc builder in the redesign
 * can reference a consistent set without re-running the sharp/react
 * pipeline per-build. Run once; output is checked into outputs/reports/.
 *
 *   node scripts/render_icon_set.js
 */
const fs = require("fs");
const path = require("path");
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");
const fa6 = require("react-icons/fa6");

const OUT_DIR = path.resolve(__dirname, "..", "outputs", "reports", "om_exhibits", "icons");

const ICON_NAMES = {
  bolt: "FaBoltLightning", tower: "FaTowerBroadcast", droplet: "FaDroplet",
  chart: "FaChartLine", chartcol: "FaChartColumn", landmark: "FaLandmarkDome",
  gaspump: "FaGasPump", industry: "FaIndustry", server: "FaServer",
  mappin: "FaMapLocationDot", locationdot: "FaLocationDot", gauge: "FaGaugeHigh",
  handshake: "FaHandshake", shield: "FaShieldHalved", building: "FaBuildingColumns",
  alert: "FaTriangleExclamation", dollar: "FaSackDollar", compass: "FaCompass",
  check: "FaCircleCheck", trendup: "FaArrowTrendUp", water: "FaWater",
  fire: "FaFireFlameSimple", exclaim: "FaCircleExclamation", ring: "FaCircleDot",
};

async function main() {
  fs.mkdirSync(OUT_DIR, { recursive: true });
  for (const [key, name] of Object.entries(ICON_NAMES)) {
    const Comp = fa6[name];
    if (!Comp) { console.error(`missing icon ${name}`); continue; }
    let svg = ReactDOMServer.renderToStaticMarkup(React.createElement(Comp, { size: 256 }));
    svg = svg.replace(/fill="currentColor"/g, 'fill="#FFFFFF"');
    const buf = await sharp(Buffer.from(svg)).resize(256, 256).png().toBuffer();
    fs.writeFileSync(path.join(OUT_DIR, `${key}.png`), buf);
  }
  console.log(`wrote ${Object.keys(ICON_NAMES).length} icons -> ${path.relative(process.cwd(), OUT_DIR)}`);
}

main().catch(err => { console.error(err); process.exit(1); });
