from typing import List, Literal, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(
    title="Pingis Shopping Backend v1",
    version="0.1.0",
    description=(
        "Minimal backend for a shopping GPT that recommends a complete table-tennis setup "
        "and can later be extended with real shop integrations."
    ),
    servers=[
        {
            "url": "https://pingis-backend.onrender.com",
            "description": "Production server"
        }
    ],
)

# For local GPT/action testing. Tighten this later.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------
# Data models
# -----------------------------
class Product(BaseModel):
    sku: str
    store: str
    country: str
    type: Literal["blade", "rubber", "glue", "accessory"]
    brand: str
    name: str
    price_sek: int
    currency: str = "SEK"
    shipping_to_sweden: bool = True
    estimated_shipping_sek: int = 79
    sticky: bool = False
    assembled_by_store: bool = False
    beginner_friendly: bool = True
    url: str
    notes: Optional[str] = None


class BuildSetupRequest(BaseModel):
    budget_sek: int = Field(..., ge=300, le=5000)
    wants_sticky_rubber: bool = True
    wants_easy_setup: bool = True
    prefers_same_store: bool = True
    skill_level: Literal["beginner", "intermediate"] = "beginner"
    country: str = "SE"
    include_backhand_rubber: bool = True
    include_glue: bool = True
    include_protect_film: bool = True

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "budget_sek": 900,
                    "wants_sticky_rubber": True,
                    "wants_easy_setup": True,
                    "prefers_same_store": True,
                    "skill_level": "beginner",
                    "country": "SE",
                    "include_backhand_rubber": True,
                    "include_glue": True,
                    "include_protect_film": True,
                }
            ]
        }
    }


class SetupLine(BaseModel):
    slot: Literal["blade", "forehand_rubber", "backhand_rubber", "glue", "protect_film"]
    product: Product


class BuildSetupResponse(BaseModel):
    selected_store: str
    lines: List[SetupLine]
    products_total_sek: int
    shipping_total_sek: int
    grand_total_sek: int
    within_budget: bool
    summary: str
    next_step: str


class SearchProductsRequest(BaseModel):
    query: str
    store: Optional[str] = None
    country: str = "SE"


class SearchProductsResponse(BaseModel):
    matches: List[Product]


# -----------------------------
# Mock catalog (v1)
# Replace this with real store/API integration later.
# -----------------------------
CATALOG: List[Product] = [
    Product(
        sku="tt11-blade-stiga-allround-classic",
        store="TableTennis11",
        country="EE",
        type="blade",
        brand="Stiga",
        name="Allround Classic",
        price_sek=449,
        assembled_by_store=True,
        url="https://tabletennis11.com/",
        notes="Safe beginner blade with good control.",
    ),
    Product(
        sku="tt11-rubber-dhs-neo-hurricane-3",
        store="TableTennis11",
        country="EE",
        type="rubber",
        brand="DHS",
        name="Neo Hurricane 3",
        price_sek=299,
        sticky=True,
        beginner_friendly=True,
        assembled_by_store=True,
        url="https://tabletennis11.com/",
        notes="Sticky Chinese forehand rubber for spin.",
    ),
    Product(
        sku="tt11-rubber-xiom-musa",
        store="TableTennis11",
        country="EE",
        type="rubber",
        brand="Xiom",
        name="Musa",
        price_sek=259,
        sticky=False,
        beginner_friendly=True,
        assembled_by_store=True,
        url="https://tabletennis11.com/",
        notes="Simple, forgiving backhand rubber.",
    ),
    Product(
        sku="tt11-glue-butterfly-free-chack-ii",
        store="TableTennis11",
        country="EE",
        type="glue",
        brand="Butterfly",
        name="Free Chack II",
        price_sek=119,
        url="https://tabletennis11.com/",
        notes="Water-based table tennis glue.",
    ),
    Product(
        sku="tt11-film-butterfly-protect-film",
        store="TableTennis11",
        country="EE",
        type="accessory",
        brand="Butterfly",
        name="Rubber Protect Film",
        price_sek=49,
        url="https://tabletennis11.com/",
        notes="Protects tacky rubber between sessions.",
    ),
    Product(
        sku="ttshop-blade-donic-appelgren-allplay",
        store="TT-Shop",
        country="DE",
        type="blade",
        brand="Donic",
        name="Appelgren Allplay",
        price_sek=479,
        assembled_by_store=True,
        url="https://www.tt-shop.com/",
        notes="Another allround beginner blade.",
    ),
    Product(
        sku="ttshop-rubber-dhs-neo-hurricane-3",
        store="TT-Shop",
        country="DE",
        type="rubber",
        brand="DHS",
        name="Neo Hurricane 3",
        price_sek=319,
        sticky=True,
        beginner_friendly=True,
        assembled_by_store=True,
        url="https://www.tt-shop.com/",
        notes="Sticky forehand rubber.",
    ),
    Product(
        sku="ttshop-rubber-yasaka-mark-v",
        store="TT-Shop",
        country="DE",
        type="rubber",
        brand="Yasaka",
        name="Mark V",
        price_sek=299,
        sticky=False,
        beginner_friendly=True,
        assembled_by_store=True,
        url="https://www.tt-shop.com/",
        notes="Classic backhand rubber.",
    ),
    Product(
        sku="ttshop-glue-andro-turbo-fix",
        store="TT-Shop",
        country="DE",
        type="glue",
        brand="Andro",
        name="Turbo Fix",
        price_sek=99,
        url="https://www.tt-shop.com/",
        notes="Water-based glue.",
    ),
    Product(
        sku="ttshop-film-andro-rubber-protection",
        store="TT-Shop",
        country="DE",
        type="accessory",
        brand="Andro",
        name="Rubber Protection Film",
        price_sek=39,
        url="https://www.tt-shop.com/",
        notes="Protective film for rubber.",
    ),
]


