from pymongo import MongoClient
from typing import Union
import pymongo
from datetime import datetime

MONGO_URI = "mongodb://mongo:27017/"
DATABASE_NAME = "ammo_data"        # Nombre de la base de datos
COLLECTION_NAME = "bullets"
ID_FIELD = "id"


def upload_to_mongodb(data: Union[dict[str], list[dict[str]]]) -> None:
    """
    Establece conexión con MongoDB e inserta los datos proporcionados.

    Acepta un diccionario (para una inserción) o una lista de diccionarios 
    (para inserción múltiple).
    """
    client = None
    try:
        # 1. Establecer la conexión
        client = MongoClient(MONGO_URI)
        client.admin.command('ping')
        print(f"Sucessfully connected to mongodb {MONGO_URI}")

        # 2. Seleccionar la base de datos y la colección
        db = client[DATABASE_NAME]
        collection = db[COLLECTION_NAME]

        # 3. Determinar el método de inserción
        if isinstance(data, list):
            # Tu estructura de datos es una lista, así que usamos insert_many
            print(f"Inserting {len(data)} into collection: '{COLLECTION_NAME}'...")
            resultado = collection.insert_many(data)
            print(f" {len(resultado.inserted_ids)} inserted into collection")
        elif isinstance(data, dict):
            # Inserción de un solo documento
            resultado = collection.insert_one(data)
            print(f"Document ID {resultado.inserted_id}")
        else:
            print("ERROR: 'data' must be a dictionary or a list.")
            return

    except pymongo.errors.ConnectionError:
        print("CONNECTION ERROR: Could not connect to MongoDB.")
        print("Verify docker container.")

    except Exception as e:
        print(f"Occured something unexpected: {e}")

    finally:
        # 4. Cerrar la conexión
        if client:
            client.close()
            print("Mongodb connection closed.")

def upload_to_mongodb_2(data: Union[dict[str], list[dict[str]]]) -> None:
    """
    Establece conexión con MongoDB e inserta los datos proporcionados.
    Evita duplicados comprobando si el 'id' ya existe antes de insertar.
    """
    client = None
    try:
        # 1. Establecer la conexión
        client = MongoClient(MONGO_URI)
        # client.admin.command('ping') # Opcional: verificar conexión
        print(f"Conectado a MongoDB para carga de datos.")

        # 2. Seleccionar la base de datos y la colección
        db = client[DATABASE_NAME]
        collection = db[COLLECTION_NAME]

        # 3. Lógica de inserción 'elemento a elemento' sin duplicados
        if isinstance(data, list):
            print(f"Procesando lista de {len(data)} elementos...")
            inserted_count = 0
            skipped_count = 0

            for item in data:
                # IMPORTANTE: Asegúrate de que tu JSON tiene un campo llamado 'id'
                # Si tu campo único se llama de otra forma (ej. '_id', 'uid'), cámbialo aquí.
                item_id = item.get('id')

                if item_id and collection.find_one({"id": item_id}):
                    # Si ya existe, no hacemos nada (skip)
                    skipped_count += 1
                else:
                    # Si no existe, insertamos
                    collection.insert_one(item)
                    inserted_count += 1
            
            print(f"Resumen: {inserted_count} insertados, {skipped_count} omitidos (ya existían).")

        elif isinstance(data, dict):
            # Lógica para un solo documento
            item_id = data.get('id')
            
            if item_id and collection.find_one({"id": item_id}):
                print(f"El documento con id {item_id} ya existe. Omitiendo.")
            else:
                resultado = collection.insert_one(data)
                print(f"Documento insertado con ID interno: {resultado.inserted_id}")

        else:
            print("ERROR: 'data' debe ser un diccionario o una lista.")

    except pymongo.errors.ConnectionError:
        print("ERROR DE CONEXIÓN: No se pudo conectar a MongoDB.")
        print("Verifica que el contenedor de Docker esté corriendo.")

    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")

    finally:
        # 4. Cerrar la conexión
        if client:
            client.close()
            print("Conexión con MongoDB cerrada.")



def smart_update_mongodb_2(new_data: Union[dict[str], list[dict[str]]]) -> dict[str]:
    """
    Actualiza MongoDB. Muestra logs limpios (solo name).
    """
    client = None
    results = {
        "estado": "Éxito",
        "documentos_procesados": 0,
        "documentos_modificados": 0,
        "documentos_sin_cambios": 0,
        "documentos_insertados": 0,
        "detalles_modificados": []
    }

    data_list = new_data if isinstance(new_data, list) else [new_data]

    try:
        client = MongoClient(MONGO_URI)
        db = client[DATABASE_NAME]
        collection = db[COLLECTION_NAME]

        print(f"🚀 Procesando {len(data_list)} elementos...")

        for raw_item in data_list:
            results["documentos_procesados"] += 1

            # 1. Aplanar (si viene de GraphQL)
            item = raw_item.copy()
            if "item" in item and isinstance(item["item"], dict):
                nested_item_data = item.pop("item")
                item.update(nested_item_data)

            # 2. Obtener ID
            item_id = item.get(ID_FIELD)
            if not item_id:
                continue

            query = {ID_FIELD: item_id}
            existing_doc = collection.find_one(query)

            # --- 4. VISUALIZACIÓN LIMPIA (SOLO NAME) ---
            if existing_doc:
                # Extraemos solo el name para mostrarlo en el log
                db_name = existing_doc.get('name', 'Sin Nombre')
                # new_name = item.get('name', 'Sin Nombre')

                print(f"\n🔍 Revisando: {db_name} (ID: {item_id})")
                # print(f"   💾 [BD]:  {db_name}")  # Opcional, ya lo mostramos arriba
                # print(f"   ✨ [NEW]: {new_name}") # Opcional, suelen ser iguales
            else:
                print(f"\n🆕 Creando nueva entrada: {item.get('name')} (ID: {item_id})")

            # --- 5. LÓGICA DE ACTUALIZACIÓN ---

            # CASO A: INSERTAR
            if not existing_doc:
                item["last_updated"] = datetime.now().isoformat()
                collection.insert_one(item)
                results["documentos_insertados"] += 1
                continue

            # CASO B: COMPARAR
            changes = {}
            for key, new_value in item.items():
                if key in ['_id', 'last_updated']: continue

                existing_value = existing_doc.get(key)

                # Nota: Si tienes tipos numpy (np.float64) esto puede dar falso positivo
                # si no son exactamente iguales al float de python.
                # Generalmente funciona bien, pero ojo con eso.
                if new_value != existing_value:
                    changes[key] = {
                        "antes": existing_value,
                        "ahora": new_value
                    }

            # --- 6. APLICAR CAMBIOS ---
            if changes:
                print(f"   ⚠️ CAMBIOS DETECTADOS ({len(changes)} campos):")
                for k, v in changes.items():
                    # Aquí mostramos el detalle del cambio específico
                    print(f"      ✏️ {k}: {v['antes']} -> {v['ahora']}")

                mongo_changes = {k: v["ahora"] for k, v in changes.items()}
                mongo_changes["last_updated"] = datetime.now().isoformat()

                collection.update_one(query, {"$set": mongo_changes})

                results["documentos_modificados"] += 1
                results["detalles_modificados"].append({
                    "id": item_id,
                    "nombre": item.get('name'),
                    "cambios": list(changes.keys())
                })
            else:
                # Mensaje corto para no saturar si no hay cambios
                print(f"   ✅ Sin cambios.")
                results["documentos_sin_cambios"] += 1

        return results

    except Exception as e:
        return {"estado": "ERROR", "mensaje": str(e)}
    finally:
        if client:
            client.close()
