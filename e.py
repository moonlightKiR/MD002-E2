import requests
import json
from pydantic import BaseModel, ValidationError
from colorama import Fore

# Classes con Pydantic
class Trade(BaseModel):
    price: int
    currency: str
    priceRUB: int
    source: str

class Item(BaseModel):
    id: str
    shortName: str
    name: str
    basePrice: int
    buyFor: list[Trade]
    sellFor: list[Trade]

class Ammo(BaseModel):
    item: Item
    ammoType: str
    caliber: str
    projectileCount: int
    damage: int
    armorDamage: int
    fragmentationChance: float
    penetrationChance: float
    penetrationPower: int
    penetrationPowerDeviation: float | None = None
    accuracyModifier: float
    recoilModifier: float
    lightBleedModifier: float
    heavyBleedModifier: float
    staminaBurnPerDamage: float | None = None

class AmmoResponse(BaseModel):
    ammo: list[Ammo]

GRAPHQL_QUERY = """
{
  ammo(lang: en) {
    item {
      id
      shortName
      name
      basePrice
      buyFor {
        price
        currency
        priceRUB
        source
      }
      sellFor {
        price
        currency
        priceRUB
        source
      }
    }
    ammoType
    caliber
    projectileCount
    damage
    armorDamage
    fragmentationChance
    penetrationChance
    penetrationPower
    penetrationPowerDeviation
    accuracyModifier
    recoilModifier
    lightBleedModifier
    heavyBleedModifier
    staminaBurnPerDamage
  }
}
"""

def fetch_and_save_ammo_data():
    api_url = "https://api.tarkov.dev/graphql"
    output_filename = "ammo_data.json"
    
    print(f"{Fore.CYAN}Realizando solicitud a la API de Tarkov...")
    
    try:
        response = requests.post(api_url, json={'query': GRAPHQL_QUERY})
        response.raise_for_status() 
        raw_data = response.json()
        
        if 'errors' in raw_data:
            print(f"{Fore.RED}Error en la respuesta de GraphQL:")
            print(raw_data['errors'])
            return
            
        ammo_data = raw_data.get('data')
        if not ammo_data:
            print(f"{Fore.RED}No se encontró la clave 'data' en la respuesta.")
            return

        print("Validando datos con Pydantic...")
        try:
            # 1. Validación (igual que antes)
            validated_response = AmmoResponse(**ammo_data)
            print(f"{Fore.BLUE}Validación exitosa. Se encontraron {len(validated_response.ammo)} tipos de munición.")
            
            # --- INICIO DEL CAMBIO ---
            # 2. Transformación de los datos
            print(f"{Fore.BLUE}Aplanando la estructura de datos...")
            
            output_list = []
            for ammo_object in validated_response.ammo:
                # Convertimos el 'item' anidado a un diccionario
                item_data = ammo_object.item.model_dump()
                
                # Convertimos el objeto 'ammo' principal a un diccionario,
                # pero *excluimos* el 'item' para que no se duplique.
                ammo_data = ammo_object.model_dump(exclude={'item'})
                
                # Unimos los dos diccionarios. 
                # (Los campos del 'item' ahora están al mismo nivel)
                item_data.update(ammo_data)
                
                output_list.append(item_data)
            
            # 3. Guardado (ahora guardamos la 'output_list')
            print(f"{Fore.GREEN}Guardando {len(output_list)} items aplanados en '{output_filename}'...")
            
            with open(output_filename, "w", encoding="utf-8") as f:
                # Usamos json.dump() para guardar la lista directamente
                json.dump(output_list, f, indent=4, ensure_ascii=False)
            # --- FIN DEL CAMBIO ---
                
            print(f"¡Éxito! Datos aplanados guardados en '{output_filename}'.")

        except ValidationError as e:
            print(f"{Fore.RED}Error de validación de Pydantic:")
            print(e)

    except requests.exceptions.RequestException as e:
        print(f"{Fore.RED} al conectar con la API: {e}")
    except json.JSONDecodeError:
        print(f"{Fore.RED}Error: No se pudo decodificar la respuesta JSON de la API.")
