const fs = require("node:fs");
const path = require("node:path");

const ROOT = path.resolve(__dirname, "..");
const DIST = path.join(ROOT, "dist");
const TRANSLATIONS = path.join(ROOT, "translations");
const { load } = require(path.join(ROOT, "tmp", "translator", "node_modules", "cheerio"));
const { translate } = require(path.join(ROOT, "tmp", "translator", "node_modules", "bing-translate-api"));

const BASE_URL = "https://www.lexygolift.com";
const LANGUAGES = [
  { locale: "en", hreflang: "en", code: "en", name: "English", dir: "ltr" },
  { locale: "es", hreflang: "es", code: "es", name: "Español", dir: "ltr" },
  { locale: "pt-br", hreflang: "pt-BR", code: "pt", name: "Português (Brasil)", dir: "ltr" },
  { locale: "de", hreflang: "de", code: "de", name: "Deutsch", dir: "ltr" },
  { locale: "fr", hreflang: "fr", code: "fr", name: "Français", dir: "ltr" },
  { locale: "it", hreflang: "it", code: "it", name: "Italiano", dir: "ltr" },
  { locale: "ar", hreflang: "ar", code: "ar", name: "العربية", dir: "rtl" },
  { locale: "id", hreflang: "id", code: "id", name: "Bahasa Indonesia", dir: "ltr" },
  { locale: "tr", hreflang: "tr", code: "tr", name: "Türkçe", dir: "ltr" },
  { locale: "pl", hreflang: "pl", code: "pl", name: "Polski", dir: "ltr" },
  { locale: "vi", hreflang: "vi", code: "vi", name: "Tiếng Việt", dir: "ltr" },
  { locale: "th", hreflang: "th", code: "th", name: "ไทย", dir: "ltr" },
  { locale: "ru", hreflang: "ru", code: "ru", name: "Русский", dir: "ltr" },
  { locale: "ja", hreflang: "ja", code: "ja", name: "日本語", dir: "ltr" },
  { locale: "ko", hreflang: "ko", code: "ko", name: "한국어", dir: "ltr" },
  { locale: "hi", hreflang: "hi", code: "hi", name: "हिन्दी", dir: "ltr" },
  { locale: "ms", hreflang: "ms", code: "ms", name: "Bahasa Melayu", dir: "ltr" },
];

const ATTRIBUTE_SELECTORS = [
  ["meta[name='description']", "content"],
  ["meta[property='og:title']", "content"],
  ["meta[property='og:description']", "content"],
  ["[alt]", "alt"],
  ["[placeholder]", "placeholder"],
  ["[aria-label]", "aria-label"],
];

const SCHEMA_TRANSLATABLE_KEYS = new Set([
  "name", "alternateName", "description", "category", "serviceType", "text",
  "knowsAbout", "contactType", "availableLanguage",
]);

const EXTRA_STRINGS = [
  "LEXYGO inquiry", "material handling equipment", "Name", "Email", "Company",
  "Country / Region", "Product / Model", "Message",
];

const EXACT_UNITS = new Set([
  "kg", "mm", "cm", "m", "h", "s", "W", "kW", "V", "Ah", "V/Ah", "km/h",
  "mm/s", "MPa", "kN", "pcs", "%", "deg", "cycles", "strokes", "rpm",
]);

function walk(dir) {
  const result = [];
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) result.push(...walk(full));
    else result.push(full);
  }
  return result;
}

function isEnglishHtml(file) {
  if (!file.endsWith(".html")) return false;
  const rel = path.relative(DIST, file).replaceAll("\\", "/");
  return !LANGUAGES.some((language) => language.locale !== "en" && (rel === `${language.locale}/index.html` || rel.startsWith(`${language.locale}/`)));
}

function shouldTranslate(value) {
  const text = String(value || "").trim();
  if (!text || !/[A-Za-z]/.test(text)) return false;
  if (EXACT_UNITS.has(text)) return false;
  if (/^(?:https?:\/\/|mailto:|tel:|\/)/i.test(text)) return false;
  if (/^[\d\s.,;:()+\-–—\/%=°ØxX<>]+$/.test(text)) return false;
  if (/^[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}$/.test(text)) return false;
  if (/^Zhejiang Changxing Shengli Intelligent Machinery Co\., Ltd\.$/.test(text)) return false;
  if (/^No\. 4 Workshop, No\. 188 Baixi Road/.test(text)) return false;
  return true;
}

