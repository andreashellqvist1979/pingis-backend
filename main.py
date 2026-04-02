from typing import List, Literal, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(
    title="Pingis Shopping Backend v1",
    version="0.1.4",
    description=(
        "Minimal backend for a shopping GPT that recommends a complete table-tennis setup "
        "and can later be extended with real shop integrations."
    ),
    servers=[
        {
            "url": "https://pingis-backend.onrender.com",
            "description": "Production server",
        }
    ],
)

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
    preference: Literal["budget", "best_value", "premium_within_budget"] = "best_value"

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
                    "preference": "best_value",
                }
            ]
        }
    }


class SetupLine(BaseModel):
    slot: Literal["blade", "forehand_rubber", "backhand_rubber", "glue", "protect_film"]
    product: Product


class SetupOption(BaseModel):
    label: str
    lines: List[SetupLine]
    products_total_sek: int
    shipping_total_sek: int
    grand_total_sek: int
    within_budget: bool
    compromise_notes: List[str] = []


class BuildSetupResponse(BaseModel):
    selected_store: str
    budget_sek: int
    best_within_budget: Optional[SetupOption] = None
    closest_over_budget: Optional[SetupOption] = None
    budget_compromise: Optional[SetupOption] = None
    summary: str
    next_step: str


class SearchProductsRequest(BaseModel):
    query: str
    store: Optional[str] = None
    country: str = "SE"


class SearchProductsResponse(BaseModel):
    matches: List[Product]


