from __future__ import annotations

import html
import json
import re
import shutil
from pathlib import Path

from site_data import CATEGORIES, COMPANY, GUIDES, PRODUCTS, SOURCE_ROOT


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
ASSETS = DIST / "assets"
PRODUCT_ASSETS = ASSETS / "products"
BASE_URL = COMPANY["domain"]
FULL_SPECS = json.loads((ROOT / "product_specs.json").read_text(encoding="utf-8"))


def esc(value):
    return html.escape(str(value), quote=True)


def route_url(route):
    return BASE_URL + ("/" if route == "/" else route.rstrip("/") + "/")


def write_route(route, content):
    target = DIST / "index.html" if route == "/" else DIST / route.strip("/") / "index.html"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def icon(name, size=18):
    return f'<i data-lucide="{esc(name)}" width="{size}" height="{size}" aria-hidden="true"></i>'


def button(label, href, style="primary", icon_name="arrow-right"):
    return f'<a class="button button-{style}" href="{href}"><span>{esc(label)}</span>{icon(icon_name)}</a>'


def capacity_number(value):
    match = re.search(r"([\d,]+)", value)
    return int(match.group(1).replace(",", "")) if match else 0


def header():
    return f"""
    <a class="skip-link" href="#main">Skip to content</a>
    <header class="site-header"><div class="shell nav-row">
      <a class="brand" href="/" aria-label="LEXYGO home"><span class="brand-mark">L</span><span><strong>LEXYGO</strong><small>Material Handling Equipment</small></span></a>
      <button class="icon-button" type="button" aria-label="Open navigation" aria-expanded="false" data-menu-button title="Menu">{icon('menu')}</button>
      <nav class="main-nav" aria-label="Main navigation" data-menu><a href="/products/">Products</a><a href="/solutions/">Applications</a><a href="/quality/">Manufacturing</a><a href="/oem-odm/">OEM</a><a href="/about/">Company</a><a class="nav-contact" href="/contact/">Inquiry {icon('arrow-up-right', 16)}</a></nav>
    </div></header>
    """


def footer():
    families = "".join(f'<li><a href="/products/{slug}/">{esc(data["name"])}</a></li>' for slug, data in CATEGORIES.items())
    return f"""
    <footer class="site-footer"><div class="shell footer-grid">
      <div><a class="brand brand-footer" href="/"><span class="brand-mark">L</span><span><strong>LEXYGO</strong><small>Material Handling Equipment</small></span></a><p>Manufacturer-direct equipment for pallet movement, stacking, lifting, and industrial logistics.</p></div>
      <div><h2>Products</h2><ul>{families}</ul></div>
      <div><h2>Company</h2><ul><li><a href="/quality/">Manufacturing &amp; quality</a></li><li><a href="/oem-odm/">OEM support</a></li><li><a href="/about/">About us</a></li><li><a href="/contact/">Contact</a></li></ul></div>
      <div><h2>Contact</h2><p>{esc(COMPANY['location'])}</p><p><a href="mailto:{COMPANY['email']}">{esc(COMPANY['email'])}</a></p></div>
    </div><div class="shell footer-bottom"><span>&copy; 2026 {esc(COMPANY['legal_name'])}</span><span>Final specifications are confirmed in the quotation.</span></div></footer>
    """


def breadcrumbs(items):
    visible, structured = [], []
    for index, (label, href) in enumerate(items, start=1):
        visible.append(f'<a href="{href}">{esc(label)}</a><span>/</span>' if href else f'<span aria-current="page">{esc(label)}</span>')
        entry = {"@type": "ListItem", "position": index, "name": label}
        if href:
            entry["item"] = route_url(href)
        structured.append(entry)
    return '<nav class="breadcrumbs shell" aria-label="Breadcrumb">' + "".join(visible) + "</nav>", {"@type": "BreadcrumbList", "itemListElement": structured}


