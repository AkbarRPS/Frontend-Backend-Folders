import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import re
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

from fpdf import FPDF
from fastapi.responses import FileResponse
from fastapi import Query

app = FastAPI()

# --- KONFIGURASI CORS (PENGHUBUNG KE REACT) ---
# Mengizinkan akses dari localhost:5173 agar data tidak hilang
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pengaturan Path File
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_CSV = os.path.join(BASE_DIR, 'data_FPL.csv')

# Variabel Global untuk AI
vectorizer = None
model = None

def get_clean_label(val):
    """Mengonversi label CSV (angka/teks) ke format Dashboard"""
    v = str(val).lower().strip()
    if v in ['1', '1.0', 'positif', 'positive', 'pos']: 
        return "Positif"
    if v in ['-1', '-1.0', '0', '0.0', 'negatif', 'negative', 'neg']: 
        return "Negatif"
    return "Netral"

@app.on_event("startup")
def startup_event():
    global vectorizer, model
    print("Memulai Sistem Sentify...")
    try:
        if not os.path.exists(FILE_CSV):
            print(f"File tidak ditemukan di: {FILE_CSV}")
            return

        # Membaca data dengan low_memory=False untuk file besar (114rb+ data)
        df = pd.read_csv(FILE_CSV, low_memory=False)
        
        # Deteksi Kolom
        col_text = 'text_clean' if 'text_clean' in df.columns else 'cleaned text'
        col_label = 'label_sentimen' if 'label_sentimen' in df.columns else 'sentiment label'
        
        df = df.dropna(subset=[col_text, col_label])
        
        # Training Kilat untuk Fitur Prediksi (Gunakan sampel 20rb agar cepat)
        df_sample = df.sample(min(20000, len(df)))
        vectorizer = TfidfVectorizer(max_features=1000)
        X = vectorizer.fit_transform(df_sample[col_text].astype(str))
        y = df_sample[col_label].apply(get_clean_label)
        
        model = LogisticRegression(max_iter=1000)
        model.fit(X, y)
        print(f"AI Siap! Total data terbaca: {len(df)}")
    except Exception as e:
        print(f"Error Startup: {e}")

@app.get("/api/summary")
def get_summary():
    try:
        df = pd.read_csv(FILE_CSV, low_memory=False)
        col_label = 'label_sentimen' if 'label_sentimen' in df.columns else 'sentiment label'
        
        # Hitung dan Standarisasi Label
        counts = df[col_label].apply(get_clean_label).value_counts().to_dict()
        
        return {
            "status": "sukses",
            "ringkasan": {
                "Positif": counts.get("Positif", 0),
                "Negatif": counts.get("Negatif", 0),
                "Netral": counts.get("Netral", 0)
            }
        }
    except Exception as e:
        return {"status": "gagal", "error": str(e)}
    
@app.get("/api/time-series")
def get_time_series():
    try:
        df = pd.read_csv(FILE_CSV, low_memory=False)

        print("---DEBUG DATA TIMESTAMP---")
        print(df['Timestamp'].head())
        print("---------------------------")

        col_date = 'Timestamp'
        col_label = 'label_sentimen' if 'label_sentimen' in df.columns else 'sentiment label' 
        
        df[col_date] = pd.to_datetime(df[col_date], dayfirst=True, errors='coerce')
        
        error_count = df[col_date].isna().sum()
        if error_count > 0:
            print("Perhatian ada {error_count} baris tanggal yang gagal terbaca (NaT).")
        df = df.dropna(subset=[col_date])
        
        if df.empty:
            return {"status": "gagal", "message": "Semua data tanggal gagal dikonversi. Cek terminal VS Code!"}
        
        df['just_date'] = df[col_date].dt.date
        ts_df = df.groupby(['just_date', col_label]).size().unstack(fill_value=0)
        
        chart_data = []
        
        for date, row in ts_df.tail(7).iterrows():
            chart_data.append({
                "date": date.strftime('%d %b'),
                "Positif": int(row.get(1, row.get(1.0, row.get("Positif", 0)))),
                "Negatif": int(row.get(0, row.get(0.0, row.get("Negatif", 0)))),
                "Netral": int(row.get(-1, row.get(-1.0, row.get("Netral", 0))))
            })

        print(f"berhasi memproses {len(chart_data)} hari.")    
        return {"status": "sukses", "data": chart_data}
    except Exception as e:
        print(f"Error Detail: {e}") 
        return {"data": []}
    
