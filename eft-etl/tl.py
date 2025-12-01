from colorama import Fore, Style
import numpy as np


def clean_caliber_data(data: list) -> list:
    """
    Recorre la lista de municiones, elimina la palabra "Caliber" del campo 'caliber',
    e introduce un guion ('-') si el valor se convierte en una cadena vacía.

    Retorna la lista de datos modificada.
    """
    if not data:
        print(f"{Fore.RED}La lista de municiones está vacía. No hay datos para limpiar.")
        return []

    print(f"\n{Fore.CYAN}Limpiando el campo 'caliber'{Style.RESET_ALL}")

    count_cleaned = 0

    for item in data:
        # Verificamos que el campo 'caliber' exista y sea una cadena de texto
        if 'caliber' in item and isinstance(item['caliber'], str):
            original_value = item['caliber']

            # 1. Reemplazamos "Caliber" por una cadena vacía
            cleaned_value = original_value.replace("Caliber", "")

            # 2. Manejo de posibles espacios extra (opcional pero recomendado)
            cleaned_value = cleaned_value.strip()

            # 3. Asignamos el valor limpio de nuevo al diccionario
            item['caliber'] = cleaned_value

            # Si el valor cambió, incrementamos el contador
            if original_value != cleaned_value:
                count_cleaned += 1

    print(f"{Fore.GREEN}Limpieza completada. Se modificaron {count_cleaned} registros.")

    # Retornar la lista de datos modificada
    return data


def statistical_analitic(score: list) -> list:

    Q1 = np.percentile(score, 25)
    Q3 = np.percentile(score, 75)
    IQR = Q3 - Q1
    maxScoreValue = Q3 + (1.5 * IQR)
    print(f"{maxScoreValue}")
    return maxScoreValue


def normalize_and_update_scores(bullets_list: list[dict[str]]) -> list[dict[str]]:
    """
    Toma una lista de balas con 'meta_score' calculado, normaliza estos puntajes
    en una escala de 0 a 100 basada en el valor máximo encontrado, y actualiza
    cada diccionario con el nuevo campo 'normalized_score' y su 'tier'.
    """
    print("Normalizando scores")
    if not bullets_list:
        return []

    # 1. Encontrar el puntaje máximo (El "Techo" del Meta actual)
    # Extraemos todos los scores. Si la lista está vacía o el max es 0, evitamos errores.
    
    scores = [b.get('finalScore', 0) for b in bullets_list]
    max_score = statistical_analitic(scores)
    """"
    unique_scores_sorted = sorted(list(set(scores)), reverse=True)
    print(f"1 - Max : {unique_scores_sorted[0]}")
    print(f"2 - Max : {unique_scores_sorted[1]}")
    print(f"3 - Max : {unique_scores_sorted[2]}")
    max_score = unique_scores_sorted[2]  # max(scores) if scores else 0
    """

    if max_score == 0:
        print("Advertencia: El puntaje máximo es 0. No se puede normalizar.")
        return bullets_list

    print(f"Normalizando datos... (Puntaje Máximo de Referencia: {max_score:.2f})")


    # 2. Iterar, Normalizar y Actualizar
    for bullet in bullets_list:
        raw_score = bullet.get('finalScore', 0)

        # Fórmula de Normalización: (Valor / Máximo) * 100
        # Esto nos da un porcentaje de efectividad comparado con la mejor bala.
        normalized = (raw_score / max_score) * 100
        # Guardamos el valor redondeado a 1 decimal
        bullet['normalized'] = round(normalized, 1)

        # 3. Asignación Automática de Tier (Opcional pero útil)
        if normalized >= 95:
            tier = 'S+' # La crème de la crème (Meta absoluto)
        elif normalized >= 85:
            tier = 'S'  # Excelente
        elif normalized >= 70:
            tier = 'A'  # Muy bueno
        elif normalized >= 50:
            tier = 'B'  # Decente / Budget
        elif normalized >= 30:
            tier = 'C'  # Malo
        else:
            tier = 'D'  # "Scav tier" (Inusable)

        bullet['tier'] = tier

    # Retornamos la lista ordenada por el puntaje normalizado (de mayor a menor)
    return bullets_list

