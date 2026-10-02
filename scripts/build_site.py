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


def esc(value):
    return html.escape(str(value), quote=True)


def route_url(route):
    if route == "/":
        return BASE_URL + "/"
    return BASE_URL + route.rstrip("/") + "/"


def write_route(route, content):
    if route == "/":
        target = DIST / "index.html"
    else:
        target = DIST / route.strip("/") / "index.html"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def icon(name, size=18):
    return f'<i data-lucide="{esc(name)}" width="{size}" height="{size}" aria-hidden="true"></i>'


def button(label, href, style="primary", icon_name="arrow-right"):
    return (
        f'<a class="button button-{style}" href="{href}">'
        f'<span>{esc(label)}</span>{icon(icon_name)}</a>'
    )


def header():
    return f"""
    <a class="skip-link" href="#main">Skip to content</a>
    <header class="site-header">
      <div class="utility-bar"><div class="shell utility-inner">
        <span>Manufacturer-direct material handling equipment</span>
        <a href="mailto:{COMPANY['email']}">{icon('mail', 15)} {COMPANY['email']}</a>
      </div></div>
      <div class="shell nav-row">
        <a class="brand" href="/" aria-label="LEXYGO home">
          <span class="brand-mark">L</span><span><strong>LEXYGO</strong><small>Material Handling</small></span>
        </a>
        <button class="icon-button menu-button" type="button" aria-label="Open navigation" aria-expanded="false" data-menu-button title="Menu">{icon('menu')}</button>
        <nav class="main-nav" aria-label="Main navigation" data-menu>
          <a href="/products/">Products</a>
          <a href="/solutions/">Solutions</a>
          <a href="/guides/">Buyer Guides</a>
          <a href="/quality/">Quality</a>
          <a href="/oem-odm/">OEM &amp; ODM</a>
          <a href="/about/">About</a>
          <a class="nav-cta" href="/contact/">Request a Quote {icon('arrow-up-right', 16)}</a>
        </nav>
      </div>
    </header>
    """


def footer():
    categories = "".join(
        f'<li><a href="/products/{slug}/">{esc(data["name"])}</a></li>'
        for slug, data in CATEGORIES.items()
    )
    return f"""
    <footer class="site-footer">
      <div class="shell footer-grid">
        <div>
          <a class="brand brand-footer" href="/"><span class="brand-mark">L</span><span><strong>LEXYGO</strong><small>Material Handling</small></span></a>
          <p>Practical electric and manual equipment for pallet movement, stacking, and warehouse material flow.</p>
        </div>
        <div><h2>Product families</h2><ul>{categories}</ul></div>
        <div><h2>Company</h2><ul>
          <li><a href="/quality/">Quality process</a></li><li><a href="/oem-odm/">OEM &amp; ODM</a></li>
          <li><a href="/about/">About the manufacturer</a></li><li><a href="/contact/">Contact</a></li>
        </ul></div>
        <div><h2>Contact</h2><p>{esc(COMPANY['location'])}</p><p><a href="mailto:{COMPANY['email']}">{esc(COMPANY['email'])}</a></p></div>
      </div>
      <div class="shell footer-bottom"><span>&copy; 2026 LEXYGO. {esc(COMPANY['legal_name'])}.</span><span>Specifications are subject to confirmed configuration.</span></div>
    </footer>
    """


def breadcrumbs(items):
    links = []
    structured = []
    for index, (label, href) in enumerate(items, start=1):
        if href:
            links.append(f'<a href="{href}">{esc(label)}</a><span>/</span>')
            item_url = route_url(href)
        else:
            links.append(f'<span aria-current="page">{esc(label)}</span>')
            item_url = None
        entry = {"@type": "ListItem", "position": index, "name": label}
        if item_url:
            entry["item"] = item_url
        structured.append(entry)
    return (
        '<nav class="breadcrumbs shell" aria-label="Breadcrumb">' + "".join(links) + "</nav>",
        {"@type": "BreadcrumbList", "itemListElement": structured},
    )


def page(title, description, route, body, schema=None, body_class=""):
    canonical = route_url(route)
    graph = [
        {
            "@type": "Organization",
            "@id": BASE_URL + "/#organization",
            "name": COMPANY["legal_name"],
            "alternateName": COMPANY["brand"],
            "url": BASE_URL + "/",
            "email": COMPANY["email"],
            "address": {"@type": "PostalAddress", "addressLocality": "Changxing", "addressRegion": "Zhejiang", "addressCountry": "CN"},
        },
        {
            "@type": "WebSite",
            "@id": BASE_URL + "/#website",
            "url": BASE_URL + "/",
            "name": "LEXYGO Material Handling",
            "publisher": {"@id": BASE_URL + "/#organization"},
        },
    ]
    if schema:
        graph.extend(schema if isinstance(schema, list) else [schema])
    ld = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)} | LEXYGO</title>
  <meta name="description" content="{esc(description)}">
  <link rel="canonical" href="{canonical}">
  <link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
  <meta property="og:type" content="website"><meta property="og:title" content="{esc(title)} | LEXYGO">
  <meta property="og:description" content="{esc(description)}"><meta property="og:url" content="{canonical}">
  <meta property="og:image" content="{BASE_URL}/assets/og-cover.png">
  <link rel="stylesheet" href="/assets/site.css">
  <script type="application/ld+json">{ld}</script>
</head>
<body class="{esc(body_class)}">
  {header()}
  <main id="main">{body}</main>
  {footer()}
  <script src="https://unpkg.com/lucide@0.468.0/dist/umd/lucide.min.js" defer></script>
  <script src="/assets/site.js" defer></script>
