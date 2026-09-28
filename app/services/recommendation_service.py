from typing import Any
from urllib.parse import quote_plus

PLATFORMS = {
    "Amazon": "https://www.amazon.in/s?k={q}",
    "Flipkart": "https://www.flipkart.com/search?q={q}",
    "IKEA": "https://www.ikea.com/in/en/search/?q={q}",
    "Swiggy": "https://www.swiggy.com/search?query={q}",
    "Zomato": "https://www.zomato.com/search?q={q}",
    "OYO": "https://www.oyorooms.com/search?location={q}",
}

def link(platform: str, query: str) -> str:
    template = PLATFORMS.get(platform, PLATFORMS["Amazon"])
    return template.format(q=quote_plus(query))

def fallback_home(data: dict[str, Any]) -> dict[str, Any]:
    budget = float(data["budget"])
    items = data.get("items") or [{"category": "Lighting", "quantity": 2}, {"category": "Wall Decor", "quantity": 2}]
    weights = {"Furniture": .35, "Lighting": .15, "Decor": .15, "Storage": .20, "Textiles": .10, "Wall Decor": .10}
    recs = []
    for item in items:
        category = item["category"]
        qty = item["quantity"]
        per = budget * weights.get(category, .10) / max(qty, 1)
        platform = "IKEA" if category.lower() in {"furniture", "storage", "textiles"} else "Amazon"
        recs.append({"category": category, "title": f"Budget-friendly {category} for {data['room_type']}", "description": f"A {data['style']} option sized for practical everyday use.", "estimated_price": round(per, 2), "quantity": qty, "platform": platform, "url": link(platform, f"{data['style']} {category}"), "why": "Keeps the recommendation within the requested budget allocation."})
    return {"planner":"home", "budget":budget, "allocated_budget":budget, "summary":f"A {data['style']} {data['room_type']} plan focused on value and budget control.", "tips":["Compare delivered prices before checkout.","Reserve 5–10% for installation or unexpected costs."],"recommendations":recs}

def fallback_party(data: dict[str, Any]) -> dict[str, Any]:
    budget = float(data["budget"])
    guests = int(data["guests"])
    allocations = [("Catering", .55, "Swiggy"), ("Decoration", .20, "Amazon"), ("Entertainment", .15, "Amazon"), ("Venue/Stay", .10, "OYO")]
    recs = []
    for category, share, platform in allocations:
        amount = budget * share
        q = f"{data['event_type']} {category}"
        recs.append({"category":category,"title":f"{data['event_type']} {category} package","description":f"Planning allowance for approximately {guests} guests.","estimated_price":round(amount,2),"quantity":1,"platform":platform,"url":link(platform,q),"why":f"Uses about {round(share*100)}% of the total budget to keep the event balanced."})
    return {"planner":"party","budget":budget,"allocated_budget":budget,"summary":f"A {data['event_type']} plan for {guests} guests with proportional spending across major event needs.","tips":["Get at least two catering quotes for the guest count.","Keep a contingency reserve for last-minute purchases."],"recommendations":recs}

def fallback_jewelry(data: dict[str, Any]) -> dict[str, Any]:
    budget = float(data["budget"])
    types = [data.get("jewelry_type") if data.get("jewelry_type") != "Any" else "Necklace", "Earrings", "Bracelet"]
    recs=[]
    shares=[.55,.25,.20]
    for typ, share in zip(types, shares):
        amount=budget*share
        query=f"{data['style']} {typ} {data['occasion']} {data.get('outfit_color','')}"
        recs.append({"category":typ,"title":f"{data['style']} {typ}","description":f"A style direction for {data['occasion']} in the requested budget range.","estimated_price":round(amount,2),"quantity":1,"platform":"Amazon","url":link("Amazon",query),"why":"Balances the main jewelry piece with supporting accessories without exceeding the budget."})
    return {"planner":"jewelry","budget":budget,"allocated_budget":budget,"summary":f"Jewelry styling for {data['occasion']} with a {data['style']} preference and outfit color {data.get('outfit_color','Not specified')}.","tips":["Check the actual product material and seller rating before purchase.","Use the outfit image and lighting in the room as a final color reference."],"recommendations":recs}
