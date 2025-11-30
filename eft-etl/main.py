import e
import tl
import crypt
import mondongo

if __name__ == "__main__":

    e.fetch_and_save_ammo_data()
    # crypt.encrypt_and_cleanup()
    data = crypt.load_and_decrypt_data()
    data = tl.clean_caliber_data(data)
    data = tl.calculate_finalScore(data)
    data = tl.normalize_and_update_scores(data)
    data = tl.print_ammo(data)
    # print(data)
    mondongo.upload_to_mongodb_2(data)
