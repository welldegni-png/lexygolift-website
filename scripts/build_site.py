from __future__ import annotations

import html
import json
import shutil
from pathlib import Path

from site_data import CATEGORIES, COMPANY, GUIDES, PRODUCTS, SOURCE_ROOT


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
ASSETS = DIST / "assets"
PRODUCT_ASSETS = ASSETS / "products"
BASE_URL = COMPANY["domain"]
FULL_SPECS = json.loads((ROOT / "product_specs.json").read_text(encoding="utf-8"))
LOGO_SOURCE = ROOT / "assets" / "lexygo-logo.gif"


def esc(value):
    return html.escape(str(value), quote=True)


def known(value):
    text = str(value or "").strip()
    return "" if text.lower() in {"configuration based", "configurable"} else text


def route_url(route):
    return BASE_URL + ("/" if route == "/" else route.rstrip("/") + "/")


def write_route(route, content):
    target = DIST / "index.html" if route == "/" else DIST / route.strip("/") / "index.html"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def icon(name, size=18):
    return f'<i data-lucide="{esc(name)}" width="{size}" height="{size}" aria-hidden="true"></i>'


def brand_icon(name, size=15):
    icons = {
        "Facebook": '<path d="M13.5 22v-8h2.7l.4-3h-3.1V9.1c0-.9.3-1.6 1.6-1.6h1.7V4.8c-.3 0-1.4-.1-2.6-.1-2.6 0-4.4 1.6-4.4 4.5V11H7v3h2.8v8h3.7z"/>',
        "LinkedIn": '<path d="M6.5 8.1H3.2V20h3.3V8.1zM4.8 3A1.9 1.9 0 1 0 4.8 6.8 1.9 1.9 0 0 0 4.8 3zM20.8 13.2c0-3.6-1.9-5.3-4.5-5.3-2.1 0-3 1.1-3.5 1.9V8.1H9.5V20h3.3v-5.9c0-1.6.3-3.1 2.3-3.1 2 0 2 1.8 2 3.2V20h3.3l.4-6.8z"/>',
        "YouTube": '<path d="M21.6 7.2a2.8 2.8 0 0 0-2-2C17.8 4.7 12 4.7 12 4.7s-5.8 0-7.6.5a2.8 2.8 0 0 0-2 2A29 29 0 0 0 2 12a29 29 0 0 0 .4 4.8 2.8 2.8 0 0 0 2 2c1.8.5 7.6.5 7.6.5s5.8 0 7.6-.5a2.8 2.8 0 0 0 2-2A29 29 0 0 0 22 12a29 29 0 0 0-.4-4.8zM10 15.5v-7l6 3.5-6 3.5z"/>',
        "Instagram": '<rect x="3" y="3" width="18" height="18" rx="5" ry="5" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="12" cy="12" r="4" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="17.4" cy="6.6" r="1.1"/>',
    }
    return f'<svg viewBox="0 0 24 24" width="{size}" height="{size}" fill="currentColor" aria-hidden="true">{icons[name]}</svg>'


def social_links():
    return "".join(
        f'<a class="social-{esc(item["name"].lower())}" href="{esc(item["url"])}" target="_blank" '
        f'rel="noopener noreferrer" aria-label="{esc(item["name"])}" title="{esc(item["name"])}">'
        f'{brand_icon(item["name"])}<span class="sr-only">{esc(item["name"])}</span></a>'
        for item in COMPANY["social"]
    )


def button(label, href, style="primary", icon_name="arrow-right"):
    return f'<a class="button button-{style}" href="{href}"><span>{esc(label)}</span>{icon(icon_name)}</a>'


def image_class(item):
    classes = ["product-image"]
    if item["slug"] in {"wces500j", "wces1000j"}:
        classes.append("product-image-compact")
    return " ".join(classes)


def products_for(category):
    return [item for item in PRODUCTS if item["category"] == category]


def category_menu():
    links = "".join(
        f'<li><a href="/products/{slug}/">{esc(data["name"])}<span>{len(products_for(slug))}</span></a></li>'
        for slug, data in CATEGORIES.items()
    )
    return f'<div class="side-box"><h2>PRODUCT CATEGORY</h2><ul class="category-menu">{links}</ul></div>'


def header(active=""):
    product_links = "".join(
        f'<a href="/products/{slug}/">{esc(data["name"])}</a>' for slug, data in CATEGORIES.items()
    )
    return f"""
    <a class="skip-link" href="#main">Skip to content</a>
    <div class="top-strip"><div class="shell"><span class="top-location">{esc(COMPANY['location'])}</span><div class="top-contact"><a href="tel:{esc(COMPANY['telephone_href'])}">{esc(COMPANY['telephone'])}</a><a href="mailto:{esc(COMPANY['email'])}">{esc(COMPANY['email'])}</a><nav class="top-social" aria-label="LEXYGO social media">{social_links()}</nav></div></div></div>
    <header class="site-header"><div class="shell nav-row">
      <a class="brand" href="/" aria-label="LEXYGO home"><img src="/assets/lexygo-logo.gif" alt="LEXYGO Material Handling Equipment"></a>
      <button class="menu-button" type="button" aria-label="Open navigation" aria-expanded="false" data-menu-button>{icon('menu', 22)}</button>
      <nav class="main-nav" aria-label="Main navigation" data-menu>
        <a class="{'active' if active == 'home' else ''}" href="/">Home</a>
        <div class="nav-group"><a class="{'active' if active == 'company' else ''}" href="/company/">Company {icon('chevron-down', 14)}</a><div class="dropdown"><a href="/company/">Company Profile</a><a href="/company/why-choose-us/">Why Choose Us</a><a href="/company/quality-management/">Quality Management</a></div></div>
        <div class="nav-group"><a class="{'active' if active == 'products' else ''}" href="/products/">Products {icon('chevron-down', 14)}</a><div class="dropdown wide-dropdown">{product_links}</div></div>
        <a class="{'active' if active == 'services' else ''}" href="/services/">Services</a>
        <div class="nav-group"><a class="{'active' if active == 'resources' else ''}" href="/resources/">Resources {icon('chevron-down', 14)}</a><div class="dropdown resource-dropdown"><a href="/guides/">Buyer Guides</a><a href="/resources/compliance/">Compliance Center</a><a href="/resources/download/">Downloads</a><a href="/resources/faq/">FAQ</a><a href="/resources/cases/">Application Cases</a></div></div>
        <div class="nav-group"><a class="{'active' if active == 'blogs' else ''}" href="/blogs/">Blogs {icon('chevron-down', 14)}</a><div class="dropdown"><a href="/blogs/company-news/">Company News</a><a href="/blogs/industry-knowledge/">Industry Knowledge</a></div></div>
        <a class="{'active' if active == 'contact' else ''}" href="/contact/">Contact Us</a>
      </nav>
    </div></header>
    """


def footer():
    category_links = "".join(
        f'<li><a href="/products/{slug}/">{esc(data["name"])}</a></li>' for slug, data in CATEGORIES.items()
    )
    return f"""
    <footer class="site-footer">
      <div class="shell footer-grid">
        <section><h2>CONTACT US</h2><dl class="contact-list"><div><dt>Address</dt><dd>{esc(COMPANY['address'])}</dd></div><div><dt>Telephone</dt><dd><a href="tel:{esc(COMPANY['telephone_href'])}">{esc(COMPANY['telephone'])}</a></dd></div><div><dt>WhatsApp</dt><dd><a href="https://wa.me/{esc(COMPANY['whatsapp_href'])}">{esc(COMPANY['whatsapp'])}</a></dd></div><div><dt>Email</dt><dd><a href="mailto:{esc(COMPANY['email'])}">{esc(COMPANY['email'])}</a></dd></div><div><dt>Web</dt><dd><a href="{esc(COMPANY['domain'])}">{esc(COMPANY['website'])}</a></dd></div></dl></section>
        <section><h2>QUICK LINKS</h2><ul><li><a href="/">Home</a></li><li><a href="/company/">Company Profile</a></li><li><a href="/services/">Services</a></li><li><a href="/resources/">Resource Center</a></li><li><a href="/guides/">Buyer Guides</a></li><li><a href="/resources/compliance/">Compliance Center</a></li><li><a href="/resources/download/">Downloads</a></li><li><a href="/resources/faq/">FAQ</a></li><li><a href="/contact/">Contact Us</a></li></ul></section>
        <section><h2>PRODUCT CATEGORY</h2><ul>{category_links}</ul></section>
        <section><h2>NEWSLETTER</h2><p>Receive product and company updates.</p><form class="newsletter" onsubmit="return false"><label><span class="sr-only">Email address</span><input type="email" placeholder="Email address"></label><button type="submit" aria-label="Subscribe">{icon('send', 18)}</button></form></section>
      </div>
      <div class="footer-bottom"><div class="shell"><span>&copy; 2026 {esc(COMPANY['legal_name'])}</span><a class="footer-brand" href="/" aria-label="LEXYGO home"><img src="/assets/lexygo-logo.gif" alt="LEXYGO"></a></div></div>
    </footer>
    """


def organization_schema():
    return {
        "@type": "Organization",
        "name": COMPANY["display_name"],
        "legalName": COMPANY["legal_name"],
        "alternateName": COMPANY["brand"],
        "brand": COMPANY["brand"],
        "url": BASE_URL,
        "email": COMPANY["email"],
        "telephone": COMPANY["telephone_href"],
        "sameAs": [item["url"] for item in COMPANY["social"]],
        "address": {
            "@type": "PostalAddress",
            "streetAddress": "No. 4 Workshop, No. 188 Baixi Road, Changxing Development Zone",
            "addressLocality": "Huzhou",
            "addressRegion": "Zhejiang",
            "addressCountry": "CN",
        },
        "contactPoint": {
            "@type": "ContactPoint",
            "contactType": "sales",
            "telephone": COMPANY["telephone_href"],
            "email": COMPANY["email"],
            "availableLanguage": ["English", "Chinese"],
        },
        "knowsAbout": [
            "Electric forklifts",
            "Electric pallet stackers",
            "Electric pallet trucks",
            "ANSI/ITSDF B56.1-2020",
            "UL 583 NRTL Type E",
            "UN 38.3 lithium battery transport testing",
        ],
    }


