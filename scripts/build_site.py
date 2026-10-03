from __future__ import annotations

import html
import json
import shutil
from pathlib import Path

from site_data import CATEGORIES, COMPANY, PRODUCTS, SOURCE_ROOT


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
ASSETS = DIST / "assets"
PRODUCT_ASSETS = ASSETS / "products"
BASE_URL = COMPANY["domain"]
FULL_SPECS = json.loads((ROOT / "product_specs.json").read_text(encoding="utf-8"))


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


def button(label, href, style="primary", icon_name="arrow-right"):
    return f'<a class="button button-{style}" href="{href}"><span>{esc(label)}</span>{icon(icon_name)}</a>'


def image_class(item):
    classes = ["product-image"]
    if item["slug"] in {"mpt5tn", "mpjsc1500", "mpjtsc1500"}:
        classes.append("source-brochure")
    if item["slug"] in {"mpjsc1500", "mpjtsc1500"}:
        classes.append("source-brochure-highlift")
    if item["slug"] == "mpjtsc1500":
        classes.append("source-brochure-two-stage")
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
    <div class="top-strip"><div class="shell"><span>{esc(COMPANY['location'])}</span><a href="mailto:{esc(COMPANY['email'])}">{esc(COMPANY['email'])}</a></div></div>
    <header class="site-header"><div class="shell nav-row">
      <a class="brand" href="/" aria-label="LEXYGO home"><strong>LEXYGO</strong><small>MATERIAL HANDLING EQUIPMENT</small></a>
      <button class="menu-button" type="button" aria-label="Open navigation" aria-expanded="false" data-menu-button>{icon('menu', 22)}</button>
      <nav class="main-nav" aria-label="Main navigation" data-menu>
        <a class="{'active' if active == 'home' else ''}" href="/">Home</a>
        <div class="nav-group"><a class="{'active' if active == 'company' else ''}" href="/company/">Company {icon('chevron-down', 14)}</a><div class="dropdown"><a href="/company/">Company Profile</a><a href="/company/why-choose-us/">Why Choose Us</a><a href="/company/quality-management/">Quality Management</a></div></div>
        <div class="nav-group"><a class="{'active' if active == 'products' else ''}" href="/products/">Products {icon('chevron-down', 14)}</a><div class="dropdown wide-dropdown">{product_links}</div></div>
        <a class="{'active' if active == 'services' else ''}" href="/services/">Services</a>
        <div class="nav-group"><a class="{'active' if active == 'resources' else ''}" href="/resources/">Resources {icon('chevron-down', 14)}</a><div class="dropdown"><a href="/resources/download/">Download</a><a href="/resources/faq/">FAQ</a><a href="/resources/cases/">Cases</a></div></div>
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
        <section><h2>CONTACT US</h2><dl class="contact-list"><div><dt>Address</dt><dd>{esc(COMPANY['location'])}</dd></div><div><dt>Telephone</dt><dd>&nbsp;</dd></div><div><dt>WhatsApp</dt><dd>&nbsp;</dd></div><div><dt>Email</dt><dd><a href="mailto:{esc(COMPANY['email'])}">{esc(COMPANY['email'])}</a></dd></div></dl></section>
        <section><h2>QUICK LINKS</h2><ul><li><a href="/">Home</a></li><li><a href="/company/">Company Profile</a></li><li><a href="/services/">Services</a></li><li><a href="/resources/download/">Download</a></li><li><a href="/resources/faq/">FAQ</a></li><li><a href="/resources/cases/">Cases</a></li><li><a href="/blogs/">Blogs</a></li><li><a href="/contact/">Contact Us</a></li></ul></section>
        <section><h2>PRODUCT CATEGORY</h2><ul>{category_links}</ul></section>
        <section><h2>NEWSLETTER</h2><p>Receive product and company updates.</p><form class="newsletter" onsubmit="return false"><label><span class="sr-only">Email address</span><input type="email" placeholder="Email address"></label><button type="submit" aria-label="Subscribe">{icon('send', 18)}</button></form></section>
      </div>
      <div class="footer-bottom"><div class="shell"><span>&copy; 2026 {esc(COMPANY['legal_name'])}</span><span>{esc(COMPANY['brand'])}</span></div></div>
    </footer>
    """


def organization_schema():
    return {
        "@type": "Organization",
        "name": COMPANY["legal_name"],
        "brand": COMPANY["brand"],
        "url": BASE_URL,
        "email": COMPANY["email"],
        "address": {"@type": "PostalAddress", "addressLocality": "Changxing", "addressRegion": "Zhejiang", "addressCountry": "CN"},
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
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="/assets/site.css"><script type="application/ld+json">{json_ld}</script></head>
<body>{header(active)}<main id="main">{body}</main>{footer()}<script src="https://unpkg.com/lucide@0.468.0/dist/umd/lucide.min.js"></script><script src="/assets/site.js"></script></body></html>"""


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
    <section class="hero"><div class="shell hero-grid"><div class="hero-copy"><p>LEXYGO MATERIAL HANDLING EQUIPMENT</p><h1>Electric Forklifts, Stackers &amp; Pallet Trucks</h1><p class="hero-intro">Direct product access for professional buyers, distributors, and material handling projects.</p>{button('View Products', '/products/', 'primary')} {button('Contact Us', '/contact/', 'light')}</div><div class="hero-machine"><img src="/assets/products/r4efl3t.png" alt="LEXYGO four-wheel electric forklift"></div></div></section>
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


