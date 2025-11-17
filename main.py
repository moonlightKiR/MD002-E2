import e
import crypt
import tl
# Pyarmor gen main.py

# --- 4. Ejecutar el Script ---
if __name__ == "__main__":
    e.fetch_and_save_ammo_data()
    crypt.encrypt_and_cleanup()
    data = crypt.load_and_decrypt_data()
    print(type(data))
    data = tl.clean_caliber_data(data)
    tl.calculate_and_sort_ammo(data)
