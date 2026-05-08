import pandas as pd
import re
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

nltk.download('vader_lexicon')


def bersihkan_teks(teks):
    if not isinstance(teks, str):
        return ""
    
    teks = re.sub(r"http\S+|www\S+|https\S+", '', teks)
    teks = re.sub(r'@\w+', '', teks)
    teks = re.sub(r'#', '', teks)
    teks = re.sub(r'[^a-zA-Z\s]', '', teks)
    return teks.lower().strip()


def tentukan_label(skor):
    if skor >= 0.05:
        return 'Positif'
    elif skor <= -0.05:
        return 'Negatif'
    else:
        return 'Netral'


def main():
    file_path = 'FPL_tweets.csv'

    try:
        df = pd.read_csv(file_path)
        print(f"Berhasil memuat {len(df)} baris data.")
    except FileNotFoundError:
        print("File tidak ditemukan.")
        return

    # 🔍 cek kolom yang tersedia
    print("Kolom tersedia:", df.columns)

    # pilih kolom teks yang ada
    possible_columns = ['Text', 'content']
    nama_kolom_teks = None

    for col in possible_columns:
        if col in df.columns:
            nama_kolom_teks = col
            break

    if nama_kolom_teks is None:
        print("Kolom teks tidak ditemukan.")
        return

    print(f"Menggunakan kolom: {nama_kolom_teks}")

    # cleaning
    print("Membersihkan data...")
    df['cleaned_text'] = df[nama_kolom_teks].apply(bersihkan_teks)

    # sentiment
    sia = SentimentIntensityAnalyzer()

    print("Menghitung sentimen...")
    df['scores'] = df['cleaned_text'].apply(lambda teks: sia.polarity_scores(teks))
    df['compound'] = df['scores'].apply(lambda s: s['compound'])

    df['sentiment_label'] = df['compound'].apply(tentukan_label)

    # hasil
    print("\n--- Hasil Analisis Sentimen ---")
    print(df['sentiment_label'].value_counts())

    print("\nContoh Data:")
    print(df[[nama_kolom_teks, 'sentiment_label']].head())

    # simpan
    output_file = 'hasil_analisis_tweet.csv'
    df.to_csv(output_file, index=False)
    print(f"Hasil disimpan di {output_file}")


if __name__ == "__main__":
    main()