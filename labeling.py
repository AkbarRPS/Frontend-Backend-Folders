import pandas as pd
from transformers import pipeline
from tqdm import tqdm

print("memuat data bersih")
df = pd.read_csv('data_tahap1_bersih.csv')

df['text_clean'] = df['text_clean'].fillna("")

print("membuat model AI... (Ini mungkin memakan waktu beberapa detik)")
model_name = "mdhugol/indonesia-bert-sentiment-classification"
sentiment_analyzer = pipeline("sentiment-analysis", model=model_name)

def predict_sentiment(text):
    if len(str(text).strip()) == 0:
        return "Netral"
    try:
        hasil = sentiment_analyzer(str(text)[:512])
        label = hasil[0]['label']

        if label.lower() in ['positive', 'positif', 'label_0']:
            return "Positif"
        elif label.lower() in ['negative', 'negatif', 'label_0']:
            return "Negatif"
        else:
            return "Netral"
    except Exception as e:
        return "Netral"
    
print("memulai proses pelabelan sentimen massal...")

tqdm.pandas(desc="AI sedang berfikir...")
df['label_sentimen'] = df['text_clean'].progress_apply(predict_sentiment)
file_output = 'labeling.csv'
df.to_csv(file_output, index=False)

print(f"data berhasil dilabeling dan disimpan di '{file_output}'")
print("\nRingkasan hasil:")
print(df['label_sentimen'].value_counts())
    