# -----------------------------
# Mock catalog
# -----------------------------
CATALOG: List[Product] = [
    # TableTennis11 blades
    Product(
        sku="tt11-blade-donic-waldner-allplay",
        store="TableTennis11",
        country="EE",
        type="blade",
        brand="Donic",
        name="Waldner Allplay",
        price_sek=399,
        assembled_by_store=True,
        url="https://tabletennis11.com/",
        notes="Budget-friendly allround blade.",
    ),
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
        sku="tt11-blade-yasaka-sweden-extra",
        store="TableTennis11",
        country="EE",
        type="blade",
        brand="Yasaka",
        name="Sweden Extra",
        price_sek=599,
        assembled_by_store=True,
        url="https://tabletennis11.com/",
        notes="Higher-quality allround/offensive blade with better feel.",
    ),

    # TableTennis11 rubbers - sticky FH
    Product(
        sku="tt11-rubber-friendship-729-super-fx",
        store="TableTennis11",
        country="EE",
        type="rubber",
        brand="729 Friendship",
        name="Super FX",
        price_sek=169,
        sticky=True,
        beginner_friendly=True,
        assembled_by_store=True,
        url="https://tabletennis11.com/",
        notes="Cheaper sticky rubber with simpler feel.",
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

    # TableTennis11 rubbers - non-sticky / BH / premium
    Product(
        sku="tt11-rubber-yasaka-original-extra-hg",
        store="TableTennis11",
        country="EE",
        type="rubber",
        brand="Yasaka",
        name="Original Extra HG",
        price_sek=199,
        sticky=False,
        beginner_friendly=True,
        assembled_by_store=True,
        url="https://tabletennis11.com/",
        notes="Budget backhand rubber.",
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
        sku="tt11-rubber-yasaka-mark-v",
        store="TableTennis11",
        country="EE",
        type="rubber",
        brand="Yasaka",
        name="Mark V",
        price_sek=299,
        sticky=False,
        beginner_friendly=True,
        assembled_by_store=True,
        url="https://tabletennis11.com/",
        notes="Classic quality rubber with balanced control and speed.",
    ),
    Product(
        sku="tt11-rubber-yasaka-rakza-7",
        store="TableTennis11",
        country="EE",
        type="rubber",
        brand="Yasaka",
        name="Rakza 7",
        price_sek=449,
        sticky=False,
        beginner_friendly=False,
        assembled_by_store=True,
        url="https://tabletennis11.com/",
        notes="Modern offensive rubber with much more speed and spin.",
    ),

    # TableTennis11 accessories
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

    # TT-Shop blades
    Product(
        sku="ttshop-blade-andro-kinetic-allround",
        store="TT-Shop",
        country="DE",
        type="blade",
        brand="Andro",
        name="Kinetic Allround",
        price_sek=419,
        assembled_by_store=True,
        url="https://www.tt-shop.com/",
        notes="Affordable allround blade.",
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
        sku="ttshop-blade-yasaka-sweden-extra",
        store="TT-Shop",
        country="DE",
        type="blade",
        brand="Yasaka",
        name="Sweden Extra",
        price_sek=619,
        assembled_by_store=True,
        url="https://www.tt-shop.com/",
        notes="Higher-quality allround/offensive blade.",
    ),

    # TT-Shop rubbers
    Product(
        sku="ttshop-rubber-friendship-729-super-fx",
        store="TT-Shop",
        country="DE",
        type="rubber",
        brand="729 Friendship",
        name="Super FX",
        price_sek=179,
        sticky=True,
        beginner_friendly=True,
        assembled_by_store=True,
        url="https://www.tt-shop.com/",
        notes="Budget sticky forehand rubber.",
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
        sku="ttshop-rubber-donic-vario",
        store="TT-Shop",
        country="DE",
        type="rubber",
        brand="Donic",
        name="Vario",
        price_sek=219,
        sticky=False,
        beginner_friendly=True,
        assembled_by_store=True,
        url="https://www.tt-shop.com/",
        notes="Budget backhand rubber.",
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
        sku="ttshop-rubber-yasaka-rakza-7",
        store="TT-Shop",
        country="DE",
        type="rubber",
        brand="Yasaka",
        name="Rakza 7",
        price_sek=459,
        sticky=False,
        beginner_friendly=False,
        assembled_by_store=True,
        url="https://www.tt-shop.com/",
        notes="Modern offensive rubber with much more speed and spin.",
    ),

    # TT-Shop accessories
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
    return 79


def _pick_first(items: List[Product]) -> Optional[Product]:
    return items[0] if items else None


def _store_priority(store: str) -> int:
    priorities = {
        "TableTennis11": 0,
        "TT-Shop": 1,
    }
    return priorities.get(store, 99)


def _is_complete_option(option: "SetupOption") -> bool:
    slots = {line.slot for line in option.lines}
    return "forehand_rubber" in slots and "backhand_rubber" in slots


def _has_glue(option: "SetupOption") -> bool:
    return any(line.slot == "glue" for line in option.lines)


def _has_film(option: "SetupOption") -> bool:
    return any(line.slot == "protect_film" for line in option.lines)


def _label_priority(label: str) -> int:
    priorities = {
        "full_setup": 0,
        "premium_upgrade": 1,
        "no_glue": 2,
        "no_glue_no_film": 3,
        "budget_compromise": 4,
        "absolute_minimum": 5,
    }
    return priorities.get(label, 99)


def _budget_distance(option: "SetupOption", budget_sek: int) -> int:
    return budget_sek - option.grand_total_sek


def _option_score_within_budget(option: "SetupOption", budget_sek: int, preference: str = "best_value") -> tuple:
    """
    Lägre tuple = bättre val.
    """
    distance = _budget_distance(option, budget_sek)

    if preference == "budget":
        return (
            not _is_complete_option(option),
            _label_priority(option.label),
            option.grand_total_sek,
            -int(_has_glue(option)),
            -int(_has_film(option)),
        )

    if preference == "premium_within_budget":
        return (
            not _is_complete_option(option),
            distance,
            _label_priority(option.label),
            -option.products_total_sek,
            -int(_has_glue(option)),
            -int(_has_film(option)),
        )

    # best_value
    return (
        not _is_complete_option(option),
        _label_priority(option.label),
        distance,
        -int(_has_glue(option)),
        -int(_has_film(option)),
        -option.products_total_sek,
    )


def _option_score_over_budget(option: "SetupOption", budget_sek: int) -> tuple:
    overshoot = option.grand_total_sek - budget_sek
    return (
        not _is_complete_option(option),
        _label_priority(option.label),
        overshoot,
        option.grand_total_sek,
    )


def _make_option(
    *,
    store: str,
    req: BuildSetupRequest,
    label: str,
    blade: Product,
    fh: Product,
    bh: Optional[Product] = None,
    glue: Optional[Product] = None,
    film: Optional[Product] = None,
    compromise_notes: Optional[List[str]] = None,
) -> SetupOption:
    lines: List[SetupLine] = [
        SetupLine(slot="blade", product=blade),
        SetupLine(slot="forehand_rubber", product=fh),
    ]

    if bh is not None:
        lines.append(SetupLine(slot="backhand_rubber", product=bh))
    if glue is not None:
        lines.append(SetupLine(slot="glue", product=glue))
    if film is not None:
        lines.append(SetupLine(slot="protect_film", product=film))

    products_total = sum(line.product.price_sek for line in lines)
    shipping_total = _shipping_for_store(store)
    grand_total = products_total + shipping_total

    return SetupOption(
        label=label,
        lines=lines,
        products_total_sek=products_total,
        shipping_total_sek=shipping_total,
        grand_total_sek=grand_total,
        within_budget=grand_total <= req.budget_sek,
        compromise_notes=compromise_notes or [],
    )


def _first_different(candidates: List[Product], sku_to_avoid: str) -> Optional[Product]:
    return next((p for p in candidates if p.sku != sku_to_avoid), None)


def _build_candidate_options(req: BuildSetupRequest, store: str) -> List[SetupOption]:
    blade_options = _find_products(store, "blade")
    sticky_rubbers = _find_products(store, "rubber", sticky=True)
    nonsticky_rubbers = _find_products(store, "rubber", sticky=False)
    all_rubbers = _find_products(store, "rubber")
    glue = _pick_first(_find_products(store, "glue"))
    film = _pick_first(_find_products(store, "accessory"))

    if not blade_options:
        return []

    # Blade profiles
    blade_budget = blade_options[0]
    blade_mid = blade_options[min(1, len(blade_options) - 1)]
    blade_premium = blade_options[-1]

    # FH profiles
    fh_budget = _pick_first([p for p in sticky_rubbers if p.price_sek <= 200]) or _pick_first(sticky_rubbers) or _pick_first(all_rubbers)
    fh_default = _pick_first(sticky_rubbers) or _pick_first(all_rubbers)
    fh_premium = _pick_first([p for p in all_rubbers if "Rakza 7" in p.name]) or all_rubbers[-1] if all_rubbers else None

    if not fh_default:
        return []

    # BH profiles
    bh_budget = _first_different([p for p in nonsticky_rubbers if p.price_sek <= 220], fh_budget.sku if fh_budget else "")
    if bh_budget is None:
        bh_budget = _first_different(nonsticky_rubbers, fh_budget.sku if fh_budget else "")
    if bh_budget is None:
        bh_budget = _first_different(all_rubbers, fh_budget.sku if fh_budget else "")

    bh_default = _first_different(nonsticky_rubbers, fh_default.sku)
    if bh_default is None:
        bh_default = _first_different(all_rubbers, fh_default.sku)

    bh_premium = _pick_first([p for p in nonsticky_rubbers if "Mark V" in p.name or "Rakza 7" in p.name])
    if bh_premium is None or (fh_premium and bh_premium.sku == fh_premium.sku):
        bh_premium = _first_different(nonsticky_rubbers, fh_premium.sku if fh_premium else "")
    if bh_premium is None:
        bh_premium = _first_different(all_rubbers, fh_premium.sku if fh_premium else "")

    options: List[SetupOption] = []

    # Full setup - standard
    if req.include_backhand_rubber and fh_default and bh_default:
        options.append(
            _make_option(
                store=store,
                req=req,
                label="full_setup",
                blade=blade_budget,
                fh=fh_default,
                bh=bh_default,
                glue=glue if req.include_glue else None,
                film=film if req.include_protect_film else None,
                compromise_notes=[],
            )
        )

    # Full setup - premium upgrade within budget if possible
    if req.include_backhand_rubber and fh_premium and bh_premium:
        options.append(
            _make_option(
                store=store,
                req=req,
                label="premium_upgrade",
                blade=blade_premium,
                fh=fh_premium,
                bh=bh_premium,
                glue=glue if req.include_glue else None,
                film=film if req.include_protect_film else None,
                compromise_notes=["Uppgraderad setup med bättre trä och/eller gummin."],
            )
        )

    # No glue
    if req.include_backhand_rubber and fh_default and bh_default:
        options.append(
            _make_option(
                store=store,
                req=req,
                label="no_glue",
                blade=blade_budget,
                fh=fh_default,
                bh=bh_default,
                glue=None,
                film=film if req.include_protect_film else None,
                compromise_notes=["Skippa lim och välj montering i butik om det erbjuds."],
            )
        )

    # No glue, no film
    if req.include_backhand_rubber and fh_default and bh_default:
        options.append(
            _make_option(
                store=store,
                req=req,
                label="no_glue_no_film",
                blade=blade_budget,
                fh=fh_default,
                bh=bh_default,
                glue=None,
                film=None,
                compromise_notes=[
                    "Skippa lim och välj montering i butik om det erbjuds.",
                    "Skippa skyddsfilm till att börja med.",
                ],
            )
        )

    # Budget compromise
    if req.include_backhand_rubber and fh_budget and bh_budget:
        options.append(
            _make_option(
                store=store,
                req=req,
                label="budget_compromise",
                blade=blade_budget,
                fh=fh_budget,
                bh=bh_budget,
                glue=None,
                film=None,
                compromise_notes=[
                    "Välj billigare forehand-gummi för att klara budgeten.",
                    "Skippa lim och skyddsfilm till att börja med.",
                ],
            )
        )

    # Mid upgrade
    if req.include_backhand_rubber and fh_default and bh_premium:
        options.append(
            _make_option(
                store=store,
                req=req,
                label="premium_upgrade",
                blade=blade_mid,
                fh=fh_default,
                bh=bh_premium,
                glue=glue if req.include_glue else None,
                film=film if req.include_protect_film else None,
                compromise_notes=["Mellannivå med bättre känsla och kvalitet."],
            )
        )

    # Absolute minimum
    if fh_budget:
        options.append(
            _make_option(
                store=store,
                req=req,
                label="absolute_minimum",
                blade=blade_budget,
                fh=fh_budget,
                bh=None,
                glue=None,
                film=None,
                compromise_notes=[
                    "Endast ett gummi ingår.",
                    "Detta är billigast möjliga start men inte ett komplett racket med två sidor.",
                ],
            )
        )

    deduped: List[SetupOption] = []
    seen = set()
    for option in options:
        key = (
            option.label,
            tuple((line.slot, line.product.sku) for line in option.lines),
            option.grand_total_sek,
        )
        if key not in seen:
            deduped.append(option)
            seen.add(key)

    return deduped


def _best_response_for_store(req: BuildSetupRequest, store: str) -> Optional[BuildSetupResponse]:
    candidates = _build_candidate_options(req, store)
    if not candidates:
        return None

    within_budget = sorted(
        [c for c in candidates if c.within_budget],
        key=lambda c: _option_score_within_budget(c, req.budget_sek, req.preference),
    )

    over_budget = sorted(
        [c for c in candidates if not c.within_budget],
        key=lambda c: _option_score_over_budget(c, req.budget_sek),
    )

    best_within_budget = within_budget[0] if within_budget else None
    closest_over_budget = over_budget[0] if over_budget else None

    compromise_candidates = [
        c for c in candidates
        if c.label in {"budget_compromise", "no_glue", "no_glue_no_film", "absolute_minimum"}
    ]
    compromise_candidates = sorted(
        compromise_candidates,
        key=lambda c: (
            not c.within_budget,
            not _is_complete_option(c),
            _label_priority(c.label),
            abs(req.budget_sek - c.grand_total_sek) if c.within_budget else (c.grand_total_sek - req.budget_sek),
        ),
    )
    budget_compromise = compromise_candidates[0] if compromise_candidates else None

    if best_within_budget:
        summary = (
            f"Found a setup from {store} within the user's budget. "
            f"Main recommendation: {best_within_budget.label}."
        )
        next_step = "Present the best option first. If relevant, also mention the closest over-budget alternative."
    else:
        summary = (
            f"No setup from {store} fit within budget. "
            f"Returning the closest over-budget option and a cheaper compromise."
        )
        next_step = "Explain clearly that no within-budget setup exists and show the nearest alternative."

    return BuildSetupResponse(
        selected_store=store,
        budget_sek=req.budget_sek,
        best_within_budget=best_within_budget,
        closest_over_budget=closest_over_budget,
        budget_compromise=budget_compromise,
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


@app.post(
    "/search-products",
    response_model=SearchProductsResponse,
    tags=["shopping"],
    openapi_extra={"x-openai-isConsequential": False},
)
def search_products(req: SearchProductsRequest):
    q = req.query.lower().strip()
    matches = [
        p for p in CATALOG
        if (req.store is None or p.store.lower() == req.store.lower())
        and q in f"{p.brand} {p.name} {p.type} {p.notes or ''}".lower()
    ]
    return SearchProductsResponse(matches=matches)


@app.post(
    "/build-setup",
    response_model=BuildSetupResponse,
    tags=["shopping"],
    openapi_extra={"x-openai-isConsequential": False},
)
def build_setup(req: BuildSetupRequest):
    stores = STORE_PRIORITY[:] if req.prefers_same_store else sorted({p.store for p in CATALOG})
    responses: List[BuildSetupResponse] = []

    for store in stores:
        response = _best_response_for_store(req, store)
        if response:
            responses.append(response)

    if not responses:
        raise HTTPException(status_code=404, detail="No valid setup found for the request.")

    responses.sort(
        key=lambda r: (
            r.best_within_budget is None,
            _store_priority(r.selected_store),
            _option_score_within_budget(r.best_within_budget, req.budget_sek, req.preference)
            if r.best_within_budget else (True, 99, 999999, 0, 0, 0),
            _option_score_over_budget(r.closest_over_budget, req.budget_sek)
            if r.closest_over_budget else (True, 99, 999999, 999999),
        )
    )
    return responses[0]


@app.post(
    "/create-cart",
    tags=["shopping"],
    openapi_extra={"x-openai-isConsequential": True},
)
def create_cart(req: BuildSetupRequest):
    response = build_setup(req)
    chosen_option = response.best_within_budget or response.budget_compromise or response.closest_over_budget
    if not chosen_option:
        raise HTTPException(status_code=404, detail="No setup option available for cart creation.")

    cart_items = [
        {
            "sku": line.product.sku,
            "name": f"{line.product.brand} {line.product.name}",
            "store": line.product.store,
            "url": line.product.url,
        }
        for line in chosen_option.lines
    ]
    return {
        "selected_store": response.selected_store,
        "chosen_option_label": chosen_option.label,
        "cart_status": "not_yet_integrated",
        "message": "Backend v1.4 returns the chosen items. Replace this with a real shop cart API later.",
        "cart_items": cart_items,
        "estimated_total_sek": chosen_option.grand_total_sek,
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
