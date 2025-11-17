from colorama import Fore, Style


def clean_caliber_data(data: list) -> list:
    """
    Recorre la lista de municiones, elimina la palabra "Caliber" del campo 'caliber',
    e introduce un guion ('-') si el valor se convierte en una cadena vacía.

    Retorna la lista de datos modificada.
    """
    if not data:
        print(f"{Fore.RED}La lista de municiones está vacía. No hay datos para limpiar.")
        return []

    print(f"\n{Fore.CYAN}impiando el campo 'caliber'{Style.RESET_ALL}")

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


def calculate_and_sort_ammo(data: list):
    """
    1. Calcula 'finalDamage'.
    2. Encuentra el 'minBuyPrice' (precio de compra más bajo).
    3. Ordena la lista por ammoType, caliber, y finalDamage (descendente).
    4. Muestra la tabla con el Daño antes del Precio.
    """
    if not data:
        print(f"{Fore.RED}La lista de municiones está vacía. No hay datos para procesar.")
        return

    print(f"\n{Fore.CYAN}Análisis, Cálculo y Ordenamiento de Municiones.{Style.RESET_ALL}")

    # --- 1. Procesar y Calcular Campos ---
    for item in data:
        # a) Calcular finalDamage
        if 'finalDamage' not in item:
            try:
                # Cálculo: damage * projectileCount
                item['finalDamage'] = item.get('damage', 0) * item.get('projectileCount', 1)
            except TypeError:
                item['finalDamage'] = 0

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

    print(f"{Fore.GREEN}Campos 'finalDamage' y 'minBuyPrice' calculados/encontrados.")

    # --- 2. Ordenar por Múltiples Criterios (La lógica de ordenamiento no cambia) ---
    sorted_ammo = sorted(
        data,
        key=lambda item: (
            item['ammoType'],
            item['caliber'],
            -item['finalDamage']
        )
    )

    # --- 3. Mostrar los Resultados ---

    print("\nOrdenado por: Tipo > Calibre > Daño Total (Mayor a Menor)\n")

    # NUEVO ORDEN DE ENCABEZADO: Calibre | DAÑO TOTAL | PRECIO MÁS BAJO
    print(f"{'NOMBRE':<30} | {'TIPO':<10} | {'CALIBRE':<15} | {'DAÑO TOTAL':>12} | {'PRECIO MÁS BAJO':<20}")
    print("-" * 90)

    for ammo in sorted_ammo:
        price_info = ammo['minBuyPrice']

        # Formateamos la columna de precio
        price_display = f"{price_info['price']} {price_info['currency']} ({price_info['source']})"

        print(
            f"{ammo['name'][:28]:<30} | "
            f"{ammo['ammoType']:<10} | "
            f"{ammo['caliber']:<15} | "
            f"{ammo['finalDamage']:>12} | "  # Columna de Daño (posición 4)
            f"{price_display:<20}"         # Columna de Precio (posición 5)
        )
    print("-" * 90)
