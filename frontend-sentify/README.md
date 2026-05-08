# SENTIFY: FPL Sentiment Analysis Engine 📊⚽

**Sentify** adalah dashboard analisis sentimen tingkat lanjut yang dirancang khusus untuk komunitas *Fantasy Premier League*. Proyek ini mengintegrasikan kekuatan **FastAPI (Python)** di backend dan **React JS** di frontend untuk mengolah lebih dari 114.000 data tweet.

## 🚀 Fitur Utama
* **AI Player Recommendation**: Menggunakan algoritma pembobotan untuk menyarankan pemain "Must Buy" berdasarkan sentimen positif tertinggi.
* **Compare Players (VS Mode)**: Fitur komparatif *side-by-side* untuk membandingkan dua pemain secara langsung.
* **Real-time Player Deep Dive**: Pencarian spesifik untuk melihat statistik sentimen dan kutipan tweet terbaru per pemain.
* **Professional Dashboard**: Visualisasi data interaktif menggunakan Recharts dengan dukungan *Dark Mode* dan *Export PDF*.

## 💻 Tech Stack
* **Frontend**: React JS, Tailwind CSS, Recharts, React Router.
* **Backend**: Python, FastAPI, Pandas (Data Processing).
* **Data Source**: 114k+ Tweets Dataset (CSV).

## 🛠️ Cara Menjalankan Proyek

### 1. Backend (Python)
1. Masuk ke folder backend: `cd backend`
2. Install library: `pip install -r requirements.txt`
3. Jalankan server: `uvicorn main:app --reload`

### 2. Frontend (React)
1. Masuk ke folder frontend: `cd frontend`
2. Install package: `npm install`
3. Jalankan aplikasi: `npm run dev`