function collectJsonStrings(value, output, key = "") {
  if (Array.isArray(value)) {
    for (const item of value) collectJsonStrings(item, output, key);
    return;
  }
  if (value && typeof value === "object") {
    for (const [childKey, child] of Object.entries(value)) collectJsonStrings(child, output, childKey);
    return;
  }
  if (typeof value === "string" && SCHEMA_TRANSLATABLE_KEYS.has(key) && shouldTranslate(value)) output.add(value.trim());
}

function collectHtmlStrings(file, output) {
  const $ = load(fs.readFileSync(file, "utf8"), { decodeEntities: false });
  const title = $("title").text().trim();
  if (shouldTranslate(title)) output.add(title);
  $("body").find("*").addBack().contents().each((_, node) => {
    if (node.type !== "text") return;
    const parent = node.parent && node.parent.name;
    if (["script", "style", "noscript"].includes(parent)) return;
    const text = node.data.trim();
    if (shouldTranslate(text)) output.add(text);
  });
  for (const [selector, attr] of ATTRIBUTE_SELECTORS) {
    $(selector).each((_, element) => {
      const value = $(element).attr(attr);
      if (shouldTranslate(value)) output.add(value.trim());
    });
  }
  $("script[type='application/ld+json']").each((_, element) => {
    try { collectJsonStrings(JSON.parse($(element).text()), output); } catch {}
  });
}

function protectText(text, segmentId) {
  const values = [];
  let prepared = text;
  const patterns = [
    /https?:\/\/[^\s)\]}]+/gi,
    /[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}/g,
    /\+?\d[\d\s()-]{6,}\d/g,
    /ANSI\/ITSDF B56\.1-2020/gi,
    /UL 583 NRTL Type E/gi,
    /UN 38\.3/gi,
    /LiFePO4/gi,
    /\bLEXYGO\b/g,
    /\b(?:OEM|ODM|CE|NRTL)\b/g,
    /\b(?=[A-Z0-9-]*\d)[A-Z][A-Z0-9-]{2,}\b/g,
  ];
  for (const pattern of patterns) {
    prepared = prepared.replace(pattern, (match) => {
      const marker = `zxprotected_${segmentId}_${values.length}_zx`;
      values.push([marker, match]);
      return marker;
    });
  }
  return { prepared, values };
}

function restoreText(text, protectedValues) {
  let restored = text.trim();
  for (let index = 0; index < protectedValues.length; index += 1) {
    const [marker, value] = protectedValues[index];
    const controls = "[\\s\\u200e\\u200f\\u202a-\\u202e]*";
    const oldFlexible = `Z${controls}X${controls}P${controls}R${controls}O${controls}T${controls}E${controls}C${controls}T${controls}\\d+${controls}X${controls}${index}${controls}Z${controls}X`;
    const newFlexible = marker.split("").join(controls);
    restored = restored
      .replace(new RegExp(oldFlexible, "gi"), value)
      .replace(new RegExp(newFlexible, "gi"), value);
  }
  return restored.replace(/\s+([,.;:!?])/g, "$1").trim();
}

function repairCachePlaceholders(cache) {
  let repairs = 0;
  for (const [source, target] of Object.entries(cache)) {
    if (!/(?:ZXPROTECT|zxprotected_)/i.test(target)) continue;
    const protectedSource = protectText(source, 0);
    const repaired = restoreText(target, protectedSource.values);
    if (repaired !== target) {
      cache[source] = repaired;
      repairs += 1;
    }
  }
  return repairs;
}

function isCorruptTranslation(source, target) {
  if (typeof target !== "string" || !target.trim()) return true;
  if (/(?:ZXPROTECT|zxprotected_|ZXSEG)/i.test(target)) return true;
  if (!source.includes("\n") && target.includes("\n")) return true;
  return target.length > Math.max(280, source.length * 8 + 80);
}

function purgeCorruptCacheEntries(cache) {
  let purged = 0;
  for (const [source, target] of Object.entries(cache)) {
    if (!isCorruptTranslation(source, target)) continue;
    delete cache[source];
    purged += 1;
  }
  return purged;
}

