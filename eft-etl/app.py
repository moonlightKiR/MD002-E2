from flask import Flask, jsonify, render_template_string
from pymongo import MongoClient
from collections import defaultdict

app = Flask(__name__)

# --- CONFIGURACIÓN ---
MONGO_URI = "mongodb://mongo:27017/"
DATABASE_NAME = "ammo_data"
COLLECTION_NAME = "bullets"

# --- FUNCIÓN DE UTILIDAD: ENCONTRAR MEJOR PRECIO ---
def get_best_trader_offer(bullet):
    """
    Busca la opción de compra más barata basándose en priceRUB.
    Retorna: { 'price': 123, 'currency': 'RUB', 'source': 'Prapor' } o None
    """
    offers = bullet.get('buyFor', [])
    
    if not offers:
        return None
        
    # Encontramos el mínimo basándonos en el valor normalizado en Rublos (priceRUB)
    # Usamos float('inf') para ignorar entradas sin precio válido
    best_offer = min(offers, key=lambda x: x.get('priceRUB', float('inf')))
    
    # Mapeo de símbolos de divisa para que quede bonito
    currency_map = {"RUB": "₽", "USD": "$", "EUR": "€"}
    currency_sym = currency_map.get(best_offer.get('currency'), best_offer.get('currency'))

    return {
        "price": best_offer.get('price'),
        "symbol": currency_sym,
        "source": best_offer.get('source').capitalize() # Ej: 'prapor' -> 'Prapor'
    }


def get_classified_data():
    client = MongoClient(MONGO_URI)
    db = client[DATABASE_NAME]
    collection = db[COLLECTION_NAME]

    cursor = collection.find({}, {"_id": 0})

    classified_data = defaultdict(lambda: defaultdict(list))

    count = 0
    for bullet in cursor:
        count += 1
        a_type = bullet.get("ammoType", "Desconocido")
        cal = bullet.get("caliber", "Desconocido")
        classified_data[a_type][cal].append(bullet)

    client.close()

    final_structure = {}
    for tipo, calibres in classified_data.items():
        final_structure[tipo] = {}
        for calibre, balas in calibres.items():
            # Ordenamos por penetración
            balas_ordenadas = sorted(balas, key=lambda x: x.get('penetrationPower', 0), reverse=True)
            final_structure[tipo][calibre] = balas_ordenadas

    return final_structure, count


