import e
import tl
import crypt
import mondongo


def update_database():

    print("UPDATING DATABASE WITH SMART UPDATE...")
    e.fetch_and_save_ammo_data()
    # crypt.encrypt_and_cleanup()
    data = crypt.load_and_decrypt_data()
    data = tl.clean_caliber_data(data)
    data = tl.calculate_finalScore(data)
    data = tl.normalize_and_update_scores(data)
    print(f"UPDATINGMONGO")
    mondongo.smart_update_mongodb_2(data)
    print("ALL DONE!")


if __name__ == "__main__":
    update_database()