def company_page():
    banner, crumb_schema = inner_banner("COMPANY PROFILE", [("Home", "/"), ("Company", None)])
    body = f"""{banner}<section class="company-profile"><div class="shell profile-grid"><div><p class="section-kicker">COMPANY PROFILE</p><h2>{esc(COMPANY['legal_name'])}</h2><p>LEXYGO is the material handling equipment range of our intelligent machinery factory in {esc(COMPANY['location'])}.</p><p>Our current range includes electric pallet trucks, electric pallet stackers, electric forklifts, manual pallet trucks, and warehouse equipment.</p></div><div class="company-machine"><img src="/assets/products/r4efl5t.png" alt="LEXYGO electric forklift"></div></div></section><section class="factory-stats"><div class="shell stats-grid"><div><strong>&nbsp;</strong><span>Factory Area</span></div><div><strong>&nbsp;</strong><span>Production Lines</span></div><div><strong>&nbsp;</strong><span>Annual Capacity</span></div><div><strong>&nbsp;</strong><span>Export Markets</span></div></div></section>"""
    return page("Company Profile", "Company profile for LEXYGO material handling equipment.", "/company/", body, crumb_schema, "company")


def resources_page():
    return blank_page("/resources/", "Resources", active="resources")


def blogs_page():
    return blank_page("/blogs/", "Blogs", active="blogs")


def contact_page():
    banner, crumb_schema = inner_banner("CONTACT US", [("Home", "/"), ("Contact Us", None)])
    body = f"""{banner}<section class="contact-page"><div class="shell contact-page-grid"><div><p class="section-kicker">CONTACT DETAILS</p><h2>Contact LEXYGO</h2><dl class="contact-details"><div><dt>Company</dt><dd>{esc(COMPANY['legal_name'])}</dd></div><div><dt>Address</dt><dd>{esc(COMPANY['location'])}</dd></div><div><dt>Email</dt><dd><a href="mailto:{esc(COMPANY['email'])}">{esc(COMPANY['email'])}</a></dd></div><div><dt>Telephone</dt><dd>&nbsp;</dd></div><div><dt>WhatsApp</dt><dd>&nbsp;</dd></div></dl></div>{inquiry_form()}</div></section>"""
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
    warehouse = ROOT / "tmp" / "warehouse-assets"
    explicit = {
        "r4efl12t.png": find_source_file("REEF12T.png"), "sc1016.png": warehouse / "image190.png", "qes12e.png": warehouse / "image251.png",
        "qes15e.png": warehouse / "image252.png", "qes15lie.png": warehouse / "image254.png", "qed1530.png": warehouse / "image191.png",
        "warehouse-scissor-lift-table.png": warehouse / "image139.png", "warehouse-material-lift-cart.png": warehouse / "image3.png",
    }
    for item in PRODUCTS:
        source = explicit[item["image"]] if item["image"] in explicit else find_source_file(item["image"])
        if not source.exists():
            raise FileNotFoundError(source)
        shutil.copy2(source, PRODUCT_ASSETS / item["image"])
    shutil.copy2(PRODUCT_ASSETS / "r4efl3t.png", ASSETS / "og-cover.png")