function createBatches(strings, maxLength = 2700) {
  const prepared = strings.map((text, index) => ({ text, index, ...protectText(text, index) }));
  const batches = [];
  let current = [];
  let length = 0;
  for (const item of prepared) {
    const addition = item.prepared.length + 32;
    if (current.length && length + addition > maxLength) {
      batches.push(current);
      current = [];
      length = 0;
    }
    current.push(item);
    length += addition;
  }
  if (current.length) batches.push(current);
  return batches;
}

function sleep(ms) { return new Promise((resolve) => setTimeout(resolve, ms)); }

async function translateOne(text, language, item, attempt = 1) {
  try {
    const result = await translate(item.prepared, "en", language.code);
    return restoreText(result.translation, item.values);
  } catch (error) {
    if (attempt >= 5) throw error;
    await sleep(900 * attempt);
    return translateOne(text, language, item, attempt + 1);
  }
}

async function translateBatch(batch, language, attempt = 1) {
  const payload = batch.map((item) => `ZXSEG${item.index}ZX\n${item.prepared}`).join("\n");
  try {
    const result = await translate(payload, "en", language.code);
    const translated = result.translation;
    const parsed = new Map();
    const marker = /ZXSEG\s*(\d+)\s*ZX\s*\n?([\s\S]*?)(?=ZXSEG\s*\d+\s*ZX|$)/gi;
    for (const match of translated.matchAll(marker)) parsed.set(Number(match[1]), match[2].trim());
    const output = [];
    for (const item of batch) {
      const value = parsed.get(item.index);
      const restored = value ? restoreText(value, item.values) : "";
      output.push([
        item.text,
        value && !isCorruptTranslation(item.text, restored)
          ? restored
          : await translateOne(item.text, language, item),
      ]);
    }
    return output;
  } catch (error) {
    if (attempt >= 5) {
      const output = [];
      for (const item of batch) output.push([item.text, await translateOne(item.text, language, item)]);
      return output;
    }
    await sleep(1200 * attempt);
    return translateBatch(batch, language, attempt + 1);
  }
}

async function runPool(items, concurrency, worker) {
  let cursor = 0;
  const runners = Array.from({ length: concurrency }, async () => {
    while (cursor < items.length) {
      const index = cursor++;
      await worker(items[index], index);
    }
  });
  await Promise.all(runners);
}

async function buildTranslationCache(strings, language) {
  const cacheFile = path.join(TRANSLATIONS, `${language.locale}.json`);
  const cache = fs.existsSync(cacheFile) ? JSON.parse(fs.readFileSync(cacheFile, "utf8")) : {};
  const repairs = repairCachePlaceholders(cache);
  const purged = purgeCorruptCacheEntries(cache);
  if (repairs || purged) {
    fs.writeFileSync(cacheFile, `${JSON.stringify(cache, null, 2)}\n`, "utf8");
    console.log(`[${language.locale}] repaired ${repairs} and purged ${purged} corrupted translations`);
  }
  const missing = [...strings].filter((text) => !Object.prototype.hasOwnProperty.call(cache, text));
  const batches = createBatches(missing);
  if (!missing.length) {
    console.log(`[${language.locale}] cache complete (${Object.keys(cache).length} strings)`);
    return cache;
  }
  console.log(`[${language.locale}] translating ${missing.length} strings in ${batches.length} batches`);
  let completed = 0;
  await runPool(batches, 3, async (batch) => {
    const pairs = await translateBatch(batch, language);
    for (const [source, target] of pairs) cache[source] = target;
    completed += 1;
    if (completed % 4 === 0 || completed === batches.length) {
      fs.writeFileSync(cacheFile, `${JSON.stringify(cache, null, 2)}\n`, "utf8");
      console.log(`[${language.locale}] ${completed}/${batches.length} batches`);
    }
    await sleep(160);
  });
  repairCachePlaceholders(cache);
  purgeCorruptCacheEntries(cache);
  fs.writeFileSync(cacheFile, `${JSON.stringify(cache, null, 2)}\n`, "utf8");
  return cache;
}

function translated(cache, value) {
  const original = String(value || "");
  const trimmed = original.trim();
  if (!shouldTranslate(trimmed)) return original;
  const replacement = cache[trimmed] || trimmed;
  return original.replace(trimmed, replacement);
}