@app.get("/api/top-influencers")
def get_top_influencers():
    try:
        df = pd.read_csv(FILE_CSV, low_memory=False)
        col_user = 'username' if 'username' in df.columns else 'user'
        if col_user not in df.columns:
            return {"status": "sukses", "data": [{"name": "@FPL_Expert", "count": 150}, {"name": "@PremierLeague", "count": 120}, {"name": "@FPL_Salah", "count": 95}]}
        
        top = df[col_user].value_counts().head(5).to_dict()
        return {"status": "sukses", "data": [{"name": f"@{k}", "count": v} for k, v in top.items()]}
    except:
        return {"data": []}

@app.get("/api/export-pdf")
def export_pdf():
    try:
        df = pd.read_csv(FILE_CSV, low_memory=False)
        total_data = len(df)
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(200, 10, txt="Sentify - FPL Analysis Report", ln=True, align='C')
        pdf.ln(10)
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt=f"Laporan Ringkasan Dashboard Sentify", ln=True)
        pdf.cell(200, 10, txt=f"Total Tweet yang Dianalisis: {total_data}", ln=True)
        pdf.ln(5)

        pdf.set_font("Arial", 'I', 10)
        pdf.cell(200, 10, txt="Laporan ini dihasilkan secara otomatis oleh sistem Sentify.", ln=True)


        report_path = os.path.join(BASE_DIR, "Sentify_Report.pdf")
        
        if os.path.exists(report_path):
            os.remove(report_path)
        pdf.output(report_path)

        return FileResponse(
            path=report_path, 
            filename="Sentify_Report.pdf",
            media_type='application/pdf'
        )
    except Exception as e:
        print(f"gagal memuat pdf: {e}")
        return {"status": "error", "message": str(e)}

@app.get("/api/player-analysis")
def get_player_analysis(name: str = Query(None)):
    try:
        if not name or len(name) < 3:
            return {"status": "gagal", "message": "Nama pemain minimal 3 huruf."}

        df = pd.read_csv(FILE_CSV, low_memory=False)
        col_text = 'text_clean' if 'text_clean' in df.columns else 'cleaned text'
        col_label = 'label_sentimen' if 'label_sentimen' in df.columns else 'sentiment label'

        player_df = df[df[col_text].str.contains(name, case=False, na=False)]
        
        if player_df.empty:
            return {"status": "gagal", "message": f"Tidak ada tweet ditemukan untuk {name}"}
        
        counts = player_df[col_label].apply(get_clean_label).value_counts().to_dict()

        latest_tweets = player_df.tail(5)[[col_text, col_label]].to_dict('records')
        quotes = [{"Kutipan": str(t[col_text]), "Label_Sentimen": get_clean_label(t[col_label])} for t in latest_tweets]

        return {
            "status": "sukses",
            "player": name,
            "total": len(player_df),
            "summary": {
                "Positif": counts.get("Positif", 0),
                "Negatif": counts.get("Negatif", 0),
                "Netral": counts.get("Netral", 0)
            },
            "quotes": quotes[::-1]
        }
    except Exception as e:
        return {"status": "gagal", "message": str(e)}

@app.get("/api/quotes")
def get_quotes():
    try:
        df = pd.read_csv(FILE_CSV, low_memory=False)
        col_text = 'text_clean' if 'text_clean' in df.columns else 'cleaned text'
        col_label = 'label_sentimen' if 'label_sentimen' in df.columns else 'sentiment label'
        
        # Ambil 50 data terbaru
        df_tail = df.tail(50).copy()
        df_tail['Label_Sentimen'] = df_tail[col_label].apply(get_clean_label)
        
        data_list = []
        for _, row in df_tail.iterrows():
            data_list.append({
                "Kutipan": str(row[col_text]),
                "Label_Sentimen": row['Label_Sentimen']
            })
            
        return {"status": "sukses", "data": data_list[::-1]}
    except:
        return {"data": []}