CSS = r"""
:root{--green:#0a6763;--green-dark:#074d4b;--orange:#ef7d25;--ink:#242a2d;--muted:#687277;--line:#d9dfe1;--soft:#f5f6f6;--white:#fff;--max:1200px}*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;color:var(--ink);font-family:Arial,"Helvetica Neue",sans-serif;line-height:1.6;background:#fff}img{display:block;max-width:100%}a{color:inherit;text-decoration:none}button,input,textarea{font:inherit}h1,h2,h3,p{overflow-wrap:anywhere;letter-spacing:0}.shell{width:min(calc(100% - 40px),var(--max));margin-inline:auto}.skip-link{position:fixed;left:8px;top:8px;z-index:1000;transform:translateY(-150%);background:#fff;padding:8px}.skip-link:focus{transform:none}.sr-only{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}
.top-strip{background:#293033;color:#cbd2d4;font-size:12px}.top-strip .shell{height:34px;display:flex;align-items:center;justify-content:flex-end;gap:28px}.top-strip a:hover{color:#fff}.site-header{position:sticky;top:0;z-index:80;background:#fff;border-bottom:1px solid var(--line)}.nav-row{height:82px;display:flex;align-items:center;justify-content:space-between;gap:35px}.brand{display:flex;flex-direction:column;line-height:1;min-width:180px}.brand strong{font-size:31px;color:var(--green-dark);font-weight:900}.brand small{font-size:10px;color:#555;margin-top:6px}.main-nav{height:100%;display:flex;align-items:stretch}.main-nav>a,.nav-group>a{position:relative;display:flex;align-items:center;gap:4px;padding:0 15px;font-size:14px;font-weight:700}.main-nav>a:after,.nav-group>a:after{content:"";position:absolute;left:15px;right:15px;bottom:0;height:3px;background:var(--orange);transform:scaleX(0);transition:.2s}.main-nav>a:hover,.nav-group:hover>a,.main-nav .active{color:var(--green)}.main-nav>a:hover:after,.nav-group:hover>a:after,.main-nav .active:after{transform:scaleX(1)}.nav-group{position:relative;display:flex}.dropdown{display:none;position:absolute;top:100%;left:0;min-width:220px;background:#fff;border-top:3px solid var(--orange);box-shadow:0 12px 28px rgba(0,0,0,.14);padding:8px 0}.dropdown a{display:block;padding:9px 15px;font-size:13px;border-bottom:1px solid #edf0f1}.dropdown a:hover{background:var(--soft);color:var(--green)}.nav-group:hover .dropdown{display:block}.wide-dropdown{min-width:270px}.menu-button{display:none;width:42px;height:42px;border:0;background:transparent;color:var(--ink)}
.hero{min-height:540px;background:linear-gradient(100deg,#074d4b 0%,#0a6763 58%,#e8f2f1 58%,#f6f8f8 100%);overflow:hidden}.hero-grid{min-height:540px;display:grid;grid-template-columns:1fr 1fr;align-items:center}.hero-copy{position:relative;z-index:2;color:#fff;padding:65px 30px 65px 0}.hero-copy>p:first-child{font-size:13px;font-weight:800;color:#bfe1de}.hero h1{font-size:50px;line-height:1.08;margin:12px 0 18px;max-width:640px}.hero-intro{font-size:18px;max-width:570px;color:#e7f1f0}.hero-machine{align-self:stretch;display:grid;place-items:center;padding:35px 0 35px 30px}.hero-machine img{width:116%;max-width:none;height:470px;object-fit:contain;filter:drop-shadow(0 24px 20px rgba(0,0,0,.18))}.button{display:inline-flex;align-items:center;justify-content:center;gap:8px;min-height:44px;padding:10px 18px;margin:10px 8px 0 0;border:1px solid transparent;font-size:13px;font-weight:800;text-transform:uppercase}.button-primary{background:var(--orange);color:#fff}.button-primary:hover{background:#d9650f}.button-light{background:#fff;color:var(--green-dark)}.button-outline{border-color:var(--green);color:var(--green);background:#fff}.button-outline:hover{background:var(--green);color:#fff}
.home-section{padding:70px 0}.section-heading{text-align:center;max-width:760px;margin:0 auto 36px}.section-heading span,.section-kicker{display:block;margin-bottom:7px;color:var(--orange);font-size:12px;font-weight:900;text-transform:uppercase}.section-heading h2,.about-grid h2,.contact-band h2,.detail-inquiry h2,.contact-page h2,.company-profile h2{font-size:32px;line-height:1.2;margin:0}.section-heading p{color:var(--muted);margin:12px auto 0}.featured-section{background:#fff}.featured-grid{display:grid;grid-template-columns:1.2fr .8fr;gap:18px}.featured-grid>.product-card{height:100%}.featured-grid>.product-card .product-image{height:410px}.featured-stack{display:grid;grid-template-columns:1fr;gap:18px}.featured-stack .product-card{display:grid;grid-template-columns:190px 1fr}.featured-stack .product-image{height:100%;min-height:160px}.featured-stack .product-card-copy{padding:16px}.featured-stack .product-card-copy ul{display:none}.center-action{text-align:center;margin-top:28px}.solutions-section{background:var(--soft)}.solution-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:18px}.solution-card{position:relative;height:285px;background:#fff;overflow:hidden}.solution-card img{width:100%;height:100%;object-fit:contain;padding:22px;transition:.25s}.solution-card span{position:absolute;left:0;right:0;bottom:0;padding:14px;background:rgba(7,77,75,.94);color:#fff;font-size:16px;font-weight:800}.solution-card:hover img{transform:scale(1.04)}.about-band{padding:0;background:#fff}.about-grid{display:grid;grid-template-columns:1fr 1fr;min-height:430px;align-items:center}.about-grid>div:first-child{padding:60px 60px 60px 0}.about-grid p{color:var(--muted)}.about-photo{align-self:stretch;background:#eef3f3;display:grid;place-items:center;overflow:hidden}.about-photo img{width:88%;height:390px;object-fit:contain}.factory-stats{background:var(--green-dark);color:#fff}.stats-grid{display:grid;grid-template-columns:repeat(4,1fr)}.stats-grid div{min-height:130px;display:flex;flex-direction:column;align-items:center;justify-content:center;border-right:1px solid rgba(255,255,255,.18)}.stats-grid div:last-child{border:0}.stats-grid strong{min-height:35px;font-size:30px}.stats-grid span{font-size:13px;color:#cce1df}.why-section{background:#fff}.why-grid{display:grid;grid-template-columns:repeat(3,1fr);border-top:1px solid var(--line);border-left:1px solid var(--line)}.why-grid article{padding:30px;border-right:1px solid var(--line);border-bottom:1px solid var(--line)}.why-grid article>span{font-size:30px;font-weight:900;color:#bdd2d1}.why-grid h3{font-size:19px;margin:14px 0 8px}.why-grid p{margin:0;color:var(--muted);font-size:14px}.showroom-section{background:var(--soft)}.blank-media{height:380px;border:1px solid var(--line);background:#fff}.cases-section{background:#fff}.blank-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:22px}.blank-grid.three{grid-template-columns:repeat(3,1fr)}.blank-grid article{height:260px;border:1px solid var(--line);background:var(--soft)}.insights-section{background:#fff}.contact-band{padding:65px 0;background:#eef3f3}.contact-band-grid,.detail-inquiry-grid{display:grid;grid-template-columns:.75fr 1.25fr;gap:65px;align-items:start}.contact-band-grid>div>p:not(.section-kicker),.detail-inquiry-grid>div>p:not(.section-kicker){color:var(--muted)}
.inner-banner{height:235px;display:grid;align-items:center;background:linear-gradient(rgba(7,55,54,.82),rgba(7,55,54,.82)),url('/assets/og-cover.png') center 58%/cover no-repeat;color:#fff;text-align:center}.inner-banner h1{font-size:38px;margin:0;text-transform:uppercase}.breadcrumbs{height:48px;display:flex;align-items:center;gap:6px;color:var(--muted);font-size:12px;border-bottom:1px solid var(--line)}.breadcrumbs a:hover{color:var(--orange)}.catalog-layout-section{padding:52px 0 75px}.catalog-layout{display:grid;grid-template-columns:260px minmax(0,1fr);gap:36px}.catalog-sidebar{min-width:0}.side-box{border:1px solid var(--line);margin-bottom:28px}.side-box>h2{margin:0;padding:13px 15px;background:var(--green);color:#fff;font-size:14px}.category-menu,.site-footer ul{margin:0;padding:0;list-style:none}.category-menu li+li{border-top:1px solid var(--line)}.category-menu a{display:flex;justify-content:space-between;gap:10px;padding:11px 13px;font-size:13px}.category-menu a:hover{color:var(--green);background:var(--soft)}.category-menu span{color:#999}.inquiry-box .compact-form{padding:15px}.catalog-title{border-bottom:1px solid var(--line);padding-bottom:18px;margin-bottom:25px}.catalog-title>p:first-child{margin:0 0 4px;color:var(--orange);font-size:12px;font-weight:900}.catalog-title h2{font-size:29px;margin:0 0 8px}.catalog-title>p:last-child{margin:0;color:var(--muted)}.category-answer{padding:15px 18px;margin:-5px 0 25px;background:var(--soft);border-left:4px solid var(--orange)}.category-answer strong{font-size:13px}.category-answer p{margin:3px 0 0;color:var(--muted);font-size:13px}.product-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:22px}.product-grid.four{grid-template-columns:repeat(4,minmax(0,1fr))}.product-card{min-width:0;background:#fff;border:1px solid var(--line);transition:.2s}.product-card:hover{box-shadow:0 10px 28px rgba(0,0,0,.09);transform:translateY(-2px)}.product-image{position:relative;height:225px;display:grid;place-items:center;overflow:hidden;background:#f7f8f8;padding:17px}.product-image img{width:100%;height:100%;object-fit:contain}.product-card-copy{padding:17px}.model-code{margin:0 0 4px;color:var(--green);font-size:12px;font-weight:900}.product-card h3{font-size:16px;line-height:1.35;margin:0 0 13px;min-height:44px}.product-card h3 a:hover{color:var(--green)}.product-card ul{margin:0 0 14px;padding:0;list-style:none;border-top:1px solid var(--line)}.product-card li{display:flex;justify-content:space-between;gap:8px;padding:6px 0;border-bottom:1px solid var(--line);font-size:11px}.product-card li span{color:var(--muted)}.product-card li strong{text-align:right}.card-actions{display:flex;justify-content:space-between;gap:15px}.card-actions a{color:var(--green);font-size:12px;font-weight:800}.card-actions a:first-child{color:var(--orange)}
.product-intro{padding:55px 0}.product-intro-grid{display:grid;grid-template-columns:1.05fr .95fr;gap:55px;align-items:center}.product-gallery{border:1px solid var(--line);background:#f7f8f8}.product-gallery .product-image{height:460px}.product-summary h2{font-size:33px;line-height:1.2;margin:6px 0 14px}.product-summary>p{color:var(--muted)}.feature-list{margin:22px 0;padding:0;list-style:none;border-top:1px solid var(--line)}.feature-list li{display:flex;justify-content:space-between;gap:20px;padding:9px 0;border-bottom:1px solid var(--line);font-size:13px}.feature-list span{color:var(--muted)}.feature-list strong{text-align:right}.availability{display:grid;grid-template-columns:1fr 1fr;margin:18px 0 6px}.availability div{border-left:3px solid var(--line);padding:4px 11px}.availability dt{font-size:11px;color:var(--muted)}.availability dd{min-height:22px;margin:2px 0 0}.product-identity{display:flex;gap:25px;margin-top:19px;font-size:12px;color:var(--muted)}.product-description{padding:55px 0;background:#fff}.tab-heading{border-bottom:2px solid var(--green);margin-bottom:25px}.tab-heading span{display:inline-block;padding:11px 18px;background:var(--green);color:#fff;font-weight:800}.description-grid{display:grid;grid-template-columns:1fr 1fr;gap:55px}.description-grid h2{font-size:25px;margin-top:0}.description-grid p{color:var(--muted)}.quick-table table{min-width:0}.parameter-section{padding:55px 0;background:var(--soft)}.spec-group{margin-bottom:25px}.spec-group h3{font-size:15px;margin:0;padding:11px 13px;background:var(--green-dark);color:#fff}.table-wrap{overflow-x:auto;background:#fff}table{width:100%;border-collapse:collapse;min-width:680px}th,td{padding:9px 12px;text-align:left;border:1px solid var(--line);font-size:12px}thead th{background:#e7ecec}.spec-empty{height:180px;background:#fff;border:1px solid var(--line)}.detail-inquiry{padding:60px 0;background:#eef3f3}.related-section{padding:65px 0}.related-section .product-image{height:180px}.related-section .product-card h3{font-size:14px}
.inquiry-form{background:#fff;border-top:4px solid var(--orange);padding:24px}.form-grid{display:grid;grid-template-columns:1fr 1fr;gap:13px}.form-grid label{font-size:11px;font-weight:700}.form-grid label span{display:block}.form-grid .full{grid-column:1/-1}.form-grid input,.form-grid textarea{width:100%;margin-top:4px;border:1px solid #bdc6c8;background:#fff;padding:9px;min-height:40px}.compact-form{border-top:0}.compact-form .form-grid{grid-template-columns:1fr}.compact-form .full{grid-column:auto}.compact-form .button{width:100%;margin-right:0}.company-profile,.contact-page,.blank-page{padding:65px 0}.profile-grid{display:grid;grid-template-columns:1fr 1fr;gap:60px;align-items:center}.profile-grid p{color:var(--muted)}.company-machine{height:390px;background:var(--soft);display:grid;place-items:center}.company-machine img{width:90%;height:90%;object-fit:contain}.contact-page-grid{display:grid;grid-template-columns:.75fr 1.25fr;gap:60px}.contact-details{margin:25px 0 0}.contact-details div{padding:11px 0;border-top:1px solid var(--line)}.contact-details dt{font-size:11px;color:var(--muted)}.contact-details dd{margin:3px 0 0;font-weight:700}.blank-page h2{font-size:29px;margin:0 0 22px}.blank-content{height:330px;border:1px solid var(--line);background:var(--soft)}
.site-footer{background:#222a2d;color:#bfc8ca;padding-top:55px}.footer-grid{display:grid;grid-template-columns:1.2fr .8fr 1.2fr 1fr;gap:45px}.site-footer h2{font-size:14px;color:#fff;margin:0 0 20px}.site-footer p,.site-footer li,.contact-list{font-size:12px}.site-footer li{margin:8px 0}.site-footer a:hover{color:#fff}.contact-list{margin:0}.contact-list div{margin-bottom:10px}.contact-list dt{color:#879598}.contact-list dd{margin:2px 0 0;min-height:19px}.newsletter{display:flex}.newsletter input{width:100%;height:42px;border:0;padding:8px}.newsletter button{width:45px;border:0;background:var(--orange);color:#fff}.footer-bottom{margin-top:45px;border-top:1px solid #3b4549}.footer-bottom .shell{min-height:58px;display:flex;align-items:center;justify-content:space-between;gap:20px;font-size:11px;color:#869397}
.source-brochure img{position:absolute;inset:0;width:100%;height:100%;max-width:none;object-fit:contain;transform:scale(3.2);transform-origin:75% 18%}.source-brochure-highlift img{transform:scale(2.6);transform-origin:85% 28%}.source-brochure-two-stage img{transform-origin:85% 28%}
@media(max-width:1050px){.main-nav{display:none;position:absolute;top:100%;left:0;right:0;height:auto;max-height:calc(100vh - 100px);overflow:auto;background:#fff;box-shadow:0 12px 25px rgba(0,0,0,.13);padding:10px 20px;align-items:stretch;flex-direction:column}.main-nav.is-open{display:flex}.main-nav>a,.nav-group>a{min-height:44px;padding:9px 5px}.nav-group{display:block}.nav-group:hover .dropdown{display:none}.dropdown{position:static;box-shadow:none;border-top:0;padding:0 0 5px 15px}.nav-group.is-open .dropdown{display:block}.menu-button{display:block}.hero h1{font-size:43px}.product-grid{grid-template-columns:repeat(2,1fr)}.product-grid.four{grid-template-columns:repeat(2,1fr)}.solution-grid{grid-template-columns:repeat(2,1fr)}.footer-grid{grid-template-columns:1fr 1fr}}
@media(max-width:760px){.shell{width:min(calc(100% - 28px),var(--max))}.top-strip{display:none}.nav-row{height:68px}.brand strong{font-size:26px}.brand small{font-size:8px}.hero{min-height:0;background:linear-gradient(160deg,var(--green-dark) 0 63%,#edf3f2 63%)}.hero-grid{min-height:0;grid-template-columns:1fr}.hero-copy{padding:45px 0 22px}.hero h1{font-size:37px}.hero-machine{height:285px;padding:0}.hero-machine img{height:300px;width:100%}.home-section{padding:52px 0}.section-heading h2,.about-grid h2,.contact-band h2,.detail-inquiry h2,.company-profile h2,.contact-page h2{font-size:27px}.featured-grid{grid-template-columns:1fr}.featured-grid>.product-card .product-image{height:280px}.featured-stack .product-card{grid-template-columns:130px 1fr}.solution-grid{grid-template-columns:1fr 1fr}.solution-card{height:220px}.about-grid,.profile-grid{grid-template-columns:1fr}.about-grid>div:first-child{padding:45px 0}.about-photo,.company-machine{height:320px}.stats-grid{grid-template-columns:1fr 1fr}.stats-grid div:nth-child(2){border-right:0}.stats-grid div:nth-child(-n+2){border-bottom:1px solid rgba(255,255,255,.18)}.why-grid{grid-template-columns:1fr}.blank-grid,.blank-grid.three{grid-template-columns:1fr}.blank-grid article{height:220px}.contact-band-grid,.detail-inquiry-grid,.contact-page-grid{grid-template-columns:1fr;gap:30px}.inner-banner{height:175px}.inner-banner h1{font-size:29px}.catalog-layout{grid-template-columns:1fr}.catalog-sidebar{order:2}.catalog-main{order:1}.inquiry-box{display:none}.category-menu{display:grid;grid-template-columns:1fr 1fr}.product-intro-grid{grid-template-columns:1fr;gap:30px}.product-gallery .product-image{height:340px}.product-summary h2{font-size:28px}.description-grid{grid-template-columns:1fr}.form-grid{grid-template-columns:1fr}.form-grid .full{grid-column:auto}.footer-grid{grid-template-columns:1fr}.footer-bottom .shell{align-items:flex-start;justify-content:center;flex-direction:column;padding-block:15px}.product-grid,.product-grid.four{grid-template-columns:1fr 1fr}.source-brochure img{transform:scale(3.2);transform-origin:75% 18%}.source-brochure-highlift img{transform:scale(2.6);transform-origin:85% 28%}.source-brochure-two-stage img{transform-origin:85% 28%}}
@media(max-width:500px){.hero h1{font-size:32px}.button{width:100%;margin-right:0}.solution-grid,.product-grid,.product-grid.four{grid-template-columns:1fr}.solution-card{height:245px}.featured-stack .product-card{grid-template-columns:115px 1fr}.category-menu{grid-template-columns:1fr}.product-card h3{min-height:0}.product-image{height:240px}.product-identity{flex-direction:column;gap:4px}.availability{grid-template-columns:1fr}.product-gallery .product-image{height:300px}}
"""