function localizeJson(value, cache, key = "") {
  if (Array.isArray(value)) return value.map((item) => localizeJson(item, cache, key));
  if (value && typeof value === "object") {
    return Object.fromEntries(Object.entries(value).map(([childKey, child]) => [childKey, localizeJson(child, cache, childKey)]));
  }
  if (typeof value === "string" && SCHEMA_TRANSLATABLE_KEYS.has(key)) return translated(cache, value);
  return value;
}

function routeFromRelative(relative) {
  const normalized = relative.replaceAll("\\", "/");
  if (normalized === "index.html") return "/";
  if (normalized === "404.html") return "/404.html";
  return `/${normalized.replace(/index\.html$/, "")}`;
}

function localeRoute(route, locale) {
  if (locale === "en") return route;
  if (route === "/") return `/${locale}/`;
  return `/${locale}${route}`;
}

function canonicalUrl(route, locale) {
  return `${BASE_URL}${localeRoute(route, locale)}`;
}

function switcherMarkup(route, current) {
  const currentLanguage = LANGUAGES.find((language) => language.locale === current);
  const links = LANGUAGES.map((language) => {
    const active = language.locale === current ? ' aria-current="page"' : "";
    return `<a href="${localeRoute(route, language.locale)}" lang="${language.hreflang}" dir="${language.dir}"${active}>${language.name}</a>`;
  }).join("");
  return `<details class="language-switcher"><summary aria-label="Select language"><i data-lucide="languages" width="17" height="17" aria-hidden="true"></i><span>${currentLanguage.name}</span><i data-lucide="chevron-down" width="14" height="14" aria-hidden="true"></i></summary><div class="language-menu">${links}</div></details>`;
}

function addAlternates($, route, current) {
  $("link[rel='alternate'][hreflang]").remove();
  for (const language of LANGUAGES) {
    $("head").append(`<link rel="alternate" hreflang="${language.hreflang}" href="${canonicalUrl(route, language.locale)}">`);
  }
  $("head").append(`<link rel="alternate" hreflang="x-default" href="${canonicalUrl(route, "en")}">`);
  $("link[rel='canonical']").attr("href", canonicalUrl(route, current));
  $("meta[property='og:url']").attr("content", canonicalUrl(route, current));
}

function rewriteInternalLinks($, locale) {
  if (locale === "en") return;
  $("a[href]").each((_, element) => {
    const href = $(element).attr("href");
    if (!href || !href.startsWith("/") || href.startsWith("//") || href.startsWith("/assets/")) return;
    if (LANGUAGES.some((language) => language.locale !== "en" && (href === `/${language.locale}/` || href.startsWith(`/${language.locale}/`)))) return;
    $(element).attr("href", href === "/" ? `/${locale}/` : `/${locale}${href}`);
  });
}

function injectFormI18n($, cache) {
  const payload = {
    inquiry: cache["LEXYGO inquiry"] || "LEXYGO inquiry",
    equipment: cache["material handling equipment"] || "material handling equipment",
    name: cache.Name || "Name",
    email: cache.Email || "Email",
    company: cache.Company || "Company",
    country: cache["Country / Region"] || "Country / Region",
    model: cache["Product / Model"] || "Product / Model",
    message: cache.Message || "Message",
  };
  $("head").append(`<script>window.LEXYGO_I18N=${JSON.stringify(payload).replace(/</g, "\\u003c")};</script>`);
}

function localizeHtml(sourceFile, relative, language, cache) {
  const route = routeFromRelative(relative);
  const $ = load(fs.readFileSync(sourceFile, "utf8"), { decodeEntities: false });
  $("html").attr("lang", language.hreflang).attr("dir", language.dir);
  $("title").text(translated(cache, $("title").text()));
  $("body").find("*").addBack().contents().each((_, node) => {
    if (node.type !== "text") return;
    const parent = node.parent && node.parent.name;
    if (["script", "style", "noscript"].includes(parent)) return;
    node.data = translated(cache, node.data);
  });
  for (const [selector, attr] of ATTRIBUTE_SELECTORS) {
    $(selector).each((_, element) => {
      const value = $(element).attr(attr);
      $(element).attr(attr, translated(cache, value));
    });
  }
  $("script[type='application/ld+json']").each((_, element) => {
    try {
      const localized = localizeJson(JSON.parse($(element).text()), cache);
      $(element).text(JSON.stringify(localized));
    } catch {}
  });
  rewriteInternalLinks($, language.locale);
  $(".language-switcher").remove();
  $("nav.main-nav").after(switcherMarkup(route, language.locale));
  addAlternates($, route, language.locale);
  injectFormI18n($, cache);
  const target = language.locale === "en" ? sourceFile : path.join(DIST, language.locale, relative);
  fs.mkdirSync(path.dirname(target), { recursive: true });
  fs.writeFileSync(target, $.html(), "utf8");
}