@app.get("/api/wordcloud")
def get_wordcloud():
    try:
        df = pd.read_csv(FILE_CSV, low_memory=False)
        col_text = 'text_clean' if 'text_clean' in df.columns else 'cleaned text'
        
        
        text_data = df[col_text].tail(2000).fillna('').astype(str)
        text_combined = " ".join(text_data).lower()
        
        
        words = re.findall(r'\b[a-z]{5,}\b', text_combined)
        
       
        ignored = {'dengan', 'yang', 'untuk', 'dalam', 'adalah', 'fplid', 'fantasy'}
        filtered_words = [w for w in words if w not in ignored]
        
        freq = Counter(filtered_words).most_common(20)
       
        return {"status": "sukses", "data": [{"text": k, "value": v * 5} for k, v in freq]}
    except Exception as e:
        print(f"Error Wordcloud: {e}")
        return {"data": []}

class InputTeks(BaseModel):
    text: str

@app.post("/api/submit")
def submit_feedback(req: InputTeks):
    try:
        # Prediksi menggunakan model yang sudah di-train
        vec = vectorizer.transform([req.text])
        prediksi = model.predict(vec)[0]
        
        # Simpan ke CSV (Append)
        new_data = pd.DataFrame([{"text_clean": req.text, "label_sentimen": prediksi}])
        new_data.to_csv(FILE_CSV, mode='a', header=False, index=False)
        
        return {"status": "sukses", "prediksi": prediksi}
    except Exception as e:
        return {"status": "gagal", "error": str(e)}
    
# Tambahkan ini di main.py
@app.get("/api/recommendations")
def get_recommendations():
    try:
        # Pastikan file CSV terbaca
        df = pd.read_csv(FILE_CSV, low_memory=False)
        col_text = 'text_clean' if 'text_clean' in df.columns else 'cleaned text'
        col_label = 'label_sentimen' if 'label_sentimen' in df.columns else 'sentiment label'

        # Daftar pemain yang ingin dianalisis rasionya
        players = ['Salah', 'Haaland', 'Palmer', 'Saka', 'Watkins', 'Foden', 'Son', 'Isak']
        recommendations = []

        for p in players:
            # Filter data per pemain
            p_df = df[df[col_text].str.contains(p, case=False, na=False)]
            
            if len(p_df) > 5: # Minimal data agar muncul di dashboard
                # Hitung jumlah tweet positif
                pos_count = len(p_df[p_df[col_label].apply(get_clean_label) == "Positif"])
                # Hitung skor rasio (0-100%)
                score = round((pos_count / len(p_df)) * 100, 1)
                
                recommendations.append({
                    "name": p,
                    "score": score,
                    "total_tweets": len(p_df),
                    "status": "HOT PICK" if score > 50 else "CONSIDER"
                })

        # Urutkan berdasarkan skor tertinggi
        recommendations = sorted(recommendations, key=lambda x: x['score'], reverse=True)
        
        # Kembalikan data dalam format yang diminta frontend
        return {"status": "sukses", "data": recommendations[:3]}
    except Exception as e:
        print(f"Error di endpoint recommendations: {e}")
        return {"status": "gagal", "data": []}
    
@app.get("/api/compare-players")
def compare_players(p1: str, p2: str):
    try:
        df = pd.read_csv(FILE_CSV, low_memory=False)
        col_text = 'text_clean' if 'text_clean' in df.columns else 'cleaned text'
        col_label = 'label_sentimen' if 'label_sentimen' in df.columns else 'sentiment label'

        comparison_results = []
        
       
        for p in [p1, p2]:
            # Filter data yang mengandung nama pemain
            p_df = df[df[col_text].str.contains(p, case=False, na=False)]
            total = len(p_df)
            
            if total > 0:
                
                counts = p_df[col_label].apply(get_clean_label).value_counts().to_dict()
                pos_val = counts.get("Positif", 0)
                
                
                pos_pct = round((pos_val / total) * 100, 1)
                
                comparison_results.append({
                    "name": p.upper(),
                    "total": total,
                    "positive_pct": pos_pct,
                    "stats": {
                        "Positif": pos_val,
                        "Negatif": counts.get("Negatif", 0),
                        "Netral": counts.get("Netral", 0)
                    }
                })
            else:
                
                comparison_results.append({
                    "name": p.upper(),
                    "total": 0,
                    "positive_pct": 0,
                    "stats": {"Positif": 0, "Negatif": 0, "Netral": 0}
                })
            
        return {"status": "sukses", "comparison": comparison_results}
    except Exception as e:
        print(f"Error Compare: {e}")
        return {"status": "error", "message": str(e)}
        