JS = r"""
document.addEventListener('DOMContentLoaded',()=>{if(window.lucide)window.lucide.createIcons();const button=document.querySelector('[data-menu-button]');const menu=document.querySelector('[data-menu]');if(button&&menu){button.addEventListener('click',()=>{const open=menu.classList.toggle('is-open');button.setAttribute('aria-expanded',String(open))});menu.querySelectorAll('.nav-group>a').forEach(link=>link.addEventListener('click',event=>{if(window.innerWidth<=1050&&link.nextElementSibling){event.preventDefault();link.parentElement.classList.toggle('is-open')}}))}const model=new URLSearchParams(location.search).get('model');document.querySelectorAll('[data-model-field]').forEach(field=>{if(model)field.value=model});document.querySelectorAll('[data-mailto-form]').forEach(form=>form.addEventListener('submit',event=>{event.preventDefault();const data=new FormData(form);const subject=`LEXYGO inquiry: ${data.get('model')||'material handling equipment'}${data.get('company')?' - '+data.get('company'):''}`;const body=[`Name: ${data.get('name')||''}`,`Email: ${data.get('email')||''}`,`Company: ${data.get('company')||''}`,`Country / Region: ${data.get('country')||''}`,`Product / Model: ${data.get('model')||''}`,'',`Message:`,` ${data.get('details')||''}`].join('\n');location.href=`mailto:${form.dataset.email}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`}))});
"""