def calculate_finalScore(data: list):

    if not data:
        print(f"{Fore.RED}La lista de municiones está vacía. No hay datos para procesar.")
        return

    print(f"\n{Fore.CYAN}Análisis, Cálculo y Ordenamiento de Municiones.{Style.RESET_ALL}")

    # --- 1. Procesar y Calcular Campos ---
    for item in data:
        # a) Calcular finalScore 
        if 'finalScore' not in item:
            try:
                rawDamage = item.get('damage', 0) * item.get('projectileCount', 1)
                lethalScore = rawDamage * (1 + item.get('fragmentationChance', 0))
                penetrationScore = ((item.get('penetrationPower', 0) * 4.0) + (item.get('penetrationChance', 0) * 20)
                                    - (item.get('penetrationPowerDeviation', 0)))
                utilityScore = ((item.get('armorDamage', 0) * 1.5) + (item.get('lightBleedModifier', 0) * 50) +
                                (item.get('heavyBleedModifier', 0) * 75) + (item.get('staminaBurnPerDamage', 0) * 150))
                handlingScore = (item.get('accuracyModifier', 0) * 200) - (item.get('recoilModifier', 0) * 200)
                item['finalScore'] = ((penetrationScore * 1.8) + (lethalScore * 0.8) + (utilityScore * 0.5) +
                                      handlingScore)
            except TypeError:
                item['finalScore'] = 0

        # b) Encontrar el buyFor más bajo
        min_buy = None

        # Usamos 'priceRUB' para comparar y encontrar el precio más bajo en RUB
        for buy_offer in item.get('buyFor', []):
            if buy_offer.get('priceRUB'):
                # Usamos item['buyFor'][0] como un valor inicial si no hay 'min_buy' aún
                if min_buy is None or buy_offer['priceRUB'] < min_buy['priceRUB']:
                    min_buy = buy_offer

        # Almacenar solo la información relevante del precio más bajo
        if min_buy:
            item['minBuyPrice'] = {
                'price': min_buy.get('price'),
                'currency': min_buy.get('currency'),
                'source': min_buy.get('source')
            }
        else:
            item['minBuyPrice'] = {'price': 'N/A', 'currency': 'N/A', 'source': 'N/A'}

    print(f"{Fore.GREEN}Campos 'finalScore' y 'minBuyPrice' calculados/encontrados.")

    return data


def print_ammo(data: list):

    # --- 2. Ordenar por Múltiples Criterios (La lógica de ordenamiento no cambia) ---
    sorted_ammo = sorted(
        data,
        key=lambda item: (
            item['ammoType'],
            item['caliber'],
            -item['finalScore']
        )
    )

    # --- 3. Mostrar los Resultados ---

    print("\nOrdenado por: Tipo > Calibre > Daño Total (Mayor a Menor)\n")

    # NUEVO ORDEN DE ENCABEZADO: Calibre | DAÑO TOTAL | PRECIO MÁS BAJO
    print(f"{'NOMBRE':<30} | {'TIPO':<10} | {'CALIBRE':<15} | {'SCORE TOTAL':>12} | {'PRECIO MÁS BAJO':<20}")
    print("-" * 90)

    for ammo in sorted_ammo:
        price_info = ammo['minBuyPrice']

        # Formateamos la columna de precio
        price_display = f"{price_info['price']} {price_info['currency']} ({price_info['source']})"

        print(
            f"{ammo['name'][:28]:<30} | "
            f"{ammo['ammoType']:<10} | "
            f"{ammo['caliber']:<15} | "
            f"{ammo['tier']:>12} | "  # Columna de Daño (posición 4)
            f"{price_display:<20}"         # Columna de Precio (posición 5)
        )
    print("-" * 90)

    return sorted_ammo
