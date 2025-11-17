import os
import json
from colorama import Fore
# Importamos Fernet para la encriptación
from cryptography.fernet import Fernet
# Nota: La librería 'cryptography' debe estar instalada (pip install cryptography)


# --- LÓGICA DE CRIPTOGRAFÍA (Anteriormente en crypto_utils.py) ---

# 1. CLAVE DE ENCRIPTACIÓN (Debe ser la misma para encriptar y desencriptar)
# GENERAR UNA CLAVE SEGURA: Fernet.generate_key()
key = Fernet.generate_key()
print(key)

ENCRYPTION_KEY = key  # Reemplaza esto con tu clave segura y constante
def encrypt_data(data_bytes: bytes) -> bytes:
    """Encripta los datos usando Fernet."""
    try:
        f = Fernet(ENCRYPTION_KEY)
        encrypted_data = f.encrypt(data_bytes)
        return encrypted_data
    except Exception as e:
        print(f"{Fore.RED}Error en la encriptación: {e}")
        return data_bytes

def decrypt_data(encrypted_data: bytes) -> bytes:
    """Desencripta los datos usando Fernet."""
    try:
        f = Fernet(ENCRYPTION_KEY)
        decrypted_data = f.decrypt(encrypted_data)
        return decrypted_data
    except Exception as e:
        # Esto ocurre si la clave es incorrecta o los datos están corruptos.
        print(f"{Fore.RED}Error en la desencriptación: {e}") 
        return b''

# --- FIN LÓGICA DE CRIPTOGRAFÍA ---


# 2. FUNCIÓN AUTÓNOMA PARA ENCRIPTAR Y LIMPIAR (Ahora usa la función local)
def encrypt_and_cleanup(input_filename: str = "ammo_data.json", output_filename: str = "ade.bin"):

    print(f"\n{Fore.CYAN}--- Paso 2: Iniciando Encriptación y Limpieza ---")
    
    # 1. Verificar si el archivo plano existe antes de comenzar
    if not os.path.exists(input_filename):
        print(f"{Fore.RED}Error: El archivo '{input_filename}' no fue encontrado. Saltando la encriptación.")
        return

    try:
        # Leer el contenido del archivo PLAIN como texto
        with open(input_filename, "r", encoding="utf-8") as f:
            plain_content = f.read()
            
        # Codificar a bytes y ENCRIPTAR (Llama a la función definida arriba)
        data_to_encrypt = plain_content.encode('utf-8')
        encrypted_content = encrypt_data(data_to_encrypt) 
        
        # Guardar los bytes encriptados
        with open(output_filename, "wb") as f: # 'wb' para escribir bytes
            f.write(encrypted_content)
        
        # --- ELIMINACIÓN DEL ARCHIVO NO ENCRIPTADO ---
        os.remove(input_filename)
            
        print(f"{Fore.GREEN}Archivo encriptado y guardado en '{output_filename}'.")
        print(f"{Fore.YELLOW}Archivo original '{input_filename}' eliminado correctamente.")
        
    except Exception as e:
        print(f"{Fore.RED}Error durante la encriptación o eliminación: {e}")
        print(f"{Fore.RED}El archivo '{input_filename}' puede que no se haya borrado.")


# --- FIN FUNCIÓN AUTÓNOMA PARA ENCRIPTAR Y LIMPIAR ---

def load_and_decrypt_data(filename: str = "ade.bin") -> list:
    """
    Lee el archivo cifrado, lo desencripta y carga el contenido
    en una variable de Python (lista de diccionarios).
    """
    print(f"\n{Fore.CYAN}--- Iniciando Desencriptación y Carga ---")
    
    # 1. Leer el archivo binario cifrado
    try:
        with open(filename, "rb") as f:
            encrypted_data = f.read()
            
    except FileNotFoundError:
        print(f"{Fore.RED}Error: Archivo '{filename}' no encontrado. Asegúrate de que existe.")
        return []
        
    print(f"{Fore.CYAN}Desencriptando datos...")
    
    # 2. Desencriptar los datos (usando la función definida arriba)
    decrypted_data_bytes = decrypt_data(encrypted_data)
    
    if not decrypted_data_bytes:
        print(f"{Fore.RED}La desencriptación falló. Los datos no se pudieron recuperar.")
        return []

    # 3. Decodificar los bytes a string JSON
    decrypted_json_string = decrypted_data_bytes.decode('utf-8')

    # 4. Cargar el string JSON en una variable de Python
    try:
        # La variable `ammo_data_list` contendrá tu estructura de datos aplanada
        data_variable = json.loads(decrypted_json_string) 
        print(f"{Fore.GREEN}Desencriptación y carga exitosa. Datos listos en una variable.")
        # print(data_variable)
        return data_variable
        
    except json.JSONDecodeError:
        print(f"{Fore.RED}Error: El contenido desencriptado no es JSON válido.")
        return []

# --- Bloque de Ejecución para Pruebas ---