# --- VISTA WEB ---
@app.route('/')
def index():
    data, total = get_classified_data()

    # Pasamos la función 'get_best_trader_offer' al contexto del template
    html_template = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Tarkov Ammo Meta</title>
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #121212; color: #e0e0e0; padding: 20px; }
            h1 { color: #f5a623; border-bottom: 2px solid #f5a623; padding-bottom: 10px; }

            .type-container { margin-bottom: 30px; background: #1e1e1e; padding: 15px; border-radius: 8px; border: 1px solid #333; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
            .type-title { font-size: 1.5em; color: #4ec9b0; text-transform: uppercase; margin-bottom: 15px; border-left: 4px solid #4ec9b0; padding-left: 10px; }
            .cal-container { margin-left: 10px; margin-bottom: 20px; }
            .cal-title { font-size: 1.2em; color: #569cd6; margin-bottom: 8px; font-weight: bold; margin-top: 15px; }

            table { width: 100%; border-collapse: collapse; background: #252526; font-size: 0.9em; }
            th, td { border-bottom: 1px solid #3e3e42; padding: 10px; text-align: left; vertical-align: middle; }
            th { background-color: #333; color: #fff; text-transform: uppercase; font-size: 0.8em; letter-spacing: 1px; }
            tr:hover { background-color: #2d2d30; }

            .ammo-img { width: 64px; height: 64px; object-fit: contain; background-color: #1a1a1a; border-radius: 4px; border: 1px solid #333; }

            /* Estilos de Precio y Trader */
            .price-container { display: flex; flex-direction: column; }
            .price-val { color: #85bb65; font-weight: bold; font-size: 1.1em; }
            .trader-val { font-size: 0.8em; color: #aaa; font-style: italic; }
            .no-price { color: #666; font-size: 0.8em; }

            .high-pen { color: #ff6b6b; font-weight: bold; }
            .stat-box { display:inline-block; padding: 2px 8px; border-radius: 4px; font-size: 0.85em; text-align: center; min-width: 25px; }

            .tier-s { background: #d4af37; color: black; font-weight: bold; box-shadow: 0 0 5px #d4af37; }
            .tier-a { background: #ff4500; color: white; }
            .tier-b { background: #1e90ff; color: white; }
            .tier-c { background: #32cd32; color: black; }
            .tier-d { background: #808080; color: white; }
            .tier-op { background: #9400d3; color: white; font-weight: bold; border: 1px solid white; }
        </style>
    </head>
    <body>
        <h1>📦 Tarkov Ammo Database ({total} items)</h1>

        {% for tipo, calibres in data.items() %}
            <div class="type-container">
                <div class="type-title">📂 {{ tipo }}</div>

                {% for calibre, balas in calibres.items() %}
                    <div class="cal-container">
                        <div class="cal-title">📐 {{ calibre }}</div>
                        <table>
                            <thead>
                                <tr>
                                    <th style="width: 80px;">Icon</th>
                                    <th>Name</th>
                                    <th>Best Price</th> <th>Damage</th>
                                    <th>Penetration</th>
                                    <th>Armor Dmg</th>
                                    <th>Score</th>
                                    <th>Tier</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for bala in balas %}
                                {% set img_url = bala.get('iconLink') or bala.get('item', {}).get('iconLink') %}

                                {% set best_deal = get_price_func(bala) %}

                                <tr>
                                    <td>
                                        {% if img_url %}
                                            <img src="{{ img_url }}" class="ammo-img">
                                        {% else %}
                                            <div class="ammo-img" style="display:flex;align-items:center;justify-content:center;color:#555;font-size:0.7em;">No Icon</div>
                                        {% endif %}
                                    </td>

                                    <td style="font-weight: bold; font-size: 1.1em;">
                                        {{ bala.get('name') }}
                                        <div style="font-size:0.8em; color:#888;">{{ bala.get('shortName') }}</div>
                                    </td>

                                    <td>
                                        {% if best_deal %}
                                            <div class="price-container">
                                                <span class="price-val">
                                                    {{ best_deal.symbol }} {{ best_deal.price }}
                                                </span>
                                                <span class="trader-val">
                                                    @ {{ best_deal.source }}
                                                </span>
                                            </div>
                                        {% else %}
                                            <span class="no-price">Not sold</span>
                                        {% endif %}
                                    </td>

                                    <td>{{ bala.get('damage') }}</td>
                                    <td class="high-pen">{{ bala.get('penetrationPower') }}</td>
                                    <td>{{ bala.get('armorDamage') }}</td>
                                    <td>{{ bala.get('normalized', 'N/A') }}</td>
                                    <td>
                                        {% if bala.get('tier') %}
                                            <span class="stat-box tier-{{ bala.get('tier').lower().replace('+','') }}">
                                                {{ bala.get('tier') }}
                                            </span>
                                        {% endif %}
                                    </td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                {% endfor %}
            </div>
        {% endfor %}
    </body>
    </html>
    """
    # IMPORTANTE: Pasamos la función python 'get_best_trader_offer' al template con el nombre 'get_price_func'
    return render_template_string(html_template, data=data, total=total, get_price_func=get_best_trader_offer)


# --- API JSON ---
@app.route('/api/ammo')
def api_ammo():
    data, count = get_classified_data()
    return jsonify({"total": count, "data": data})


if __name__ == '__main__':
    print("Servidor Flask activo: http://localhost:5000")
    app.run(debug=True, port=5000, host="0.0.0.0")