</body>
</html>"""


def capacity_number(value):
    match = re.search(r"([\d,]+)", value)
    return int(match.group(1).replace(",", "")) if match else 0


def product_card(item):
    category = CATEGORIES[item["category"]]["name"]
    return f"""
    <article class="product-card" data-product-card data-category="{item['category']}" data-operation="{esc(item['operation'].lower())}" data-capacity="{capacity_number(item['capacity'])}" data-search="{esc((item['model'] + ' ' + item['name'] + ' ' + item['best_for']).lower())}">
      <a class="product-image" href="/products/{item['slug']}/"><img src="/assets/products/{item['image']}" alt="{esc(item['model'] + ' ' + item['name'])}" loading="lazy"></a>
      <div class="product-card-body">
        <p class="eyebrow">{esc(category)}</p><h3><a href="/products/{item['slug']}/">{esc(item['name'])}</a></h3>
        <div class="model-line"><strong>{esc(item['model'])}</strong><span>{esc(item['operation'])}</span></div>
        <dl class="quick-specs"><div><dt>Capacity</dt><dd>{esc(item['capacity'])}</dd></div><div><dt>Lift</dt><dd>{esc(item['lift'])}</dd></div></dl>
        <a class="text-link" href="/products/{item['slug']}/">View model {icon('arrow-right', 16)}</a>
      </div>
    </article>
    """


def category_link(slug, data):
    count = sum(1 for item in PRODUCTS if item["category"] == slug)
    return f"""
    <a class="category-item" href="/products/{slug}/">
      <span class="category-icon">{icon({'electric-pallet-trucks':'truck','electric-pallet-stackers':'package-open','electric-forklifts':'forklift','manual-pallet-trucks':'move-horizontal','warehouse-equipment':'warehouse'}[slug], 22)}</span>
      <span><strong>{esc(data['name'])}</strong><small>{count} models</small></span>{icon('arrow-up-right', 18)}
    </a>
    """


def home_page():
    categories = "".join(category_link(slug, data) for slug, data in CATEGORIES.items())
    featured_slugs = ["wep20j", "wes1500a", "r4efl3t", "mpt5tn"]
    featured = "".join(product_card(next(x for x in PRODUCTS if x["slug"] == slug)) for slug in featured_slugs)
    faqs = [
        ("Which product should I choose for horizontal pallet movement?", "Choose a pallet truck. A walkie electric model suits compact routes, a rider model suits longer travel, and an all-terrain model suits uneven surfaces."),
        ("When do I need a pallet stacker?", "Choose a stacker when the task includes lifting pallets to a storage position. Confirm pallet type, rated load, lift height, aisle width, and residual capacity."),
        ("Can LEXYGO configure equipment for OEM projects?", "Yes. Configuration discussions can cover branding, color, battery, fork dimensions, mast options, packaging, and documentation. Feasibility is confirmed before quotation."),
    ]
    faq_html = "".join(f'<details><summary>{esc(q)}{icon("chevron-down",16)}</summary><p>{esc(a)}</p></details>' for q, a in faqs)
    body = f"""
    <section class="hero">
      <div class="shell hero-grid">
        <div class="hero-copy">
          <p class="eyebrow">LEXYGO material handling equipment</p>
          <h1>Electric Pallet Trucks, Stackers &amp; Forklifts</h1>
          <p class="lede">Manufacturer-direct equipment for moving, lifting, and stacking palletized loads. Start with the task, load, route, and lift height to identify the right configuration.</p>
          <div class="button-row">{button('Browse products','/products/')} {button('Send your requirements','/contact/','secondary','send')}</div>
          <ul class="proof-list"><li>{icon('check-circle',18)} Model-level specifications</li><li>{icon('check-circle',18)} Configuration-based quotations</li><li>{icon('check-circle',18)} OEM and export project support</li></ul>
        </div>
        <div class="hero-media"><img src="/assets/products/r4efl3t.png" alt="LEXYGO four-wheel electric forklift" fetchpriority="high"><span class="hero-caption"><strong>R4EFL3T</strong> Four-wheel electric forklift</span></div>
      </div>
    </section>
    <section class="category-band"><div class="shell"><div class="section-heading compact"><div><p class="eyebrow">Find by equipment type</p><h2>Choose a product family</h2></div><a class="text-link" href="/products/">Compare all models {icon('arrow-right',16)}</a></div><div class="category-list">{categories}</div></div></section>
    <section class="section finder-section"><div class="shell finder-grid">
      <div><p class="eyebrow">Quick product finder</p><h2>Start with your actual handling task</h2><p>Four details usually determine the shortlist: whether the load only moves or must be stacked, rated load, route surface, and operator mode.</p></div>
      <form class="finder" action="/products/" method="get">
        <label>Task<select name="task"><option value="">Select a task</option><option value="move">Move pallets</option><option value="stack">Stack pallets</option><option value="forklift">Forklift handling</option><option value="position">Position loads</option></select></label>
        <label>Minimum capacity<select name="capacity"><option value="0">Any capacity</option><option value="1000">1,000 kg</option><option value="1500">1,500 kg</option><option value="2000">2,000 kg</option><option value="3000">3,000 kg</option><option value="5000">5,000 kg</option></select></label>
        <label>Operator mode<select name="operation"><option value="">Any mode</option><option value="walk">Walk-behind</option><option value="stand">Stand-on / rider</option><option value="seated">Seated</option><option value="manual">Manual</option></select></label>
        <button class="button button-primary" type="submit">Find matching models {icon('search',18)}</button>
      </form>
    </div></section>
    <section class="section section-muted"><div class="shell"><div class="section-heading"><div><p class="eyebrow">Selected models</p><h2>A practical starting range</h2></div>{button('View full catalog','/products/','secondary')}</div><div class="product-grid">{featured}</div></div></section>
    <section class="section"><div class="shell answer-grid"><div><p class="eyebrow">Specification before promotion</p><h2>Clear answers for purchasing decisions</h2><p>Each model page states its intended task, known specifications, and the configuration points that must be confirmed. This gives buyers and AI search systems precise, quotable information instead of broad claims.</p>{button('Read buyer guides','/guides/','secondary','book-open')}</div><div class="faq-list">{faq_html}</div></div></section>
    <section class="cta-band"><div class="shell cta-inner"><div><p class="eyebrow">Need a shortlist?</p><h2>Send the load, lift height, aisle, and working conditions.</h2></div>{button('Request a configuration','/contact/','light','send')}</div></section>
    """
    faq_schema = {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]}
    return page("Material Handling Equipment Manufacturer", "Electric pallet trucks, pallet stackers, electric forklifts, manual pallet trucks, and warehouse equipment from LEXYGO.", "/", body, faq_schema, "home")


def products_page():
    cards = "".join(product_card(item) for item in PRODUCTS)
    options = "".join(f'<option value="{slug}">{esc(data["name"])}</option>' for slug, data in CATEGORIES.items())
    crumb, crumb_schema = breadcrumbs([("Home", "/"), ("Products", None)])
    body = f"""
    {crumb}
    <section class="page-intro"><div class="shell intro-grid"><div><p class="eyebrow">Product catalog</p><h1>Find equipment by task and specification</h1><p class="lede">Filter the range by product family, operating mode, minimum capacity, or model number.</p></div><div class="intro-note"><strong>{len(PRODUCTS)} product configurations</strong><span>Final project specifications are confirmed against the working conditions.</span></div></div></section>
    <section class="section catalog-section"><div class="shell">
      <div class="filter-bar" data-filters>
        <label class="search-field"><span>Search model or use</span><div>{icon('search',18)}<input type="search" placeholder="Example: WEP20J or narrow aisle" data-search-input></div></label>
        <label><span>Product family</span><select data-category-filter><option value="">All families</option>{options}</select></label>
        <label><span>Operation</span><select data-operation-filter><option value="">All modes</option><option value="walk">Walk-behind</option><option value="stand">Stand-on / rider</option><option value="seated">Seated</option><option value="manual">Manual</option></select></label>
        <label><span>Minimum capacity</span><select data-capacity-filter><option value="0">Any</option><option value="1000">1,000 kg</option><option value="1500">1,500 kg</option><option value="2000">2,000 kg</option><option value="3000">3,000 kg</option><option value="5000">5,000 kg</option></select></label>
      </div>
      <div class="catalog-status"><strong data-result-count>{len(PRODUCTS)} models</strong><button type="button" class="text-button" data-clear-filters>Clear filters</button></div>
      <div class="product-grid" data-product-grid>{cards}</div>
      <div class="empty-state" data-empty-state hidden><h2>No exact match found</h2><p>Adjust the filters or send the application details for a configuration review.</p>{button('Ask for a recommendation','/contact/','primary','send')}</div>
    </div></section>
    """
    schema = [crumb_schema, {"@type": "CollectionPage", "name": "LEXYGO Product Catalog", "url": route_url("/products/")}]
    return page("Product Catalog", "Compare LEXYGO electric pallet trucks, stackers, electric forklifts, manual pallet trucks, and warehouse equipment.", "/products/", body, schema)


def category_page(slug, data):
    items = [item for item in PRODUCTS if item["category"] == slug]
    cards = "".join(product_card(item) for item in items)
    crumb, crumb_schema = breadcrumbs([("Home", "/"), ("Products", "/products/"), (data["name"], None)])
    body = f"""
    {crumb}
    <section class="page-intro category-intro"><div class="shell category-hero"><div><p class="eyebrow">{len(items)} available configurations</p><h1>{esc(data['name'])}</h1><p class="lede">{esc(data['short'])}</p><div class="answer-box"><strong>Selection answer</strong><p>{esc(data['answer'])}</p></div></div><img src="/assets/products/{data['image']}" alt="{esc(data['name'])}" fetchpriority="high"></div></section>
    <section class="section"><div class="shell"><div class="section-heading"><div><p class="eyebrow">Model range</p><h2>Compare key specifications</h2></div>{button('Request help choosing','/contact/','secondary','messages-square')}</div><div class="product-grid">{cards}</div></div></section>
    <section class="section section-muted"><div class="shell selection-grid"><div><h2>Information needed for selection</h2><p>A reliable recommendation requires more than rated capacity.</p></div><ul class="check-grid"><li>{icon('weight')} Maximum load and load center</li><li>{icon('move-up')} Required lift height</li><li>{icon('ruler')} Aisle width and turning space</li><li>{icon('route')} Route length and floor condition</li><li>{icon('battery-charging')} Shift time and charging plan</li><li>{icon('box')} Pallet entry and fork dimensions</li></ul></div></section>
    """
    schema = [crumb_schema, {"@type": "CollectionPage", "name": data["name"], "description": data["short"], "url": route_url(f"/products/{slug}/")}]
    return page(data["name"], data["short"], f"/products/{slug}/", body, schema)


def product_page(item):
    category = CATEGORIES[item["category"]]
    crumb, crumb_schema = breadcrumbs([("Home", "/"), ("Products", "/products/"), (category["name"], f'/products/{item["category"]}/'), (item["model"], None)])
    specs = {"Rated capacity": item["capacity"], "Lift": item["lift"], "Operation": item["operation"], **item["specs"]}
    spec_rows = "".join(f'<tr><th>{esc(k)}</th><td>{esc(v)}</td></tr>' for k, v in specs.items())
    additional = [{"@type": "PropertyValue", "name": k, "value": v} for k, v in specs.items()]
    related = [x for x in PRODUCTS if x["category"] == item["category"] and x["slug"] != item["slug"]][:3]
    related_cards = "".join(product_card(x) for x in related)
    body = f"""
    {crumb}
    <section class="product-detail"><div class="shell product-detail-grid">
      <div class="detail-media"><img src="/assets/products/{item['image']}" alt="{esc(item['model'] + ' ' + item['name'])}" fetchpriority="high"></div>
      <div class="detail-copy"><p class="eyebrow">{esc(category['name'])}</p><h1>{esc(item['name'])}</h1><p class="model-badge">Model {esc(item['model'])}</p><p class="lede">Designed for {esc(item['best_for'].lower())}.</p>
        <dl class="key-specs"><div><dt>Rated capacity</dt><dd>{esc(item['capacity'])}</dd></div><div><dt>Lift</dt><dd>{esc(item['lift'])}</dd></div><div><dt>Operation</dt><dd>{esc(item['operation'])}</dd></div></dl>
        <div class="button-row">{button('Request this model','/contact/?model=' + item['model'],'primary','send')} {button('Compare models','/products/' + item['category'] + '/','secondary','columns-3')}</div>
      </div>
    </div></section>
    <section class="section section-muted"><div class="shell detail-info-grid"><div><p class="eyebrow">Application fit</p><h2>Where {esc(item['model'])} fits</h2><p>{esc(item['best_for'])}. Confirm load dimensions, pallet entry, route, gradient, floor condition, and duty cycle before ordering.</p><div class="callout">{icon('info',20)}<p>{esc(item['note'])}</p></div></div><div><h2>Reference specifications</h2><div class="table-wrap"><table><tbody>{spec_rows}</tbody></table></div></div></div></section>
    <section class="section"><div class="shell"><div class="section-heading"><div><p class="eyebrow">Same product family</p><h2>Related models</h2></div><a class="text-link" href="/products/{item['category']}/">View all {esc(category['name'])} {icon('arrow-right',16)}</a></div><div class="product-grid product-grid-three">{related_cards}</div></div></section>
    <section class="cta-band"><div class="shell cta-inner"><div><p class="eyebrow">Quote checklist</p><h2>Tell us the load, lift height, aisle, pallet, and shift time.</h2></div>{button('Send project details','/contact/?model=' + item['model'],'light','send')}</div></section>
    """
    product_schema = {
        "@type": "Product",
        "name": item["name"],
        "model": item["model"],
        "sku": item["model"],
        "image": BASE_URL + "/assets/products/" + item["image"],
        "description": f"{item['name']} for {item['best_for'].lower()}.",
        "brand": {"@type": "Brand", "name": COMPANY["brand"]},
        "manufacturer": {"@id": BASE_URL + "/#organization"},
        "category": category["name"],
        "additionalProperty": additional,
    }
    return page(f"{item['model']} {item['name']}", f"{item['model']} {item['name']}: {item['capacity']} capacity, {item['lift']} lift, {item['operation'].lower()} operation.", f"/products/{item['slug']}/", body, [crumb_schema, product_schema], "product-page")


def solutions_page():
    crumb, crumb_schema = breadcrumbs([("Home", "/"), ("Solutions", None)])
    solutions = [
        ("Warehouse pallet movement", "Move loads between receiving, storage, production, and dispatch.", "Electric pallet trucks", "/products/electric-pallet-trucks/", "route"),
        ("Low- and mid-level stacking", "Place pallets into storage positions without a full-size forklift.", "Electric pallet stackers", "/products/electric-pallet-stackers/", "package-open"),
        ("Tight turning areas", "Prioritize compact dimensions and maneuverability in constrained layouts.", "Three-wheel forklifts", "/products/efl1200r3/", "rotate-3d"),
        ("Closed-pallet handling", "Use a counterbalanced stacker when support legs cannot enter beneath the load.", "Counterbalanced stackers", "/products/wces1500j/", "box"),
        ("Uneven outdoor routes", "Match tires, gradeability, stability, and ingress protection to the route.", "All-terrain pallet truck", "/products/atep3000y/", "mountain"),
        ("Workstation positioning", "Raise loads to a practical handling height for feeding, assembly, or packing.", "Warehouse equipment", "/products/warehouse-equipment/", "panels-top-left"),
    ]
    blocks = "".join(f'<article class="solution-item"><span>{icon(i,22)}</span><div><h2>{esc(t)}</h2><p>{esc(d)}</p><a class="text-link" href="{u}">{esc(l)} {icon("arrow-right",16)}</a></div></article>' for t,d,l,u,i in solutions)
    body = f"""{crumb}<section class="page-intro"><div class="shell narrow"><p class="eyebrow">Application-first selection</p><h1>Material handling solutions by task</h1><p class="lede">Start with what the equipment must do, then confirm the technical limits of the application.</p></div></section><section class="section"><div class="shell solution-list">{blocks}</div></section><section class="section section-muted"><div class="shell selection-grid"><div><h2>A useful project brief</h2><p>Send these details to reduce clarification time and avoid an incorrect shortlist.</p></div><ol class="number-list"><li><strong>Load</strong><span>Maximum weight, dimensions, and center of gravity</span></li><li><strong>Movement</strong><span>Horizontal travel, stacking, loading, or positioning</span></li><li><strong>Environment</strong><span>Floor, gradient, temperature, dust, moisture, and indoor/outdoor use</span></li><li><strong>Layout</strong><span>Aisle width, turning space, door height, and rack dimensions</span></li><li><strong>Duty cycle</strong><span>Travel distance, lifts per hour, shifts, and charging window</span></li></ol></div></section><section class="cta-band"><div class="shell cta-inner"><div><p class="eyebrow">Application review</p><h2>Send the task before choosing the model.</h2></div>{button('Discuss your application','/contact/','light','messages-square')}</div></section>"""
    return page("Material Handling Solutions", "Choose pallet trucks, stackers, forklifts, and warehouse equipment by application and working conditions.", "/solutions/", body, crumb_schema)


def guides_index():
    crumb, crumb_schema = breadcrumbs([("Home", "/"), ("Buyer Guides", None)])
    cards = "".join(f'<article class="guide-card"><p class="eyebrow">Buyer guide</p><h2><a href="/guides/{g["slug"]}/">{esc(g["title"])}</a></h2><p>{esc(g["summary"])}</p><a class="text-link" href="/guides/{g["slug"]}/">Read guide {icon("arrow-right",16)}</a></article>' for g in GUIDES)
    body = f"""{crumb}<section class="page-intro"><div class="shell narrow"><p class="eyebrow">Decision support</p><h1>Material handling buyer guides</h1><p class="lede">Plain-language answers to common equipment selection questions.</p></div></section><section class="section"><div class="shell guide-grid">{cards}</div></section>"""
    return page("Buyer Guides", "Practical buyer guides for selecting electric pallet trucks, pallet stackers, and electric forklifts.", "/guides/", body, [crumb_schema, {"@type": "CollectionPage", "name": "LEXYGO Buyer Guides"}])


GUIDE_CONTENT = {
    "how-to-choose-an-electric-pallet-truck": {
        "answer": "Choose the truck by the maximum pallet weight, route length, floor condition, turning space, operator mode, and daily duty cycle. Capacity is only the first filter.",
        "sections": [
            ("1. Define the load", "Record the maximum pallet weight, pallet dimensions, load center, fork-entry direction, and whether the load is stable."),
            ("2. Measure the route", "Check travel distance, aisle width, door openings, dock plates, gradients, floor joints, and turning areas."),
            ("3. Choose operator mode", "Walkie trucks suit shorter routes. Rider trucks reduce walking on longer, repeated routes. All-terrain trucks are intended for less uniform surfaces."),
            ("4. Confirm duty cycle", "State hours per shift, pallets per hour, travel speed expectations, and the available charging window."),
            ("5. Confirm configuration", "Fork dimensions, wheel material, battery, charger, controls, and documentation should be fixed in the quotation."),
        ],
        "links": [("Compare electric pallet trucks", "/products/electric-pallet-trucks/")],
    },
    "pallet-truck-vs-stacker": {
        "answer": "Use a pallet truck when the job is mainly horizontal transport. Use a stacker when pallets must be raised to racks, platforms, trucks, or process equipment.",
        "sections": [
            ("Pallet truck", "Best for moving palletized loads at floor level. Key choices are capacity, route length, operator mode, fork size, wheel material, and surface."),
            ("Pallet stacker", "Best for lifting and placing pallets. Key choices add lift height, mast type, residual capacity, aisle width, overhead clearance, and pallet compatibility."),
            ("Counterbalanced stacker", "Useful when the load is closed underneath or support legs cannot pass under the pallet. It needs sufficient counterweight and turning space."),
            ("Reach stacker", "Useful when a reaching mast helps place pallets while keeping the chassis compact. Confirm rack geometry and residual capacity."),
        ],
        "links": [("Compare pallet trucks", "/products/electric-pallet-trucks/"), ("Compare pallet stackers", "/products/electric-pallet-stackers/")],
    },
    "forklift-capacity-and-aisle-width": {
        "answer": "A safe forklift selection must consider residual capacity at the required lift height and load center, plus the real turning and stacking aisle. The nominal capacity alone is not enough.",
        "sections": [
            ("Rated vs. residual capacity", "The capacity shown on a model is tied to specified conditions. Higher lift, attachments, a longer load center, or unusual loads can reduce usable capacity."),
            ("Lift height and lowered height", "Confirm the highest placement point, free lift needs, mast lowered height, ceiling, doors, containers, and overhead obstructions."),
            ("Aisle and turning space", "Measure the narrowest travel path and actual stacking aisle with the intended pallet. Include wall clearance, rack guards, and load overhang."),
            ("Three-wheel vs. four-wheel", "Three-wheel electric forklifts generally emphasize maneuverability. Four-wheel models generally emphasize stability and wider capacity coverage."),
            ("Battery and shift plan", "Match usable energy and charging time to the duty cycle. Confirm battery chemistry, charger supply, charging location, and spare-battery strategy if required."),
        ],
        "links": [("Compare electric forklifts", "/products/electric-forklifts/")],
    },
}


def guide_page(guide):
    data = GUIDE_CONTENT[guide["slug"]]
    crumb, crumb_schema = breadcrumbs([("Home", "/"), ("Buyer Guides", "/guides/"), (guide["title"], None)])
    sections = "".join(f'<section><h2>{esc(h)}</h2><p>{esc(p)}</p></section>' for h,p in data["sections"])
    links = " ".join(button(label, href, "secondary") for label, href in data["links"])
    body = f"""{crumb}<article class="article shell"><header><p class="eyebrow">Buyer guide</p><h1>{esc(guide['title'])}</h1><p class="lede">{esc(guide['summary'])}</p><div class="answer-box"><strong>Short answer</strong><p>{esc(data['answer'])}</p></div></header><div class="article-body">{sections}<div class="article-actions">{links}{button('Ask for a recommendation','/contact/','primary','send')}</div></div></article>"""
    schema = [crumb_schema, {"@type": "Article", "headline": guide["title"], "description": guide["summary"], "author": {"@id": BASE_URL + "/#organization"}, "publisher": {"@id": BASE_URL + "/#organization"}, "mainEntityOfPage": route_url(f'/guides/{guide["slug"]}/')}]
    return page(guide["title"], guide["summary"], f'/guides/{guide["slug"]}/', body, schema, "article-page")


def quality_page():
    crumb, crumb_schema = breadcrumbs([("Home", "/"), ("Quality", None)])
    body = f"""{crumb}<section class="page-intro"><div class="shell intro-grid"><div><p class="eyebrow">Quality process</p><h1>Configuration control before production</h1><p class="lede">Quality begins by translating the application into a confirmed technical specification, then checking the product against that agreed configuration.</p></div><div class="intro-note"><strong>Evidence before claims</strong><span>Certificates, test reports, and inspection records are supplied only when applicable to the confirmed model and order.</span></div></div></section><section class="section"><div class="shell process-grid"><article><span>01</span><h2>Application review</h2><p>Load, pallet, lift height, route, floor, gradient, shift, and environment.</p></article><article><span>02</span><h2>Specification confirmation</h2><p>Model, mast, forks, wheels, battery, charger, attachments, color, and documentation.</p></article><article><span>03</span><h2>Production controls</h2><p>Incoming parts, assembly checkpoints, electrical and hydraulic checks, and labeling.</p></article><article><span>04</span><h2>Pre-shipment inspection</h2><p>Functional review, configuration check, appearance, packing, and document verification.</p></article></div></section><section class="section section-muted"><div class="shell detail-info-grid"><div><h2>What buyers should request</h2><ul class="plain-list"><li>Confirmed model and configuration sheet</li><li>Applicable test or compliance documents</li><li>Battery and charger specification</li><li>Spare-parts and service information</li><li>Packing and loading plan</li></ul></div><div><h2>What changes by market</h2><p>Electrical supply, labeling, manuals, safety requirements, emissions or recycling rules, and documentation can differ by destination. These points should be agreed before order confirmation.</p>{button('Send compliance requirements','/contact/','secondary','file-check-2')}</div></div></section>"""
    return page("Quality and Inspection", "How LEXYGO confirms application requirements, product configuration, production checks, and pre-shipment inspection.", "/quality/", body, crumb_schema)


def oem_page():
    crumb, crumb_schema = breadcrumbs([("Home", "/"), ("OEM & ODM", None)])
    body = f"""{crumb}<section class="page-intro"><div class="shell intro-grid"><div><p class="eyebrow">Project manufacturing</p><h1>OEM and configuration support</h1><p class="lede">For distributors, brands, and industrial buyers that need a defined product configuration and repeatable supply process.</p></div><img class="intro-product" src="/assets/products/wes1500a.png" alt="LEXYGO electric pallet stacker"></div></section><section class="section"><div class="shell feature-columns"><div><h2>Common configuration topics</h2><ul class="plain-list"><li>Branding, nameplates, color, and packaging</li><li>Rated capacity, mast, and lift height</li><li>Fork length, width, and pallet compatibility</li><li>Battery chemistry, capacity, and charger</li><li>Wheel material and floor conditions</li><li>Manuals, labels, spare parts, and market documents</li></ul></div><div><h2>Project workflow</h2><ol class="number-list compact-list"><li><strong>Requirement brief</strong><span>Application, destination, quantity, and target configuration</span></li><li><strong>Feasibility review</strong><span>Technical scope, options, constraints, and documentation</span></li><li><strong>Sample or approval</strong><span>Agreed confirmation method before repeat production</span></li><li><strong>Production and inspection</strong><span>Controls against the approved configuration</span></li></ol></div></div></section><section class="cta-band"><div class="shell cta-inner"><div><p class="eyebrow">OEM inquiry</p><h2>Send the target specification, market, and forecast quantity.</h2></div>{button('Start an OEM discussion','/contact/?topic=OEM','light','send')}</div></section>"""
    return page("OEM and ODM Material Handling Equipment", "OEM and configuration support for electric pallet trucks, stackers, forklifts, and warehouse equipment.", "/oem-odm/", body, crumb_schema)


def about_page():
    crumb, crumb_schema = breadcrumbs([("Home", "/"), ("About", None)])
    body = f"""{crumb}<section class="page-intro"><div class="shell intro-grid"><div><p class="eyebrow">About LEXYGO</p><h1>A focused material handling equipment brand</h1><p class="lede">LEXYGO presents pallet trucks, electric stackers, electric forklifts, and warehouse support equipment manufactured and configured for international projects.</p></div><div class="intro-note"><strong>{esc(COMPANY['legal_name'])}</strong><span>{esc(COMPANY['location'])}</span></div></div></section><section class="section"><div class="shell detail-info-grid"><div><h2>What this website is for</h2><p>This site separates the material handling range from our cleaning-equipment business. Buyers can identify the correct product family, compare models, read selection guidance, and send a structured inquiry.</p></div><div><h2>How we describe products</h2><p>Published specifications come from current product materials. Values that depend on configuration are stated as such and are finalized in the quotation. We avoid unsupported performance, certification, and availability claims.</p></div></div></section><section class="section section-muted"><div class="shell selection-grid"><div><h2>Core product scope</h2><p>Five categories cover horizontal transport, stacking, forklift handling, manual pallet movement, and workstation support.</p></div><div class="category-list stacked">{''.join(category_link(slug,data) for slug,data in CATEGORIES.items())}</div></div></section>"""
    return page("About LEXYGO", "Learn about LEXYGO and Zhejiang Changxing Shengli Intelligent Machinery Co., Ltd., a material handling equipment manufacturer in China.", "/about/", body, crumb_schema)


def contact_page():
    crumb, crumb_schema = breadcrumbs([("Home", "/"), ("Contact", None)])
    body = f"""{crumb}<section class="page-intro"><div class="shell narrow"><p class="eyebrow">Request a quote</p><h1>Send the application, not only the model</h1><p class="lede">The more complete the working conditions, the faster we can confirm a suitable configuration.</p></div></section><section class="section contact-section"><div class="shell contact-grid"><form class="quote-form" data-mailto-form data-email="{COMPANY['email']}"><div class="form-grid"><label>Company name<input name="company" required autocomplete="organization"></label><label>Your name<input name="name" required autocomplete="name"></label><label>Business email<input type="email" name="email" required autocomplete="email"></label><label>Country / region<input name="country" required autocomplete="country-name"></label><label>Model or product type<input name="model" data-model-field placeholder="Example: WEP20J or electric stacker"></label><label>Quantity<input name="quantity" inputmode="numeric"></label><label>Maximum load<input name="load" placeholder="kg"></label><label>Required lift height<input name="height" placeholder="mm"></label><label class="full">Application and working conditions<textarea name="details" rows="6" required placeholder="Pallet size, aisle width, travel distance, floor, gradient, shifts, battery preference, destination port, and required documents"></textarea></label></div><button class="button button-primary" type="submit">Prepare email inquiry {icon('send',18)}</button><p class="form-note">Submitting opens your email application with the project details filled in. No data is uploaded by this static form.</p></form><aside class="contact-aside"><h2>Direct contact</h2><p><strong>Email</strong><a href="mailto:{COMPANY['email']}">{COMPANY['email']}</a></p><p><strong>Manufacturer</strong><span>{esc(COMPANY['legal_name'])}</span></p><p><strong>Location</strong><span>{esc(COMPANY['location'])}</span></p><div class="contact-checklist"><h2>Useful attachments</h2><ul><li>Load and pallet photos</li><li>Rack or aisle drawing</li><li>Current equipment nameplate</li><li>Target specification</li><li>Destination requirements</li></ul></div></aside></div></section>"""
    return page("Request a Quote", "Send load, lift height, aisle, pallet, route, duty cycle, and destination details for a LEXYGO equipment quotation.", "/contact/", body, crumb_schema)


def not_found_page():
    body = f"""<section class="page-intro"><div class="shell narrow"><p class="eyebrow">404</p><h1>That page is not in the catalog</h1><p class="lede">Use the product catalog to find a model or send the application details for help.</p><div class="button-row">{button('Open product catalog','/products/')} {button('Contact LEXYGO','/contact/','secondary','send')}</div></div></section>"""
    return page("Page Not Found", "The requested page could not be found.", "/404.html", body)


def copy_product_assets():
    PRODUCT_ASSETS.mkdir(parents=True, exist_ok=True)
    source_by_name = {path.name.lower(): path for path in SOURCE_ROOT.rglob("*") if path.is_file() and path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}}
    overrides = {
        "r4efl12t.png": "r4efl12t.png",
        "warehouse-semi-electric-stacker.png": ROOT / "tmp" / "warehouse-assets" / "image190.png",
        "warehouse-scissor-lift-table.png": ROOT / "tmp" / "warehouse-assets" / "image75.png",
        "warehouse-material-lift-cart.png": ROOT / "tmp" / "warehouse-assets" / "image4.png",
    }
    for item in PRODUCTS:
        output_name = item["image"]
        source = overrides.get(output_name)
        if isinstance(source, str):
            source = source_by_name.get(source)
        if source is None:
            source = source_by_name.get(output_name.lower())
        if not source or not Path(source).exists():
            raise FileNotFoundError(f"Missing source image for {output_name}")
        shutil.copy2(source, PRODUCT_ASSETS / output_name)
    hero = PRODUCT_ASSETS / "r4efl3t.png"
    shutil.copy2(hero, ASSETS / "og-cover.jpg") if hero.suffix.lower() == ".jpg" else shutil.copy2(hero, ASSETS / "og-cover.png")


CSS = r"""
:root{--ink:#16232a;--muted:#5a6870;--line:#dce2e5;--paper:#fff;--soft:#f3f6f7;--orange:#e65318;--orange-dark:#b83c0c;--blue:#087ca7;--blue-dark:#07516d;--max:1180px;--radius:6px;--shadow:0 14px 38px rgba(17,34,43,.09)}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;color:var(--ink);background:var(--paper);font-family:Inter,Arial,"Helvetica Neue",sans-serif;line-height:1.55;letter-spacing:0}img{display:block;max-width:100%}a{color:inherit;text-decoration:none}button,input,select,textarea{font:inherit;color:inherit}.shell{width:min(var(--max),calc(100% - 40px));margin-inline:auto}.narrow{max-width:820px}.skip-link{position:fixed;left:12px;top:-80px;z-index:1000;padding:10px 14px;background:var(--ink);color:#fff}.skip-link:focus{top:12px}.utility-bar{background:var(--ink);color:#dce8ed;font-size:13px}.utility-inner{min-height:34px;display:flex;justify-content:space-between;align-items:center;gap:20px}.utility-inner a{display:flex;align-items:center;gap:7px}.site-header{position:sticky;top:0;z-index:50;background:rgba(255,255,255,.98);border-bottom:1px solid var(--line)}.nav-row{min-height:72px;display:flex;align-items:center;justify-content:space-between;gap:28px}.brand{display:flex;align-items:center;gap:10px;min-width:max-content}.brand-mark{width:36px;height:36px;display:grid;place-items:center;background:var(--orange);color:#fff;font-weight:900;font-size:21px}.brand strong,.brand small{display:block}.brand strong{font-size:20px;line-height:1}.brand small{font-size:10px;text-transform:uppercase;color:var(--muted);margin-top:3px}.main-nav{display:flex;align-items:center;gap:24px;font-size:14px;font-weight:700}.main-nav>a:not(.nav-cta):hover{color:var(--orange)}.nav-cta{padding:10px 13px;background:var(--ink);color:#fff;display:inline-flex;gap:7px;align-items:center}.nav-cta:hover{background:var(--orange)}.icon-button{border:0;background:transparent;width:42px;height:42px;display:none;place-items:center}.hero{background:linear-gradient(90deg,#fff 0%,#fff 54%,#eef5f7 54%,#eef5f7 100%);overflow:hidden}.hero-grid{min-height:565px;display:grid;grid-template-columns:1fr 1fr;align-items:center;gap:52px}.eyebrow{margin:0 0 10px;color:var(--orange-dark);font-size:12px;font-weight:800;text-transform:uppercase}.hero h1,.page-intro h1,.product-detail h1,.article h1{font-size:clamp(38px,5vw,66px);line-height:1.03;margin:0 0 22px;max-width:760px}.lede{font-size:19px;color:var(--muted);max-width:720px;margin:0 0 28px}.hero-media{align-self:stretch;position:relative;display:grid;place-items:center;padding:40px 0 70px}.hero-media img{width:100%;height:410px;object-fit:contain}.hero-caption{position:absolute;left:10px;bottom:52px;background:#fff;border-left:4px solid var(--blue);padding:10px 14px;box-shadow:var(--shadow);font-size:13px}.hero-caption strong{display:block}.button-row{display:flex;flex-wrap:wrap;gap:10px;margin:26px 0}.button{min-height:44px;padding:10px 16px;display:inline-flex;align-items:center;justify-content:center;gap:9px;border:1px solid transparent;border-radius:3px;font-weight:800;cursor:pointer}.button-primary{background:var(--orange);color:#fff}.button-primary:hover{background:var(--orange-dark)}.button-secondary{background:#fff;border-color:#aeb9be;color:var(--ink)}.button-secondary:hover{border-color:var(--blue);color:var(--blue-dark)}.button-light{background:#fff;color:var(--ink)}.button-light:hover{background:var(--soft)}.proof-list{display:flex;flex-wrap:wrap;gap:12px 24px;padding:0;margin:24px 0 0;list-style:none;font-size:13px;color:#3b4b53}.proof-list li{display:flex;align-items:center;gap:7px}.proof-list svg{color:var(--blue)}.category-band{border-top:1px solid var(--line);border-bottom:1px solid var(--line);padding:25px 0}.section-heading{display:flex;justify-content:space-between;align-items:end;gap:24px;margin-bottom:28px}.section-heading.compact{margin-bottom:16px}.section-heading h2,.finder-grid h2,.answer-grid h2,.cta-band h2,.detail-info-grid h2,.selection-grid h2,.feature-columns h2{font-size:30px;line-height:1.15;margin:0}.category-list{display:grid;grid-template-columns:repeat(5,1fr);border:1px solid var(--line)}.category-item{padding:16px;min-height:78px;display:grid;grid-template-columns:auto 1fr auto;align-items:center;gap:11px;border-right:1px solid var(--line);background:#fff}.category-item:last-child{border-right:0}.category-item:hover{background:var(--soft);color:var(--blue-dark)}.category-icon{color:var(--orange)}.category-item strong,.category-item small{display:block}.category-item strong{font-size:14px}.category-item small{font-size:12px;color:var(--muted);margin-top:2px}.section{padding:72px 0}.section-muted{background:var(--soft)}.finder-section{padding-top:64px}.finder-grid{display:grid;grid-template-columns:.8fr 1.2fr;gap:70px;align-items:start}.finder{display:grid;grid-template-columns:1fr 1fr;gap:16px;border-left:4px solid var(--blue);padding-left:26px}.finder label,.filter-bar label,.form-grid label{font-size:12px;font-weight:800;color:#3f4e55}.finder select,.filter-bar select,.filter-bar input,.form-grid input,.form-grid textarea{width:100%;min-height:46px;margin-top:6px;border:1px solid #b8c2c7;background:#fff;border-radius:3px;padding:10px 12px}.finder .button{align-self:end}.product-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:18px}.product-grid-three{grid-template-columns:repeat(3,1fr)}.product-card{background:#fff;border:1px solid var(--line);border-radius:var(--radius);overflow:hidden;min-width:0;transition:transform .18s ease,box-shadow .18s ease}.product-card:hover{transform:translateY(-3px);box-shadow:var(--shadow)}.product-image{height:238px;background:#f7f9fa;display:grid;place-items:center;padding:14px}.product-image img{width:100%;height:100%;object-fit:contain}.product-card-body{padding:18px}.product-card h3{font-size:18px;line-height:1.25;margin:0 0 10px}.product-card h3 a:hover{color:var(--orange-dark)}.model-line{display:flex;justify-content:space-between;gap:10px;font-size:13px;border-top:1px solid var(--line);padding-top:10px}.model-line span{color:var(--muted)}.quick-specs{display:grid;grid-template-columns:1fr 1fr;margin:14px 0}.quick-specs div{border-left:2px solid var(--line);padding-left:9px}.quick-specs dt{font-size:11px;color:var(--muted)}.quick-specs dd{margin:2px 0 0;font-weight:800;font-size:13px}.text-link{display:inline-flex;align-items:center;gap:6px;color:var(--blue-dark);font-weight:800;font-size:14px}.text-link:hover{color:var(--orange-dark)}.answer-grid,.detail-info-grid,.feature-columns{display:grid;grid-template-columns:1fr 1fr;gap:72px;align-items:start}.faq-list details{border-top:1px solid var(--line);padding:16px 0}.faq-list details:last-child{border-bottom:1px solid var(--line)}.faq-list summary{display:flex;justify-content:space-between;gap:20px;font-weight:800;cursor:pointer;list-style:none}.faq-list p{color:var(--muted)}.cta-band{background:var(--blue-dark);color:#fff;padding:42px 0}.cta-band .eyebrow{color:#aee2f3}.cta-inner{display:flex;align-items:center;justify-content:space-between;gap:30px}.breadcrumbs{display:flex;align-items:center;gap:8px;min-height:48px;font-size:13px;color:var(--muted)}.breadcrumbs a:hover{color:var(--orange-dark)}.page-intro{padding:54px 0 62px;border-bottom:1px solid var(--line);background:#f8fafb}.intro-grid{display:grid;grid-template-columns:1.5fr .7fr;gap:70px;align-items:center}.intro-note{border-left:4px solid var(--orange);padding:16px 0 16px 20px}.intro-note strong,.intro-note span{display:block}.intro-note span{color:var(--muted);margin-top:5px}.intro-product{height:280px;width:100%;object-fit:contain}.catalog-section{padding-top:42px}.filter-bar{display:grid;grid-template-columns:1.4fr 1fr 1fr .8fr;gap:12px;padding:16px;background:var(--soft);border:1px solid var(--line);position:sticky;top:73px;z-index:10}.filter-bar label span{display:block}.search-field>div{position:relative}.search-field svg{position:absolute;left:12px;top:20px;color:var(--muted)}.search-field input{padding-left:38px}.catalog-status{display:flex;justify-content:space-between;align-items:center;padding:18px 0}.text-button{border:0;background:transparent;color:var(--blue-dark);font-weight:800;cursor:pointer}.empty-state{text-align:center;padding:70px 20px}.category-hero{display:grid;grid-template-columns:1fr .75fr;gap:60px;align-items:center}.category-hero img{height:330px;width:100%;object-fit:contain}.answer-box{border-left:4px solid var(--blue);background:#fff;padding:16px 18px;margin-top:26px}.answer-box p{margin:5px 0 0;color:var(--muted)}.selection-grid{display:grid;grid-template-columns:.65fr 1.35fr;gap:70px}.check-grid{display:grid;grid-template-columns:1fr 1fr;gap:0 28px;padding:0;margin:0;list-style:none}.check-grid li{padding:15px 0;border-bottom:1px solid var(--line);display:flex;align-items:center;gap:10px}.check-grid svg{color:var(--orange)}.product-detail{padding:38px 0 64px}.product-detail-grid{display:grid;grid-template-columns:1.05fr .95fr;gap:70px;align-items:center}.detail-media{height:520px;background:var(--soft);display:grid;place-items:center;padding:24px}.detail-media img{width:100%;height:100%;object-fit:contain}.detail-copy h1{font-size:48px}.model-badge{display:inline-block;background:var(--ink);color:#fff;padding:5px 9px;font-weight:800;font-size:13px}.key-specs{display:grid;grid-template-columns:repeat(3,1fr);border-top:1px solid var(--line);border-bottom:1px solid var(--line);margin:26px 0}.key-specs div{padding:16px 12px;border-right:1px solid var(--line)}.key-specs div:last-child{border:0}.key-specs dt{font-size:12px;color:var(--muted)}.key-specs dd{margin:4px 0 0;font-size:17px;font-weight:800}.callout{display:flex;gap:10px;background:#e8f4f8;padding:14px;margin-top:22px;color:var(--blue-dark)}.callout p{margin:0}.table-wrap{overflow:auto}table{border-collapse:collapse;width:100%;background:#fff}th,td{text-align:left;padding:12px 14px;border-bottom:1px solid var(--line)}th{width:45%;font-size:13px;color:var(--muted)}td{font-weight:700}.solution-list{display:grid;grid-template-columns:1fr 1fr;border-top:1px solid var(--line)}.solution-item{display:grid;grid-template-columns:auto 1fr;gap:16px;padding:28px;border-bottom:1px solid var(--line)}.solution-item:nth-child(odd){border-right:1px solid var(--line)}.solution-item>span{color:var(--orange)}.solution-item h2{font-size:21px;margin:0}.solution-item p{color:var(--muted)}.number-list{list-style:none;padding:0;margin:0;counter-reset:item}.number-list li{display:grid;grid-template-columns:30px 170px 1fr;gap:12px;padding:13px 0;border-bottom:1px solid var(--line);counter-increment:item}.number-list li:before{content:counter(item,decimal-leading-zero);color:var(--orange);font-weight:900}.number-list span{color:var(--muted)}.guide-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:20px}.guide-card{border-top:4px solid var(--blue);background:var(--soft);padding:25px;border-radius:var(--radius)}.guide-card h2{font-size:24px;line-height:1.2}.guide-card p{color:var(--muted)}.article{padding:54px 0 80px;display:grid;grid-template-columns:.85fr 1.15fr;gap:80px;align-items:start}.article header{position:sticky;top:110px}.article h1{font-size:48px}.article-body section{padding:0 0 26px;margin-bottom:26px;border-bottom:1px solid var(--line)}.article-body h2{font-size:24px;margin:0 0 8px}.article-body p{color:var(--muted)}.article-actions{display:flex;flex-wrap:wrap;gap:10px}.process-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:20px}.process-grid article{border-top:4px solid var(--orange);padding-top:18px}.process-grid article>span{color:var(--blue-dark);font-weight:900}.process-grid h2{font-size:20px}.process-grid p{color:var(--muted)}.plain-list{padding-left:20px}.plain-list li{margin:9px 0}.compact-list li{grid-template-columns:30px 1fr}.compact-list li span{grid-column:2}.stacked{grid-template-columns:1fr 1fr}.stacked .category-item{border-bottom:1px solid var(--line)}.contact-section{padding-top:36px}.contact-grid{display:grid;grid-template-columns:1.45fr .55fr;gap:50px}.quote-form{padding:28px;background:var(--soft);border-top:4px solid var(--orange)}.form-grid{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:20px}.form-grid label span{display:block}.form-grid .full{grid-column:1/-1}.form-grid textarea{resize:vertical}.form-note{font-size:12px;color:var(--muted)}.contact-aside{border-left:1px solid var(--line);padding-left:30px}.contact-aside h2{font-size:20px}.contact-aside p strong,.contact-aside p span,.contact-aside p a{display:block}.contact-aside p span,.contact-aside p a{color:var(--muted);margin-top:4px}.contact-checklist{margin-top:34px;padding-top:20px;border-top:1px solid var(--line)}.site-footer{background:#111d23;color:#c8d3d8;padding:56px 0 20px}.footer-grid{display:grid;grid-template-columns:1.3fr 1fr .8fr 1fr;gap:48px}.brand-footer{color:#fff}.brand-footer small{color:#aebbc1}.footer-grid h2{font-size:14px;color:#fff;text-transform:uppercase}.footer-grid p{font-size:14px}.footer-grid ul{padding:0;list-style:none;font-size:14px}.footer-grid li{margin:8px 0}.footer-grid a:hover{color:#fff}.footer-bottom{display:flex;justify-content:space-between;gap:20px;border-top:1px solid #2d3a40;margin-top:38px;padding-top:18px;font-size:12px;color:#91a1a8}
@media(max-width:1020px){.main-nav{position:absolute;left:0;right:0;top:100%;background:#fff;border-bottom:1px solid var(--line);padding:18px 20px;display:none;flex-direction:column;align-items:stretch}.main-nav.is-open{display:flex}.icon-button{display:grid}.hero-grid{min-height:auto;padding:46px 0;grid-template-columns:1fr 1fr;gap:24px}.product-grid{grid-template-columns:repeat(2,1fr)}.category-list{grid-template-columns:repeat(2,1fr)}.category-item{border-bottom:1px solid var(--line)}.filter-bar{grid-template-columns:1fr 1fr;top:72px}.process-grid{grid-template-columns:1fr 1fr}.footer-grid{grid-template-columns:1fr 1fr}.finder-grid,.answer-grid,.detail-info-grid,.feature-columns,.selection-grid,.contact-grid{gap:38px}.product-detail-grid{gap:34px}.detail-media{height:420px}}
@media(max-width:720px){.shell{width:min(100% - 28px,var(--max))}.utility-inner>span{display:none}.utility-inner{justify-content:flex-end}.hero{background:#fff}.hero-grid,.intro-grid,.category-hero,.finder-grid,.answer-grid,.detail-info-grid,.feature-columns,.selection-grid,.product-detail-grid,.article,.contact-grid{grid-template-columns:1fr}.hero-grid{padding:38px 0 0}.hero h1,.page-intro h1,.article h1{font-size:40px}.hero-media{background:#eef5f7;min-height:340px;padding:20px 0 64px}.hero-media img{height:300px}.category-list,.stacked{grid-template-columns:1fr}.category-item{border-right:0}.section{padding:52px 0}.section-heading,.cta-inner{align-items:flex-start;flex-direction:column}.finder{grid-template-columns:1fr;border-left:0;border-top:4px solid var(--blue);padding:22px 0 0}.product-grid,.product-grid-three,.guide-grid{grid-template-columns:1fr}.product-image{height:280px}.filter-bar{position:static;grid-template-columns:1fr}.category-hero img{height:260px}.check-grid{grid-template-columns:1fr}.detail-media{height:370px;order:2}.detail-copy h1{font-size:38px}.key-specs{grid-template-columns:1fr}.key-specs div{border-right:0;border-bottom:1px solid var(--line)}.solution-list{grid-template-columns:1fr}.solution-item:nth-child(odd){border-right:0}.number-list li{grid-template-columns:28px 1fr}.number-list li span{grid-column:2}.article{padding-top:34px}.article header{position:static}.process-grid{grid-template-columns:1fr}.form-grid{grid-template-columns:1fr}.form-grid .full{grid-column:auto}.contact-aside{border-left:0;border-top:1px solid var(--line);padding:25px 0 0}.footer-grid{grid-template-columns:1fr}.footer-bottom{flex-direction:column}.page-intro{padding:38px 0 46px}}
"""


JS = r"""
document.addEventListener('DOMContentLoaded',()=>{if(window.lucide){window.lucide.createIcons()}const mb=document.querySelector('[data-menu-button]');const menu=document.querySelector('[data-menu]');if(mb&&menu){mb.addEventListener('click',()=>{const open=menu.classList.toggle('is-open');mb.setAttribute('aria-expanded',String(open))})}const grid=document.querySelector('[data-product-grid]');if(grid){const cards=[...grid.querySelectorAll('[data-product-card]')];const search=document.querySelector('[data-search-input]');const category=document.querySelector('[data-category-filter]');const operation=document.querySelector('[data-operation-filter]');const capacity=document.querySelector('[data-capacity-filter]');const count=document.querySelector('[data-result-count]');const empty=document.querySelector('[data-empty-state]');const params=new URLSearchParams(location.search);const task=params.get('task')||'';if(task&&category){category.value=task==='move'?'electric-pallet-trucks':task==='stack'?'electric-pallet-stackers':task==='forklift'?'electric-forklifts':task==='position'?'warehouse-equipment':''}if(params.get('capacity')&&capacity)capacity.value=params.get('capacity');if(params.get('operation')&&operation)operation.value=params.get('operation');const apply=()=>{const q=(search?.value||'').trim().toLowerCase();const cat=category?.value||'';const op=(operation?.value||'').toLowerCase();const cap=Number(capacity?.value||0);let shown=0;cards.forEach(card=>{const matches=(!q||card.dataset.search.includes(q))&&(!cat||card.dataset.category===cat)&&(!op||card.dataset.operation.includes(op)||(op==='stand'&&card.dataset.operation.includes('rider')))&&(!cap||Number(card.dataset.capacity)>=cap);card.hidden=!matches;if(matches)shown++});count.textContent=`${shown} model${shown===1?'':'s'}`;empty.hidden=shown!==0};[search,category,operation,capacity].filter(Boolean).forEach(el=>el.addEventListener(el===search?'input':'change',apply));document.querySelector('[data-clear-filters]')?.addEventListener('click',()=>{if(search)search.value='';if(category)category.value='';if(operation)operation.value='';if(capacity)capacity.value='0';apply()});apply()}const modelField=document.querySelector('[data-model-field]');if(modelField){const model=new URLSearchParams(location.search).get('model');if(model)modelField.value=model}const form=document.querySelector('[data-mailto-form]');if(form){form.addEventListener('submit',event=>{event.preventDefault();const data=new FormData(form);const email=form.dataset.email;const subject=`LEXYGO inquiry: ${data.get('model')||'material handling equipment'} - ${data.get('company')}`;const body=[`Company: ${data.get('company')}`,`Name: ${data.get('name')}`,`Business email: ${data.get('email')}`,`Country / region: ${data.get('country')}`,`Model / product: ${data.get('model')||''}`,`Quantity: ${data.get('quantity')||''}`,`Maximum load: ${data.get('load')||''}`,`Required lift height: ${data.get('height')||''}`,'',`Application and working conditions:`,` ${data.get('details')}`].join('\n');location.href=`mailto:${email}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`})}});
"""


FAVICON = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" fill="#e65318"/><path d="M18 12h10v32h20v8H18z" fill="#fff"/><path d="M38 20h8v17h-8z" fill="#16232a"/></svg>"""


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

    routes = ["/", "/products/"]
    routes += [f"/products/{slug}/" for slug in CATEGORIES]
    routes += [f'/products/{item["slug"]}/' for item in PRODUCTS]
    routes += ["/solutions/", "/guides/", "/quality/", "/oem-odm/", "/about/", "/contact/"]
    routes += [f'/guides/{guide["slug"]}/' for guide in GUIDES]
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(f"  <url><loc>{route_url(route)}</loc></url>" for route in routes) + "\n</urlset>\n"
    (DIST / "sitemap.xml").write_text(sitemap, encoding="utf-8")
    (DIST / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {BASE_URL}/sitemap.xml\n", encoding="utf-8")
    llms = [
        "# LEXYGO Material Handling",
        "",
        f"> {COMPANY['legal_name']} manufactures and configures material handling equipment in {COMPANY['location']}.",
        "",
        "## Product families",
    ]
    llms += [f"- [{data['name']}]({route_url(f'/products/{slug}/')}): {data['short']}" for slug, data in CATEGORIES.items()]
    llms += ["", "## Buyer guides"]
    llms += [f"- [{g['title']}]({route_url('/guides/' + g['slug'] + '/')}): {g['summary']}" for g in GUIDES]
    llms += ["", "## Contact", f"- Email: {COMPANY['email']}", "- Published specifications must be confirmed against the final quotation and configuration."]
    (DIST / "llms.txt").write_text("\n".join(llms) + "\n", encoding="utf-8")
    print(f"Built {len(routes)} routes and {len(PRODUCTS)} product pages in {DIST}")


if __name__ == "__main__":
    build()