def page(title, description, route, body, schema=None, active=""):
    schemas = [organization_schema()]
    if schema:
        schemas.extend(schema if isinstance(schema, list) else [schema])
    json_ld = json.dumps({"@context": "https://schema.org", "@graph": schemas}, ensure_ascii=False)
    canonical = route_url(route)
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)} | LEXYGO</title><meta name="description" content="{esc(description)}"><link rel="canonical" href="{canonical}">
<meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(description)}"><meta property="og:type" content="website"><meta property="og:url" content="{canonical}"><meta property="og:image" content="{BASE_URL}/assets/og-cover.png">
<link rel="icon" href="/assets/lexygo-logo.gif" type="image/gif"><link rel="stylesheet" href="/assets/site.css?v=20261007-2"><script type="application/ld+json">{json_ld}</script></head>
<body>{header(active)}<main id="main">{body}</main>{footer()}<script src="https://unpkg.com/lucide@0.468.0/dist/umd/lucide.min.js"></script><script src="/assets/site.js?v=20261007-2"></script></body></html>"""


def breadcrumbs(items):
    visible = []
    structured = []
    for index, (label, href) in enumerate(items, start=1):
        visible.append(f'<a href="{href}">{esc(label)}</a><span>{icon("chevron-right", 13)}</span>' if href else f'<span aria-current="page">{esc(label)}</span>')
        entry = {"@type": "ListItem", "position": index, "name": label}
        if href:
            entry["item"] = route_url(href)
        structured.append(entry)
    return '<nav class="breadcrumbs shell" aria-label="Breadcrumb">' + "".join(visible) + "</nav>", {"@type": "BreadcrumbList", "itemListElement": structured}


def inner_banner(title, crumbs):
    breadcrumb_html, breadcrumb_schema = breadcrumbs(crumbs)
    return f'<section class="inner-banner"><div class="shell"><h1>{esc(title)}</h1></div></section>{breadcrumb_html}', breadcrumb_schema


def inquiry_form(compact=False):
    fields = """<label><span>Name</span><input name="name" required></label><label><span>Email</span><input type="email" name="email" required></label><label><span>Company</span><input name="company"></label><label><span>Country / Region</span><input name="country"></label><label class="full"><span>Product / Model</span><input name="model" data-model-field></label><label class="full"><span>Message</span><textarea name="details" rows="5" required></textarea></label>"""
    klass = "inquiry-form compact-form" if compact else "inquiry-form"
    return f'<form class="{klass}" data-mailto-form data-email="{esc(COMPANY["email"])}"><div class="form-grid">{fields}</div><button class="button button-primary" type="submit">Send Inquiry {icon("send", 17)}</button></form>'


def section_heading(kicker, title, copy=""):
    copy_html = f'<p>{esc(copy)}</p>' if copy else ""
    return f'<header class="section-heading"><span>{esc(kicker)}</span><h2>{esc(title)}</h2>{copy_html}</header>'


def product_card(item):
    capacity = known(item["capacity"])
    lift = known(item["lift"])
    operation = known(item["operation"])
    specs = "".join(
        f'<li><span>{label}</span><strong>{esc(value) if value else "&nbsp;"}</strong></li>'
        for label, value in [("Capacity", capacity), ("Lift height", lift), ("Operation", operation)]
    )
    return f"""
    <article class="product-card"><a class="{image_class(item)}" href="/products/{item['slug']}/"><img src="/assets/products/{esc(item['image'])}" alt="{esc(item['model'])} {esc(item['name'])}" loading="lazy"></a>
      <div class="product-card-copy"><p class="model-code">{esc(item['model'])}</p><h3><a href="/products/{item['slug']}/">{esc(item['name'])}</a></h3><ul>{specs}</ul><div class="card-actions"><a href="/contact/?model={esc(item['model'])}">Inquire</a><a href="/products/{item['slug']}/">More &gt;&gt;</a></div></div>
    </article>"""


def home_page():
    featured_slugs = ["r4efl3t", "wep20j", "wes1500a", "mpt5tn"]
    featured = [next(item for item in PRODUCTS if item["slug"] == slug) for slug in featured_slugs]
    featured_html = product_card(featured[0]) + '<div class="featured-stack">' + "".join(product_card(item) for item in featured[1:]) + "</div>"
    solution_cards = "".join(
        f'<a class="solution-card" href="/products/{slug}/"><img src="/assets/products/{esc(data["image"])}" alt="{esc(data["name"])}"><span>{esc(data["name"])}</span></a>'
        for slug, data in list(CATEGORIES.items())[:4]
    )
    why = [
        ("Factory Production", "Material handling equipment produced by an intelligent machinery manufacturer in Changxing, Zhejiang, China."),
        ("Independent LEXYGO Range", "LEXYGO pallet trucks, stackers, electric forklifts, and warehouse equipment are presented by model and application."),
        ("OEM And Configuration Support", "Product configuration and final technical details are confirmed for each quotation and application."),
    ]
    why_html = "".join(f'<article><span>{index:02d}</span><h3>{esc(title)}</h3><p>{esc(copy)}</p></article>' for index, (title, copy) in enumerate(why, start=1))
    body = f"""
    <section class="hero"><div class="shell hero-grid"><div class="hero-copy"><p>LEXYGO MATERIAL HANDLING EQUIPMENT</p><h1>Electric Forklifts, Stackers &amp; Pallet Trucks</h1><p class="hero-intro">Direct product access for professional buyers, distributors, and material handling projects.</p>{button('View Products', '/products/', 'primary')} {button('Contact Us', '/contact/', 'light')}</div><div class="hero-machine"><img src="/assets/products/efl2000r3.png" alt="LEXYGO EFL2000R3 electric forklift"></div></div></section>
    <section class="home-section featured-section"><div class="shell">{section_heading('PRODUCTS', 'FEATURED PRODUCTS', 'Browse core LEXYGO models and open the complete technical parameter page.')}
      <div class="featured-grid">{featured_html}</div><div class="center-action">{button('View All Products', '/products/', 'outline')}</div></div></section>
    <section class="home-section solutions-section"><div class="shell">{section_heading('PRODUCT RANGE', 'ONE-STOP MATERIAL HANDLING SOLUTIONS')}
      <div class="solution-grid">{solution_cards}</div></div></section>
    <section class="home-section about-band"><div class="shell about-grid"><div><p class="section-kicker">WHO WE ARE?</p><h2>{esc(COMPANY['legal_name'])}</h2><p>We manufacture and supply electric pallet trucks, electric pallet stackers, electric forklifts, manual pallet trucks, and warehouse equipment.</p><p>Our product pages present the available English technical data for professional selection and inquiry.</p>{button('Learn More', '/company/', 'primary')}</div><div class="about-photo"><img src="/assets/products/res2000e.png" alt="LEXYGO electric stacker"></div></div></section>
    <section class="factory-stats"><div class="shell stats-grid"><div><strong>&nbsp;</strong><span>Factory Area</span></div><div><strong>&nbsp;</strong><span>Production Lines</span></div><div><strong>&nbsp;</strong><span>Annual Capacity</span></div><div><strong>&nbsp;</strong><span>Export Markets</span></div></div></section>
    <section class="home-section why-section"><div class="shell">{section_heading('FACTORY & SERVICE', 'WHY CHOOSE LEXYGO')}
      <div class="why-grid">{why_html}</div></div></section>
    <section class="home-section showroom-section"><div class="shell">{section_heading('FACTORY VIEW', 'DIGITAL SHOWROOM')}<div class="blank-media" aria-label="Digital showroom content pending"></div></div></section>
    <section class="home-section cases-section"><div class="shell">{section_heading('APPLICATIONS', 'OUR CASES')}<div class="blank-grid"><article></article><article></article></div></div></section>
    <section class="home-section insights-section"><div class="shell">{section_heading('LEARN MORE', 'INDUSTRY INSIGHTS & PRODUCT KNOWLEDGE')}<div class="blank-grid three"><article></article><article></article><article></article></div></div></section>
    <section class="contact-band"><div class="shell contact-band-grid"><div><p class="section-kicker">CONTACT US</p><h2>Tell Us What You Need To Move Or Lift</h2><p>Share the load, lift height, aisle, route, quantity, and destination.</p></div>{inquiry_form()}</div></section>
    """
    schema = {"@type": "WebSite", "name": "LEXYGO", "url": BASE_URL}
    return page("Material Handling Equipment Manufacturer", "LEXYGO electric forklifts, pallet stackers, pallet trucks, and warehouse equipment for professional buyers.", "/", body, schema, "home")


def sidebar():
    return f'<aside class="catalog-sidebar">{category_menu()}<div class="side-box inquiry-box"><h2>CONTACT US</h2>{inquiry_form(True)}</div></aside>'


def products_page():
    banner, crumb_schema = inner_banner("ALL PRODUCTS", [("Home", "/"), ("Products", None)])
    cards = "".join(product_card(item) for item in PRODUCTS)
    body = f'{banner}<section class="catalog-layout-section"><div class="shell catalog-layout">{sidebar()}<div class="catalog-main"><header class="catalog-title"><p>PRODUCTS</p><h2>ALL PRODUCTS</h2><p>Select a product family or open a model page to review the available English technical parameters.</p></header><div class="product-grid">{cards}</div></div></div></section>'
    return page("All Material Handling Products", "Browse LEXYGO electric pallet trucks, stackers, electric forklifts, manual pallet trucks, and warehouse equipment.", "/products/", body, crumb_schema, "products")


def category_page(slug, data):
    items = products_for(slug)
    banner, crumb_schema = inner_banner(data["name"].upper(), [("Home", "/"), ("Products", "/products/"), (data["name"], None)])
    cards = "".join(product_card(item) for item in items)
    body = f'{banner}<section class="catalog-layout-section"><div class="shell catalog-layout">{sidebar()}<div class="catalog-main"><header class="catalog-title"><p>PRODUCT CATEGORY</p><h2>{esc(data["name"])}</h2><p>{esc(data["short"])}</p></header><div class="category-answer"><strong>Selection note</strong><p>{esc(data["answer"])}</p></div><div class="product-grid">{cards}</div></div></div></section>'
    schema = [{"@type": "CollectionPage", "name": data["name"], "description": data["short"], "url": route_url(f"/products/{slug}/")}, crumb_schema]
    return page(data["name"], data["short"], f"/products/{slug}/", body, schema, "products")


def spec_tables(item):
    groups = FULL_SPECS.get(item["slug"], [])
    if not groups:
        return '<div class="spec-empty" aria-label="Product parameters pending"></div>'
    blocks = []
    for group in groups:
        rows = "".join(
            f'<tr><th scope="row">{esc(row["name"])}</th><td>{esc(row.get("unit", ""))}</td><td>{esc(row.get("value", ""))}</td></tr>'
            for row in group["rows"]
        )
        blocks.append(f'<section class="spec-group"><h3>{esc(group["title"])}</h3><div class="table-wrap"><table><thead><tr><th>Parameter</th><th>Unit</th><th>Value</th></tr></thead><tbody>{rows}</tbody></table></div></section>')
    return "".join(blocks)


def product_page(item):
    category = CATEGORIES[item["category"]]
    banner, crumb_schema = inner_banner(item["name"].upper(), [("Home", "/"), ("Products", "/products/"), (category["name"], f'/products/{item["category"]}/'), (item["model"], None)])
    key_specs = [("Rated capacity", known(item["capacity"])), ("Lift height", known(item["lift"])), ("Operation", known(item["operation"])), ("Application", known(item["best_for"]))]
    quick_rows = "".join(f'<tr><th>{esc(label)}</th><td>{esc(value) if value else "&nbsp;"}</td></tr>' for label, value in key_specs)
    feature_items = "".join(f'<li><span>{esc(label)}</span><strong>{esc(value) if value else "&nbsp;"}</strong></li>' for label, value in key_specs)
    related_items = [related for related in products_for(item["category"]) if related["slug"] != item["slug"]][:4]
    related = "".join(product_card(product) for product in related_items)
    product_schema = {
        "@type": "Product", "name": f'{item["model"]} {item["name"]}', "sku": item["model"], "brand": {"@type": "Brand", "name": "LEXYGO"},
        "category": category["name"], "image": f'{BASE_URL}/assets/products/{item["image"]}', "description": item["best_for"],
    }
    body = f"""{banner}
    <section class="product-intro"><div class="shell product-intro-grid"><div class="product-gallery"><div class="{image_class(item)}"><img src="/assets/products/{esc(item['image'])}" alt="{esc(item['model'])} {esc(item['name'])}"></div></div><div class="product-summary"><p class="model-code">{esc(item['model'])}</p><h2>{esc(item['name'])}</h2><p>{esc(item['best_for'])}</p><ul class="feature-list">{feature_items}</ul><dl class="availability"><div><dt>Availability</dt><dd>&nbsp;</dd></div><div><dt>Quantity</dt><dd>&nbsp;</dd></div></dl>{button('INQUIRE', f'/contact/?model={esc(item["model"])}', 'primary', 'send')}<div class="product-identity"><span>Model: <strong>{esc(item['model'])}</strong></span><span>Brand: <strong>LEXYGO</strong></span></div></div></div></section>
    <section class="product-description"><div class="shell"><header class="tab-heading"><span>Product Description</span></header><div class="description-grid"><div><h2>{esc(item['model'])} {esc(item['name'])}</h2><p>{esc(item['best_for'])}.</p><p>{esc(item['note'])}</p></div><div class="quick-table"><table><tbody>{quick_rows}</tbody></table></div></div></div></section>
    <section class="parameter-section"><div class="shell"><header class="tab-heading"><span>Product Parameters</span></header>{spec_tables(item)}</div></section>
    <section class="detail-inquiry"><div class="shell detail-inquiry-grid"><div><p class="section-kicker">SEND YOUR REQUIREMENTS</p><h2>Request Price And Configuration</h2><p>Use the model number and describe the load, lift height, aisle, duty, quantity, and destination.</p></div>{inquiry_form()}</div></section>
    <section class="related-section"><div class="shell">{section_heading('MORE PRODUCTS', 'RELATED PRODUCTS')}<div class="product-grid four">{related}</div></div></section>"""
    return page(f'{item["model"]} {item["name"]}', f'{item["model"]} {item["name"]}: {known(item["capacity"])} capacity, {known(item["lift"])} lift, {known(item["operation"])} operation.', f'/products/{item["slug"]}/', body, [product_schema, crumb_schema], "products")


def blank_page(route, title, parent=None, active=""):
    crumbs = [("Home", "/")]
    if parent:
        crumbs.append(parent)
    crumbs.append((title, None))
    banner, crumb_schema = inner_banner(title.upper(), crumbs)
    body = f'{banner}<section class="blank-page"><div class="shell"><h2>{esc(title)}</h2><div class="blank-content" aria-label="Content pending"></div></div></section>'
    return page(title, f"LEXYGO {title}.", route, body, crumb_schema, active)


def services_page():
    banner, crumb_schema = inner_banner("MATERIAL HANDLING EQUIPMENT SERVICES", [("Home", "/"), ("Services", None)])
    services = [
        (
            "search-check",
            "Product Selection & Application Matching",
            "We compare the working conditions with the available model range before a quotation is prepared.",
            ["Load capacity and lift height", "Pallet type, aisle width, and terrain", "Duty cycle, battery, and destination market"],
        ),
        (
            "settings",
            "OEM & Private-Label Customization",
            "Branding and configuration requests are evaluated against the selected model, order quantity, and safety requirements.",
            ["Logo, color, and product labels", "Battery, charger, forks, and mast options", "Manuals, packaging, and spare-parts kits"],
        ),
        (
            "file-check-2",
            "Compliance & Export Documentation",
            "The available document package is confirmed by product model, supplied configuration, battery, and destination market.",
            ["Applicable CE and industrial-truck reports", "Applicable UL 583 and UN 38.3 documents", "English operating and safety information"],
        ),
        (
            "clipboard-check",
            "Quality Inspection & Pre-Shipment Testing",
            "Inspection scope is agreed with the order and can include functional, identification, battery, and packing checks.",
            ["Assembly, labels, steering, and braking", "Lifting, lowering, and agreed load checks", "Photos, video, and available records on request"],
        ),
        (
            "package-check",
            "Export Packaging & Shipping Support",
            "Packaging and shipment documents are prepared according to the machine, transport method, destination, and agreed trade terms.",
            ["Export packaging and shipping marks", "Loading information and packing confirmation", "Commercial and battery transport documents"],
        ),
        (
            "wrench",
            "Spare Parts & After-Sales Support",
            "The product model and serial information are used to identify parts and organize technical support for supplied equipment.",
            ["Parts identification and replacement support", "English manuals and remote troubleshooting", "Warranty terms confirmed in the sales contract"],
        ),
    ]
    service_html = "".join(
        f'<article><span class="service-icon">{icon(icon_name, 22)}</span><h3>{esc(title)}</h3><p>{esc(copy)}</p><ul>{"".join(f"<li>{esc(item)}</li>" for item in items)}</ul></article>'
        for icon_name, title, copy, items in services
    )
    matrix_rows = [
        ("Product selection", "Capacity, lift height, pallet, aisle, terrain, duty cycle, and destination", "Recommended models, comparison, configuration notes, and quotation"),
        ("OEM / private label", "Selected model, quantity, branding, color, electrical, fork, mast, and packaging requirements", "Feasibility confirmation, available options, cost, and lead-time basis"),
        ("Compliance documents", "Product model, battery, charger, supplied configuration, and destination market", "List of applicable reports, certificates, manuals, labels, and battery documents"),
        ("Pre-shipment inspection", "Confirmed order and any customer-specific inspection points", "Agreed inspection evidence, photos, video, and packing confirmation"),
        ("Export support", "Destination, transport method, consignee marks, and agreed trade terms", "Export packaging, packing information, and agreed commercial documents"),
        ("After-sales support", "Model, serial number, photos, working hours, and a description or video of the issue", "Parts identification, troubleshooting guidance, and warranty review"),
    ]
    matrix_html = "".join(
        f'<tr><th scope="row">{esc(service)}</th><td>{esc(required)}</td><td>{esc(deliverable)}</td></tr>'
        for service, required, deliverable in matrix_rows
    )
    steps = [
        ("01", "Submit Application Requirements", "Tell us the load, lift height, pallet, workspace, quantity, and destination."),
        ("02", "Receive Model Recommendation", "We identify suitable models and clarify any missing technical information."),
        ("03", "Confirm Configuration & Documents", "Both parties confirm the machine configuration and applicable document package."),
        ("04", "Approve Quotation & Order Details", "Commercial terms, customization, production basis, and inspection scope are agreed."),
        ("05", "Inspection & Shipment", "The agreed inspection and packing checks are completed before release."),
        ("06", "After-Sales & Parts Support", "Use the model and serial number when requesting technical or spare-parts support."),
    ]
    step_html = "".join(
        f'<li><span>{number}</span><div><h3>{esc(title)}</h3><p>{esc(copy)}</p></div></li>'
        for number, title, copy in steps
    )
    requirements = [
        "Product type or model",
        "Required quantity",
        "Rated load capacity",
        "Required lift height",
        "Pallet type and dimensions",
        "Aisle width and working environment",
        "Floor or terrain condition",
        "Daily operating hours",
        "Battery and charger preference",
        "Destination country",
        "Required compliance documents",
        "OEM, branding, or packaging requirements",
    ]
    requirement_html = "".join(f'<li>{icon("check", 16)}<span>{esc(item)}</span></li>' for item in requirements)
    faqs = [
        ("How do I select the correct pallet truck, stacker, or forklift?", "Send the load capacity, lift height, pallet type, aisle width, floor or terrain condition, daily operating hours, quantity, and destination country. LEXYGO will compare suitable models and configurations."),
        ("Can LEXYGO customize the logo and machine color?", "Logo, color, labels, manuals, and packaging can be evaluated for OEM or private-label orders. Availability depends on the product model, order quantity, and safety-label requirements."),
        ("Can fork dimensions, battery, charger, or mast height be customized?", "Configuration options vary by model. Send the required dimensions, voltage, plug type, battery preference, and lift height for a technical feasibility review."),
        ("Which compliance documents are supplied with the machine?", "Document availability depends on the model, battery, charger, supplied configuration, and destination market. LEXYGO confirms the applicable document list before order approval."),
        ("Can you provide inspection photos or videos before shipment?", "Photos, operating video, serial information, and available inspection records can be included when they are agreed in the order inspection scope."),
        ("Do you provide lithium battery transport documents?", "Applicable lithium battery packs can be matched with the available UN 38.3 and safety documentation required for shipment review."),
        ("How do I request replacement parts or technical support?", "Provide the product model, serial number, photos, operating hours, and a clear description or video of the issue so the correct parts and support route can be identified."),
        ("What is the warranty period?", "Warranty duration, covered components, exclusions, and claim conditions are confirmed in the sales contract for the ordered model and configuration."),
    ]
    faq_html = "".join(f'<details><summary>{esc(question)}{icon("plus", 18)}</summary><p>{esc(answer)}</p></details>' for question, answer in faqs)
    faq_schema = {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]}
    service_schema = {
        "@type": "Service",
        "name": "Material Handling Equipment Services",
        "serviceType": "Product selection, OEM customization, compliance documentation, inspection, export support, and after-sales support",
        "provider": {"@type": "Organization", "name": COMPANY["display_name"], "url": BASE_URL},
        "url": route_url("/services/"),
    }
    body = f"""{banner}
    <section class="services-intro"><div class="shell services-answer"><p class="section-kicker">FOR PROFESSIONAL BUYERS</p><h2>How Does LEXYGO Support An International Equipment Order?</h2><p>LEXYGO supports distributors, equipment dealers, warehouses, factories, and industrial buyers with product selection, OEM evaluation, model-specific compliance documentation, agreed pre-shipment inspection, export preparation, and after-sales parts support.</p><p class="service-note">Final configuration, document availability, inspection scope, warranty, and commercial terms are confirmed for the selected model in the quotation or sales contract.</p></div></section>
    <section class="services-section"><div class="shell">{section_heading('SERVICE SCOPE', 'Support From Selection To After-Sales', 'Each service is tied to the selected model, application, order terms, and destination-market requirements.')}<div class="services-grid">{service_html}</div></div></section>
    <section class="service-matrix-section"><div class="shell"><div class="section-heading left"><span>WHAT TO PROVIDE</span><h2>Service Inputs And Deliverables</h2><p>Clear input information allows us to provide a more accurate technical and commercial response.</p></div><div class="table-wrap"><table class="evidence-table service-matrix"><thead><tr><th>Service</th><th>Information required</th><th>What you receive</th></tr></thead><tbody>{matrix_html}</tbody></table></div></div></section>
    <section class="release-section service-workflow"><div class="shell release-grid"><div><p class="section-kicker">WORKING PROCESS</p><h2>From Requirement To After-Sales Support</h2><p>A six-step process keeps the product, supplied configuration, documentation, and commercial terms aligned.</p></div><ol>{step_html}</ol></div></section>
    <section class="requirements-section"><div class="shell requirements-grid"><div><p class="section-kicker">REQUEST A QUOTATION</p><h2>Information Required For An Accurate Recommendation</h2><p>Include as much of this information as possible. If an item is unknown, describe the application and we will help clarify it.</p>{button('Send Your Requirements', '/contact/', 'primary', 'send')}</div><ul>{requirement_html}</ul></div></section>
    <section class="faq-section"><div class="shell faq-grid"><div><p class="section-kicker">QUICK ANSWERS</p><h2>Service Questions From International Buyers</h2><p>Direct answers about selection, customization, documentation, inspection, warranty, and parts support.</p></div><div class="faq-list">{faq_html}</div></div></section>
    <section class="company-contact-strip"><div class="shell"><div><strong>Tell us what the machine needs to do</strong><span>Send the application, capacity, lift height, quantity, and destination to {esc(COMPANY['email'])}.</span></div>{button('Contact LEXYGO', '/contact/', 'primary', 'send')}</div></section>"""
    return page(
        "Material Handling Equipment Services",
        "LEXYGO provides product selection, OEM evaluation, compliance documentation, pre-shipment inspection, export support, spare parts, and after-sales support for material handling equipment buyers.",
        "/services/",
        body,
        [service_schema, faq_schema, crumb_schema],
        "services",
    )


def company_page():
    banner, crumb_schema = inner_banner("COMPANY PROFILE", [("Home", "/"), ("Company", None)])
    product_links = "".join(
        f'<a href="/products/{slug}/"><span>{esc(data["name"])}</span>{icon("arrow-up-right", 17)}</a>'
        for slug, data in CATEGORIES.items()
    )
    body = f"""{banner}
    <section class="company-profile"><div class="shell profile-grid"><div><p class="section-kicker">WHO WE ARE</p><h2>{esc(COMPANY['display_name'])}</h2><p class="answer-lead">LEXYGO is a China-based material handling equipment manufacturer serving professional buyers, distributors, warehouses, factories, and logistics operations.</p><p>Our product range includes electric pallet trucks, electric pallet stackers, electric forklifts, manual pallet trucks, and supporting warehouse equipment.</p></div><div class="company-machine"><img src="/assets/products/r4efl5t.png" alt="LEXYGO electric forklift manufactured in Zhejiang, China"></div></div></section>
    <section class="entity-section"><div class="shell entity-grid"><div><p class="section-kicker">COMPANY FACTS</p><h2>LEXYGO At A Glance</h2><p>These facts identify the manufacturer, location, product scope, and direct sales contact for sourcing and supplier verification.</p></div><dl class="entity-facts"><div><dt>Business name</dt><dd>{esc(COMPANY['display_name'])}</dd></div><div><dt>Business type</dt><dd>Material handling equipment manufacturer and supplier</dd></div><div><dt>Address</dt><dd>{esc(COMPANY['address'])}</dd></div><div><dt>Primary products</dt><dd>Electric forklifts, pallet stackers, pallet trucks, and warehouse equipment</dd></div><div><dt>Sales email</dt><dd><a href="mailto:{esc(COMPANY['email'])}">{esc(COMPANY['email'])}</a></dd></div></dl></div></section>
    <section class="profile-range"><div class="shell">{section_heading('PRODUCT SCOPE', 'Material Handling Equipment By Category', 'Open a category to compare models, capacities, lift heights, and available technical parameters.')}<div class="profile-product-links">{product_links}</div></div></section>
    <section class="compliance-band"><div class="shell compliance-band-grid"><div><p class="section-kicker">DOCUMENTED COMPLIANCE</p><h2>Compliance Evidence For International Buyers</h2><p>LEXYGO products are supplied with the applicable compliance package for their product type and configuration.</p></div><ul><li>EU CE certification and test documentation</li><li>ANSI/ITSDF B56.1-2020 test reports</li><li>UL 583 NRTL Type E certification for applicable electric industrial trucks</li><li>UN 38.3 documentation for applicable lithium battery packs</li><li>English safety and operating documentation</li></ul></div></section>
    <section class="company-contact-strip"><div class="shell"><div><strong>Discuss a product or sourcing project</strong><span>{esc(COMPANY['email'])} &nbsp; | &nbsp; {esc(COMPANY['telephone'])}</span></div>{button('Contact LEXYGO', '/contact/', 'primary', 'send')}</div></section>"""
    about_schema = {"@type": "AboutPage", "name": "LEXYGO Company Profile", "url": route_url("/company/"), "about": {"@id": route_url("/")}}
    return page("Company Profile", "LEXYGO is a material handling equipment manufacturer in Huzhou, Zhejiang, China, supplying electric forklifts, pallet stackers, pallet trucks, and warehouse equipment.", "/company/", body, [about_schema, crumb_schema], "company")


def why_choose_page():
    banner, crumb_schema = inner_banner("WHY CHOOSE US", [("Home", "/"), ("Company", "/company/"), ("Why Choose Us", None)])
    reasons = [
        ("Documented Compliance", "Applicable products are supported by CE documentation, ANSI/ITSDF B56.1-2020 test reports, UL 583 NRTL Type E certification, UN 38.3 battery documentation, and English safety materials."),
        ("Manufacturer-Direct Communication", "Buyers communicate directly with the LEXYGO team about model selection, load capacity, lift height, battery configuration, and application conditions."),
        ("A Focused Product Directory", "Products are organized by truck type, model, capacity, operation method, and application so professional buyers can compare suitable equipment quickly."),
        ("Configuration-Level Documentation", "Compliance and safety documents are matched to the applicable product type and supplied configuration rather than presented as generic marketing claims."),
    ]
    reason_html = "".join(f'<article><span>{index:02d}</span><h3>{esc(title)}</h3><p>{esc(copy)}</p></article>' for index, (title, copy) in enumerate(reasons, start=1))
    evidence_rows = [
        ("European market conformity", "EU CE certification and test documentation", "Supports technical review for applicable EU product requirements"),
        ("Industrial truck safety", "ANSI/ITSDF B56.1-2020 test report", "Provides model-level safety and performance evidence"),
        ("Electrical and fire safety", "UL 583 NRTL Type E certification for applicable electric trucks", "Supports U.S. industrial buyer and workplace approval reviews"),
        ("Lithium battery transport", "UN 38.3 test documentation for applicable battery packs", "Supports international lithium battery shipment documentation"),
        ("Safe operation", "English safety, operating, and product documentation", "Helps distributors and end users review correct use and maintenance"),
    ]
    evidence_html = "".join(f'<tr><th scope="row">{esc(claim)}</th><td>{esc(evidence)}</td><td>{esc(benefit)}</td></tr>' for claim, evidence, benefit in evidence_rows)
    faqs = [
        ("What does LEXYGO manufacture?", "LEXYGO manufactures and supplies electric forklifts, electric pallet stackers, electric pallet trucks, manual pallet trucks, and warehouse equipment."),
        ("Do LEXYGO products have CE documentation?", "Yes. LEXYGO products are supported by the applicable EU CE certification and test documentation."),
        ("Are ANSI/ITSDF B56.1-2020 test reports available?", "Yes. ANSI/ITSDF B56.1-2020 test reports are available for LEXYGO industrial truck products according to the applicable model and configuration."),
        ("Is UL 583 NRTL Type E certification available?", "Yes. Applicable LEXYGO electric industrial trucks are supported by UL 583 NRTL Type E certification."),
        ("Are lithium battery documents available?", "Yes. Applicable lithium battery packs are supported by UN 38.3 documentation, together with English safety information."),
    ]
    faq_html = "".join(f'<details><summary>{esc(question)}{icon("plus", 18)}</summary><p>{esc(answer)}</p></details>' for question, answer in faqs)
    faq_schema = {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]}
    body = f"""{banner}
    <section class="answer-section"><div class="shell answer-grid"><p class="section-kicker">THE SHORT ANSWER</p><h2>Why Do Buyers Choose LEXYGO?</h2><p>LEXYGO combines manufacturer-direct product support with documented international compliance, model-level technical information, and English safety documentation.</p></div></section>
    <section class="reason-section"><div class="shell">{section_heading('BUYER VALUE', 'Four Reasons To Work With LEXYGO')}<div class="reason-grid">{reason_html}</div></div></section>
    <section class="evidence-section"><div class="shell"><div class="section-heading left"><span>VERIFIABLE EVIDENCE</span><h2>Compliance And Documentation Matrix</h2><p>Documents are supplied according to the applicable product type, battery configuration, and destination-market requirement.</p></div><div class="table-wrap"><table class="evidence-table"><thead><tr><th>Buyer question</th><th>Available evidence</th><th>Buyer value</th></tr></thead><tbody>{evidence_html}</tbody></table></div></div></section>
    <section class="faq-section"><div class="shell faq-grid"><div><p class="section-kicker">QUICK ANSWERS</p><h2>Frequently Asked Questions</h2><p>Direct answers for sourcing teams, distributors, and industrial buyers.</p></div><div class="faq-list">{faq_html}</div></div></section>
    <section class="company-contact-strip"><div class="shell"><div><strong>Request model-specific compliance documents</strong><span>Contact {esc(COMPANY['email'])} with the product model and destination market.</span></div>{button('Request Documents', '/contact/', 'primary', 'send')}</div></section>"""
    return page("Why Choose LEXYGO", "Choose LEXYGO for manufacturer-direct material handling equipment, documented international compliance, model-level specifications, and English safety documentation.", "/company/why-choose-us/", body, [faq_schema, crumb_schema], "company")


def quality_management_page():
    banner, crumb_schema = inner_banner("QUALITY MANAGEMENT", [("Home", "/"), ("Company", "/company/"), ("Quality Management", None)])
    controls = [
        ("Product Conformity", "Applicable CE certification and test documentation support product conformity review."),
        ("Industrial Truck Safety", "ANSI/ITSDF B56.1-2020 test reports provide model-level industrial truck safety evidence."),
        ("Electrical Fire Safety", "Applicable electric industrial trucks are supported by UL 583 NRTL Type E certification."),
        ("Battery Transport Safety", "Applicable lithium battery packs are supported by UN 38.3 transport test documentation."),
        ("English Safety Information", "English operating, warning, and safety materials support distributor and end-user review."),
        ("Configuration Matching", "Documents are matched to the applicable model and supplied configuration for buyer review."),
    ]
    control_html = "".join(f'<article><span>{icon("check-circle", 22)}</span><h3>{esc(title)}</h3><p>{esc(copy)}</p></article>' for title, copy in controls)
    document_rows = [
        ("CE certification and test documentation", "Applicable LEXYGO products", "European conformity review"),
        ("ANSI/ITSDF B56.1-2020 test report", "Applicable industrial truck models", "Safety and performance review"),
        ("UL 583 NRTL Type E certification", "Applicable electric industrial trucks", "Electrical and fire-safety review"),
        ("UN 38.3 battery documentation", "Applicable lithium battery packs", "Dangerous-goods transport preparation"),
        ("English safety documentation", "Applicable products and configurations", "Operation, warning, and maintenance review"),
    ]
    documents_html = "".join(f'<tr><th scope="row">{esc(document)}</th><td>{esc(applies)}</td><td>{esc(purpose)}</td></tr>' for document, applies, purpose in document_rows)
    steps = [
        ("01", "Identify The Product Configuration", "Confirm the model, capacity, lift height, mast, battery, charger, and destination market."),
        ("02", "Match Applicable Compliance", "Determine which CE, B56.1, UL 583, UN 38.3, and English safety documents apply to the configuration."),
        ("03", "Review Product Identification", "Check the model information, rated capacity, product markings, and configuration references."),
        ("04", "Prepare The Document Package", "Compile the applicable test, certification, battery, and English safety documents for buyer review."),
        ("05", "Release For Shipment", "Confirm the supplied configuration and corresponding document package before shipment release."),
    ]
    step_html = "".join(f'<li><span>{number}</span><div><h3>{esc(title)}</h3><p>{esc(copy)}</p></div></li>' for number, title, copy in steps)
    body = f"""{banner}
    <section class="answer-section"><div class="shell answer-grid"><p class="section-kicker">QUALITY POLICY</p><h2>How Does LEXYGO Manage Product Quality?</h2><p>LEXYGO uses a compliance-led quality framework that connects each applicable product configuration with test evidence, certification records, battery transport documentation, and English safety information.</p></div></section>
    <section class="quality-controls"><div class="shell">{section_heading('CONTROL FRAMEWORK', 'Six Quality And Compliance Controls')}<div class="quality-grid">{control_html}</div></div></section>
    <section class="document-section"><div class="shell"><div class="section-heading left"><span>DOCUMENT CONTROL</span><h2>Quality Document Matrix</h2><p>The exact document package depends on the product type, battery, charger, configuration, and destination market.</p></div><div class="table-wrap"><table class="evidence-table"><thead><tr><th>Document</th><th>Applies to</th><th>Purpose</th></tr></thead><tbody>{documents_html}</tbody></table></div></div></section>
    <section class="release-section"><div class="shell release-grid"><div><p class="section-kicker">CONFIGURATION CONTROL</p><h2>From Product Selection To Shipment Release</h2><p>Our quality workflow keeps the supplied machine and its applicable compliance documentation aligned.</p></div><ol>{step_html}</ol></div></section>
    <section class="company-contact-strip"><div class="shell"><div><strong>Need a compliance package for supplier approval?</strong><span>Send the model, configuration, and destination market to {esc(COMPANY['email'])}.</span></div>{button('Contact Quality Team', '/contact/', 'primary', 'send')}</div></section>"""
    return page("Quality Management", "LEXYGO quality management connects applicable product configurations with CE, ANSI/ITSDF B56.1-2020, UL 583 NRTL Type E, UN 38.3, and English safety documentation.", "/company/quality-management/", body, crumb_schema, "company")


def resources_page():
    banner, crumb_schema = inner_banner("RESOURCE CENTER", [("Home", "/"), ("Resources", None)])
    resources = [
        ("list-checks", "Buyer Guides", "Practical selection guides for comparing equipment types, capacity, lift height, aisle space, terrain, battery, and duty cycle.", "/guides/", "Open buyer guides"),
        ("badge-check", "Compliance Center", "Understand the document package that may apply to the selected machine, battery, charger, configuration, and destination market.", "/resources/compliance/", "Review compliance information"),
        ("file-down", "Downloads & Documents", "Find product data online and request model-specific datasheets, manuals, safety information, and available compliance documents.", "/resources/download/", "Find a document"),
        ("circle-help", "Buyer FAQ", "Direct answers about product selection, pallets, batteries, OEM orders, documents, shipping, warranty, and spare parts.", "/resources/faq/", "Read buyer questions"),
        ("warehouse", "Application Cases", "Application notes that connect working conditions with suitable equipment families without using unverified customer claims.", "/resources/cases/", "Explore applications"),
    ]
    resource_html = "".join(
        f'<article><span class="resource-icon">{icon(icon_name, 23)}</span><h3>{esc(title)}</h3><p>{esc(copy)}</p><a href="{href}">{esc(link)}{icon("arrow-right", 16)}</a></article>'
        for icon_name, title, copy, href, link in resources
    )
    questions = [
        ("How do I choose an electric pallet truck?", "/guides/how-to-choose-an-electric-pallet-truck/"),
        ("Should I use a pallet truck or a pallet stacker?", "/guides/pallet-truck-vs-stacker/"),
        ("How do capacity, lift height, and aisle width affect forklift selection?", "/guides/forklift-capacity-and-aisle-width/"),
        ("Which documents should I request before ordering?", "/resources/compliance/"),
        ("What information is needed for an accurate quotation?", "/resources/faq/#ordering-shipping"),
        ("How can I request a model-specific manual or test document?", "/resources/download/"),
    ]
    question_html = "".join(f'<a href="{href}"><span>{esc(question)}</span>{icon("arrow-up-right", 17)}</a>' for question, href in questions)
    matrix = [
        ("Compare equipment", "Buyer Guides", "Load, pallet, travel route, lift height, aisle, terrain, and duty cycle", "/guides/"),
        ("Verify document scope", "Compliance Center", "Model, battery, charger, supplied configuration, and destination market", "/resources/compliance/"),
        ("Obtain technical files", "Downloads & Documents", "Model number, required file, language, company, and intended market", "/resources/download/"),
        ("Resolve a purchase question", "Buyer FAQ", "Selection, OEM, batteries, shipping, warranty, or spare-parts question", "/resources/faq/"),
        ("Review a working condition", "Application Cases", "Load, pallet, floor, route, stacking height, and operating frequency", "/resources/cases/"),
    ]
    matrix_html = "".join(
        f'<tr><th scope="row">{esc(task)}</th><td><a href="{href}">{esc(area)}</a></td><td>{esc(inputs)}</td></tr>'
        for task, area, inputs, href in matrix
    )
    collection_schema = {
        "@type": "CollectionPage",
        "name": "LEXYGO Material Handling Equipment Resource Center",
        "description": "Buyer guides, compliance information, technical documents, FAQs, and application notes for material handling equipment buyers.",
        "url": route_url("/resources/"),
    }
    body = f"""{banner}
    <section class="resource-intro"><div class="shell resource-answer"><p class="section-kicker">TECHNICAL AND BUYER INFORMATION</p><h2>Material Handling Equipment Resource Center</h2><p>Use this center to select equipment, understand the available document package, review technical data, and prepare a complete purchasing inquiry for electric pallet trucks, stackers, forklifts, manual pallet trucks, and warehouse equipment.</p><p class="resource-note">Technical and compliance information is matched to the selected model and supplied configuration. Request the current model-specific document package before placing an order.</p></div></section>
    <section class="resource-directory"><div class="shell">{section_heading('RESOURCE DIRECTORY', 'Find Information By Buyer Task', 'Each section answers a specific sourcing, selection, verification, or application question.')}<div class="resource-grid">{resource_html}</div></div></section>
    <section class="resource-questions"><div class="shell resource-question-grid"><div><p class="section-kicker">POPULAR QUESTIONS</p><h2>Start With The Decision You Need To Make</h2><p>These pages provide direct answers first, followed by tables, checklists, relevant product links, and the information needed for confirmation.</p></div><div class="question-links">{question_html}</div></div></section>
    <section class="resource-matrix-section"><div class="shell"><div class="section-heading left"><span>RESOURCE MAP</span><h2>Where To Find The Right Information</h2><p>Choose the resource area that matches the current step in your purchasing process.</p></div><div class="table-wrap"><table class="evidence-table resource-matrix"><thead><tr><th>Buyer task</th><th>Resource area</th><th>Information to prepare</th></tr></thead><tbody>{matrix_html}</tbody></table></div></div></section>
    <section class="company-contact-strip"><div class="shell"><div><strong>Cannot find the document or answer you need?</strong><span>Send the model, application, destination market, and requested document to {esc(COMPANY['email'])}.</span></div>{button('Ask The Technical Team', '/contact/', 'primary', 'send')}</div></section>"""
    return page(
        "Material Handling Equipment Resource Center",
        "Access LEXYGO buyer guides, compliance information, technical documents, FAQs, and application notes for pallet trucks, stackers, forklifts, and warehouse equipment.",
        "/resources/",
        body,
        [collection_schema, crumb_schema],
        "resources",
    )


def downloads_page():
    banner, crumb_schema = inner_banner("DOWNLOADS & DOCUMENTS", [("Home", "/"), ("Resources", "/resources/"), ("Downloads & Documents", None)])
    groups = [
        ("file-text", "Product Datasheets", "Model specifications, dimensions, capacity, lift range, battery, charger, and configuration information.", "Use the technical parameter table on each product page or request a revision-controlled datasheet."),
        ("book-open", "Operation & Safety Manuals", "Operating instructions, safety information, inspection points, charging guidance, and maintenance references.", "Request by model, serial number when available, supplied language, and destination market."),
        ("battery-charging", "Battery & Charger Documents", "Battery identification, charger information, lithium battery transport records, and available safety information.", "Confirm the battery chemistry, voltage, capacity, charger input, plug, and destination."),
        ("badge-check", "Compliance Documents", "Available declarations, test reports, certificates, labels, and supporting documents for the supplied configuration.", "Request by exact product model, battery, charger, configuration, and intended market."),
        ("wrench", "Spare Parts Information", "Parts identification and replacement support for supplied equipment.", "Provide the model, serial number, part photos, quantity, and a clear description of the requirement."),
    ]
    group_html = "".join(
        f'<article><span class="resource-icon">{icon(icon_name, 23)}</span><h3>{esc(title)}</h3><p>{esc(copy)}</p><strong>{esc(action)}</strong></article>'
        for icon_name, title, copy, action in groups
    )
    rows = [
        ("Product catalog", "Product family or full range", "English", "Current available edition", "Request"),
        ("Model datasheet", "Exact product model", "English", "Model and revision specific", "Product page / request"),
        ("Operation manual", "Model and supplied configuration", "English", "Confirm before shipment", "Request"),
        ("Safety information", "Product, battery, and charger", "English", "Configuration specific", "Request"),
        ("Compliance package", "Model, battery, charger, and market", "English", "Availability varies", "Request"),
        ("Spare-parts identification", "Model and serial number", "English", "Order specific", "Request"),
    ]
    rows_html = "".join(f'<tr><th scope="row">{esc(document)}</th><td>{esc(applies)}</td><td>{esc(language)}</td><td>{esc(revision)}</td><td>{esc(access)}</td></tr>' for document, applies, language, revision, access in rows)
    checklist = ["Product model", "Requested document type", "Company and contact name", "Destination country or market", "Battery and charger configuration", "Serial number for manuals or parts support", "Preferred language", "Reason for request or project stage"]
    checklist_html = "".join(f'<li>{icon("check", 16)}<span>{esc(item)}</span></li>' for item in checklist)
    body = f"""{banner}
    <section class="resource-intro"><div class="shell resource-answer"><p class="section-kicker">CONTROLLED TECHNICAL INFORMATION</p><h2>Find Product Data And Request Model-Specific Documents</h2><p>Product specifications are published directly on each model page. Revision-controlled manuals, safety information, battery records, compliance documents, and spare-parts information are supplied according to the selected product and configuration.</p><p class="resource-note">A document title alone does not confirm that it applies to every model. LEXYGO verifies the model, battery, charger, supplied configuration, and intended market before releasing a document package.</p>{button('Browse Product Data', '/products/', 'outline')} {button('Request Documents', '/contact/?subject=Document%20request', 'primary', 'file-down')}</div></section>
    <section class="document-groups"><div class="shell">{section_heading('DOCUMENT TYPES', 'Technical Information Available By Product And Configuration')}<div class="document-grid">{group_html}</div></div></section>
    <section class="resource-matrix-section"><div class="shell"><div class="section-heading left"><span>DOCUMENT INDEX</span><h2>Document Availability And Access</h2><p>Use the product page for published parameters and contact LEXYGO for controlled or configuration-specific files.</p></div><div class="table-wrap"><table class="evidence-table download-table"><thead><tr><th>Document</th><th>Applies to</th><th>Language</th><th>Revision basis</th><th>Access</th></tr></thead><tbody>{rows_html}</tbody></table></div></div></section>
    <section class="requirements-section"><div class="shell requirements-grid"><div><p class="section-kicker">REQUEST CHECKLIST</p><h2>Information Needed To Locate The Correct File</h2><p>Providing this information prevents the wrong model, battery, charger, or market document from being used.</p>{button('Send A Document Request', '/contact/?subject=Document%20request', 'primary', 'send')}</div><ul>{checklist_html}</ul></div></section>
    <section class="company-contact-strip"><div class="shell"><div><strong>Need a file for supplier approval or shipment review?</strong><span>Email the model, configuration, destination, and document name to {esc(COMPANY['email'])}.</span></div>{button('Contact LEXYGO', '/contact/', 'primary', 'send')}</div></section>"""
    return page("Downloads & Technical Documents", "Find LEXYGO product data and request model-specific datasheets, manuals, safety information, battery documents, compliance records, and spare-parts support.", "/resources/download/", body, crumb_schema, "resources")


def compliance_page():
    banner, crumb_schema = inner_banner("COMPLIANCE CENTER", [("Home", "/"), ("Resources", "/resources/"), ("Compliance Center", None)])
    documents = [
        ("CE documentation", "Supports review of applicable EU conformity requirements.", "Applicable products and configurations", "Model, configuration, declaration details, and referenced standards"),
        ("ANSI/ITSDF B56.1-2020 test report", "Provides test evidence against the stated powered industrial truck safety standard.", "Applicable powered industrial truck models", "Exact model, tested configuration, report scope, and report issuer"),
        ("UL 583 NRTL Type E certification", "Supports review of the stated electrical and fire-hazard classification for applicable electric industrial trucks.", "Applicable electric industrial truck configurations", "Certification listing, model/configuration coverage, labels, and supplied electrical system"),
        ("UN 38.3 battery documentation", "Supports transport review for applicable lithium battery packs.", "Applicable lithium battery configurations", "Battery model, voltage, capacity, test summary/report, and shipment configuration"),
        ("English operating and safety information", "Provides model-related operating, inspection, charging, and safety guidance.", "Supplied machine, battery, and charger", "Model, serial number when available, language, and document revision"),
    ]
    document_html = "".join(f'<tr><th scope="row">{esc(name)}</th><td>{esc(purpose)}</td><td>{esc(applies)}</td><td>{esc(verify)}</td></tr>' for name, purpose, applies, verify in documents)
    steps = [
        ("01", "Identify The Exact Model", "Use the full model name and intended capacity, lift height, battery, charger, and options."),
        ("02", "State The Destination Market", "Country, end-use environment, importer requirements, and workplace rules may affect the requested package."),
        ("03", "Request The Document List", "Ask which reports, certificates, declarations, manuals, labels, and battery records apply."),
        ("04", "Match Documents To Configuration", "Check model numbers, configuration scope, report references, battery data, and document revision."),
        ("05", "Confirm Before Order Approval", "Record the agreed document package in the quotation, purchase order, or sales contract."),
        ("06", "Retain Shipment Records", "Keep the final documents together with serial, battery, charger, packing, and shipment information."),
    ]
    step_html = "".join(f'<li><span>{number}</span><div><h3>{esc(title)}</h3><p>{esc(copy)}</p></div></li>' for number, title, copy in steps)
    faqs = [
        ("Does every LEXYGO model use the same compliance documents?", "No. The applicable package depends on the product type, exact model, battery, charger, supplied options, destination market, and intended application."),
        ("Can I receive a report before placing an order?", "Send the exact model, configuration, company details, destination market, and the document required for review. Availability and release conditions are confirmed case by case."),
        ("Does a CE document automatically satisfy U.S. requirements?", "No. EU and U.S. requirements are different. The importer, employer, dealer, or project owner should confirm the rules that apply to the destination and workplace."),
        ("What should I verify on a lithium battery document?", "Verify the battery manufacturer and model, voltage, capacity, test reference, document revision, and that the supplied battery configuration matches the document."),
        ("Can OEM branding change the document package?", "Branding, labels, manuals, electrical configuration, battery, charger, forks, mast, and other changes may affect the applicable documents and must be reviewed before approval."),
        ("Who confirms local import and workplace requirements?", "The buyer, importer, dealer, employer, or appointed compliance professional should confirm the laws, customs rules, workplace requirements, and project specifications that apply locally."),
    ]
    faq_html = "".join(f'<details><summary>{esc(question)}{icon("plus", 18)}</summary><p>{esc(answer)}</p></details>' for question, answer in faqs)
    faq_schema = {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]}
    body = f"""{banner}
    <section class="resource-intro"><div class="shell resource-answer"><p class="section-kicker">MODEL-SPECIFIC VERIFICATION</p><h2>What Compliance Information Should A Buyer Request?</h2><p>Request a document list that identifies the exact product model, battery, charger, supplied configuration, destination market, and document revision. The name of a standard or certificate is not enough unless its scope matches the machine being purchased.</p><p class="resource-note">This page explains LEXYGO document handling for buyer review. It is not legal advice and does not replace confirmation of local import, product, workplace, or project requirements.</p>{button('Request A Compliance Package', '/contact/?subject=Compliance%20document%20request', 'primary', 'file-check-2')}</div></section>
    <section class="resource-matrix-section"><div class="shell"><div class="section-heading left"><span>DOCUMENT MATRIX</span><h2>Available Evidence And What To Verify</h2><p>Document availability and applicability are confirmed against the ordered configuration.</p></div><div class="table-wrap"><table class="evidence-table compliance-table"><thead><tr><th>Document</th><th>Purpose</th><th>Typical scope</th><th>Buyer verification</th></tr></thead><tbody>{document_html}</tbody></table></div></div></section>
    <section class="release-section compliance-workflow"><div class="shell release-grid"><div><p class="section-kicker">VERIFICATION PROCESS</p><h2>Six Steps Before Order Approval</h2><p>Use this process to keep the product, supplied configuration, labels, manuals, battery records, and compliance evidence aligned.</p></div><ol>{step_html}</ol></div></section>
    <section class="faq-section"><div class="shell faq-grid"><div><p class="section-kicker">COMPLIANCE FAQ</p><h2>Direct Answers For International Buyers</h2><p>Confirm the final requirements with the destination-market importer, employer, dealer, project owner, or qualified compliance professional.</p></div><div class="faq-list">{faq_html}</div></div></section>
    <section class="company-contact-strip"><div class="shell"><div><strong>Request evidence for a specific model and market</strong><span>Send the model, configuration, battery, charger, and destination to {esc(COMPANY['email'])}.</span></div>{button('Contact Quality Team', '/contact/', 'primary', 'send')}</div></section>"""
    return page("Material Handling Equipment Compliance Center", "Review the LEXYGO model-specific process for CE, ANSI/ITSDF B56.1-2020, UL 583 Type E, UN 38.3, and English safety documents.", "/resources/compliance/", body, [faq_schema, crumb_schema], "resources")


def faq_page():
    banner, crumb_schema = inner_banner("BUYER FAQ", [("Home", "/"), ("Resources", "/resources/"), ("Buyer FAQ", None)])
    groups = [
        ("product-selection", "Product Selection", [
            ("What information is needed to recommend a material handling machine?", "Provide the load weight and dimensions, pallet type, lift height, aisle width, travel distance, floor or terrain condition, daily operating hours, quantity, and destination country."),
            ("What is the difference between a pallet truck and a pallet stacker?", "A pallet truck is mainly used for horizontal pallet movement. A pallet stacker also raises pallets for stacking, racking, loading, or process positioning."),
            ("Can rated capacity be used at every lift height?", "Not automatically. Residual capacity can change with lift height, load center, mast, attachments, and configuration. Confirm the capacity plate and model-specific data for the intended load."),
        ]),
        ("pallets-applications", "Pallets & Applications", [
            ("Why does pallet type matter when selecting a stacker?", "Fork access, pallet bottom-board design, opening direction, and straddle-leg clearance determine whether a standard, straddle, reach, or counterbalanced stacker can enter and support the load."),
            ("Which machine is suitable for closed pallets or loads without fork access underneath?", "A counterbalanced stacker may be suitable because it does not rely on support legs entering beneath the pallet, but capacity, load center, floor, and turning space must still be confirmed."),
            ("Can an indoor pallet truck be used on rough outdoor ground?", "Standard warehouse trucks are intended for prepared surfaces. Uneven ground, slopes, gaps, water, debris, and outdoor travel require a machine designed and configured for those conditions."),
        ]),
        ("battery-charger", "Battery & Charger", [
            ("Should I choose lithium-ion or lead-acid batteries?", "The choice depends on operating hours, charging opportunities, maintenance capability, temperature, cost, charger power, transport requirements, and expected duty cycle."),
            ("What charger information should I provide?", "Provide destination voltage and frequency, plug type, battery chemistry, battery voltage and capacity, charging environment, and any project-specific electrical requirement."),
            ("Are battery transport documents available?", "Applicable lithium battery configurations can be matched with the available transport and safety documentation. Confirm the exact battery model and shipment configuration before booking transport."),
        ]),
        ("oem-documents", "OEM & Documents", [
            ("Can LEXYGO provide OEM or private-label products?", "Logo, color, labels, manuals, packaging, and selected configuration requests can be evaluated by model, quantity, safety requirements, and destination market."),
            ("Which compliance documents are supplied?", "The applicable package depends on the product model, battery, charger, supplied configuration, and destination. Request the exact document list before order approval."),
            ("Can I request English manuals and safety information?", "Yes. Request the manual and safety document list for the selected model and configuration. The final revision should match the supplied machine, battery, and charger."),
        ]),
        ("ordering-shipping", "Ordering, Shipping & Support", [
            ("What should be included in an RFQ?", "Include the model or application, quantity, load, lift height, pallet dimensions, aisle width, terrain, duty cycle, battery, charger, destination, required documents, and OEM requirements."),
            ("Can inspection photos or videos be provided before shipment?", "Agreed photos, operating video, labels, serial information, packing confirmation, and available inspection records can be included in the pre-shipment scope."),
            ("How do I request spare parts or technical support?", "Provide the model, serial number, part photos, operating hours, error information, and a clear description or video of the issue."),
            ("What warranty applies to an order?", "Warranty duration, covered parts, exclusions, responsibilities, and claim conditions are confirmed in the quotation or sales contract for the ordered model and configuration."),
        ]),
    ]
    all_faqs = []
    group_html = []
    for group_id, title, faqs in groups:
        all_faqs.extend(faqs)
        details = "".join(f'<details><summary>{esc(question)}{icon("plus", 18)}</summary><p>{esc(answer)}</p></details>' for question, answer in faqs)
        group_html.append(f'<section class="faq-group" id="{group_id}"><h2>{esc(title)}</h2><div class="faq-list">{details}</div></section>')
    faq_schema = {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in all_faqs]}
    body = f"""{banner}
    <section class="resource-intro"><div class="shell resource-answer"><p class="section-kicker">DIRECT ANSWERS FOR PROFESSIONAL BUYERS</p><h2>Material Handling Equipment Buyer FAQ</h2><p>Find concise answers about equipment selection, pallet compatibility, batteries, chargers, OEM orders, compliance documents, shipping, warranty, and spare-parts support.</p><p class="resource-note">For a final recommendation, provide the exact application, model, configuration, and destination market. General answers do not replace the model-specific quotation and technical confirmation.</p></div></section>
    <section class="faq-library"><div class="shell"><nav class="faq-jump" aria-label="FAQ categories"><a href="#product-selection">Product Selection</a><a href="#pallets-applications">Pallets & Applications</a><a href="#battery-charger">Battery & Charger</a><a href="#oem-documents">OEM & Documents</a><a href="#ordering-shipping">Ordering & Support</a></nav>{''.join(group_html)}</div></section>
    <section class="company-contact-strip"><div class="shell"><div><strong>Need an answer for a specific project?</strong><span>Send the load, lift height, pallet, aisle, terrain, quantity, and destination to {esc(COMPANY['email'])}.</span></div>{button('Ask LEXYGO', '/contact/', 'primary', 'send')}</div></section>"""
    return page("Material Handling Equipment Buyer FAQ", "Answers to common buyer questions about material handling equipment selection, pallets, batteries, chargers, OEM orders, compliance, shipping, warranty, and spare parts.", "/resources/faq/", body, [faq_schema, crumb_schema], "resources")


def cases_page():
    banner, crumb_schema = inner_banner("APPLICATION CASES", [("Home", "/"), ("Resources", "/resources/"), ("Application Cases", None)])
    cases = [
        ("mountain", "Uneven-Ground Pallet Transport", "Outdoor or uneven routes require evaluation of surface condition, slope, gaps, water, debris, load stability, travel distance, and turning space.", "All-terrain electric pallet trucks", "/products/atep3000y/"),
        ("container", "Closed-Pallet And Machine-Side Handling", "Loads without suitable under-clearance may require a counterbalanced configuration instead of support legs beneath the pallet.", "Counterbalanced electric stackers", "/products/wces1000j/"),
        ("between-horizontal-start", "Narrow-Aisle Pallet Stacking", "The selected truck must be checked against pallet orientation, load length, right-angle stacking space, mast height, overhead clearance, and residual capacity.", "Walkie, rider, and reach stackers", "/products/electric-pallet-stackers/"),
        ("move-up", "Ergonomic Workstation Positioning", "Lift table carts raise boxes, components, or materials to a practical working height and reduce repeated low-level handling.", "Manual and electric lift table carts", "/products/warehouse-equipment/"),
    ]
    case_html = "".join(
        f'<article><span class="resource-icon">{icon(icon_name, 23)}</span><p class="case-label">APPLICATION NOTE</p><h3>{esc(title)}</h3><p>{esc(copy)}</p><strong>{esc(equipment)}</strong><a href="{href}">View relevant equipment{icon("arrow-right", 16)}</a></article>'
        for icon_name, title, copy, equipment, href in cases
    )
    fields = ["Country and customer type", "Material and load weight", "Load dimensions and center of gravity", "Pallet type and fork-entry direction", "Required lift height", "Aisle, doorway, and turning dimensions", "Floor, slope, and terrain condition", "Travel distance and daily operating hours", "Selected model and configuration", "Measured result with date and evidence"]
    fields_html = "".join(f'<li>{icon("check", 16)}<span>{esc(item)}</span></li>' for item in fields)
    body = f"""{banner}
    <section class="resource-intro"><div class="shell resource-answer"><p class="section-kicker">APPLICATION-LED SELECTION</p><h2>Match Working Conditions To The Right Equipment Family</h2><p>These application notes show the information that should be checked before recommending a pallet truck, stacker, forklift, or lift table. They are technical selection examples, not invented customer success claims.</p><p class="resource-note">Customer-specific results are published only when the application, selected configuration, outcome, and supporting evidence have been verified.</p></div></section>
    <section class="application-notes"><div class="shell">{section_heading('APPLICATION NOTES', 'Common Material Handling Scenarios', 'Use these starting points to identify the product family, then confirm the exact model and configuration.')}<div class="application-grid">{case_html}</div></div></section>
    <section class="requirements-section"><div class="shell requirements-grid"><div><p class="section-kicker">CASE EVIDENCE</p><h2>Information Required For A Verifiable Case Study</h2><p>This evidence keeps future customer cases useful to professional buyers and prevents unsupported performance claims.</p>{button('Discuss Your Application', '/contact/?subject=Application%20review', 'primary', 'send')}</div><ul>{fields_html}</ul></div></section>
    <section class="company-contact-strip"><div class="shell"><div><strong>Need a recommendation for your working conditions?</strong><span>Send photos, load data, pallet details, dimensions, terrain, duty cycle, and destination to {esc(COMPANY['email'])}.</span></div>{button('Request Application Review', '/contact/', 'primary', 'send')}</div></section>"""
    return page("Material Handling Equipment Application Cases", "Review LEXYGO application notes for uneven-ground pallet transport, closed pallets, narrow-aisle stacking, and ergonomic workstation positioning.", "/resources/cases/", body, crumb_schema, "resources")


GUIDE_CONTENT = {
    "how-to-choose-an-electric-pallet-truck": {
        "answer": "Choose an electric pallet truck by matching rated load, pallet entry, travel distance, floor or terrain, slope, turning space, duty cycle, battery, charger, and operator position. Do not select by capacity alone; the complete route and operating pattern determine the suitable model.",
        "rows": [
            ("Load", "Maximum load weight, dimensions, center of gravity, and stability", "Rated capacity must cover the real load and application"),
            ("Pallet", "Fork entry, opening direction, bottom boards, fork spacing, and lowered height", "The forks and wheels must enter and support the pallet correctly"),
            ("Route", "Distance, turning areas, doorways, ramps, dock plates, and traffic", "Long routes may justify a rider platform or higher-capacity battery"),
            ("Surface", "Flat indoor floor, uneven ground, gaps, debris, water, and outdoor exposure", "Use equipment designed for the actual surface and environment"),
            ("Duty cycle", "Loads per hour, shifts, travel time, charging windows, and temperature", "Battery capacity and charging method must support the work pattern"),
            ("Destination", "Voltage, frequency, plug, language, documents, and local requirements", "Confirm the supplied charger and document package before ordering"),
        ],
        "checklist": ["Maximum load weight and dimensions", "Pallet type and fork-entry direction", "Fork width, length, and lowered height", "One-way and round-trip travel distance", "Aisle, doorway, and turning dimensions", "Slope and floor or terrain condition", "Loads per hour and shifts per day", "Battery and charger preference", "Operator position: walkie or rider", "Destination country and required documents"],
        "faqs": [
            ("When should I choose a rider pallet truck?", "A rider model may be appropriate when travel distances, operating frequency, and throughput make repeated walk-behind travel inefficient. Confirm route safety, turning space, operator training, and local workplace rules."),
            ("Can I use a warehouse pallet truck outdoors?", "Only when the selected machine and configuration are suitable for the actual surface, slope, weather exposure, gaps, and debris. Standard indoor trucks are intended for prepared floors."),
            ("How do I choose fork dimensions?", "Match fork length, overall fork width, individual fork width, lowered height, and wheel position to the pallet openings and support boards."),
            ("What battery information should I compare?", "Compare chemistry, voltage, capacity, charging time, charger input, opportunity charging, temperature, maintenance, and the required transport documents."),
        ],
        "links": [("Electric Pallet Trucks", "/products/electric-pallet-trucks/"), ("All-Terrain ATEP3000Y", "/products/atep3000y/"), ("Request Selection Support", "/contact/?subject=Pallet%20truck%20selection")],
    },
    "pallet-truck-vs-stacker": {
        "answer": "Use a pallet truck when the main task is horizontal pallet transport at low lift height. Use a pallet stacker when the task includes raising pallets for racking, stacking, loading, unloading, or process positioning. Pallet construction and available fork access can determine which stacker design is suitable.",
        "rows": [
            ("Primary task", "Horizontal pallet movement", "Pallet movement plus vertical lifting and stacking"),
            ("Typical lift", "Low lift for floor transport", "Mast lift for stacking or elevated placement"),
            ("Pallet compatibility", "Requires suitable fork entry", "Also depends on support legs, straddle clearance, reach, or counterbalance design"),
            ("Selection dimensions", "Forks, lowered height, turning radius, route", "Forks, mast height, lift height, aisle, overhead clearance, residual capacity"),
            ("Common types", "Walkie, rider, all-terrain", "Walkie, rider, reach, straddle, counterbalanced"),
            ("Typical use", "Truck loading areas, staging, short or long horizontal routes", "Warehouse racking, production, closed pallets, machine-side handling"),
        ],
        "checklist": ["Is the task transport only or does it include stacking?", "What is the maximum load and load center?", "Is the pallet open or closed underneath?", "Can support legs enter below or around the pallet?", "What lift height and overhead clearance are available?", "What aisle and right-angle stacking space are available?", "How far and how often will the machine travel?", "Is the floor level, smooth, and suitable for the selected truck?"],
        "faqs": [
            ("Can a pallet truck place loads in racking?", "A standard low-lift pallet truck is not designed to raise pallets to rack levels. Use a suitable stacker or forklift for elevated placement."),
            ("Why can closed pallets be difficult for a standard stacker?", "Support legs or wheel arms may need to enter beneath or around the pallet. Closed bottom boards can block that path, so a counterbalanced or other suitable configuration may be required."),
            ("Is a stacker a replacement for every forklift task?", "No. Capacity, lift height, residual capacity, load center, aisle, travel speed, floor, attachments, operator position, and duty cycle must be matched to the application."),
            ("Which product information should I send for selection?", "Send pallet photos and dimensions, fork-entry direction, load weight and dimensions, lift height, aisle, route, floor, duty cycle, quantity, and destination."),
        ],
        "links": [("Electric Pallet Trucks", "/products/electric-pallet-trucks/"), ("Electric Pallet Stackers", "/products/electric-pallet-stackers/"), ("Request An Application Review", "/contact/?subject=Truck%20or%20stacker%20selection")],
    },
    "forklift-capacity-and-aisle-width": {
        "answer": "Forklift selection requires more than nominal capacity. Confirm the real load weight, load center, load dimensions, required lift height, residual capacity, mast and attachment configuration, truck dimensions, turning radius, aisle layout, overhead clearance, floor, slope, and duty cycle.",
        "rows": [
            ("Rated capacity", "Capacity under the stated reference conditions", "Do not assume it applies to every lift height, load center, or attachment"),
            ("Load center", "Distance from the fork face to the load center of gravity", "Long or uneven loads can increase the load moment"),
            ("Lift height", "Maximum required fork height", "Higher lifts may reduce available capacity and affect mast choice"),
            ("Residual capacity", "Permitted load for the actual height and configuration", "Confirm using model-specific data and the truck capacity plate"),
            ("Aisle width", "Working space for approach, turning, load, and clearance", "Use the real pallet/load dimensions and site layout"),
            ("Mast and overhead", "Lowered mast, raised mast, free lift, guard, doorway, and ceiling", "Verify all vertical clearances along the route"),
            ("Floor and grade", "Surface strength, levelness, traction, gaps, ramps, and slopes", "Affects stability, traction, braking, tires, and safe operation"),
        ],
        "checklist": ["Maximum load weight and dimensions", "Load center and center-of-gravity position", "Required lift and placement height", "Required residual capacity at height", "Pallet orientation and fork dimensions", "Aisle and right-angle stacking dimensions", "Doorway, container, ceiling, and overhead clearance", "Attachments and side-shift requirements", "Floor loading, surface, slope, and tire requirement", "Daily hours, travel distance, charging, and destination requirements"],
        "faqs": [
            ("Why can available capacity decrease at greater lift height?", "Higher lift, changed load center, mast configuration, and attachments can change the truck's permitted capacity. Use model-specific residual-capacity data and the capacity plate."),
            ("Is turning radius the same as required aisle width?", "No. Aisle selection also considers the truck, load, pallet, approach angle, clearances, and operating method. Check the complete site layout."),
            ("Do attachments affect forklift selection?", "They can add weight, change load center, reduce capacity, and change dimensions. Include the intended attachment in the technical review."),
            ("What site measurements should I provide?", "Provide aisle width, rack face-to-face distance, pallet orientation, load length, doorway dimensions, overhead restrictions, floor condition, slopes, and turning areas."),
        ],
        "links": [("Electric Forklifts", "/products/electric-forklifts/"), ("Electric Pallet Stackers", "/products/electric-pallet-stackers/"), ("Request Capacity Review", "/contact/?subject=Forklift%20capacity%20review")],
    },
}


def guides_page():
    banner, crumb_schema = inner_banner("BUYER GUIDES", [("Home", "/"), ("Resources", "/resources/"), ("Buyer Guides", None)])
    cards = []
    for guide in GUIDES:
        cards.append(f'''<article><p class="guide-type">SELECTION GUIDE</p><h2><a href="/guides/{guide['slug']}/">{esc(guide['title'])}</a></h2><p>{esc(guide['summary'])}</p><div><span>Reviewed by LEXYGO Technical Team</span><span>Updated 2026-10-07</span></div><a class="guide-link" href="/guides/{guide['slug']}/">Read guide{icon("arrow-right", 16)}</a></article>''')
    questions = ["What must the machine move or lift?", "What is the maximum load and load center?", "Which pallet or load-support structure is used?", "What route, aisle, doorway, and overhead space are available?", "What floor, slope, terrain, and environment are involved?", "How often and how long will the machine operate?", "Which battery, charger, documents, and market requirements apply?"]
    question_html = "".join(f'<li>{icon("check", 16)}<span>{esc(item)}</span></li>' for item in questions)
    collection_schema = {"@type": "CollectionPage", "name": "LEXYGO Material Handling Equipment Buyer Guides", "url": route_url("/guides/"), "description": "Selection guides for pallet trucks, pallet stackers, and electric forklifts."}
    body = f"""{banner}
    <section class="resource-intro"><div class="shell resource-answer"><p class="section-kicker">PRACTICAL EQUIPMENT SELECTION</p><h2>Choose By Application, Not By Model Name Alone</h2><p>These guides provide a direct answer, comparison tables, measurement checklists, common selection risks, and links to relevant LEXYGO product families.</p><p class="resource-note">A guide supports initial comparison. Final selection requires model-specific capacity, configuration, application, document, and destination-market confirmation.</p></div></section>
    <section class="buyer-guides"><div class="shell"><div class="guide-grid">{''.join(cards)}</div></div></section>
    <section class="requirements-section"><div class="shell requirements-grid"><div><p class="section-kicker">SELECTION INPUTS</p><h2>Seven Questions To Answer Before Comparing Models</h2><p>These inputs make the recommendation more accurate and reduce repeated clarification during quotation.</p>{button('Request Selection Support', '/contact/?subject=Product%20selection', 'primary', 'send')}</div><ul>{question_html}</ul></div></section>
    <section class="company-contact-strip"><div class="shell"><div><strong>Need help turning site conditions into a product shortlist?</strong><span>Send the load, pallet, route, lift height, dimensions, duty cycle, and destination to {esc(COMPANY['email'])}.</span></div>{button('Contact LEXYGO', '/contact/', 'primary', 'send')}</div></section>"""
    return page("Material Handling Equipment Buyer Guides", "Use LEXYGO buyer guides to compare pallet trucks, pallet stackers, and electric forklifts by load, pallet, lift height, aisle, terrain, battery, and duty cycle.", "/guides/", body, [collection_schema, crumb_schema], "resources")


def buyer_guide_page(guide):
    content = GUIDE_CONTENT[guide["slug"]]
    route = f'/guides/{guide["slug"]}/'
    banner, crumb_schema = inner_banner(guide["title"].upper(), [("Home", "/"), ("Resources", "/resources/"), ("Buyer Guides", "/guides/"), (guide["title"], None)])
    rows_html = "".join(f'<tr><th scope="row">{esc(factor)}</th><td>{esc(check)}</td><td>{esc(reason)}</td></tr>' for factor, check, reason in content["rows"])
    checklist_html = "".join(f'<li>{icon("check", 16)}<span>{esc(item)}</span></li>' for item in content["checklist"])
    faq_html = "".join(f'<details><summary>{esc(question)}{icon("plus", 18)}</summary><p>{esc(answer)}</p></details>' for question, answer in content["faqs"])
    related_html = "".join(f'<a href="{href}"><span>{esc(label)}</span>{icon("arrow-up-right", 17)}</a>' for label, href in content["links"])
    article_schema = {
        "@type": "TechArticle",
        "headline": guide["title"],
        "description": guide["summary"],
        "datePublished": "2026-10-07",
        "dateModified": "2026-10-07",
        "author": {"@type": "Organization", "name": "LEXYGO Technical Team"},
        "publisher": {"@type": "Organization", "name": COMPANY["display_name"], "url": BASE_URL},
        "mainEntityOfPage": route_url(route),
    }
    faq_schema = {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in content["faqs"]]}
    body = f"""{banner}
    <article class="guide-article"><section class="guide-answer"><div class="shell"><p class="section-kicker">DIRECT ANSWER</p><h2>{esc(guide['title'])}</h2><p class="answer-lead">{esc(content['answer'])}</p><div class="article-meta"><span>Reviewed by LEXYGO Technical Team</span><span>Last reviewed: 2026-10-07</span></div></div></section>
    <section class="guide-table-section"><div class="shell"><div class="section-heading left"><span>DECISION TABLE</span><h2>Factors To Check Before Selecting A Model</h2><p>Use the actual load and site conditions rather than nominal capacity alone.</p></div><div class="table-wrap"><table class="evidence-table guide-table"><thead><tr><th>Selection factor</th><th>What to check</th><th>Why it matters</th></tr></thead><tbody>{rows_html}</tbody></table></div></div></section>
    <section class="guide-checklist"><div class="shell guide-checklist-grid"><div><p class="section-kicker">BUYER CHECKLIST</p><h2>Information To Include In Your Inquiry</h2><p>Photos, dimensioned layouts, pallet details, and a short operating video can make the selection review more accurate.</p>{button('Send Application Details', '/contact/?subject=Technical%20selection%20review', 'primary', 'send')}</div><ul>{checklist_html}</ul></div></section>
    <section class="guide-related"><div class="shell resource-question-grid"><div><p class="section-kicker">NEXT STEP</p><h2>Relevant Products And Support</h2><p>Open the product family for model parameters or send the complete application for a technical comparison.</p></div><div class="question-links">{related_html}</div></div></section>
    <section class="faq-section"><div class="shell faq-grid"><div><p class="section-kicker">GUIDE FAQ</p><h2>Questions Buyers Often Ask</h2><p>The final answer depends on the selected model, load, site, configuration, and destination requirements.</p></div><div class="faq-list">{faq_html}</div></div></section></article>
    <section class="company-contact-strip"><div class="shell"><div><strong>Request a model comparison for your application</strong><span>Send the load, pallet, lift height, route, site dimensions, duty cycle, and destination to {esc(COMPANY['email'])}.</span></div>{button('Ask The Technical Team', '/contact/', 'primary', 'send')}</div></section>"""
    return page(guide["title"], guide["summary"], route, body, [article_schema, faq_schema, crumb_schema], "resources")


def blogs_page():
    return blank_page("/blogs/", "Blogs", active="blogs")


def contact_page():
    banner, crumb_schema = inner_banner("CONTACT US", [("Home", "/"), ("Contact Us", None)])
    body = f"""{banner}<section class="contact-page"><div class="shell contact-page-grid"><div><p class="section-kicker">CONTACT DETAILS</p><h2>Contact LEXYGO</h2><dl class="contact-details"><div><dt>Business name</dt><dd>{esc(COMPANY['display_name'])}</dd></div><div><dt>Legal entity</dt><dd>{esc(COMPANY['legal_name'])}</dd></div><div><dt>Address</dt><dd>{esc(COMPANY['address'])}</dd></div><div><dt>Telephone</dt><dd><a href="tel:{esc(COMPANY['telephone_href'])}">{esc(COMPANY['telephone'])}</a></dd></div><div><dt>WhatsApp</dt><dd><a href="https://wa.me/{esc(COMPANY['whatsapp_href'])}">{esc(COMPANY['whatsapp'])}</a></dd></div><div><dt>Email</dt><dd><a href="mailto:{esc(COMPANY['email'])}">{esc(COMPANY['email'])}</a></dd></div><div><dt>Website</dt><dd><a href="{esc(COMPANY['domain'])}">{esc(COMPANY['website'])}</a></dd></div></dl></div>{inquiry_form()}</div></section>"""
    return page("Contact Us", "Contact LEXYGO for material handling product and configuration inquiries.", "/contact/", body, crumb_schema, "contact")


def not_found_page():
    banner, _ = inner_banner("PAGE NOT FOUND", [("Home", "/"), ("404", None)])
    return page("Page Not Found", "The requested page was not found.", "/404/", f'{banner}<section class="blank-page"><div class="shell"><h2>Page not found</h2>{button("View Products", "/products/")}</div></section>')


def find_source_file(name):
    matches = [path for path in SOURCE_ROOT.rglob("*") if path.is_file() and path.name.lower() == name.lower()]
    if not matches:
        raise FileNotFoundError(name)
    return matches[0]


def copy_product_assets():
    PRODUCT_ASSETS.mkdir(parents=True, exist_ok=True)
    explicit = {
        "r4efl12t.png": find_source_file("REEF12T.png"),
        "qes15lion.png": find_source_file("QES15LION.png"),
    }
    for item in PRODUCTS:
        source = explicit[item["image"]] if item["image"] in explicit else find_source_file(item["image"])
        if not source.exists():
            raise FileNotFoundError(source)
        shutil.copy2(source, PRODUCT_ASSETS / item["image"])
    shutil.copy2(PRODUCT_ASSETS / "efl2000r3.png", ASSETS / "og-cover.png")


CSS = r"""
:root{--green:#0a6763;--green-dark:#074d4b;--orange:#ef7d25;--ink:#242a2d;--muted:#687277;--line:#d9dfe1;--soft:#f5f6f6;--white:#fff;--max:1200px}*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;color:var(--ink);font-family:Arial,"Helvetica Neue",sans-serif;line-height:1.6;background:#fff}img{display:block;max-width:100%}a{color:inherit;text-decoration:none}button,input,textarea{font:inherit}h1,h2,h3,p{overflow-wrap:anywhere;letter-spacing:0}.shell{width:min(calc(100% - 40px),var(--max));margin-inline:auto}.skip-link{position:fixed;left:8px;top:8px;z-index:1000;transform:translateY(-150%);background:#fff;padding:8px}.skip-link:focus{transform:none}.sr-only{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}
.top-strip{background:#293033;color:#cbd2d4;font-size:12px}.top-strip .shell{height:34px;display:flex;align-items:center;justify-content:space-between;gap:28px}.top-contact{display:flex;align-items:center;gap:22px}.top-contact>a{white-space:nowrap}.top-social{display:flex;align-items:center;gap:5px;padding-left:12px;border-left:1px solid rgba(255,255,255,.28)}.top-social a{width:24px;height:24px;display:grid;place-items:center;border-radius:3px;color:#fff;transition:transform .15s,filter .15s}.top-social a:hover,.top-social a:focus-visible{color:#fff;filter:brightness(1.18);transform:translateY(-1px)}.top-social .social-facebook{background:#1877f2}.top-social .social-linkedin{background:#0a66c2}.top-social .social-youtube{background:#f00}.top-social .social-instagram{background:linear-gradient(135deg,#833ab4,#fd1d1d 55%,#fcb045)}.site-header{position:sticky;top:0;z-index:80;background:#fff;border-bottom:1px solid var(--line)}.nav-row{height:82px;display:flex;align-items:center;justify-content:space-between;gap:35px}.brand{display:flex;flex-direction:column;line-height:1;min-width:180px}.brand strong{font-size:31px;color:var(--green-dark);font-weight:900}.brand small{font-size:10px;color:#555;margin-top:6px}.main-nav{height:100%;display:flex;align-items:stretch}.main-nav>a,.nav-group>a{position:relative;display:flex;align-items:center;gap:4px;padding:0 15px;font-size:14px;font-weight:700}.main-nav>a:after,.nav-group>a:after{content:"";position:absolute;left:15px;right:15px;bottom:0;height:3px;background:var(--orange);transform:scaleX(0);transition:.2s}.main-nav>a:hover,.nav-group:hover>a,.main-nav .active{color:var(--green)}.main-nav>a:hover:after,.nav-group:hover>a:after,.main-nav .active:after{transform:scaleX(1)}.nav-group{position:relative;display:flex}.dropdown{display:none;position:absolute;top:100%;left:0;min-width:220px;background:#fff;border-top:3px solid var(--orange);box-shadow:0 12px 28px rgba(0,0,0,.14);padding:8px 0}.dropdown a{display:block;padding:9px 15px;font-size:13px;border-bottom:1px solid #edf0f1}.dropdown a:hover{background:var(--soft);color:var(--green)}.nav-group:hover .dropdown{display:block}.wide-dropdown{min-width:270px}.menu-button{display:none;width:42px;height:42px;border:0;background:transparent;color:var(--ink)}
.hero{min-height:540px;background:linear-gradient(100deg,#074d4b 0%,#0a6763 58%,#e8f2f1 58%,#f6f8f8 100%);overflow:hidden}.hero-grid{min-height:540px;display:grid;grid-template-columns:1fr 1fr;align-items:center}.hero-copy{position:relative;z-index:2;color:#fff;padding:65px 30px 65px 0}.hero-copy>p:first-child{font-size:13px;font-weight:800;color:#bfe1de}.hero h1{font-size:50px;line-height:1.08;margin:12px 0 18px;max-width:640px}.hero-intro{font-size:18px;max-width:570px;color:#e7f1f0}.hero-machine{align-self:stretch;display:grid;place-items:center;padding:35px 0 35px 30px}.hero-machine img{width:116%;max-width:none;height:470px;object-fit:contain;filter:drop-shadow(0 24px 20px rgba(0,0,0,.18))}.button{display:inline-flex;align-items:center;justify-content:center;gap:8px;min-height:44px;padding:10px 18px;margin:10px 8px 0 0;border:1px solid transparent;font-size:13px;font-weight:800;text-transform:uppercase}.button-primary{background:var(--orange);color:#fff}.button-primary:hover{background:#d9650f}.button-light{background:#fff;color:var(--green-dark)}.button-outline{border-color:var(--green);color:var(--green);background:#fff}.button-outline:hover{background:var(--green);color:#fff}
.home-section{padding:70px 0}.section-heading{text-align:center;max-width:760px;margin:0 auto 36px}.section-heading span,.section-kicker{display:block;margin-bottom:7px;color:var(--orange);font-size:12px;font-weight:900;text-transform:uppercase}.section-heading h2,.about-grid h2,.contact-band h2,.detail-inquiry h2,.contact-page h2,.company-profile h2{font-size:32px;line-height:1.2;margin:0}.section-heading p{color:var(--muted);margin:12px auto 0}.featured-section{background:#fff}.featured-grid{display:grid;grid-template-columns:1.2fr .8fr;gap:18px}.featured-grid>.product-card{height:100%}.featured-grid>.product-card .product-image{height:410px}.featured-stack{display:grid;grid-template-columns:1fr;gap:18px}.featured-stack .product-card{display:grid;grid-template-columns:190px 1fr}.featured-stack .product-image{height:100%;min-height:160px}.featured-stack .product-card-copy{padding:16px}.featured-stack .product-card-copy ul{display:none}.center-action{text-align:center;margin-top:28px}.solutions-section{background:var(--soft)}.solution-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:18px}.solution-card{position:relative;height:285px;background:#fff;overflow:hidden}.solution-card img{width:100%;height:100%;object-fit:contain;padding:22px;transition:.25s}.solution-card span{position:absolute;left:0;right:0;bottom:0;padding:14px;background:rgba(7,77,75,.94);color:#fff;font-size:16px;font-weight:800}.solution-card:hover img{transform:scale(1.04)}.about-band{padding:0;background:#fff}.about-grid{display:grid;grid-template-columns:1fr 1fr;min-height:430px;align-items:center}.about-grid>div:first-child{padding:60px 60px 60px 0}.about-grid p{color:var(--muted)}.about-photo{align-self:stretch;background:#eef3f3;display:grid;place-items:center;overflow:hidden}.about-photo img{width:88%;height:390px;object-fit:contain}.factory-stats{background:var(--green-dark);color:#fff}.stats-grid{display:grid;grid-template-columns:repeat(4,1fr)}.stats-grid div{min-height:130px;display:flex;flex-direction:column;align-items:center;justify-content:center;border-right:1px solid rgba(255,255,255,.18)}.stats-grid div:last-child{border:0}.stats-grid strong{min-height:35px;font-size:30px}.stats-grid span{font-size:13px;color:#cce1df}.why-section{background:#fff}.why-grid{display:grid;grid-template-columns:repeat(3,1fr);border-top:1px solid var(--line);border-left:1px solid var(--line)}.why-grid article{padding:30px;border-right:1px solid var(--line);border-bottom:1px solid var(--line)}.why-grid article>span{font-size:30px;font-weight:900;color:#bdd2d1}.why-grid h3{font-size:19px;margin:14px 0 8px}.why-grid p{margin:0;color:var(--muted);font-size:14px}.showroom-section{background:var(--soft)}.blank-media{height:380px;border:1px solid var(--line);background:#fff}.cases-section{background:#fff}.blank-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:22px}.blank-grid.three{grid-template-columns:repeat(3,1fr)}.blank-grid article{height:260px;border:1px solid var(--line);background:var(--soft)}.insights-section{background:#fff}.contact-band{padding:65px 0;background:#eef3f3}.contact-band-grid,.detail-inquiry-grid{display:grid;grid-template-columns:.75fr 1.25fr;gap:65px;align-items:start}.contact-band-grid>div>p:not(.section-kicker),.detail-inquiry-grid>div>p:not(.section-kicker){color:var(--muted)}
.inner-banner{height:235px;display:grid;align-items:center;background:linear-gradient(rgba(7,55,54,.82),rgba(7,55,54,.82)),url('/assets/og-cover.png') center 58%/cover no-repeat;color:#fff;text-align:center}.inner-banner h1{font-size:38px;margin:0;text-transform:uppercase}.breadcrumbs{height:48px;display:flex;align-items:center;gap:6px;color:var(--muted);font-size:12px;border-bottom:1px solid var(--line)}.breadcrumbs a:hover{color:var(--orange)}.catalog-layout-section{padding:52px 0 75px}.catalog-layout{display:grid;grid-template-columns:260px minmax(0,1fr);gap:36px}.catalog-sidebar{min-width:0}.side-box{border:1px solid var(--line);margin-bottom:28px}.side-box>h2{margin:0;padding:13px 15px;background:var(--green);color:#fff;font-size:14px}.category-menu,.site-footer ul{margin:0;padding:0;list-style:none}.category-menu li+li{border-top:1px solid var(--line)}.category-menu a{display:flex;justify-content:space-between;gap:10px;padding:11px 13px;font-size:13px}.category-menu a:hover{color:var(--green);background:var(--soft)}.category-menu span{color:#999}.inquiry-box .compact-form{padding:15px}.catalog-title{border-bottom:1px solid var(--line);padding-bottom:18px;margin-bottom:25px}.catalog-title>p:first-child{margin:0 0 4px;color:var(--orange);font-size:12px;font-weight:900}.catalog-title h2{font-size:29px;margin:0 0 8px}.catalog-title>p:last-child{margin:0;color:var(--muted)}.category-answer{padding:15px 18px;margin:-5px 0 25px;background:var(--soft);border-left:4px solid var(--orange)}.category-answer strong{font-size:13px}.category-answer p{margin:3px 0 0;color:var(--muted);font-size:13px}.product-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:22px}.product-grid.four{grid-template-columns:repeat(4,minmax(0,1fr))}.product-card{min-width:0;background:#fff;border:1px solid var(--line);transition:.2s}.product-card:hover{box-shadow:0 10px 28px rgba(0,0,0,.09);transform:translateY(-2px)}.product-image{position:relative;height:225px;display:grid;place-items:center;overflow:hidden;background:#f7f8f8;padding:17px}.product-image img{width:100%;height:100%;object-fit:contain}.product-card-copy{padding:17px}.model-code{margin:0 0 4px;color:var(--green);font-size:12px;font-weight:900}.product-card h3{font-size:16px;line-height:1.35;margin:0 0 13px;min-height:44px}.product-card h3 a:hover{color:var(--green)}.product-card ul{margin:0 0 14px;padding:0;list-style:none;border-top:1px solid var(--line)}.product-card li{display:flex;justify-content:space-between;gap:8px;padding:6px 0;border-bottom:1px solid var(--line);font-size:11px}.product-card li span{color:var(--muted)}.product-card li strong{text-align:right}.card-actions{display:flex;justify-content:space-between;gap:15px}.card-actions a{color:var(--green);font-size:12px;font-weight:800}.card-actions a:first-child{color:var(--orange)}
.product-intro{padding:55px 0}.product-intro-grid{display:grid;grid-template-columns:1.05fr .95fr;gap:55px;align-items:center}.product-gallery{border:1px solid var(--line);background:#f7f8f8}.product-gallery .product-image{height:460px}.product-summary h2{font-size:33px;line-height:1.2;margin:6px 0 14px}.product-summary>p{color:var(--muted)}.feature-list{margin:22px 0;padding:0;list-style:none;border-top:1px solid var(--line)}.feature-list li{display:flex;justify-content:space-between;gap:20px;padding:9px 0;border-bottom:1px solid var(--line);font-size:13px}.feature-list span{color:var(--muted)}.feature-list strong{text-align:right}.availability{display:grid;grid-template-columns:1fr 1fr;margin:18px 0 6px}.availability div{border-left:3px solid var(--line);padding:4px 11px}.availability dt{font-size:11px;color:var(--muted)}.availability dd{min-height:22px;margin:2px 0 0}.product-identity{display:flex;gap:25px;margin-top:19px;font-size:12px;color:var(--muted)}.product-description{padding:55px 0;background:#fff}.tab-heading{border-bottom:2px solid var(--green);margin-bottom:25px}.tab-heading span{display:inline-block;padding:11px 18px;background:var(--green);color:#fff;font-weight:800}.description-grid{display:grid;grid-template-columns:1fr 1fr;gap:55px}.description-grid h2{font-size:25px;margin-top:0}.description-grid p{color:var(--muted)}.quick-table table{min-width:0}.parameter-section{padding:55px 0;background:var(--soft)}.spec-group{margin-bottom:25px}.spec-group h3{font-size:15px;margin:0;padding:11px 13px;background:var(--green-dark);color:#fff}.table-wrap{overflow-x:auto;background:#fff}table{width:100%;border-collapse:collapse;min-width:680px}th,td{padding:9px 12px;text-align:left;border:1px solid var(--line);font-size:12px}thead th{background:#e7ecec}.spec-empty{height:180px;background:#fff;border:1px solid var(--line)}.detail-inquiry{padding:60px 0;background:#eef3f3}.related-section{padding:65px 0}.related-section .product-image{height:180px}.related-section .product-card h3{font-size:14px}
.inquiry-form{background:#fff;border-top:4px solid var(--orange);padding:24px}.form-grid{display:grid;grid-template-columns:1fr 1fr;gap:13px}.form-grid label{font-size:11px;font-weight:700}.form-grid label span{display:block}.form-grid .full{grid-column:1/-1}.form-grid input,.form-grid textarea{width:100%;margin-top:4px;border:1px solid #bdc6c8;background:#fff;padding:9px;min-height:40px}.compact-form{border-top:0}.compact-form .form-grid{grid-template-columns:1fr}.compact-form .full{grid-column:auto}.compact-form .button{width:100%;margin-right:0}.company-profile,.contact-page,.blank-page{padding:65px 0}.profile-grid{display:grid;grid-template-columns:1fr 1fr;gap:60px;align-items:center}.profile-grid p{color:var(--muted)}.company-machine{height:390px;background:var(--soft);display:grid;place-items:center}.company-machine img{width:90%;height:90%;object-fit:contain}.contact-page-grid{display:grid;grid-template-columns:.75fr 1.25fr;gap:60px}.contact-details{margin:25px 0 0}.contact-details div{padding:11px 0;border-top:1px solid var(--line)}.contact-details dt{font-size:11px;color:var(--muted)}.contact-details dd{margin:3px 0 0;font-weight:700}.blank-page h2{font-size:29px;margin:0 0 22px}.blank-content{height:330px;border:1px solid var(--line);background:var(--soft)}
.site-footer{background:#222a2d;color:#bfc8ca;padding-top:55px}.footer-grid{display:grid;grid-template-columns:1.2fr .8fr 1.2fr 1fr;gap:45px}.site-footer h2{font-size:14px;color:#fff;margin:0 0 20px}.site-footer p,.site-footer li,.contact-list{font-size:12px}.site-footer li{margin:8px 0}.site-footer a:hover{color:#fff}.contact-list{margin:0}.contact-list div{margin-bottom:10px}.contact-list dt{color:#879598}.contact-list dd{margin:2px 0 0;min-height:19px}.newsletter{display:flex}.newsletter input{width:100%;height:42px;border:0;padding:8px}.newsletter button{width:45px;border:0;background:var(--orange);color:#fff}.footer-bottom{margin-top:45px;border-top:1px solid #3b4549}.footer-bottom .shell{min-height:58px;display:flex;align-items:center;justify-content:space-between;gap:20px;font-size:11px;color:#869397}
.source-brochure img{position:absolute;inset:0;width:100%;height:100%;max-width:none;object-fit:contain;transform:scale(3.2);transform-origin:75% 18%}.source-brochure-highlift img{transform:scale(2.6);transform-origin:85% 28%}.source-brochure-two-stage img{transform-origin:85% 28%}
@media(max-width:1050px){.main-nav{display:none;position:absolute;top:100%;left:0;right:0;height:auto;max-height:calc(100vh - 100px);overflow:auto;background:#fff;box-shadow:0 12px 25px rgba(0,0,0,.13);padding:10px 20px;align-items:stretch;flex-direction:column}.main-nav.is-open{display:flex}.main-nav>a,.nav-group>a{min-height:44px;padding:9px 5px}.nav-group{display:block}.nav-group:hover .dropdown{display:none}.dropdown{position:static;box-shadow:none;border-top:0;padding:0 0 5px 15px}.nav-group.is-open .dropdown{display:block}.menu-button{display:block}.hero h1{font-size:43px}.product-grid{grid-template-columns:repeat(2,1fr)}.product-grid.four{grid-template-columns:repeat(2,1fr)}.solution-grid{grid-template-columns:repeat(2,1fr)}.footer-grid{grid-template-columns:1fr 1fr}}
@media(max-width:760px){.shell{width:min(calc(100% - 28px),var(--max))}.top-strip{display:block}.top-strip .shell{width:100%;height:36px;padding:0 10px}.top-location{display:none}.top-contact{width:100%;justify-content:space-between;gap:6px}.top-contact>a{font-size:10px}.top-social{gap:3px;padding-left:0;border-left:0}.top-social a{width:23px;height:23px}.nav-row{height:68px}.brand strong{font-size:26px}.brand small{font-size:8px}.hero{min-height:0;background:linear-gradient(160deg,var(--green-dark) 0 63%,#edf3f2 63%)}.hero-grid{min-height:0;grid-template-columns:1fr}.hero-copy{padding:45px 0 22px}.hero h1{font-size:37px}.hero-machine{height:285px;padding:0}.hero-machine img{height:300px;width:100%}.home-section{padding:52px 0}.section-heading h2,.about-grid h2,.contact-band h2,.detail-inquiry h2,.company-profile h2,.contact-page h2{font-size:27px}.featured-grid{grid-template-columns:1fr}.featured-grid>.product-card .product-image{height:280px}.featured-stack .product-card{grid-template-columns:130px 1fr}.solution-grid{grid-template-columns:1fr 1fr}.solution-card{height:220px}.about-grid,.profile-grid{grid-template-columns:1fr}.about-grid>div:first-child{padding:45px 0}.about-photo,.company-machine{height:320px}.stats-grid{grid-template-columns:1fr 1fr}.stats-grid div:nth-child(2){border-right:0}.stats-grid div:nth-child(-n+2){border-bottom:1px solid rgba(255,255,255,.18)}.why-grid{grid-template-columns:1fr}.blank-grid,.blank-grid.three{grid-template-columns:1fr}.blank-grid article{height:220px}.contact-band-grid,.detail-inquiry-grid,.contact-page-grid{grid-template-columns:1fr;gap:30px}.inner-banner{height:175px}.inner-banner h1{font-size:29px}.catalog-layout{grid-template-columns:1fr}.catalog-sidebar{order:2}.catalog-main{order:1}.inquiry-box{display:none}.category-menu{display:grid;grid-template-columns:1fr 1fr}.product-intro-grid{grid-template-columns:1fr;gap:30px}.product-gallery .product-image{height:340px}.product-summary h2{font-size:28px}.description-grid{grid-template-columns:1fr}.form-grid{grid-template-columns:1fr}.form-grid .full{grid-column:auto}.footer-grid{grid-template-columns:1fr}.footer-bottom .shell{align-items:flex-start;justify-content:center;flex-direction:column;padding-block:15px}.product-grid,.product-grid.four{grid-template-columns:1fr 1fr}.source-brochure img{transform:scale(3.2);transform-origin:75% 18%}.source-brochure-highlift img{transform:scale(2.6);transform-origin:85% 28%}.source-brochure-two-stage img{transform-origin:85% 28%}}
@media(max-width:500px){.hero h1{font-size:32px}.button{width:100%;margin-right:0}.solution-grid,.product-grid,.product-grid.four{grid-template-columns:1fr}.solution-card{height:245px}.featured-stack .product-card{grid-template-columns:115px 1fr}.category-menu{grid-template-columns:1fr}.product-card h3{min-height:0}.product-image{height:240px}.product-identity{flex-direction:column;gap:4px}.availability{grid-template-columns:1fr}.product-gallery .product-image{height:300px}}
"""

CSS += r"""
.answer-lead{font-size:19px!important;line-height:1.55;color:var(--ink)!important;font-weight:700}.entity-section,.profile-range,.answer-section,.reason-section,.evidence-section,.faq-section,.quality-controls,.document-section,.release-section{padding:65px 0}.entity-section,.evidence-section,.document-section{background:var(--soft)}.entity-grid{display:grid;grid-template-columns:.72fr 1.28fr;gap:60px;align-items:start}.entity-grid h2,.answer-grid h2,.faq-grid h2,.release-grid h2{font-size:32px;line-height:1.2;margin:0 0 14px}.entity-grid p,.answer-grid p,.faq-grid>div>p:last-child,.release-grid>div>p:last-child{color:var(--muted)}.entity-facts{margin:0;background:#fff;border-top:3px solid var(--green)}.entity-facts div{display:grid;grid-template-columns:165px minmax(0,1fr);gap:18px;padding:12px 15px;border-bottom:1px solid var(--line)}.entity-facts dt{font-size:12px;color:var(--muted)}.entity-facts dd{margin:0;font-size:13px;font-weight:700}.entity-facts a,.contact-details a{color:var(--green)}.profile-product-links{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));border-top:1px solid var(--line);border-left:1px solid var(--line)}.profile-product-links a{min-height:88px;display:flex;align-items:center;justify-content:space-between;gap:12px;padding:18px;border-right:1px solid var(--line);border-bottom:1px solid var(--line);font-size:14px;font-weight:800;background:#fff}.profile-product-links a:hover{color:var(--green);background:var(--soft)}.compliance-band{padding:58px 0;background:var(--green-dark);color:#fff}.compliance-band-grid{display:grid;grid-template-columns:.85fr 1.15fr;gap:65px;align-items:start}.compliance-band h2{font-size:31px;line-height:1.2;margin:0 0 14px}.compliance-band p{color:#d5e8e7}.compliance-band ul{margin:0;padding:0;list-style:none;border-top:1px solid rgba(255,255,255,.24)}.compliance-band li{padding:11px 0;border-bottom:1px solid rgba(255,255,255,.24);font-size:13px;font-weight:700}.company-contact-strip{padding:29px 0;background:#293033;color:#fff}.company-contact-strip .shell{display:flex;align-items:center;justify-content:space-between;gap:30px}.company-contact-strip strong,.company-contact-strip span{display:block}.company-contact-strip strong{font-size:18px}.company-contact-strip span{font-size:12px;color:#bcc7ca;margin-top:3px}.company-contact-strip .button{margin:0;flex:0 0 auto}.answer-section{background:#fff}.answer-grid{max-width:860px;margin-inline:auto;text-align:center}.answer-grid>p:last-child{font-size:19px;margin-bottom:0}.reason-grid,.quality-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));border-top:1px solid var(--line);border-left:1px solid var(--line)}.reason-grid article,.quality-grid article{position:relative;min-height:210px;padding:26px;border-right:1px solid var(--line);border-bottom:1px solid var(--line);background:#fff}.reason-grid article>span{display:block;color:var(--orange);font-size:12px;font-weight:900}.reason-grid h3,.quality-grid h3{font-size:18px;line-height:1.3;margin:18px 0 9px}.reason-grid p,.quality-grid p{margin:0;color:var(--muted);font-size:13px}.quality-grid{grid-template-columns:repeat(3,minmax(0,1fr))}.quality-grid article{min-height:225px}.quality-grid article>span{color:var(--green)}.section-heading.left{text-align:left;margin-inline:0}.evidence-table thead th{background:var(--green-dark);color:#fff}.evidence-table tbody th{width:25%;background:#fff;font-size:12px}.evidence-table td{background:#fff;vertical-align:top}.faq-grid{display:grid;grid-template-columns:.62fr 1.38fr;gap:70px;align-items:start}.faq-list{border-top:2px solid var(--green)}.faq-list details{border-bottom:1px solid var(--line)}.faq-list summary{display:flex;align-items:center;justify-content:space-between;gap:18px;padding:17px 4px;cursor:pointer;font-size:14px;font-weight:800;list-style:none}.faq-list summary::-webkit-details-marker{display:none}.faq-list p{margin:0;padding:0 36px 18px 4px;color:var(--muted);font-size:13px}.faq-list details[open] summary{color:var(--green)}.release-grid{display:grid;grid-template-columns:.62fr 1.38fr;gap:70px;align-items:start}.release-grid ol{margin:0;padding:0;list-style:none;border-top:2px solid var(--green)}.release-grid li{display:grid;grid-template-columns:48px 1fr;gap:16px;padding:17px 0;border-bottom:1px solid var(--line)}.release-grid li>span{color:var(--orange);font-size:13px;font-weight:900}.release-grid h3{font-size:16px;margin:0 0 4px}.release-grid li p{margin:0;color:var(--muted);font-size:13px}
@media(max-width:1050px){.profile-product-links,.quality-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media(max-width:760px){.entity-section,.profile-range,.answer-section,.reason-section,.evidence-section,.faq-section,.quality-controls,.document-section,.release-section{padding:50px 0}.entity-grid,.compliance-band-grid,.faq-grid,.release-grid{grid-template-columns:1fr;gap:30px}.entity-grid h2,.answer-grid h2,.faq-grid h2,.release-grid h2,.compliance-band h2{font-size:27px}.profile-product-links,.reason-grid,.quality-grid{grid-template-columns:1fr}.reason-grid article,.quality-grid article{min-height:0}.entity-facts div{grid-template-columns:1fr;gap:2px}.company-contact-strip .shell{align-items:flex-start;flex-direction:column}.company-contact-strip .button{width:100%}.answer-grid{text-align:left}}
"""

CSS += r"""
/* LEXYGO industrial color system: graphite structure, electric blue technology, safety orange action. */
:root{--green:#1268a8;--green-dark:#1a2227;--orange:#f27a24;--ink:#1b2226;--muted:#65727a;--line:#d7dee2;--soft:#f2f5f7;--white:#fff;--blue:#1268a8;--blue-dark:#0a4f86;--blue-soft:#eaf3f9;--graphite:#1a2227;--graphite-2:#273138;--steel:#7d8b94;--orange-dark:#d65f10;--surface:#f7f9fa}
body{color:var(--ink);font-family:"Segoe UI",Arial,"Helvetica Neue",sans-serif;background:var(--white)}::selection{background:#cfe6f5;color:var(--graphite)}a,button,input,textarea{transition:border-color .18s ease,background-color .18s ease,color .18s ease,box-shadow .18s ease,transform .18s ease}a:focus-visible,button:focus-visible,input:focus-visible,textarea:focus-visible,summary:focus-visible{outline:3px solid rgba(242,122,36,.5);outline-offset:3px}
.top-strip{background:#11171b;color:#aeb9bf;border-bottom:1px solid #2f3940}.top-strip a{color:#e3e8ea}.top-strip a:hover{color:#75b5df}.site-header{border-bottom:1px solid #dfe4e7;box-shadow:0 3px 14px rgba(22,31,36,.06)}.brand{position:relative}.brand strong{color:var(--blue);font-weight:900}.brand small{color:#53616a;font-weight:700}.brand:after{content:"";width:42px;height:3px;margin-top:7px;background:var(--orange)}.main-nav>a,.nav-group>a{color:#2d363b}.main-nav>a:hover,.nav-group:hover>a,.main-nav .active{color:var(--blue)}.main-nav>a:after,.nav-group>a:after{background:var(--orange)}.dropdown{border-top-color:var(--blue);box-shadow:0 16px 36px rgba(18,27,32,.15)}.dropdown a{border-bottom-color:#e8ecef}.dropdown a:hover{background:var(--blue-soft);color:var(--blue);box-shadow:inset 3px 0 0 var(--orange)}.menu-button{color:var(--graphite)}
.hero{background:var(--graphite);overflow:hidden}.hero-grid{grid-template-columns:.86fr 1.14fr}.hero-copy{color:#fff}.hero-copy>p:first-child{display:flex;align-items:center;gap:10px;color:#91c7e8}.hero-copy>p:first-child:before{content:"";width:28px;height:3px;background:var(--orange)}.hero h1{color:#fff}.hero-intro{color:#c8d0d5}.hero-machine{position:relative;background:#101518;box-shadow:100vw 0 0 #101518}.hero-machine:before{content:"";position:absolute;inset:0 0 auto 0;height:4px;background:var(--blue)}.hero-machine img{filter:drop-shadow(0 26px 26px rgba(0,0,0,.32))}.button{border-radius:2px;min-height:46px;font-weight:800}.button-primary{background:var(--orange);color:#181d20}.button-primary:hover{background:var(--orange-dark);color:#fff;box-shadow:0 8px 20px rgba(214,95,16,.22);transform:translateY(-1px)}.button-light{background:#fff;color:var(--graphite);border-color:#fff}.button-light:hover{background:var(--blue-soft);border-color:var(--blue-soft);color:var(--blue-dark)}.button-outline{border-color:var(--blue);color:var(--blue);background:#fff}.button-outline:hover{background:var(--blue);border-color:var(--blue);color:#fff}
.section-heading span{color:var(--orange)}.section-kicker{color:var(--blue)}.section-heading h2,.catalog-title h2,.product-summary h2,.company-profile h2,.contact-page h2{color:var(--graphite)}.center-action .button{background:transparent}.featured-section,.why-section,.profile-range,.answer-section,.reason-section,.quality-controls,.release-section{background:#fff}.solutions-section,.entity-section,.evidence-section,.document-section,.parameter-section,.detail-inquiry,.contact-band{background:var(--soft)}
.product-card{border-color:var(--line);box-shadow:0 2px 8px rgba(28,36,40,.03)}.product-card:hover{border-color:#9fc7df;box-shadow:0 14px 34px rgba(26,47,59,.12);transform:translateY(-3px)}.product-image,.product-gallery,.company-machine,.about-photo{background:#f1f4f6}.product-image{border-bottom:1px solid #e4e9ec}.model-code{color:var(--blue)}.product-card h3 a:hover{color:var(--blue)}.product-card li{border-bottom-color:#e2e7ea}.card-actions a{color:var(--blue)}.card-actions a:first-child{color:var(--orange-dark)}.card-actions a:hover{text-decoration:underline;text-underline-offset:3px}.solution-card{border:1px solid var(--line);background:#fff}.solution-card span{background:rgba(25,33,38,.96);border-left:4px solid var(--orange)}.solution-card:hover{border-color:#8bbadb;box-shadow:0 12px 28px rgba(26,47,59,.12)}.solution-card:hover span{background:var(--blue-dark)}
.about-grid>div:first-child{position:relative}.about-grid>div:first-child:before{content:"";position:absolute;top:60px;left:-22px;width:4px;height:76px;background:var(--blue)}.factory-stats{background:var(--graphite);border-top:4px solid var(--blue)}.stats-grid div{border-right-color:#39464d}.stats-grid span{color:#b9c5cb}.why-grid{border-color:var(--line)}.why-grid article{position:relative;border-color:var(--line);background:#fff}.why-grid article:before{content:"";position:absolute;top:-1px;left:-1px;right:-1px;height:3px;background:transparent}.why-grid article:hover:before{background:var(--blue)}.why-grid article>span{color:#f3a46c}.blank-media,.blank-grid article,.blank-content{background:#f5f7f8;border-color:#d9e0e4}
.contact-band{border-top:1px solid #e2e7ea}.inquiry-form{border-top-color:var(--orange);box-shadow:0 12px 30px rgba(28,39,45,.08)}.form-grid label{color:#3d484e}.form-grid input,.form-grid textarea{border-color:#c7d0d5;background:#fbfcfc;color:var(--ink)}.form-grid input:hover,.form-grid textarea:hover{border-color:#94a6b0}.form-grid input:focus,.form-grid textarea:focus{border-color:var(--blue);box-shadow:0 0 0 3px rgba(18,104,168,.12);outline:0;background:#fff}
.inner-banner{position:relative;background-color:#263138;background-image:url('/assets/og-cover.png');background-position:center 58%;background-size:cover;background-repeat:no-repeat;background-blend-mode:multiply}.inner-banner:before{content:"";position:absolute;inset:0;background:rgba(14,20,24,.42)}.inner-banner .shell{position:relative;z-index:1}.inner-banner h1{text-shadow:0 2px 10px rgba(0,0,0,.28)}.breadcrumbs{color:#72808a}.breadcrumbs a:hover{color:var(--blue)}
.side-box{border-color:var(--line);background:#fff}.side-box>h2{background:var(--graphite);border-left:4px solid var(--orange)}.category-menu a:hover{background:var(--blue-soft);color:var(--blue)}.category-menu span{color:var(--blue);font-weight:800}.catalog-title{border-bottom-color:var(--line)}.catalog-title>p:first-child{color:var(--orange-dark)}.category-answer{background:var(--blue-soft);border-left-color:var(--blue)}.category-answer strong{color:var(--blue-dark)}
.product-gallery{border-color:var(--line)}.feature-list{border-top-color:var(--line)}.feature-list li{border-bottom-color:var(--line)}.availability div{border-left-color:var(--blue)}.tab-heading{border-bottom-color:var(--blue)}.tab-heading span{background:var(--blue)}.spec-group h3{background:var(--blue-dark);border-left:4px solid var(--orange)}.table-wrap{border:1px solid #d9e0e4}.table-wrap table{margin:-1px}.table-wrap th,.table-wrap td{border-color:#d9e0e4}.table-wrap thead th,.evidence-table thead th{background:var(--graphite);color:#fff}.table-wrap tbody tr:nth-child(even) th,.table-wrap tbody tr:nth-child(even) td{background:#f6f8f9}.table-wrap tbody tr:hover th,.table-wrap tbody tr:hover td{background:var(--blue-soft)}
.entity-facts{border-top-color:var(--blue);box-shadow:0 8px 24px rgba(28,39,45,.06)}.entity-facts a,.contact-details a{color:var(--blue)}.profile-product-links a:hover{color:var(--blue);background:var(--blue-soft);box-shadow:inset 0 -3px 0 var(--orange)}.compliance-band{position:relative;background:var(--graphite);border-top:4px solid var(--blue)}.compliance-band p{color:#c6d0d5}.compliance-band li{position:relative;padding-left:22px;border-bottom-color:#3d484e}.compliance-band li:before{content:"";position:absolute;left:2px;top:18px;width:7px;height:7px;background:var(--orange)}.company-contact-strip{background:var(--blue-dark);border-top:1px solid #267caf}.company-contact-strip span{color:#d5e5ef}.reason-grid article,.quality-grid article{border-color:var(--line)}.reason-grid article:hover,.quality-grid article:hover{background:var(--blue-soft)}.quality-grid article>span{color:var(--blue)}.faq-list,.release-grid ol{border-top-color:var(--blue)}.faq-list details[open] summary{color:var(--blue)}.release-grid li>span{color:var(--orange-dark)}
.site-footer{background:#13191d;color:#b5c0c6;border-top:4px solid var(--blue)}.site-footer h2{position:relative;padding-bottom:10px;color:#fff}.site-footer h2:after{content:"";position:absolute;left:0;bottom:0;width:32px;height:2px;background:var(--orange)}.site-footer a:hover{color:#7fc0e7}.contact-list dt{color:#7f919b}.newsletter input{background:#eef2f4;color:var(--ink)}.newsletter button{background:var(--orange);color:var(--graphite)}.newsletter button:hover{background:var(--orange-dark);color:#fff}.footer-bottom{border-top-color:#303b41;color:#7f8e96}
@media(max-width:1050px){.main-nav{border-top:3px solid var(--blue)}.main-nav>a,.nav-group>a{border-bottom:1px solid #edf0f2}.dropdown a:hover{box-shadow:inset 3px 0 0 var(--orange)}}
@media(max-width:760px){.brand:after{width:32px;height:2px;margin-top:5px}.hero{background:var(--graphite)}.hero-grid{grid-template-columns:1fr}.hero-machine{margin-inline:-14px;padding-inline:14px;background:#101518;box-shadow:none}.hero-machine:before{height:3px}.about-grid>div:first-child:before{display:none}.inner-banner{background-position:center}.company-contact-strip{background:var(--blue-dark)}}
"""

CSS += r"""
.brand{width:194px;min-width:194px;height:68px;display:flex;align-items:center;justify-content:flex-start}.brand:after{display:none}.brand img{width:180px;height:64px;object-fit:contain;object-position:left center}.footer-brand{display:flex;align-items:center;justify-content:center;width:122px;min-height:48px;padding:5px 8px;background:#fff;border:1px solid #39464d}.footer-brand img{display:block;width:104px;height:38px;object-fit:contain}.footer-brand:hover{border-color:#7fc0e7;background:#f6f8f9}
@media(max-width:760px){.brand{width:150px;min-width:150px;height:58px}.brand img{width:142px;height:54px}.footer-brand{width:116px}}
"""

CSS += r"""
/* Bright energetic palette: clean white space, vivid blue, cyan product accents, and safety orange actions. */
:root{--green:#0878cf;--green-dark:#075a99;--orange:#ff8a1f;--ink:#17324d;--muted:#5f7486;--line:#cfe2ef;--soft:#f1f9ff;--white:#fff;--blue:#0878cf;--blue-dark:#075a99;--blue-soft:#e9f6ff;--graphite:#17324d;--graphite-2:#244760;--steel:#6f8798;--orange-dark:#e96f08;--surface:#fbfdff;--cyan:#14b9cf;--cyan-soft:#e8fbfd;--yellow:#ffd34d}
body{color:var(--ink);background:#fff}::selection{background:#bfeeff;color:#17324d}a:focus-visible,button:focus-visible,input:focus-visible,textarea:focus-visible,summary:focus-visible{outline-color:rgba(255,138,31,.65)}
.top-strip{background:var(--blue);color:#eaf7ff;border-bottom:0}.top-strip a{color:#fff}.top-strip a:hover{color:var(--yellow)}.site-header{background:#fff;border-bottom-color:#d8ebf6;box-shadow:0 4px 18px rgba(7,90,153,.08)}.brand small{color:#527186}.main-nav>a,.nav-group>a{color:#29465a}.main-nav>a:hover,.nav-group:hover>a,.main-nav .active{color:var(--blue)}.dropdown{border-top-color:var(--orange);box-shadow:0 16px 36px rgba(7,90,153,.14)}.dropdown a:hover{background:var(--cyan-soft);color:var(--blue-dark);box-shadow:inset 3px 0 0 var(--orange)}
.hero{min-height:560px;background:#eff9ff;border-bottom:1px solid #ccecf4}.hero-grid{min-height:560px;grid-template-columns:.9fr 1.1fr}.hero-copy{color:var(--ink)}.hero-copy>p:first-child{color:var(--blue);letter-spacing:.02em}.hero-copy>p:first-child:before{background:var(--orange)}.hero h1{color:var(--ink)}.hero-intro{color:var(--muted)}.hero-machine{background:var(--cyan-soft);box-shadow:100vw 0 0 var(--cyan-soft)}.hero-machine:before{height:5px;background:var(--cyan)}.hero-machine img{width:108%;height:490px;filter:drop-shadow(0 24px 18px rgba(7,90,153,.19))}.button-primary{background:var(--orange);color:#17324d}.button-primary:hover{background:var(--orange-dark);color:#fff;box-shadow:0 9px 22px rgba(233,111,8,.25)}.button-light{background:#fff;color:var(--blue-dark);border-color:#91cdeb;box-shadow:0 5px 16px rgba(7,90,153,.08)}.button-light:hover{background:var(--blue);border-color:var(--blue);color:#fff}.button-outline{border-color:var(--blue);color:var(--blue-dark)}.button-outline:hover{background:var(--blue);border-color:var(--blue);color:#fff}
.section-heading span{color:var(--orange-dark)}.section-kicker{color:var(--blue)}.section-heading h2,.catalog-title h2,.product-summary h2,.company-profile h2,.contact-page h2{color:var(--ink)}.featured-section,.why-section,.profile-range,.answer-section,.reason-section,.quality-controls,.release-section{background:#fff}.solutions-section,.entity-section,.evidence-section,.document-section,.parameter-section,.detail-inquiry,.contact-band{background:var(--soft)}
.product-card{border-color:#cfe3ef;background:#fff;box-shadow:0 4px 14px rgba(7,90,153,.05)}.product-card:hover{border-color:#5fc9d8;box-shadow:0 15px 34px rgba(7,90,153,.14)}.product-image,.product-gallery,.company-machine,.about-photo{background:var(--cyan-soft)}.product-image{border-bottom-color:#cfeaf0}.model-code,.card-actions a{color:var(--blue)}.card-actions a:first-child{color:var(--orange-dark)}.solution-card{border-color:#cfe3ef;background:#fff}.solution-card span{background:rgba(7,90,153,.94);border-left-color:var(--orange)}.solution-card:hover{border-color:var(--cyan);box-shadow:0 13px 28px rgba(7,90,153,.14)}.solution-card:hover span{background:var(--blue)}
.about-grid>div:first-child:before{background:var(--orange)}.factory-stats{background:var(--blue);border-top-color:var(--cyan)}.stats-grid div{border-right-color:rgba(255,255,255,.25)}.stats-grid strong{color:#fff}.stats-grid span{color:#dff6ff}.why-grid article:hover:before{background:var(--cyan)}.why-grid article>span{color:var(--orange-dark)}.blank-media,.blank-grid article,.blank-content{background:var(--cyan-soft);border-color:#c8edf1}
.contact-band{border-top-color:#cfe8f5}.inquiry-form{background:#fff;border-top-color:var(--orange);box-shadow:0 14px 30px rgba(7,90,153,.1)}.form-grid label{color:#365a70}.form-grid input,.form-grid textarea{border-color:#bcd8e8;background:#fff}.form-grid input:hover,.form-grid textarea:hover{border-color:#78badc}.form-grid input:focus,.form-grid textarea:focus{border-color:var(--blue);box-shadow:0 0 0 3px rgba(8,120,207,.13)}
.inner-banner{background-color:var(--blue);background-image:url('/assets/og-cover.png');background-position:74% 58%;background-size:58% auto;background-blend-mode:soft-light;border-bottom:5px solid var(--orange)}.inner-banner:before{background:rgba(5,89,154,.28)}.inner-banner h1{color:#fff;text-shadow:0 2px 10px rgba(5,70,120,.22)}.breadcrumbs{color:#6a8091}.breadcrumbs a:hover{color:var(--blue)}
.side-box{border-color:#cfe3ef}.side-box>h2{background:var(--blue);border-left-color:var(--orange)}.category-menu a:hover{background:var(--cyan-soft);color:var(--blue-dark)}.category-menu span{color:var(--orange-dark)}.catalog-title{border-bottom-color:#cfe3ef}.catalog-title>p:first-child{color:var(--orange-dark)}.category-answer{background:var(--cyan-soft);border-left-color:var(--cyan)}.category-answer strong{color:var(--blue-dark)}
.product-gallery{border-color:#cfe3ef}.availability div{border-left-color:var(--cyan)}.tab-heading{border-bottom-color:var(--blue)}.tab-heading span{background:var(--blue)}.spec-group h3{background:var(--blue);border-left-color:var(--orange)}.table-wrap{border-color:#c7dfea}.table-wrap th,.table-wrap td{border-color:#c7dfea}.table-wrap thead th,.evidence-table thead th{background:var(--blue);color:#fff}.table-wrap tbody tr:nth-child(even) th,.table-wrap tbody tr:nth-child(even) td{background:#f2faff}.table-wrap tbody tr:hover th,.table-wrap tbody tr:hover td{background:var(--cyan-soft)}
.entity-facts{border-top-color:var(--cyan);box-shadow:0 9px 25px rgba(7,90,153,.08)}.entity-facts a,.contact-details a{color:var(--blue)}.profile-product-links a:hover{color:var(--blue-dark);background:var(--cyan-soft);box-shadow:inset 0 -3px 0 var(--orange)}.compliance-band{background:var(--blue);border-top-color:var(--orange)}.compliance-band p{color:#e4f7ff}.compliance-band li{border-bottom-color:rgba(255,255,255,.28)}.compliance-band li:before{background:var(--yellow)}.company-contact-strip{background:var(--orange);color:var(--ink);border-top:0}.company-contact-strip span{color:#5f3d18}.company-contact-strip .button{background:#fff;color:var(--blue-dark);border-color:#fff}.company-contact-strip .button:hover{background:var(--blue);border-color:var(--blue);color:#fff}.reason-grid article:hover,.quality-grid article:hover{background:var(--cyan-soft)}.quality-grid article>span{color:var(--cyan)}.faq-list,.release-grid ol{border-top-color:var(--cyan)}.faq-list details[open] summary{color:var(--blue)}
.site-footer{background:var(--blue-dark);color:#d8effb;border-top-color:var(--cyan)}.site-footer h2{color:#fff}.site-footer h2:after{background:var(--orange)}.site-footer a:hover{color:var(--yellow)}.contact-list dt{color:#aad4ea}.newsletter input{background:#fff;color:var(--ink)}.newsletter button{background:var(--orange);color:var(--ink)}.newsletter button:hover{background:#fff;color:var(--blue-dark)}.footer-bottom{border-top-color:rgba(255,255,255,.2);color:#b7d9eb}.footer-brand{border-color:#79cde0}.footer-brand:hover{border-color:var(--yellow);background:#fff}
@media(max-width:1050px){.main-nav{border-top-color:var(--orange)}.main-nav>a,.nav-group>a{border-bottom-color:#e1eef5}}
@media(max-width:760px){.hero{min-height:0;background:#eff9ff}.hero-grid{min-height:0;grid-template-columns:1fr}.hero-copy{padding:40px 0 18px}.hero-machine{height:270px;margin-inline:-14px;padding:0 14px;background:var(--cyan-soft);box-shadow:none}.hero-machine:before{background:var(--cyan)}.hero-machine img{height:268px;width:100%}.inner-banner{background-position:78% center;background-size:auto 88%}.company-contact-strip{background:var(--orange)}}
"""

CSS += r"""
.product-gallery .product-image img{position:absolute;inset:17px;width:calc(100% - 34px);height:calc(100% - 34px);max-width:none;object-fit:contain}
.product-image-compact img{width:86%;height:86%}.product-gallery .product-image-compact img{inset:34px;width:calc(100% - 68px);height:calc(100% - 68px)}
.product-card .product-image:not(.source-brochure) img{position:absolute;inset:22px;width:calc(100% - 44px);height:calc(100% - 44px);max-width:none;max-height:none;object-fit:contain}
.product-card .source-brochure img{transform:scale(2.15)}.product-card .source-brochure-highlift img{transform:scale(2)}
@media(max-width:760px){.product-gallery .product-image-compact img{inset:26px;width:calc(100% - 52px);height:calc(100% - 52px)}}
"""

CSS += r"""
.services-intro,.services-section,.service-matrix-section,.requirements-section{padding:65px 0}.services-intro{background:#fff}.services-answer{max-width:930px;text-align:center}.services-answer h2{font-size:34px;line-height:1.2;margin:0 0 18px}.services-answer>p:not(.section-kicker){font-size:18px;color:var(--muted)}.services-answer .service-note{margin:24px auto 0;padding:15px 18px;border-left:4px solid var(--orange);background:var(--cyan-soft);font-size:13px!important;text-align:left;color:var(--ink)!important}.services-section{background:#fff}.services-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));border-top:1px solid var(--line);border-left:1px solid var(--line)}.services-grid article{min-height:310px;padding:27px;border-right:1px solid var(--line);border-bottom:1px solid var(--line);background:#fff}.services-grid article:hover{background:var(--cyan-soft)}.service-icon{width:44px;height:44px;display:grid;place-items:center;background:var(--blue);color:#fff;border-bottom:4px solid var(--orange)}.services-grid h3{font-size:18px;line-height:1.3;margin:18px 0 9px}.services-grid p{margin:0;color:var(--muted);font-size:13px}.services-grid ul{list-style:none;margin:17px 0 0;padding:0;border-top:1px solid var(--line)}.services-grid li{position:relative;padding:8px 0 8px 15px;border-bottom:1px solid var(--line);font-size:12px;font-weight:700}.services-grid li:before{content:"";position:absolute;left:1px;top:15px;width:6px;height:6px;background:var(--orange)}.service-matrix-section{background:var(--soft)}.service-matrix tbody th{width:19%;background:#fff}.service-matrix td{background:#fff;vertical-align:top}.service-workflow{background:#fff}.requirements-section{background:var(--blue);color:#fff}.requirements-grid{display:grid;grid-template-columns:.8fr 1.2fr;gap:70px;align-items:start}.requirements-grid h2{font-size:32px;line-height:1.2;margin:0 0 14px;color:#fff}.requirements-grid>div>p:not(.section-kicker){color:#e2f5ff}.requirements-grid .button{margin-bottom:0}.requirements-grid ul{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:0 28px;margin:0;padding:0;list-style:none;border-top:1px solid rgba(255,255,255,.35)}.requirements-grid li{display:flex;align-items:flex-start;gap:9px;padding:11px 0;border-bottom:1px solid rgba(255,255,255,.25);font-size:13px;font-weight:700}.requirements-grid li svg{flex:0 0 auto;margin-top:3px;color:var(--yellow)}
@media(max-width:900px){.services-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.requirements-grid{grid-template-columns:1fr;gap:35px}}
@media(max-width:760px){.services-intro,.services-section,.service-matrix-section,.requirements-section{padding:50px 0}.services-answer{text-align:left}.services-answer h2,.requirements-grid h2{font-size:27px}.services-answer>p:not(.section-kicker){font-size:16px}.services-grid{grid-template-columns:1fr}.services-grid article{min-height:0}.service-matrix th,.service-matrix td{min-width:190px}.requirements-grid ul{grid-template-columns:1fr}}
"""

CSS += r"""
.resource-dropdown{min-width:255px}.resource-intro,.resource-directory,.resource-questions,.resource-matrix-section,.document-groups,.application-notes,.buyer-guides,.guide-answer,.guide-table-section,.guide-checklist,.guide-related,.faq-library{padding:65px 0}.resource-intro{background:#fff}.resource-answer{max-width:930px;text-align:center}.resource-answer h2,.resource-question-grid h2,.guide-checklist h2{font-size:34px;line-height:1.2;margin:0 0 18px}.resource-answer>p:not(.section-kicker){font-size:18px;color:var(--muted)}.resource-answer .resource-note{margin:24px auto 0;padding:15px 18px;border-left:4px solid var(--orange);background:var(--cyan-soft);font-size:13px!important;text-align:left;color:var(--ink)!important}.resource-directory,.document-groups,.buyer-guides{background:var(--soft)}.resource-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));border-top:1px solid var(--line);border-left:1px solid var(--line)}.resource-grid article,.document-grid article{padding:27px;background:#fff;border-right:1px solid var(--line);border-bottom:1px solid var(--line)}.resource-grid article{min-height:275px}.resource-grid article:hover,.document-grid article:hover{background:var(--cyan-soft)}.resource-icon{width:46px;height:46px;display:grid;place-items:center;background:var(--blue);color:#fff;border-bottom:4px solid var(--orange)}.resource-grid h3,.document-grid h3,.application-grid h3{font-size:18px;line-height:1.3;margin:18px 0 9px}.resource-grid p,.document-grid p,.application-grid p{color:var(--muted);font-size:13px}.resource-grid article>a,.application-grid article>a{display:inline-flex;align-items:center;gap:7px;margin-top:14px;color:var(--blue);font-size:12px;font-weight:800}.resource-grid article>a:hover,.application-grid article>a:hover{color:var(--orange-dark)}.resource-questions,.guide-related{background:#fff}.resource-question-grid{display:grid;grid-template-columns:.78fr 1.22fr;gap:70px;align-items:start}.resource-question-grid>div:first-child>p:not(.section-kicker){color:var(--muted)}.question-links{border-top:3px solid var(--cyan)}.question-links a{display:flex;align-items:center;justify-content:space-between;gap:18px;padding:14px 16px;border-bottom:1px solid var(--line);background:#fff;font-weight:700;font-size:14px}.question-links a:hover{background:var(--cyan-soft);color:var(--blue)}.question-links svg{flex:0 0 auto;color:var(--orange-dark)}.resource-matrix-section,.guide-table-section{background:var(--soft)}.resource-matrix-section .table-wrap,.guide-table-section .table-wrap{overflow-y:hidden}.resource-matrix a{color:var(--blue);font-weight:800}.resource-matrix tbody th{width:23%}.document-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));border-top:1px solid var(--line);border-left:1px solid var(--line)}.document-grid article{min-height:285px}.document-grid article strong{display:block;margin-top:16px;padding-top:13px;border-top:1px solid var(--line);font-size:12px;color:var(--blue-dark)}.download-table th,.download-table td,.compliance-table th,.compliance-table td{vertical-align:top}.compliance-workflow{background:#fff}.faq-library{background:var(--soft)}.faq-jump{position:sticky;top:82px;z-index:10;display:flex;flex-wrap:wrap;gap:1px;margin-bottom:38px;background:var(--line);border:1px solid var(--line)}.faq-jump a{flex:1 1 170px;padding:11px 13px;background:#fff;color:var(--blue-dark);font-size:12px;font-weight:800;text-align:center}.faq-jump a:hover{background:var(--cyan-soft)}.faq-group{scroll-margin-top:150px;display:grid;grid-template-columns:240px minmax(0,1fr);gap:45px;margin-bottom:46px}.faq-group h2{margin:0;font-size:23px}.faq-group .faq-list{background:#fff}.application-notes{background:var(--soft)}.application-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:22px}.application-grid article{min-height:330px;padding:28px;background:#fff;border:1px solid var(--line);border-top:4px solid var(--cyan)}.application-grid article:hover{border-top-color:var(--orange);box-shadow:0 12px 30px rgba(7,90,153,.1)}.application-grid .case-label,.guide-type{margin:16px 0 0;color:var(--orange-dark);font-size:11px;font-weight:900}.application-grid article>strong{display:block;margin-top:18px;color:var(--blue-dark);font-size:13px}.guide-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:22px}.guide-grid article{display:flex;flex-direction:column;min-height:345px;padding:28px;background:#fff;border:1px solid var(--line);border-top:4px solid var(--cyan)}.guide-grid article:hover{border-top-color:var(--orange);box-shadow:0 12px 30px rgba(7,90,153,.1)}.guide-grid .guide-type{margin:0}.guide-grid h2{font-size:20px;line-height:1.3;margin:13px 0 9px}.guide-grid h2 a:hover{color:var(--blue)}.guide-grid>article>p:not(.guide-type){color:var(--muted);font-size:13px}.guide-grid article>div{display:grid;gap:3px;margin-top:auto;padding-top:18px;border-top:1px solid var(--line);color:var(--muted);font-size:11px}.guide-link{display:inline-flex;align-items:center;gap:7px;margin-top:15px;color:var(--blue);font-size:12px;font-weight:800}.guide-answer{background:#fff}.guide-answer .shell{max-width:930px}.guide-answer h2{font-size:34px;line-height:1.2;margin:0 0 18px}.guide-answer .answer-lead{font-size:19px;line-height:1.7;color:var(--ink)}.article-meta{display:flex;flex-wrap:wrap;gap:10px 24px;margin-top:25px;padding-top:14px;border-top:1px solid var(--line);color:var(--muted);font-size:12px}.guide-table-section .guide-table tbody th{width:20%}.guide-checklist{background:var(--blue);color:#fff}.guide-checklist-grid{display:grid;grid-template-columns:.8fr 1.2fr;gap:70px}.guide-checklist h2{color:#fff}.guide-checklist-grid>div>p:not(.section-kicker){color:#e2f5ff}.guide-checklist ul{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:0 28px;margin:0;padding:0;list-style:none;border-top:1px solid rgba(255,255,255,.35)}.guide-checklist li{display:flex;align-items:flex-start;gap:9px;padding:11px 0;border-bottom:1px solid rgba(255,255,255,.25);font-size:13px;font-weight:700}.guide-checklist li svg{flex:0 0 auto;margin-top:3px;color:var(--yellow)}
@media(max-width:900px){.resource-grid,.document-grid,.guide-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.resource-question-grid,.guide-checklist-grid{grid-template-columns:1fr;gap:35px}.faq-group{grid-template-columns:1fr;gap:15px}}
@media(max-width:760px){.resource-intro,.resource-directory,.resource-questions,.resource-matrix-section,.document-groups,.application-notes,.buyer-guides,.guide-answer,.guide-table-section,.guide-checklist,.guide-related,.faq-library{padding:50px 0}.resource-answer{text-align:left}.resource-answer h2,.resource-question-grid h2,.guide-checklist h2,.guide-answer h2{font-size:27px}.resource-answer>p:not(.section-kicker),.guide-answer .answer-lead{font-size:16px}.resource-grid,.document-grid,.application-grid,.guide-grid{grid-template-columns:1fr}.resource-grid article,.document-grid article,.application-grid article,.guide-grid article{min-height:0}.faq-jump{position:static}.resource-matrix th,.resource-matrix td,.download-table th,.download-table td,.compliance-table th,.compliance-table td,.guide-table th,.guide-table td{min-width:185px}.guide-checklist ul{grid-template-columns:1fr}}
"""

CSS += r"""
.language-switcher{position:relative;flex:0 0 auto;color:var(--blue-dark)}.language-switcher summary{height:42px;max-width:175px;display:flex;align-items:center;gap:7px;padding:0 10px;border:1px solid #cfe3ef;background:#fff;cursor:pointer;font-size:12px;font-weight:800;list-style:none;white-space:nowrap}.language-switcher summary::-webkit-details-marker{display:none}.language-switcher summary span{overflow:hidden;text-overflow:ellipsis}.language-switcher[open] summary,.language-switcher summary:hover{border-color:var(--cyan);background:var(--cyan-soft)}.language-menu{position:absolute;top:calc(100% + 8px);right:0;z-index:120;width:390px;max-height:min(68vh,560px);overflow:auto;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));padding:8px;background:#fff;border-top:3px solid var(--orange);box-shadow:0 18px 40px rgba(7,55,88,.18)}.language-menu a{display:block;padding:10px 11px;border-bottom:1px solid #e4eff5;font-size:13px;font-weight:700}.language-menu a:hover,.language-menu a[aria-current="page"]{background:var(--cyan-soft);color:var(--blue)}.language-menu a[aria-current="page"]{box-shadow:inset 3px 0 0 var(--orange)}
[dir="rtl"] body{text-align:right}[dir="rtl"] .language-menu{right:auto;left:0}[dir="rtl"] .language-menu a[aria-current="page"]{box-shadow:inset -3px 0 0 var(--orange)}[dir="rtl"] .section-kicker,[dir="rtl"] .model-code{letter-spacing:0}[dir="rtl"] .services-grid li:before,[dir="rtl"] .compliance-band li:before{left:auto;right:1px}[dir="rtl"] .services-grid li{padding-left:0;padding-right:15px}[dir="rtl"] .form-grid input,[dir="rtl"] .form-grid textarea{direction:rtl}[dir="rtl"] .table-wrap{direction:rtl}
@media(max-width:1180px){.nav-row{gap:18px}.main-nav>a,.nav-group>a{padding-inline:10px}.main-nav>a:after,.nav-group>a:after{left:10px;right:10px}.language-switcher summary{max-width:132px}}
@media(max-width:1050px){.brand{order:1}.language-switcher{order:2;margin-left:auto}.menu-button{order:3}.main-nav{order:4}.language-switcher summary{max-width:165px}.language-menu{width:360px}}
@media(max-width:560px){.nav-row{gap:7px}.brand{min-width:0}.brand img{width:128px}.language-switcher summary{width:42px;padding:0;justify-content:center}.language-switcher summary span,.language-switcher summary svg:last-child{display:none}.language-menu{position:fixed;top:68px;left:14px;right:14px;width:auto;grid-template-columns:1fr 1fr}.language-menu a{font-size:12px;padding:9px}}
"""


JS = r"""
document.addEventListener('DOMContentLoaded',()=>{if(window.lucide)window.lucide.createIcons();const button=document.querySelector('[data-menu-button]');const menu=document.querySelector('[data-menu]');if(button&&menu){button.addEventListener('click',()=>{const open=menu.classList.toggle('is-open');button.setAttribute('aria-expanded',String(open))});menu.querySelectorAll('.nav-group>a').forEach(link=>link.addEventListener('click',event=>{if(window.innerWidth<=1050&&link.nextElementSibling){event.preventDefault();link.parentElement.classList.toggle('is-open')}}))}document.addEventListener('click',event=>{document.querySelectorAll('.language-switcher[open]').forEach(item=>{if(!item.contains(event.target))item.removeAttribute('open')})});const model=new URLSearchParams(location.search).get('model');document.querySelectorAll('[data-model-field]').forEach(field=>{if(model)field.value=model});const t=window.LEXYGO_I18N||{inquiry:'LEXYGO inquiry',equipment:'material handling equipment',name:'Name',email:'Email',company:'Company',country:'Country / Region',model:'Product / Model',message:'Message'};document.querySelectorAll('[data-mailto-form]').forEach(form=>form.addEventListener('submit',event=>{event.preventDefault();const data=new FormData(form);const subject=`${t.inquiry}: ${data.get('model')||t.equipment}${data.get('company')?' - '+data.get('company'):''}`;const body=[`${t.name}: ${data.get('name')||''}`,`${t.email}: ${data.get('email')||''}`,`${t.company}: ${data.get('company')||''}`,`${t.country}: ${data.get('country')||''}`,`${t.model}: ${data.get('model')||''}`,'',`${t.message}:`,` ${data.get('details')||''}`].join('\n');location.href=`mailto:${form.dataset.email}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`}))});
"""


FAVICON = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" fill="#1a2227"/><path d="M16 11h11v31h22v11H16z" fill="#f7f9fa"/><path d="M39 20h9v17h-9z" fill="#1268a8"/><path d="M16 49h33v4H16z" fill="#f27a24"/></svg>"""


def build():
    if DIST.exists():
        shutil.rmtree(DIST)
    ASSETS.mkdir(parents=True)
    copy_product_assets()
    (ASSETS / "site.css").write_text(CSS, encoding="utf-8")
    (ASSETS / "site.js").write_text(JS, encoding="utf-8")
    (ASSETS / "favicon.svg").write_text(FAVICON, encoding="utf-8")
    shutil.copy2(LOGO_SOURCE, ASSETS / "lexygo-logo.gif")

    routes = ["/", "/products/"]
    write_route("/", home_page())
    write_route("/products/", products_page())
    for slug, data in CATEGORIES.items():
        route = f"/products/{slug}/"
        write_route(route, category_page(slug, data))
        routes.append(route)
    for item in PRODUCTS:
        route = f'/products/{item["slug"]}/'
        write_route(route, product_page(item))
        routes.append(route)

    static_pages = {
        "/company/": company_page(),
        "/company/why-choose-us/": why_choose_page(),
        "/company/quality-management/": quality_management_page(),
        "/services/": services_page(),
        "/resources/": resources_page(),
        "/resources/compliance/": compliance_page(),
        "/resources/download/": downloads_page(),
        "/resources/faq/": faq_page(),
        "/resources/cases/": cases_page(),
        "/blogs/": blogs_page(),
        "/blogs/company-news/": blank_page("/blogs/company-news/", "Company News", ("Blogs", "/blogs/"), "blogs"),
        "/blogs/industry-knowledge/": blank_page("/blogs/industry-knowledge/", "Industry Knowledge", ("Blogs", "/blogs/"), "blogs"),
        "/contact/": contact_page(),
    }
    for route, content in static_pages.items():
        write_route(route, content)
        routes.append(route)

    aliases = {
        "/about/": static_pages["/company/"],
        "/quality/": static_pages["/company/quality-management/"],
        "/oem-odm/": static_pages["/services/"],
        "/solutions/": static_pages["/services/"],
        "/guides/": guides_page(),
    }
    for guide in GUIDES:
        route = f'/guides/{guide["slug"]}/'
        aliases[route] = buyer_guide_page(guide)
    for route, content in aliases.items():
        write_route(route, content)
        routes.append(route)

    (DIST / "404.html").write_text(not_found_page(), encoding="utf-8")
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(f"  <url><loc>{route_url(route)}</loc></url>" for route in routes) + "\n</urlset>\n"
    (DIST / "sitemap.xml").write_text(sitemap, encoding="utf-8")
    (DIST / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {BASE_URL}/sitemap.xml\n", encoding="utf-8")
    llms = ["# LEXYGO Material Handling Equipment", "", f"> {COMPANY['legal_name']} supplies electric pallet trucks, stackers, electric forklifts, manual pallet trucks, and warehouse equipment.", "", "## Product families"]
    llms += [f"- [{data['name']}]({route_url(f'/products/{slug}/')}): {data['short']}" for slug, data in CATEGORIES.items()]
    llms += ["", "## Product models"] + [f"- [{item['model']} {item['name']}]({route_url('/products/' + item['slug'] + '/')}): {known(item['capacity'])}; {known(item['lift'])}; {known(item['operation'])}." for item in PRODUCTS]
    llms += ["", "## Buyer resources", f"- [Resource Center]({route_url('/resources/')}): Product selection, compliance, documents, FAQs, and applications.", f"- [Compliance Center]({route_url('/resources/compliance/')}): Model-specific document verification guidance.", f"- [Downloads and Documents]({route_url('/resources/download/')}): Product data and controlled document requests.", f"- [Buyer FAQ]({route_url('/resources/faq/')}): Direct answers for professional buyers."]
    llms += [f"- [{guide['title']}]({route_url('/guides/' + guide['slug'] + '/')}): {guide['summary']}" for guide in GUIDES]
    llms += ["", "## Contact", f"- Email: {COMPANY['email']}"]
    (DIST / "llms.txt").write_text("\n".join(llms) + "\n", encoding="utf-8")
    print(f"Built {len(routes)} routes and {len(PRODUCTS)} product pages in {DIST}")


if __name__ == "__main__":
    build()
