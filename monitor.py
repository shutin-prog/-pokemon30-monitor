import os
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from zoneinfo import ZoneInfo

DISCORD_WEBHOOK = os.environ.get("DISCORD_WEBHOOK")
PARIS = ZoneInfo("Europe/Paris")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) "
        "AppleWebKit/605.1.15 Version/18.0 Mobile/15E148 Safari/604.1"
    ),
    "Accept-Language": "fr-FR,fr;q=0.9",
}

PRODUCTS = [
    (
        "LorenZone UPC Mentali / Noctali",
        "https://lorenzone.fr/products/coffret-ultra-premium-upc-30eme-anniversaire",
        270,
    ),
    (
        "LorenZone Classeur",
        "https://lorenzone.fr/products/classeur-collection-30eme-anniversaire",
        60,
    ),
    (
        "VCollect UPC Mentali",
        "https://vcollect.fr/products/upc-mentali-30e-anniversaire-francais",
        270,
    ),
    (
        "VCollect UPC Noctali",
        "https://vcollect.fr/products/upc-noctali-30e-anniversaire-francais",
        270,
    ),
    (
        "VCollect Classeur",
        "https://vcollect.fr/products/coffret-collection-classeur-30eme-anniversaire-francais",
        60,
    ),
    (
        "Hikaru UPC Mentali",
        "https://hikarudistribution.com/products/upc-mentali-collection-ultra-premium-30eme-anniversaire-francais",
        270,
    ),
    (
        "Hikaru UPC Noctali",
        "https://hikarudistribution.com/products/upc-noctali-collection-ultra-premium-30eme-anniversaire-francais",
        270,
    ),
    (
        "Hikaru Classeur",
        "https://hikarudistribution.com/products/coffret-collection-classeur-30eme-anniversaire",
        60,
    ),
]


def discord_alert(name, variant, price, url):
    if not DISCORD_WEBHOOK:
        print("Discord : webhook absent")
        return

    message = (
        "🚨 **STOCK POKÉMON 30e DÉTECTÉ !**\n"
        f"🏪 **{name}**\n"
        f"📦 {variant}\n"
        f"💶 **{price:.2f} €**\n"
        f"🔗 {url}\n"
        "⚠️ Vérifie le stock et finalise manuellement l'achat."
    )

    try:
        r = requests.post(
            DISCORD_WEBHOOK,
            json={"content": message},
            timeout=10,
        )
        print("Discord HTTP :", r.status_code)
    except requests.RequestException as e:
        print("Erreur Discord :", e)


def shopify(url):
    try:
        r = requests.get(
            url.rstrip("/") + ".js",
            headers=HEADERS,
            timeout=15,
        )

        if r.status_code != 200:
            return None

        data = r.json()

        if isinstance(data, dict) and "variants" in data:
            return data

    except (requests.RequestException, ValueError):
        pass

    return None


def analyser(name, url, plafond):
    print("\n" + "=" * 55)
    print(name)
    print(url)

    data = shopify(url)

    if not data:
        print("Données Shopify non disponibles.")
        return

    variants = data.get("variants", [])

    for variant in variants:
        title = variant.get("title") or "Default Title"
        available = bool(variant.get("available"))

        raw_price = variant.get("price")

        try:
            price = float(raw_price) / 100
        except (TypeError, ValueError):
            print(title, ": prix non détecté")
            continue

        print(f"{title} : {price:.2f} €")
        print("Disponible :", available)
        print("Plafond :", plafond, "€")

        if available and price <= plafond:
            print(">>> ALERTE STOCK <<<")
            discord_alert(name, title, price, url)


def main():
    print("=" * 55)
    print("BOT POKEMON 30e - GITHUB ACTIONS")
    print("Heure :", datetime.now(PARIS).strftime("%d/%m/%Y %H:%M:%S"))
    print("Paiement automatique : DESACTIVE")
    print("=" * 55)

    for name, url, plafond in PRODUCTS:
        analyser(name, url, plafond)

    print("\nVérification terminée.")


if __name__ == "__main__":
    main()
