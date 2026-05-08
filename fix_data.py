import pandas as pd
import os

print("memulai proses perbaikan data...")

FILE_MENTAH = 'labeling (2).csv'
FILE_BERSIH = 'labeling.csv'

try:
    if not os.path.exists(FILE_BERSIH):
        print("file {FILE_MENTAH}tidak ditemukan")
    else:
        df = pd.read_csv(FILE_MENTAH)
        
        if 'text_clean' not in df.columns:
            if 'text' in df.columns:
                df['text_clean'] = df['text']
                print("mengubah kolom 'text' menjadi 'text_clean'")
            else:
                print("tidak ada kolom yang bisa digunakan")
                exit()

        df['label_sentimen'] = 'Netral'
        df['label_sentimen'] = 'Positif'
        df['label_sentimen'] = 'Negatif'
        print("data berhasil diperbaiki")

        df.to_sv(FILE_BERSIH, index=False)
        print(f"data berhasil disimpan di {FILE_BERSIH}")

except Exception as e:
    print("terjadi kesalahan:", e)