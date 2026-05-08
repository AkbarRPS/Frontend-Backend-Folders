import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom'
import { 
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell,
  LineChart, Line, CartesianGrid, Legend 
} from 'recharts'

// --- KONFIGURASI API ---
// Ganti URL di bawah ini dengan link Hugging Face Space kamu
const API_BASE_URL = 'https://akbarabay-sentify-backend.hf.space';

// --- 1. KOMPONEN PERBANDINGAN PEMAIN (COMPARE SECTION) ---
function CompareSection({ darkMode }) {
  const [p1, setP1] = useState('Salah');
  const [p2, setP2] = useState('Haaland');
  const [data, setData] = useState(null);

  const handleCompare = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/compare-players?p1=${p1}&p2=${p2}`);
      const d = await res.json();
      if (d.status === 'sukses') setData(d.comparison);
    } catch (e) { console.error("Error fetching comparison:", e); }
  };

  return (
    <section className={`p-8 md:p-10 rounded-[56px] border transition-all duration-500 ${darkMode ? 'bg-slate-900/40 border-white/5' : 'bg-white border-slate-200 shadow-2xl'}`}>
      <div className="flex flex-col md:flex-row justify-between items-end gap-6 mb-10">
        <div className="w-full grid grid-cols-2 gap-4">
          <div>
            <label className="text-[10px] font-black uppercase opacity-40 ml-4 mb-2 block tracking-widest">Player 1</label>
            <input value={p1} onChange={(e) => setP1(e.target.value)} className={`w-full p-4 rounded-3xl border outline-none focus:border-indigo-500 ${darkMode ? 'bg-slate-800 border-white/10' : 'bg-slate-50'}`} />
          </div>
          <div>
            <label className="text-[10px] font-black uppercase opacity-40 ml-4 mb-2 block tracking-widest">Player 2</label>
            <input value={p2} onChange={(e) => setP2(e.target.value)} className={`w-full p-4 rounded-3xl border outline-none focus:border-indigo-500 ${darkMode ? 'bg-slate-800 border-white/10' : 'bg-slate-50'}`} />
          </div>
        </div>
        <button onClick={handleCompare} className="w-full md:w-auto bg-indigo-600 hover:bg-indigo-500 text-white font-black px-12 py-4 rounded-3xl transition-all shadow-lg shadow-indigo-500/20">VS</button>
      </div>

      {data && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-12 animate-in zoom-in duration-500">
          {data.map((player, i) => (
            <div key={i} className="space-y-5">
              <div className="flex justify-between items-end">
                <h4 className="text-3xl font-black italic uppercase text-indigo-500 tracking-tighter">{player.name}</h4>
                <span className="text-[10px] font-bold opacity-40 uppercase tracking-widest">{player.total.toLocaleString()} Mentions</span>
              </div>
              <div className="h-4 w-full bg-slate-500/10 rounded-full overflow-hidden">
                <div className="h-full bg-indigo-500 transition-all duration-1000 shadow-[0_0_15px_rgba(99,102,241,0.5)]" style={{ width: `${player.positive_pct}%` }}></div>
              </div>
              <div className="flex justify-between items-center">
                 <p className="text-[10px] font-black uppercase tracking-widest">Positive Vibe Score</p>
                 <p className="text-xl font-black italic text-indigo-400">{player.positive_pct}%</p>
              </div>
              <div className="grid grid-cols-3 gap-3">
                {[
                  { label: 'Pos', val: player.stats.Positif, color: 'text-green-500' },
                  { label: 'Neg', val: player.stats.Negatif, color: 'text-red-500' },
                  { label: 'Net', val: player.stats.Netral, color: 'text-slate-500' }
                ].map(s => (
                  <div key={s.label} className={`p-4 rounded-2xl text-center border ${darkMode ? 'bg-white/5 border-white/5' : 'bg-slate-50 border-slate-100'}`}>
                    <p className="text-[9px] opacity-40 uppercase font-black mb-1">{s.label}</p>
                    <p className={`font-black ${s.color}`}>{s.val}</p>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}

// --- 2. KOMPONEN LAYOUT ---
function Layout({ children, darkMode, setDarkMode }) {
  const loc = useLocation();
  const navs = [
    { name: 'Home', path: '/', icon: '📊' },
    { name: 'Data', path: '/data', icon: '📁' },
  ];

  return (
    <div className={`min-h-screen flex transition-colors duration-500 ${darkMode ? 'bg-[#0f172a] text-slate-200' : 'bg-slate-50 text-slate-900'}`}>
      <aside className={`w-64 border-r p-6 flex flex-col hidden md:flex ${darkMode ? 'bg-slate-900/50 border-white/5' : 'bg-white border-slate-200'}`}>
        <div className={`p-4 mb-10 text-3xl font-black italic tracking-tighter uppercase ${darkMode ? 'text-indigo-500' : 'text-indigo-600'}`}>SENTIFY.</div>
        <nav className="space-y-2 flex-grow">
          {navs.map(n => (
            <Link key={n.path} to={n.path} className={`flex items-center gap-4 p-4 rounded-2xl transition-all ${loc.pathname === n.path ? 'bg-indigo-600 text-white shadow-lg' : 'hover:bg-indigo-500/10'}`}>
              <span className="text-xl">{n.icon}</span><span className="font-bold">{n.name}</span>
            </Link>
          ))}
        </nav>
        <button onClick={() => setDarkMode(!darkMode)} className={`mt-auto p-4 rounded-2xl font-bold transition-all ${darkMode ? 'bg-white/5 text-white' : 'bg-slate-200 text-slate-900'}`}>
          {darkMode ? '☀️ Light Mode' : '🌙 Dark Mode'}
        </button>
      </aside>
      <main className="flex-grow p-6 md:p-12 overflow-y-auto">{children}</main>
    </div>
  );
}

// --- 3. KOMPONEN DATA EXPLORER ---
function DataExplorer({ quotes, darkMode }) {
  const [search, setSearch] = useState('');
  const filtered = quotes.filter(q => q.Kutipan.toLowerCase().includes(search.toLowerCase()));

  return (
    <div className="space-y-8 animate-in slide-in-from-bottom duration-500">
      <div className="flex flex-col md:flex-row justify-between items-center gap-6">
        <h1 className="text-4xl font-black tracking-tighter uppercase italic">Data Explorer</h1>
        <input type="text" placeholder="Search tweets..." className={`w-full md:w-96 p-4 rounded-2xl border outline-none focus:border-indigo-500 ${darkMode ? 'bg-slate-900 border-white/10' : 'bg-white border-slate-200'}`} onChange={(e) => setSearch(e.target.value)} />
      </div>
      <div className={`rounded-[40px] border overflow-hidden shadow-2xl ${darkMode ? 'bg-slate-900/50 border-white/5' : 'bg-white border-slate-200'}`}>
        <div className="max-h-[600px] overflow-y-auto">
          <table className="w-full text-left">
            <thead className={`sticky top-0 ${darkMode ? 'bg-slate-800' : 'bg-slate-100'}`}>
              <tr>
                <th className="p-6 font-black uppercase text-[10px] tracking-widest opacity-50">Tweet</th>
                <th className="p-6 font-black uppercase text-[10px] tracking-widest opacity-50 w-32 text-center">Label</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {filtered.map((item, i) => (
                <tr key={i} className="hover:bg-indigo-500/5 transition-colors">
                  <td className="p-6 text-sm opacity-80 italic">"{item.Kutipan}"</td>
                  <td className="p-6 text-center">
                    <span className={`text-[10px] font-black uppercase px-3 py-1 rounded-full ${item.Label_Sentimen === 'Positif' ? 'bg-green-500/20 text-green-400' : item.Label_Sentimen === 'Negatif' ? 'bg-red-500/20 text-red-400' : 'bg-slate-500/20'}`}>
                      {item.Label_Sentimen}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

// --- 4. KOMPONEN DASHBOARD UTAMA ---
function Dashboard({ summary, timeSeries, influencers, recs, darkMode }) {
  const chartData = [
    { name: 'Positif', value: summary.Positif, color: '#10b981' },
    { name: 'Negatif', value: summary.Negatif, color: '#f43f5e' },
    { name: 'Netral', value: summary.Netral, color: '#64748b' },
  ];

  return (
    <div className="space-y-12 animate-in fade-in duration-700">
      <header>
        <h1 className="text-5xl font-black tracking-tighter uppercase italic">Overview</h1>
        <p className="text-indigo-500 font-bold text-xs uppercase tracking-[0.4em] mt-2">Sentify Analysis Engine</p>
      </header>

      {/* AI RECOMMENDATION CARDS */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {recs.map((player, i) => (
          <div key={i} className={`p-6 rounded-[32px] border-2 flex items-center justify-between transition-all ${darkMode ? 'bg-indigo-500/5 border-indigo-500/20' : 'bg-white border-indigo-100 shadow-xl'}`}>
            <div>
              <span className="text-[10px] font-black bg-indigo-600 text-white px-3 py-1 rounded-full uppercase"> {player.status} </span>
              <h4 className="text-2xl font-black mt-2 italic tracking-tighter">{player.name}</h4>
              <p className="text-[10px] opacity-50 font-bold uppercase tracking-tighter">Confidence: {player.score}%</p>
            </div>
            <div className="text-4xl">{i === 0 ? '🔥' : i === 1 ? '📈' : '💎'}</div>
          </div>
        ))}
      </div>

      {/* COMPARE SECTION */}
      <CompareSection darkMode={darkMode} />

      {/* GENERAL STATS CARDS */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {chartData.map(d => (
          <div key={d.name} className="p-10 rounded-[48px] shadow-2xl text-white relative overflow-hidden" style={{ backgroundColor: d.color }}>
            <p className="text-xs font-black opacity-50 uppercase tracking-widest">{d.name}</p>
            <h2 className="text-6xl font-black mt-2 tracking-tighter">{d.value.toLocaleString()}</h2>
            <div className="absolute -right-4 -bottom-4 text-9xl opacity-10 font-black italic">{d.name[0]}</div>
          </div>
        ))}
      </div>

      {/* CHARTS */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className={`p-8 rounded-[48px] border h-[400px] ${darkMode ? 'bg-slate-900 border-white/5' : 'bg-white border-slate-200 shadow-lg'}`}>
          <h3 className="text-center font-black text-[10px] uppercase tracking-[0.3em] mb-8 opacity-30">Sentiment Distribution</h3>
          <ResponsiveContainer width="100%" height="80%">
            <BarChart data={chartData}>
              <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{fill: '#94a3b8', fontSize: 12, fontWeight: 'bold'}} />
              <Tooltip cursor={{fill: 'transparent'}} contentStyle={{borderRadius: '20px', border: 'none', backgroundColor: '#1e293b', color: '#fff'}} />
              <Bar dataKey="value" radius={[20, 20, 20, 20]}>
                {chartData.map((entry, index) => <Cell key={index} fill={entry.color} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div className={`p-10 rounded-[48px] border h-[400px] ${darkMode ? 'bg-slate-900 border-white/5' : 'bg-white border-slate-200 shadow-lg'}`}>
          <h3 className="text-center font-black text-[10px] uppercase tracking-[0.3em] mb-8 opacity-30">7-Day Sentiment Trend</h3>
          <ResponsiveContainer width="100%" height="85%">
            <LineChart data={timeSeries}>
              <CartesianGrid strokeDasharray="3 3" strokeOpacity={0.05} vertical={false} />
              <XAxis dataKey="date" axisLine={false} tickLine={false} tick={{fontSize: 10}} />
              <YAxis axisLine={false} tickLine={false} tick={{fontSize: 10}} />
              <Tooltip contentStyle={{borderRadius: '24px', border: 'none'}} />
              <Line type="monotone" dataKey="Positif" stroke="#10b981" strokeWidth={5} dot={false} />
              <Line type="monotone" dataKey="Negatif" stroke="#f43f5e" strokeWidth={5} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 pb-12">
        <div className={`p-8 rounded-[48px] border ${darkMode ? 'bg-slate-900 border-white/5' : 'bg-white border-slate-200 shadow-lg'}`}>
           <h3 className="text-[10px] font-black uppercase opacity-30 mb-6 tracking-widest text-center">Top Discussion Leaders</h3>
           <div className="space-y-3">
             {influencers.map((inf, i) => (
               <div key={i} className={`flex justify-between items-center p-4 rounded-2xl ${darkMode ? 'bg-white/5' : 'bg-slate-100'}`}>
                 <span className="font-bold text-indigo-500">@{inf.name}</span>
                 <span className="text-[10px] font-black opacity-40">{inf.count} Tweets</span>
               </div>
             ))}
           </div>
        </div>
        <div className="bg-indigo-600 p-10 rounded-[48px] text-center text-white flex flex-col justify-center items-center shadow-2xl">
          <h3 className="text-3xl font-black mb-4 uppercase italic">Export Report</h3>
          <button onClick={() => window.open(`${API_BASE_URL}/api/export-pdf`)} className="w-full bg-white text-indigo-600 font-black py-5 rounded-3xl hover:scale-[1.02] transition-all uppercase tracking-widest text-xs"> Download PDF </button>
        </div>
      </div>
    </div>
  );
}

// --- 5. MAIN APP ---
export default function App() {
  const [darkMode, setDarkMode] = useState(true);
  const [state, setState] = useState({ summary: { Positif: 0, Negatif: 0, Netral: 0 }, quotes: [], timeSeries: [], influencers: [], recs: [] });
  const [loading, setLoading] = useState(true);

  const fetchAll = async () => {
    try {
      const endpoints = ['summary', 'quotes', 'time-series', 'top-influencers', 'recommendations'];
      const responses = await Promise.all(endpoints.map(ep => fetch(`${API_BASE_URL}/api/${ep}`)));
      const [dSum, dQuo, dTS, dInf, dRec] = await Promise.all(responses.map(r => r.json()));
      setState({ summary: dSum.ringkasan, quotes: dQuo.data, timeSeries: dTS.data, influencers: dInf.data, recs: dRec.data });
    } catch (e) { 
      console.error("Fetch error:", e); 
    } finally { 
      setLoading(false); 
    }
  };

  useEffect(() => { fetchAll(); }, []);

  if (loading) return (
    <div className="h-screen flex flex-col items-center justify-center bg-[#0f172a] text-indigo-500">
      <div className="w-12 h-12 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin mb-4"></div>
      <p className="font-black italic uppercase tracking-widest animate-pulse">Connecting to Sentify API...</p>
    </div>
  );

  return (
    <Router>
      <Layout darkMode={darkMode} setDarkMode={setDarkMode}>
        <Routes>
          <Route path="/" element={<Dashboard {...state} darkMode={darkMode} />} />
          <Route path="/data" element={<DataExplorer quotes={state.quotes} darkMode={darkMode} />} />
        </Routes>
      </Layout>
    </Router>
  );
}