STORE_PRIORITY = ["TableTennis11", "TT-Shop"]


# -----------------------------
# Helpers
# -----------------------------
def _find_products(store: str, ptype: str, sticky: Optional[bool] = None) -> List[Product]:
    items = [p for p in CATALOG if p.store == store and p.type == ptype and p.shipping_to_sweden]
    if sticky is not None:
        items = [p for p in items if p.sticky == sticky]
    return sorted(items, key=lambda p: p.price_sek)


def _shipping_for_store(store: str) -> int:
    # Very simple v1 logic: one shipping charge per selected store.
    store_items = [p for p in CATALOG if p.store == store]
    return min((p.estimated_shipping_sek for p in store_items), default=79)


def _build_from_store(req: BuildSetupRequest, store: str) -> Optional[BuildSetupResponse]:
    blade_options = _find_products(store, "blade")
    if not blade_options:
        return None

    fh_options = _find_products(store, "rubber", sticky=True if req.wants_sticky_rubber else None)
    if not fh_options and req.wants_sticky_rubber:
        fh_options = _find_products(store, "rubber")
    if not fh_options:
        return None

    bh_options = _find_products(store, "rubber", sticky=False)
    if req.include_backhand_rubber and not bh_options:
        bh_options = _find_products(store, "rubber")

    glue_options = _find_products(store, "glue") if req.include_glue else []
    film_options = _find_products(store, "accessory") if req.include_protect_film else []

    lines: List[SetupLine] = [
        SetupLine(slot="blade", product=blade_options[0]),
        SetupLine(slot="forehand_rubber", product=fh_options[0]),
    ]

    if req.include_backhand_rubber:
        if not bh_options:
            return None
        # Avoid selecting the same rubber object if possible
        bh_choice = next((p for p in bh_options if p.sku != fh_options[0].sku), bh_options[0])
        lines.append(SetupLine(slot="backhand_rubber", product=bh_choice))

    if req.include_glue:
        if not glue_options:
            return None
        lines.append(SetupLine(slot="glue", product=glue_options[0]))

    if req.include_protect_film:
        if not film_options:
            return None
        lines.append(SetupLine(slot="protect_film", product=film_options[0]))

    products_total = sum(line.product.price_sek for line in lines)
    shipping_total = _shipping_for_store(store)
    grand_total = products_total + shipping_total

    summary = (
        f"Selected {store} because it can cover the setup in one shop. "
        f"Forehand uses a sticky rubber for spin, and the rest is kept simple and budget-friendly."
    )

    if req.wants_easy_setup:
        next_step = (
            f"Open the store links and choose racket assembly if offered by {store}. "
            "That avoids doing the gluing yourself the first time."
        )
    else:
        next_step = "Buy the listed products and glue the rubbers to the blade yourself."

    return BuildSetupResponse(
        selected_store=store,
        lines=lines,
        products_total_sek=products_total,
        shipping_total_sek=shipping_total,
        grand_total_sek=grand_total,
        within_budget=grand_total <= req.budget_sek,
        summary=summary,
        next_step=next_step,
    )


# -----------------------------
# Routes
# -----------------------------
@app.get("/")
def root():
    return {
        "name": "Pingis Shopping Backend v1",
        "status": "ok",
        "docs": "/docs",
        "openapi": "/openapi.json",
    }


@app.post("/search-products", response_model=SearchProductsResponse, tags=["shopping"])
def search_products(req: SearchProductsRequest):
    q = req.query.lower().strip()
    matches = [
        p for p in CATALOG
        if (req.store is None or p.store.lower() == req.store.lower())
        and q in f"{p.brand} {p.name} {p.type} {p.notes or ''}".lower()
    ]
    return SearchProductsResponse(matches=matches)


@app.post("/build-setup", response_model=BuildSetupResponse, tags=["shopping"])
def build_setup(req: BuildSetupRequest):
    stores = STORE_PRIORITY[:] if req.prefers_same_store else sorted({p.store for p in CATALOG})

    candidates: List[BuildSetupResponse] = []
    for store in stores:
        candidate = _build_from_store(req, store)
        if candidate:
            candidates.append(candidate)

    if not candidates:
        raise HTTPException(status_code=404, detail="No valid setup found for the request.")

    # Prefer within budget first, then cheapest total.
    candidates.sort(key=lambda c: (not c.within_budget, c.grand_total_sek))
    best = candidates[0]
    return best


@app.post("/create-cart", tags=["shopping"])
def create_cart(req: BuildSetupRequest):
    # v1 placeholder: build the setup and return a cart intent structure.
    setup = build_setup(req)
    cart_items = [
        {
            "sku": line.product.sku,
            "name": f"{line.product.brand} {line.product.name}",
            "store": line.product.store,
            "url": line.product.url,
        }
        for line in setup.lines
    ]
    return {
        "selected_store": setup.selected_store,
        "cart_status": "not_yet_integrated",
        "message": "Backend v1 returns the chosen items. Replace this with a real shop cart API later.",
        "cart_items": cart_items,
        "estimated_total_sek": setup.grand_total_sek,
    }


@app.get("/checkout-link/{store}", tags=["shopping"])
def get_checkout_link(store: str):
    normalized = store.lower()
    if normalized == "tabletennis11":
        return {
            "store": "TableTennis11",
            "checkout_url": "https://tabletennis11.com/",
            "status": "manual_checkout_for_now",
        }
    if normalized in {"tt-shop", "ttshop"}:
        return {
            "store": "TT-Shop",
            "checkout_url": "https://www.tt-shop.com/",
            "status": "manual_checkout_for_now",
        }
    raise HTTPException(status_code=404, detail="Unknown store")