def page(title, description, route, body, schema=None, body_class=""):
    graph = [
        {"@type": "Organization", "@id": BASE_URL + "/#organization", "name": COMPANY["legal_name"], "alternateName": COMPANY["brand"], "url": BASE_URL + "/", "email": COMPANY["email"], "address": {"@type": "PostalAddress", "addressLocality": "Changxing", "addressRegion": "Zhejiang", "addressCountry": "CN"}},
        {"@type": "WebSite", "@id": BASE_URL + "/#website", "url": BASE_URL + "/", "name": "LEXYGO Material Handling Equipment", "publisher": {"@id": BASE_URL + "/#organization"}},
    ]
    if schema:
        graph.extend(schema if isinstance(schema, list) else [schema])
    ld = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False)
    canonical = route_url(route)
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{esc(title)} | LEXYGO</title><meta name="description" content="{esc(description)}"><link rel="canonical" href="{canonical}"><link rel="icon" href="/assets/favicon.svg" type="image/svg+xml"><meta property="og:type" content="website"><meta property="og:title" content="{esc(title)} | LEXYGO"><meta property="og:description" content="{esc(description)}"><meta property="og:url" content="{canonical}"><meta property="og:image" content="{BASE_URL}/assets/og-cover.png"><link rel="stylesheet" href="/assets/site.css"><script type="application/ld+json">{ld}</script></head><body class="{esc(body_class)}">{header()}<main id="main">{body}</main>{footer()}<script src="https://unpkg.com/lucide@0.468.0/dist/umd/lucide.min.js" defer></script><script src="/assets/site.js" defer></script></body></html>"""


def image_class(item):
    if item["slug"] == "mpjtsc1500":
        return " source-brochure source-brochure-highlift source-brochure-two-stage"
    if item["slug"] == "mpjsc1500":
        return " source-brochure source-brochure-highlift"
    return " source-brochure" if item["slug"] == "mpt5tn" else ""


def product_row(item):
    category = CATEGORIES[item["category"]]["name"]
    searchable = " ".join([item["model"], item["name"], item["best_for"], category]).lower()
    return f"""
    <article class="model-row" data-product-card data-category="{item['category']}" data-operation="{esc(item['operation'].lower())}" data-capacity="{capacity_number(item['capacity'])}" data-search="{esc(searchable)}">
      <a class="model-photo{image_class(item)}" href="/products/{item['slug']}/"><img src="/assets/products/{item['image']}" alt="{esc(item['model'] + ' ' + item['name'])}" loading="lazy"></a>
      <div class="model-copy"><p class="overline">{esc(category)}</p><h3><a href="/products/{item['slug']}/"><strong>{esc(item['model'])}</strong> {esc(item['name'])}</a></h3><p>{esc(item['best_for'])}.</p></div>
      <dl class="model-specs"><div><dt>Capacity</dt><dd>{esc(item['capacity'])}</dd></div><div><dt>Lift</dt><dd>{esc(item['lift'])}</dd></div><div><dt>Operation</dt><dd>{esc(item['operation'])}</dd></div></dl>
      <a class="row-action" href="/products/{item['slug']}/" aria-label="View {esc(item['model'])}">{icon('arrow-right', 20)}</a>
    </article>"""


def category_tile(slug, data):
    items = [item for item in PRODUCTS if item["category"] == slug]
    values = [capacity_number(item["capacity"]) for item in items if capacity_number(item["capacity"])]
    capacity_range = f"{min(values):,}-{max(values):,} kg" if values else "Configuration based"
    models = " / ".join(item["model"] for item in items[:4])
    return f"""
    <article class="category-tile"><a class="category-photo" href="/products/{slug}/"><img src="/assets/products/{data['image']}" alt="{esc(data['name'])}" loading="lazy"></a><div class="category-copy"><p class="overline">{len(items)} models</p><h2><a href="/products/{slug}/">{esc(data['name'])}</a></h2><p>{esc(data['short'])}</p><dl><div><dt>Capacity range</dt><dd>{esc(capacity_range)}</dd></div><div><dt>Models</dt><dd>{esc(models)}{(' / ...' if len(items) > 4 else '')}</dd></div></dl><a class="text-link" href="/products/{slug}/">View category {icon('arrow-right', 16)}</a></div></article>"""


def home_page():
    tiles = "".join(category_tile(slug, data) for slug, data in CATEGORIES.items())
    featured = "".join(product_row(next(item for item in PRODUCTS if item["slug"] == slug)) for slug in ["wep20j", "wes1500a", "r4efl3t", "mpt5tn"])
    faqs = [
        ("Which machine is used only to move pallets horizontally?", "Choose a manual or electric pallet truck. Select by load capacity, route length, floor condition, and operator mode."),
        ("When should I choose a pallet stacker?", "Choose a pallet stacker when pallets must be raised into racking or positioned above floor level. Confirm pallet entry, load center, lift height, and residual capacity."),
        ("What information is needed for a forklift quotation?", "Provide the maximum load, load dimensions, lift height, aisle width, floor or outdoor conditions, daily working hours, battery preference, and destination market."),
    ]
    faq_html = "".join(f'<details><summary>{esc(q)}{icon("chevron-down", 16)}</summary><p>{esc(a)}</p></details>' for q, a in faqs)
    body = f"""
    <section class="catalog-intro"><div class="shell catalog-intro-grid"><div><p class="overline">LEXYGO product directory</p><h1>Material Handling Equipment by Product Type</h1><p>Find the right pallet truck, stacker, electric forklift, or warehouse lifting product. Every model page presents the available technical data as searchable English HTML.</p><div class="button-row">{button('Browse all models', '/products/')} {button('Send requirements', '/contact/', 'secondary', 'send')}</div></div><dl class="catalog-summary"><div><dt>Product families</dt><dd>{len(CATEGORIES)}</dd></div><div><dt>Model pages</dt><dd>{len(PRODUCTS)}</dd></div><div><dt>Detailed spec tables</dt><dd>{len(FULL_SPECS)}</dd></div></dl></div></section>
    <section class="directory-section"><div class="shell"><div class="section-heading"><div><p class="overline">Start here</p><h2>Product directory</h2><p>Select a category, then compare model, capacity, lift height, and operating mode.</p></div><a class="text-link" href="/products/">All products {icon('arrow-right', 16)}</a></div><div class="category-grid">{tiles}</div></div></section>
    <section class="model-section model-section-muted"><div class="shell"><div class="section-heading"><div><p class="overline">Common starting points</p><h2>Frequently selected models</h2></div></div><div class="model-list">{featured}</div></div></section>
    <section class="buying-section"><div class="shell buying-grid"><div><p class="overline">Faster product selection</p><h2>Four details narrow the range quickly</h2></div><ol class="selection-steps"><li><strong>Load</strong><span>Maximum weight and load center</span></li><li><strong>Lift</strong><span>Floor movement or required lift height</span></li><li><strong>Route</strong><span>Aisle, turning radius, floor, and gradient</span></li><li><strong>Duty</strong><span>Travel distance, shift length, and charging plan</span></li></ol></div></section>
    <section class="faq-section"><div class="shell two-column"><div><p class="overline">Buyer questions</p><h2>Direct answers before inquiry</h2></div><div class="faq-list">{faq_html}</div></div></section>
    <section class="cta-band"><div class="shell cta-inner"><div><p class="overline">Need a model shortlist?</p><h2>Send the load, lift height, aisle, route, and daily duty.</h2></div>{button('Request a recommendation', '/contact/', 'light', 'send')}</div></section>"""
    schema = {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]}
    return page("Material Handling Equipment Manufacturer", "Compare LEXYGO pallet trucks, pallet stackers, electric forklifts, and warehouse lifting equipment by model and specification.", "/", body, schema, "home")


def products_page():
    rows_html = "".join(product_row(item) for item in PRODUCTS)
    options = "".join(f'<option value="{slug}">{esc(data["name"])}</option>' for slug, data in CATEGORIES.items())
    crumb, crumb_schema = breadcrumbs([("Home", "/"), ("Products", None)])
    body = f"""{crumb}<section class="page-heading"><div class="shell"><p class="overline">Complete catalog</p><h1>Material Handling Equipment</h1><p>Filter {len(PRODUCTS)} product pages by equipment type, operation, capacity, or model number.</p></div></section>
    <section class="catalog-section"><div class="shell"><div class="filter-bar" data-filters><label class="search-field"><span>Search model or application</span><div>{icon('search', 18)}<input type="search" placeholder="Example: WEP20J or narrow aisle" data-search-input></div></label><label><span>Product family</span><select data-category-filter><option value="">All families</option>{options}</select></label><label><span>Operation</span><select data-operation-filter><option value="">All modes</option><option value="walk">Walk-behind</option><option value="stand">Stand-on / rider</option><option value="seated">Seated</option><option value="manual">Manual</option></select></label><label><span>Minimum capacity</span><select data-capacity-filter><option value="0">Any capacity</option><option value="1000">1,000 kg</option><option value="1500">1,500 kg</option><option value="2000">2,000 kg</option><option value="3000">3,000 kg</option><option value="5000">5,000 kg</option><option value="10000">10,000 kg</option></select></label></div><div class="catalog-status"><strong data-result-count>{len(PRODUCTS)} models</strong><button type="button" class="text-button" data-clear-filters>Clear filters</button></div><div class="model-list" data-product-grid>{rows_html}</div><div class="empty-state" data-empty-state hidden><h2>No exact match found</h2><p>Adjust the filters or send the application details for a configuration review.</p>{button('Ask for a recommendation', '/contact/', 'primary', 'send')}</div></div></section>"""
    return page("Product Catalog", "Browse and compare LEXYGO material handling equipment by capacity, lift height, operation, and model.", "/products/", body, [crumb_schema, {"@type": "CollectionPage", "name": "LEXYGO Product Catalog", "url": route_url("/products/")}])


def category_page(slug, data):
    items = [item for item in PRODUCTS if item["category"] == slug]
    rows_html = "".join(product_row(item) for item in items)
    crumb, crumb_schema = breadcrumbs([("Home", "/"), ("Products", "/products/"), (data["name"], None)])
    body = f"""{crumb}<section class="category-heading"><div class="shell category-heading-grid"><div><p class="overline">{len(items)} product pages</p><h1>{esc(data['name'])}</h1><p>{esc(data['short'])}</p><div class="selection-note"><strong>How to choose</strong><span>{esc(data['answer'])}</span></div></div><div class="category-heading-image"><img src="/assets/products/{data['image']}" alt="{esc(data['name'])}" fetchpriority="high"></div></div></section><section class="model-section"><div class="shell"><div class="comparison-head"><span>Model</span><span>Capacity / lift / operation</span></div><div class="model-list">{rows_html}</div></div></section><section class="requirements-band"><div class="shell"><h2>Information required for selection</h2><ul><li>Maximum load and load center</li><li>Required lift height</li><li>Aisle and turning space</li><li>Floor and gradient</li><li>Shift length and battery plan</li><li>Pallet and fork dimensions</li></ul></div></section><section class="cta-band"><div class="shell cta-inner"><div><p class="overline">Selection support</p><h2>Send your working conditions for a model recommendation.</h2></div>{button('Contact LEXYGO', '/contact/', 'light', 'send')}</div></section>"""
    return page(data["name"], data["short"], f"/products/{slug}/", body, [crumb_schema, {"@type": "CollectionPage", "name": data["name"], "description": data["short"], "url": route_url(f"/products/{slug}/")}])


def spec_tables(item):
    sections = FULL_SPECS.get(item["slug"], [])
    if not sections:
        return '<div class="spec-empty"><h2>Configuration data</h2><p>This product is supplied against the confirmed platform size, lifting range, and duty requirement. Request the current configuration sheet.</p></div>'
    blocks = []
    for section in sections:
        rows_html = "".join(f'<tr><th scope="row">{esc(row["name"])}</th><td>{esc(row["unit"] or "-")}</td><td>{esc(row["value"])}</td></tr>' for row in section["rows"])
        blocks.append(f'<section class="spec-group"><h3>{esc(section["title"])}</h3><div class="table-wrap"><table><thead><tr><th>Specification</th><th>Unit</th><th>Value</th></tr></thead><tbody>{rows_html}</tbody></table></div></section>')
    return "".join(blocks)


def product_page(item):
    category = CATEGORIES[item["category"]]
    crumb, crumb_schema = breadcrumbs([("Home", "/"), ("Products", "/products/"), (category["name"], f'/products/{item["category"]}/'), (item["model"], None)])
    quick = [("Rated capacity", item["capacity"]), ("Lift", item["lift"]), ("Operation", item["operation"])] + list(item["specs"].items())[:3]
    quick_html = "".join(f'<div><dt>{esc(name)}</dt><dd>{esc(value)}</dd></div>' for name, value in quick)
    sections = FULL_SPECS.get(item["slug"], [])
    all_rows = [row for section in sections for row in section["rows"]]
    additional = [{"@type": "PropertyValue", "name": row["name"], "unitText": row["unit"], "value": row["value"]} for row in all_rows]
    faqs = [(f"What is the rated capacity of the {item['model']}?", f"The stated rated capacity is {item['capacity']}. Final suitability depends on load center, lift height, attachment, and operating conditions."), (f"What is the lift specification of the {item['model']}?", f"The listed lift specification is {item['lift']}. Confirm the required maximum height and residual capacity before ordering."), (f"What information is needed to quote the {item['model']}?", "Provide load weight and dimensions, lift height, aisle or route conditions, daily duty, battery requirement, quantity, and destination.")]
    faq_html = "".join(f'<details><summary>{esc(q)}{icon("chevron-down", 16)}</summary><p>{esc(a)}</p></details>' for q, a in faqs)
    body = f"""{crumb}<section class="product-overview"><div class="shell product-overview-grid"><div class="product-visual{image_class(item)}"><img src="/assets/products/{item['image']}" alt="{esc(item['model'] + ' ' + item['name'])}" fetchpriority="high"></div><div class="product-title"><p class="overline">{esc(category['name'])}</p><p class="model-code">{esc(item['model'])}</p><h1>{esc(item['name'])}</h1><p>{esc(item['best_for'])}.</p><dl class="product-key-specs">{quick_html}</dl><div class="button-row">{button('Request quotation', '/contact/?model=' + item['model'], 'primary', 'send')} {button('Back to category', '/products/' + item['category'] + '/', 'secondary', 'list')}</div></div></div></section><section class="specification-section"><div class="shell"><div class="specification-heading"><div><p class="overline">Rebuilt from the supplied specification sheet</p><h2>Technical specifications</h2></div><p>All supplied parameters are presented below as English HTML data. Values shown for different mast options remain configuration dependent.</p></div>{spec_tables(item)}</div></section><section class="application-section"><div class="shell two-column"><div><p class="overline">Application</p><h2>Where {esc(item['model'])} fits</h2><p>{esc(item['best_for'])}. Confirm load dimensions, pallet entry, route, gradient, floor condition, and duty cycle before ordering.</p></div><div class="source-note">{icon('info', 20)}<p>{esc(item['note'])}</p></div></div></section><section class="faq-section"><div class="shell two-column"><div><p class="overline">Model questions</p><h2>{esc(item['model'])} FAQ</h2></div><div class="faq-list">{faq_html}</div></div></section><section class="cta-band"><div class="shell cta-inner"><div><p class="overline">Quote this model</p><h2>Send the load, lift height, aisle, pallet, and shift time.</h2></div>{button('Send project details', '/contact/?model=' + item['model'], 'light', 'send')}</div></section>"""
    product_schema = {"@type": "Product", "name": item["name"], "model": item["model"], "sku": item["model"], "image": BASE_URL + "/assets/products/" + item["image"], "description": f"{item['name']} for {item['best_for'].lower()}.", "brand": {"@type": "Brand", "name": COMPANY["brand"]}, "manufacturer": {"@id": BASE_URL + "/#organization"}, "category": category["name"], "additionalProperty": additional}
    faq_schema = {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]}
    return page(f"{item['model']} {item['name']}", f"{item['model']} {item['name']}: {item['capacity']} capacity, {item['lift']} lift, and complete English technical specifications.", f"/products/{item['slug']}/", body, [crumb_schema, product_schema, faq_schema], "product-page")


def simple_page(route, title, eyebrow, intro, sections):
    crumb, crumb_schema = breadcrumbs([("Home", "/"), (title, None)])
    blocks = "".join(f'<section><h2>{esc(heading)}</h2><p>{esc(copy)}</p></section>' for heading, copy in sections)
    body = f'{crumb}<section class="page-heading"><div class="shell"><p class="overline">{esc(eyebrow)}</p><h1>{esc(title)}</h1><p>{esc(intro)}</p></div></section><section class="text-sections"><div class="shell text-section-grid">{blocks}</div></section><section class="cta-band"><div class="shell cta-inner"><div><p class="overline">Project inquiry</p><h2>Send your product and application requirements.</h2></div>{button("Contact LEXYGO", "/contact/", "light", "send")}</div></section>'
    return page(title, intro, route, body, crumb_schema)


def solutions_page():
    return simple_page("/solutions/", "Material Handling Applications", "Selection by task", "Match the equipment type to the load movement, lift height, route, pallet, and daily duty.", [(data["name"], data["answer"]) for data in CATEGORIES.values()])


def guides_index():
    crumb, crumb_schema = breadcrumbs([("Home", "/"), ("Buyer Guides", None)])
    cards = "".join(f'<article><p class="overline">Selection guide</p><h2><a href="/guides/{guide["slug"]}/">{esc(guide["title"])}</a></h2><p>{esc(guide["summary"])}</p><a class="text-link" href="/guides/{guide["slug"]}/">Read guide {icon("arrow-right", 16)}</a></article>' for guide in GUIDES)
    return page("Buyer Guides", "Practical buyer guides for pallet trucks, stackers, and electric forklifts.", "/guides/", f'{crumb}<section class="page-heading"><div class="shell"><p class="overline">Technical buying support</p><h1>Buyer Guides</h1><p>Short answers for common material handling equipment decisions.</p></div></section><section class="text-sections"><div class="shell guide-grid">{cards}</div></section>', crumb_schema)


def guide_page(guide):
    content = {
        "how-to-choose-an-electric-pallet-truck": [("1. Confirm the load", "Record the maximum pallet weight, load center, fork entry, and pallet dimensions."), ("2. Measure the route", "Check travel distance, aisle width, turning space, floor condition, ramps, and thresholds."), ("3. Select operator mode", "Walkie trucks suit compact routes. Rider trucks suit longer and more frequent travel."), ("4. Confirm the battery", "Match battery capacity and charging method to the shift length and available charging time.")],
        "pallet-truck-vs-stacker": [("Pallet truck", "Use a pallet truck for horizontal movement and low fork lift only."), ("Pallet stacker", "Use a stacker when the pallet must be placed into racking or raised for positioning."), ("Selection checkpoint", "If lifting height is above floor-transfer level, specify a stacker and verify residual capacity.")],
        "forklift-capacity-and-aisle-width": [("Rated capacity", "Capacity depends on load center, lift height, attachment, and mast configuration."), ("Aisle width", "Compare right-angle stacking aisle data with the real pallet size and safety clearance."), ("Turning radius", "Turning radius is useful but does not replace the full aisle-width calculation."), ("Site conditions", "Confirm floor loading, surface quality, gradients, door height, and charging area.")],
    }[guide["slug"]]
    crumb, crumb_schema = breadcrumbs([("Home", "/"), ("Buyer Guides", "/guides/"), (guide["title"], None)])
    blocks = "".join(f'<section><h2>{esc(title)}</h2><p>{esc(copy)}</p></section>' for title, copy in content)
    body = f'{crumb}<article class="guide-article shell"><header><p class="overline">Buyer guide</p><h1>{esc(guide["title"])}</h1><p>{esc(guide["summary"])}</p>{button("Browse products", "/products/", "secondary", "list")}</header><div>{blocks}</div></article>'
    return page(guide["title"], guide["summary"], f'/guides/{guide["slug"]}/', body, crumb_schema)


def quality_page():
    return simple_page("/quality/", "Manufacturing & Quality", "Factory support", "A clear specification and inspection process keeps supplied equipment aligned with the approved configuration.", [("Requirement review", "Application, capacity, lift height, route, pallet, battery, destination, and documentation are confirmed before quotation."), ("Configuration control", "The confirmed model, mast, forks, battery, wheels, branding, and packaging form the project baseline."), ("Inspection", "Functional checks, appearance, labels, accessories, and shipment preparation are reviewed against the order."), ("Export documentation", "Manuals, labels, packing information, and available conformity documents are coordinated for the destination market.")])


def oem_page():
    return simple_page("/oem-odm/", "OEM & Configuration Support", "Distributor projects", "LEXYGO supports defined product configurations for distributors, brands, and industrial buyers.", [("Branding", "Nameplates, color, labels, packaging, and documentation can be discussed for qualified projects."), ("Product configuration", "Capacity, mast, lift height, fork dimensions, battery, charger, wheel material, and attachments are reviewed before quotation."), ("Approval", "The agreed sample, drawing, specification, or confirmation method becomes the production reference."), ("Repeat supply", "Packaging, spare parts, and order-level inspection can be aligned with repeat purchasing requirements.")])


def about_page():
    return simple_page("/about/", "About LEXYGO", "Material handling manufacturer", f"{COMPANY['legal_name']} develops and supplies practical equipment for moving, lifting, and stacking material loads.", [("Product focus", "Electric pallet trucks, electric pallet stackers, electric forklifts, manual pallet trucks, and warehouse lifting equipment."), ("Factory location", f"Manufacturing and project coordination in {COMPANY['location']}."), ("Commercial approach", "Model-level data, application-based selection, configurable projects, and direct export communication."), ("Brand", "LEXYGO is used for the independently marketed material handling product range.")])


def contact_page():
    crumb, crumb_schema = breadcrumbs([("Home", "/"), ("Contact", None)])
    body = f"""{crumb}<section class="page-heading"><div class="shell"><p class="overline">Factory inquiry</p><h1>Request a Model or Configuration</h1><p>Provide the product, load, lift height, route, quantity, and destination. Your email client will open with the completed inquiry.</p></div></section><section class="contact-section"><div class="shell contact-grid"><form class="quote-form" data-mailto-form data-email="{COMPANY['email']}"><div class="form-grid"><label><span>Company</span><input name="company" required></label><label><span>Name</span><input name="name" required></label><label><span>Business email</span><input type="email" name="email" required></label><label><span>Country / region</span><input name="country" required></label><label><span>Model / product</span><input name="model" data-model-field></label><label><span>Quantity</span><input name="quantity"></label><label><span>Maximum load</span><input name="load" placeholder="kg"></label><label><span>Required lift height</span><input name="height" placeholder="mm"></label><label class="full"><span>Application and working conditions</span><textarea name="details" rows="6" required></textarea></label></div><button class="button button-primary" type="submit">Create email inquiry {icon('send', 18)}</button></form><aside><h2>Direct contact</h2><p><strong>Email</strong><a href="mailto:{COMPANY['email']}">{esc(COMPANY['email'])}</a></p><p><strong>Location</strong><span>{esc(COMPANY['location'])}</span></p><h2>Useful details</h2><ul><li>Load weight and dimensions</li><li>Lift height and aisle width</li><li>Floor, gradient, and route</li><li>Daily duty and battery preference</li><li>Quantity and destination</li></ul></aside></div></section>"""
    return page("Contact LEXYGO", "Contact LEXYGO for pallet truck, stacker, electric forklift, and warehouse equipment quotations.", "/contact/", body, crumb_schema)


def not_found_page():
    return page("Page Not Found", "The requested LEXYGO page was not found.", "/404/", f'<section class="not-found shell"><p class="overline">404</p><h1>Page not found</h1><p>Browse the product directory or return to the home page.</p>{button("Product directory", "/products/")} {button("Home", "/", "secondary", "home")}</section>')


def find_source_file(name):
    matches = [path for path in SOURCE_ROOT.rglob("*") if path.is_file() and path.name.lower() == name.lower()]
    if not matches:
        raise FileNotFoundError(name)
    return matches[0]


def copy_product_assets():
    PRODUCT_ASSETS.mkdir(parents=True, exist_ok=True)
    warehouse = ROOT / "tmp" / "warehouse-assets"
    explicit = {"r4efl12t.png": find_source_file("REEF12T.png"), "sc1016.png": warehouse / "image190.png", "qes12e.png": warehouse / "image251.png", "qes15e.png": warehouse / "image252.png", "qes15lie.png": warehouse / "image254.png", "qed1530.png": warehouse / "image191.png", "warehouse-scissor-lift-table.png": warehouse / "image139.png", "warehouse-material-lift-cart.png": warehouse / "image3.png"}
    for item in PRODUCTS:
        source = explicit[item["image"]] if item["image"] in explicit else find_source_file(item["image"])
        if not source.exists():
            raise FileNotFoundError(source)
        shutil.copy2(source, PRODUCT_ASSETS / item["image"])
    shutil.copy2(PRODUCT_ASSETS / "r4efl3t.png", ASSETS / "og-cover.png")


CSS = r"""
:root{--ink:#162126;--muted:#596a72;--line:#d8e0e3;--soft:#f4f7f8;--teal:#0d6b73;--teal-dark:#084b52;--orange:#e45b25;--orange-dark:#b94014;--white:#fff;--max:1220px;--shadow:0 12px 30px rgba(19,40,48,.1)}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;color:var(--ink);background:#fff;font-family:Arial,"Helvetica Neue",sans-serif;line-height:1.55}img{display:block;max-width:100%}a{color:inherit;text-decoration:none}button,input,select,textarea{font:inherit}h1,h2,h3,p{overflow-wrap:anywhere}h1,h2,h3{letter-spacing:0}.shell{width:min(calc(100% - 48px),var(--max));margin-inline:auto}.skip-link{position:fixed;top:8px;left:8px;z-index:1000;background:#fff;padding:8px;transform:translateY(-150%)}.skip-link:focus{transform:none}.site-header{position:sticky;top:0;z-index:50;background:rgba(255,255,255,.97);border-bottom:1px solid var(--line)}.nav-row{height:74px;display:flex;align-items:center;justify-content:space-between;gap:28px}.brand{display:inline-flex;align-items:center;gap:10px;min-width:238px}.brand-mark{width:38px;height:38px;display:grid;place-items:center;background:var(--orange);color:#fff;font-weight:900;font-size:22px;border-radius:3px}.brand strong,.brand small{display:block}.brand strong{font-size:21px;line-height:1}.brand small{margin-top:3px;color:var(--muted);font-size:11px}.main-nav{display:flex;align-items:center;gap:25px;font-size:14px;font-weight:700}.main-nav>a:hover{color:var(--teal)}.nav-contact{background:var(--teal);color:#fff;padding:10px 13px;display:inline-flex;align-items:center;gap:7px;border-radius:3px}.nav-contact:hover{background:var(--teal-dark);color:#fff!important}.icon-button{width:42px;height:42px;border:0;background:transparent;display:none;place-items:center}.overline{margin:0 0 8px;color:var(--orange-dark);font-size:12px;font-weight:800;text-transform:uppercase;letter-spacing:0}.catalog-intro{border-bottom:1px solid var(--line);background:linear-gradient(90deg,#fff 0 70%,#edf5f5 70%)}.catalog-intro-grid{min-height:320px;display:grid;grid-template-columns:minmax(0,1fr) 340px;align-items:center;gap:70px;padding-block:46px}.catalog-intro h1,.page-heading h1,.category-heading h1,.product-title h1,.guide-article h1,.not-found h1{font-size:48px;line-height:1.08;margin:0 0 16px}.catalog-intro p:not(.overline),.page-heading p,.category-heading p,.product-title>p:last-of-type,.guide-article header p{font-size:18px;color:var(--muted);max-width:800px;margin:0}.catalog-summary{margin:0;border-left:4px solid var(--teal);background:#fff}.catalog-summary div{display:flex;justify-content:space-between;align-items:center;gap:16px;padding:15px 18px;border-bottom:1px solid var(--line)}.catalog-summary div:last-child{border-bottom:0}.catalog-summary dt{font-size:13px;color:var(--muted)}.catalog-summary dd{font-size:21px;font-weight:900;margin:0}.button-row{display:flex;flex-wrap:wrap;gap:10px;margin-top:24px}.button{min-height:44px;padding:10px 15px;display:inline-flex;align-items:center;justify-content:center;gap:8px;border:1px solid transparent;border-radius:3px;font-weight:800}.button-primary{background:var(--orange);color:#fff}.button-primary:hover{background:var(--orange-dark)}.button-secondary{background:#fff;border-color:#aebbc0}.button-secondary:hover{border-color:var(--teal);color:var(--teal)}.button-light{background:#fff;color:var(--ink)}.directory-section,.model-section,.buying-section,.faq-section,.catalog-section,.specification-section,.application-section,.text-sections,.contact-section{padding:62px 0}.section-heading{display:flex;align-items:end;justify-content:space-between;gap:30px;margin-bottom:28px}.section-heading h2,.buying-grid h2,.two-column h2,.specification-heading h2,.requirements-band h2,.text-section-grid h2,.contact-grid h2{font-size:30px;line-height:1.2;margin:0}.section-heading p{margin:6px 0 0;color:var(--muted)}.text-link{display:inline-flex;align-items:center;gap:6px;color:var(--teal-dark);font-size:14px;font-weight:800}.text-link:hover{color:var(--orange-dark)}.category-grid{display:grid;grid-template-columns:1fr 1fr;border-top:1px solid var(--line);border-left:1px solid var(--line)}.category-tile{display:grid;grid-template-columns:220px minmax(0,1fr);min-width:0;border-right:1px solid var(--line);border-bottom:1px solid var(--line);background:#fff}.category-tile:last-child:nth-child(odd){grid-column:1/-1;grid-template-columns:260px minmax(0,1fr)}.category-photo{aspect-ratio:4/3;align-self:center;display:grid;place-items:center;background:var(--soft);padding:16px;margin:20px}.category-photo img{width:100%;height:100%;object-fit:contain}.category-copy{padding:24px 24px 24px 0;min-width:0}.category-copy h2{font-size:23px;line-height:1.2;margin:0 0 8px}.category-copy>p:not(.overline){font-size:14px;color:var(--muted);margin:0 0 14px}.category-copy dl{display:grid;grid-template-columns:150px minmax(0,1fr);margin:0 0 14px;font-size:13px}.category-copy dl div{display:contents}.category-copy dt,.category-copy dd{padding:6px 0;border-top:1px solid var(--line)}.category-copy dt{color:var(--muted)}.category-copy dd{margin:0;font-weight:700}.model-section-muted{background:var(--soft)}.model-list{border-top:1px solid var(--line)}.model-row{display:grid;grid-template-columns:180px minmax(260px,1fr) minmax(320px,390px) 50px;gap:24px;align-items:center;min-width:0;padding:16px 0;border-bottom:1px solid var(--line);background:#fff}.model-section-muted .model-row{padding-inline:16px}.model-photo{aspect-ratio:4/3;display:grid;place-items:center;background:var(--soft);overflow:hidden;padding:10px}.model-photo img,.category-heading-image img,.product-visual img{width:100%;height:100%;object-fit:contain}.source-brochure{padding:0}.source-brochure img{width:185%;height:185%;max-width:none;object-fit:cover;object-position:90% 7%}.model-copy{min-width:0}.model-copy h3{font-size:18px;line-height:1.28;margin:0 0 7px}.model-copy h3 strong{color:var(--teal-dark);margin-right:8px}.model-copy p:not(.overline){font-size:13px;color:var(--muted);margin:0}.model-specs{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));margin:0}.model-specs div{min-width:0;padding:8px 13px;border-left:2px solid var(--line)}.model-specs dt{font-size:11px;color:var(--muted)}.model-specs dd{font-size:13px;font-weight:800;margin:2px 0 0}.row-action{width:40px;height:40px;display:grid;place-items:center;border:1px solid var(--line);border-radius:3px}.row-action:hover{border-color:var(--teal);color:var(--teal)}.buying-grid{display:grid;grid-template-columns:.75fr 1.25fr;gap:70px}.selection-steps{display:grid;grid-template-columns:1fr 1fr;list-style:none;counter-reset:step;margin:0;padding:0;border-top:1px solid var(--line)}.selection-steps li{counter-increment:step;display:grid;grid-template-columns:34px 90px 1fr;gap:10px;padding:16px 0;border-bottom:1px solid var(--line)}.selection-steps li:before{content:counter(step,decimal-leading-zero);color:var(--orange);font-weight:900}.selection-steps span{color:var(--muted)}.two-column{display:grid;grid-template-columns:.75fr 1.25fr;gap:70px;align-items:start}.faq-section{background:var(--soft)}.faq-list details{border-top:1px solid var(--line);padding:16px 0}.faq-list details:last-child{border-bottom:1px solid var(--line)}.faq-list summary{display:flex;justify-content:space-between;gap:20px;font-weight:800;cursor:pointer;list-style:none}.faq-list p{margin:9px 30px 0 0;color:var(--muted)}.cta-band{background:var(--teal-dark);color:#fff;padding:38px 0}.cta-band .overline{color:#ffd19d}.cta-inner{display:flex;align-items:center;justify-content:space-between;gap:30px}.cta-band h2{font-size:28px;line-height:1.2;margin:0}.breadcrumbs{min-height:48px;display:flex;align-items:center;gap:8px;color:var(--muted);font-size:13px}.breadcrumbs a:hover{color:var(--orange-dark)}.page-heading{padding:44px 0 50px;border-bottom:1px solid var(--line);background:var(--soft)}.filter-bar{display:grid;grid-template-columns:1.4fr 1fr 1fr .8fr;gap:12px;padding:15px;background:var(--soft);border:1px solid var(--line);position:sticky;top:74px;z-index:20}.filter-bar label,.form-grid label{font-size:12px;font-weight:800;color:#394a52}.filter-bar label>span,.form-grid label span{display:block}.filter-bar select,.filter-bar input,.form-grid input,.form-grid textarea{width:100%;min-height:44px;margin-top:6px;border:1px solid #b8c3c7;background:#fff;border-radius:3px;padding:9px 11px}.search-field>div{position:relative}.search-field svg{position:absolute;left:11px;top:19px;color:var(--muted)}.search-field input{padding-left:37px}.catalog-status{display:flex;align-items:center;justify-content:space-between;padding:18px 0}.text-button{border:0;background:transparent;color:var(--teal);font-weight:800;cursor:pointer}.empty-state{text-align:center;padding:70px 20px}.category-heading{padding:38px 0 50px;border-bottom:1px solid var(--line);background:var(--soft)}.category-heading-grid{display:grid;grid-template-columns:minmax(0,1fr) 360px;gap:70px;align-items:center}.category-heading-image{aspect-ratio:4/3;display:grid;place-items:center;background:#fff;padding:18px}.selection-note{display:grid;grid-template-columns:110px 1fr;gap:14px;margin-top:22px;padding:14px 0;border-top:1px solid var(--line);border-bottom:1px solid var(--line);font-size:14px}.selection-note span{color:var(--muted)}.comparison-head{display:grid;grid-template-columns:1fr 390px 50px;gap:24px;margin-left:204px;padding:0 0 8px;color:var(--muted);font-size:11px;font-weight:800;text-transform:uppercase}.requirements-band{padding:42px 0;background:var(--soft);border-top:1px solid var(--line)}.requirements-band ul{display:grid;grid-template-columns:repeat(3,1fr);gap:0 25px;margin:20px 0 0;padding:0;list-style:none}.requirements-band li{padding:11px 0;border-top:1px solid var(--line)}.product-overview{padding:30px 0 58px}.product-overview-grid{display:grid;grid-template-columns:minmax(0,1.05fr) minmax(0,.95fr);gap:60px;align-items:center}.product-visual{aspect-ratio:4/3;display:grid;place-items:center;background:var(--soft);overflow:hidden;padding:24px}.product-title .model-code{font-size:15px;font-weight:900;color:var(--teal);margin:0 0 5px}.product-title h1{font-size:42px}.product-key-specs{display:grid;grid-template-columns:1fr 1fr;margin:24px 0 0;border-top:1px solid var(--line)}.product-key-specs div{padding:12px 10px 12px 0;border-bottom:1px solid var(--line)}.product-key-specs dt{font-size:11px;color:var(--muted)}.product-key-specs dd{font-size:14px;font-weight:800;margin:3px 0 0}.specification-section{background:var(--soft)}.specification-heading{display:grid;grid-template-columns:1fr 1fr;gap:50px;align-items:end;margin-bottom:28px}.specification-heading p{margin:0;color:var(--muted)}.spec-group{margin-bottom:28px}.spec-group h3{font-size:17px;margin:0;padding:10px 13px;background:var(--teal-dark);color:#fff}.table-wrap{overflow-x:auto;background:#fff}table{width:100%;border-collapse:collapse;min-width:690px}th,td{text-align:left;padding:10px 13px;border-bottom:1px solid var(--line);vertical-align:top}thead th{background:#e8eef0;color:#34464e;font-size:11px;text-transform:uppercase}tbody th{width:48%;font-size:13px;font-weight:600}tbody td:nth-child(2){width:16%;color:var(--muted);font-size:13px}tbody td:last-child{font-weight:700;font-size:13px}.spec-empty{background:#fff;border-left:4px solid var(--orange);padding:22px}.source-note{display:flex;gap:12px;background:#e9f3f3;padding:18px;color:var(--teal-dark)}.source-note p{margin:0}.text-section-grid{display:grid;grid-template-columns:1fr 1fr;border-top:1px solid var(--line)}.text-section-grid section{padding:26px;border-bottom:1px solid var(--line)}.text-section-grid section:nth-child(odd){border-right:1px solid var(--line)}.text-section-grid p{color:var(--muted)}.guide-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:22px}.guide-grid article{padding:24px;background:var(--soft);border-top:4px solid var(--teal)}.guide-grid h2{font-size:22px}.guide-grid p{color:var(--muted)}.guide-article{display:grid;grid-template-columns:.8fr 1.2fr;gap:70px;padding-block:55px}.guide-article header{position:sticky;top:110px;align-self:start}.guide-article>div section{padding:0 0 24px;margin-bottom:24px;border-bottom:1px solid var(--line)}.guide-article h2{font-size:23px;margin:0 0 8px}.guide-article>div p{color:var(--muted)}.contact-grid{display:grid;grid-template-columns:1.35fr .65fr;gap:50px}.quote-form{padding:26px;background:var(--soft);border-top:4px solid var(--orange)}.form-grid{display:grid;grid-template-columns:1fr 1fr;gap:15px;margin-bottom:19px}.form-grid .full{grid-column:1/-1}.contact-grid aside{border-left:1px solid var(--line);padding-left:30px}.contact-grid aside h2{font-size:20px}.contact-grid aside p strong,.contact-grid aside p span,.contact-grid aside p a{display:block}.contact-grid aside p span,.contact-grid aside p a{color:var(--muted)}.contact-grid aside ul{padding-left:20px}.not-found{padding-block:100px}.site-footer{background:#152227;color:#bdc9ce;padding:50px 0 20px}.footer-grid{display:grid;grid-template-columns:1.35fr 1fr .8fr 1fr;gap:42px}.brand-footer{color:#fff}.brand-footer small{color:#a7b5bb}.footer-grid h2{font-size:13px;color:#fff;text-transform:uppercase}.footer-grid p,.footer-grid ul{font-size:13px}.footer-grid ul{padding:0;list-style:none}.footer-grid li{margin:7px 0}.footer-grid a:hover{color:#fff}.footer-bottom{display:flex;justify-content:space-between;gap:20px;margin-top:35px;padding-top:17px;border-top:1px solid #314047;font-size:12px;color:#8fa0a7}
@media(max-width:1020px){.main-nav{position:absolute;top:100%;left:0;right:0;display:none;flex-direction:column;align-items:stretch;gap:0;background:#fff;border-bottom:1px solid var(--line);padding:10px 24px}.main-nav.is-open{display:flex}.main-nav>a{padding:10px}.icon-button{display:grid}.catalog-intro-grid{grid-template-columns:1fr 280px;gap:35px}.category-grid{grid-template-columns:1fr}.category-tile:last-child:nth-child(odd){grid-column:auto;grid-template-columns:220px minmax(0,1fr)}.model-row{grid-template-columns:150px minmax(220px,1fr) 290px 44px;gap:16px}.filter-bar{grid-template-columns:1fr 1fr}.product-overview-grid{gap:35px}.footer-grid{grid-template-columns:1fr 1fr}}
@media(max-width:760px){.shell{width:min(calc(100% - 28px),var(--max))}.nav-row{height:66px}.brand{min-width:0}.brand small{display:none}.catalog-intro{background:#fff}.catalog-intro-grid{grid-template-columns:1fr;min-height:0;padding-block:36px}.catalog-intro h1,.page-heading h1,.category-heading h1,.guide-article h1{font-size:36px}.catalog-summary{display:grid;grid-template-columns:repeat(3,1fr);border-left:0;border-top:4px solid var(--teal)}.catalog-summary div{display:block;padding:12px 8px;text-align:center;border-right:1px solid var(--line);border-bottom:0}.catalog-summary div:last-child{border-right:0}.catalog-summary dt{font-size:10px}.directory-section,.model-section,.buying-section,.faq-section,.catalog-section,.specification-section,.application-section,.text-sections,.contact-section{padding:46px 0}.section-heading,.cta-inner{align-items:flex-start;flex-direction:column}.category-tile,.category-tile:last-child:nth-child(odd){grid-template-columns:130px minmax(0,1fr)}.category-photo{margin:12px;padding:8px}.category-copy{padding:16px 14px 16px 0}.category-copy h2{font-size:19px}.category-copy dl{grid-template-columns:1fr}.category-copy dl div{display:block;border-top:1px solid var(--line);padding:5px 0}.category-copy dt,.category-copy dd{border:0;padding:0}.model-row{grid-template-columns:112px minmax(0,1fr) 40px;gap:12px;padding:14px 0}.model-copy{grid-column:2}.model-specs{grid-column:1/-1;grid-row:2}.row-action{grid-column:3;grid-row:1}.model-photo{grid-column:1;grid-row:1}.model-specs div{padding-left:9px}.buying-grid,.two-column,.category-heading-grid,.product-overview-grid,.specification-heading,.guide-article,.contact-grid{grid-template-columns:1fr;gap:32px}.selection-steps{grid-template-columns:1fr}.filter-bar{position:static;grid-template-columns:1fr}.category-heading-image{max-width:420px;width:100%;margin:auto}.comparison-head{display:none}.requirements-band ul{grid-template-columns:1fr 1fr}.product-visual{padding:14px}.product-title h1{font-size:34px}.product-key-specs{grid-template-columns:1fr}.text-section-grid,.guide-grid{grid-template-columns:1fr}.text-section-grid section:nth-child(odd){border-right:0}.guide-article header{position:static}.form-grid{grid-template-columns:1fr}.form-grid .full{grid-column:auto}.contact-grid aside{border-left:0;border-top:1px solid var(--line);padding:24px 0 0}.footer-grid{grid-template-columns:1fr}.footer-bottom{flex-direction:column}.source-brochure img{width:190%;height:190%;object-position:91% 7%}}
@media(max-width:480px){.category-tile,.category-tile:last-child:nth-child(odd){grid-template-columns:1fr}.category-photo{aspect-ratio:16/9;margin:0}.category-copy{padding:18px}.model-row{grid-template-columns:92px minmax(0,1fr) 36px}.model-specs{grid-template-columns:1fr}.model-specs div{border-left:0;border-top:1px solid var(--line)}.requirements-band ul{grid-template-columns:1fr}.catalog-summary{grid-template-columns:1fr}.catalog-summary div{display:flex;text-align:left;border-right:0;border-bottom:1px solid var(--line)}.button{width:100%}}
"""


CSS += r"""
.source-brochure{position:relative}
.source-brochure img{position:absolute;inset:0;width:100%;height:100%;max-width:none;object-fit:contain;object-position:center;transform:scale(3.2);transform-origin:75% 18%}
.source-brochure-highlift img{transform:scale(2.6);transform-origin:85% 28%}
.source-brochure-two-stage img{transform-origin:85% 28%}
@media(max-width:760px){.source-brochure img{width:100%;height:100%;object-position:center;transform:scale(3.2);transform-origin:75% 18%}.source-brochure-highlift img{transform:scale(2.6);transform-origin:85% 28%}.source-brochure-two-stage img{transform-origin:85% 28%}}
"""


JS = r"""
document.addEventListener('DOMContentLoaded',()=>{if(window.lucide){window.lucide.createIcons()}const menuButton=document.querySelector('[data-menu-button]');const menu=document.querySelector('[data-menu]');if(menuButton&&menu){menuButton.addEventListener('click',()=>{const open=menu.classList.toggle('is-open');menuButton.setAttribute('aria-expanded',String(open))})}const grid=document.querySelector('[data-product-grid]');if(grid){const cards=[...grid.querySelectorAll('[data-product-card]')];const search=document.querySelector('[data-search-input]');const category=document.querySelector('[data-category-filter]');const operation=document.querySelector('[data-operation-filter]');const capacity=document.querySelector('[data-capacity-filter]');const count=document.querySelector('[data-result-count]');const empty=document.querySelector('[data-empty-state]');const params=new URLSearchParams(location.search);if(params.get('category')&&category)category.value=params.get('category');if(params.get('capacity')&&capacity)capacity.value=params.get('capacity');if(params.get('operation')&&operation)operation.value=params.get('operation');const apply=()=>{const q=(search?.value||'').trim().toLowerCase();const cat=category?.value||'';const op=(operation?.value||'').toLowerCase();const cap=Number(capacity?.value||0);let shown=0;cards.forEach(card=>{const matches=(!q||card.dataset.search.includes(q))&&(!cat||card.dataset.category===cat)&&(!op||card.dataset.operation.includes(op)||(op==='stand'&&card.dataset.operation.includes('rider')))&&(!cap||Number(card.dataset.capacity)>=cap);card.hidden=!matches;if(matches)shown++});if(count)count.textContent=`${shown} model${shown===1?'':'s'}`;if(empty)empty.hidden=shown!==0};[search,category,operation,capacity].filter(Boolean).forEach(el=>el.addEventListener(el===search?'input':'change',apply));document.querySelector('[data-clear-filters]')?.addEventListener('click',()=>{if(search)search.value='';if(category)category.value='';if(operation)operation.value='';if(capacity)capacity.value='0';apply()});apply()}const modelField=document.querySelector('[data-model-field]');if(modelField){const model=new URLSearchParams(location.search).get('model');if(model)modelField.value=model}const form=document.querySelector('[data-mailto-form]');if(form){form.addEventListener('submit',event=>{event.preventDefault();const data=new FormData(form);const subject=`LEXYGO inquiry: ${data.get('model')||'material handling equipment'} - ${data.get('company')}`;const body=[`Company: ${data.get('company')}`,`Name: ${data.get('name')}`,`Business email: ${data.get('email')}`,`Country / region: ${data.get('country')}`,`Model / product: ${data.get('model')||''}`,`Quantity: ${data.get('quantity')||''}`,`Maximum load: ${data.get('load')||''}`,`Required lift height: ${data.get('height')||''}`,'',`Application and working conditions:`,` ${data.get('details')}`].join('\n');location.href=`mailto:${form.dataset.email}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`})}});
"""


FAVICON = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="4" fill="#e45b25"/><path d="M18 12h10v32h20v8H18z" fill="#fff"/><path d="M38 20h8v17h-8z" fill="#0d6b73"/></svg>"""


def build():
    if DIST.exists():
        shutil.rmtree(DIST)
    ASSETS.mkdir(parents=True)
    copy_product_assets()
    (ASSETS / "site.css").write_text(CSS, encoding="utf-8")
    (ASSETS / "site.js").write_text(JS, encoding="utf-8")
    (ASSETS / "favicon.svg").write_text(FAVICON, encoding="utf-8")
    write_route("/", home_page())
    write_route("/products/", products_page())
    for slug, data in CATEGORIES.items():
        write_route(f"/products/{slug}/", category_page(slug, data))
    for item in PRODUCTS:
        write_route(f'/products/{item["slug"]}/', product_page(item))
    write_route("/solutions/", solutions_page())
    write_route("/guides/", guides_index())
    for guide in GUIDES:
        write_route(f'/guides/{guide["slug"]}/', guide_page(guide))
    write_route("/quality/", quality_page())
    write_route("/oem-odm/", oem_page())
    write_route("/about/", about_page())
    write_route("/contact/", contact_page())
    (DIST / "404.html").write_text(not_found_page(), encoding="utf-8")
    routes = ["/", "/products/"] + [f"/products/{slug}/" for slug in CATEGORIES] + [f'/products/{item["slug"]}/' for item in PRODUCTS] + ["/solutions/", "/guides/", "/quality/", "/oem-odm/", "/about/", "/contact/"] + [f'/guides/{guide["slug"]}/' for guide in GUIDES]
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(f"  <url><loc>{route_url(route)}</loc></url>" for route in routes) + "\n</urlset>\n"
    (DIST / "sitemap.xml").write_text(sitemap, encoding="utf-8")
    (DIST / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {BASE_URL}/sitemap.xml\n", encoding="utf-8")
    llms = ["# LEXYGO Material Handling Equipment", "", f"> {COMPANY['legal_name']} supplies model-specific pallet trucks, pallet stackers, electric forklifts, manual pallet trucks, and warehouse equipment.", "", "## Product families"]
    llms += [f"- [{data['name']}]({route_url(f'/products/{slug}/')}): {data['short']}" for slug, data in CATEGORIES.items()]
    llms += ["", "## Model pages"] + [f"- [{item['model']} {item['name']}]({route_url('/products/' + item['slug'] + '/')}): {item['capacity']}; {item['lift']}; {item['operation']}." for item in PRODUCTS]
    llms += ["", "## Contact", f"- Email: {COMPANY['email']}", "- Final specifications are confirmed against the quotation and project configuration."]
    (DIST / "llms.txt").write_text("\n".join(llms) + "\n", encoding="utf-8")
    print(f"Built {len(routes)} routes and {len(PRODUCTS)} product pages in {DIST}")


if __name__ == "__main__":
    build()