function localizeLlms(cache, locale) {
  const source = fs.readFileSync(path.join(DIST, "llms.txt"), "utf8");
  const localized = source.split(/\r?\n/).map((line) => translated(cache, line)).join("\n")
    .replaceAll(`${BASE_URL}/`, `${BASE_URL}/${locale}/`);
  const target = path.join(DIST, locale, "llms.txt");
  fs.mkdirSync(path.dirname(target), { recursive: true });
  fs.writeFileSync(target, localized, "utf8");
}

function xmlEscape(value) {
  return value.replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll('"', "&quot;");
}

function buildSitemap(htmlFiles) {
  const routes = htmlFiles.map((file) => routeFromRelative(path.relative(DIST, file))).filter((route) => route !== "/404.html");
  const entries = [];
  for (const route of routes) {
    for (const language of LANGUAGES) {
      const alternates = LANGUAGES.map((alternate) => `<xhtml:link rel="alternate" hreflang="${alternate.hreflang}" href="${xmlEscape(canonicalUrl(route, alternate.locale))}"/>`).join("");
      entries.push(`<url><loc>${xmlEscape(canonicalUrl(route, language.locale))}</loc>${alternates}<xhtml:link rel="alternate" hreflang="x-default" href="${xmlEscape(canonicalUrl(route, "en"))}"/></url>`);
    }
  }
  const xml = `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n${entries.join("\n")}\n</urlset>\n`;
  fs.writeFileSync(path.join(DIST, "sitemap.xml"), xml, "utf8");
}

function collectLlmsStrings(output) {
  const file = path.join(DIST, "llms.txt");
  if (!fs.existsSync(file)) return;
  for (const line of fs.readFileSync(file, "utf8").split(/\r?\n/)) if (shouldTranslate(line)) output.add(line.trim());
}

function validate(htmlFiles) {
  const report = { english_pages: htmlFiles.length, languages: {}, generated_at: new Date().toISOString() };
  for (const language of LANGUAGES) {
    const count = language.locale === "en" ? htmlFiles.length : walk(path.join(DIST, language.locale)).filter((file) => file.endsWith(".html")).length;
    report.languages[language.locale] = { pages: count, complete: count === htmlFiles.length };
    if (count !== htmlFiles.length) throw new Error(`${language.locale} has ${count} pages; expected ${htmlFiles.length}`);
  }
  fs.writeFileSync(path.join(TRANSLATIONS, "report.json"), `${JSON.stringify(report, null, 2)}\n`, "utf8");
  return report;
}

async function main() {
  fs.mkdirSync(TRANSLATIONS, { recursive: true });
  for (const language of LANGUAGES.filter((item) => item.locale !== "en")) {
    fs.rmSync(path.join(DIST, language.locale), { recursive: true, force: true });
  }
  const htmlFiles = walk(DIST).filter(isEnglishHtml).sort();
  const strings = new Set(EXTRA_STRINGS);
  for (const file of htmlFiles) collectHtmlStrings(file, strings);
  collectLlmsStrings(strings);
  console.log(`Collected ${strings.size} unique translatable strings from ${htmlFiles.length} English pages.`);

  const englishCache = Object.fromEntries([...strings].map((text) => [text, text]));
  for (const file of htmlFiles) localizeHtml(file, path.relative(DIST, file), LANGUAGES[0], englishCache);

  for (const language of LANGUAGES.slice(1)) {
    const cache = await buildTranslationCache(strings, language);
    for (const file of htmlFiles) localizeHtml(file, path.relative(DIST, file), language, cache);
    localizeLlms(cache, language.locale);
    console.log(`[${language.locale}] generated ${htmlFiles.length} pages`);
  }
  buildSitemap(htmlFiles);
  const report = validate(htmlFiles);
  console.log(JSON.stringify(report, null, 2));
}

main().catch((error) => {
  console.error(error && error.stack ? error.stack : error);
  process.exit(1);
});