FAVICON = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" fill="#0a6763"/><path d="M16 11h11v31h22v11H16z" fill="#fff"/><path d="M39 20h9v17h-9z" fill="#ef7d25"/></svg>"""


def build():
    if DIST.exists():
        shutil.rmtree(DIST)
    ASSETS.mkdir(parents=True)
    copy_product_assets()
    (ASSETS / "site.css").write_text(CSS, encoding="utf-8")
    (ASSETS / "site.js").write_text(JS, encoding="utf-8")
    (ASSETS / "favicon.svg").write_text(FAVICON, encoding="utf-8")

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
        "/company/why-choose-us/": blank_page("/company/why-choose-us/", "Why Choose Us", ("Company", "/company/"), "company"),
        "/company/quality-management/": blank_page("/company/quality-management/", "Quality Management", ("Company", "/company/"), "company"),
        "/services/": blank_page("/services/", "Services", active="services"),
        "/resources/": resources_page(),
        "/resources/download/": blank_page("/resources/download/", "Download", ("Resources", "/resources/"), "resources"),
        "/resources/faq/": blank_page("/resources/faq/", "FAQ", ("Resources", "/resources/"), "resources"),
        "/resources/cases/": blank_page("/resources/cases/", "Cases", ("Resources", "/resources/"), "resources"),
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
        "/guides/": static_pages["/resources/"],
        "/guides/forklift-capacity-and-aisle-width/": blank_page(
            "/guides/forklift-capacity-and-aisle-width/", "Forklift Capacity And Aisle Width", ("Resources", "/resources/"), "resources"
        ),
        "/guides/how-to-choose-an-electric-pallet-truck/": blank_page(
            "/guides/how-to-choose-an-electric-pallet-truck/", "How To Choose An Electric Pallet Truck", ("Resources", "/resources/"), "resources"
        ),
        "/guides/pallet-truck-vs-stacker/": blank_page(
            "/guides/pallet-truck-vs-stacker/", "Pallet Truck Vs Stacker", ("Resources", "/resources/"), "resources"
        ),
    }
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
    llms += ["", "## Contact", f"- Email: {COMPANY['email']}"]
    (DIST / "llms.txt").write_text("\n".join(llms) + "\n", encoding="utf-8")
    print(f"Built {len(routes)} routes and {len(PRODUCTS)} product pages in {DIST}")


if __name__ == "__main__":
    build()
