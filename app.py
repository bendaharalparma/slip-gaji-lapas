import streamlit as st
from datetime import datetime

# ==========================================
# 1. KONFIGURASI HALAMAN (WAJIB DI ATAS)
# ==========================================
st.set_page_config(
    page_title="E-Slip Gaji | Lapas Arga Makmur",
    page_icon="🇮🇩",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ==========================================
# 2. CUSTOM CSS (UNTUK TAMPILAN MENARIK)
# ==========================================
st.markdown("""
<style>
    /* Import Font Keren (Poppins) */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
    }

    /* Background Utama: Gradasi Biru Dongker Resmi */
    .stApp {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        background-attachment: fixed;
    }

    /* Kartu Container Utama (Putih Melayang) */
    .main-card {
        background-color: rgba(255, 255, 255, 0.95);
        padding: 40px;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        margin-top: 20px;
        border-top: 5px solid #FFD700; /* Aksen Emas di atas */
    }

    /* Styling Header Teks */
    h1 {
        color: #1e3c72;
        font-weight: 700;
        text-align: center;
        font-size: 28px !important;
        margin-bottom: 5px;
    }
    h3 {
        color: #555;
        font-weight: 400;
        text-align: center;
        font-size: 16px !important;
        margin-top: 0;
    }

    /* Styling Input Field */
    .stTextInput input, .stSelectbox div[data-baseweb="select"] {
        border-radius: 10px;
        border: 1px solid #ddd;
        padding: 10px;
    }

    /* Styling Tombol Utama */
    .stButton > button {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        font-weight: bold;
        border: none;
        border-radius: 50px;
        padding: 12px 30px;
        width: 100%;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(30, 60, 114, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(30, 60, 114, 0.5);
        color: #FFD700; /* Teks jadi emas saat hover */
    }

    /* Footer */
    .footer {
        text-align: center;
        margin-top: 30px;
        color: rgba(255,255,255, 0.7);
        font-size: 12px;
    }
    
    /* Menghilangkan elemen bawaan Streamlit yang mengganggu */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. LAYOUT APLIKASI
# ==========================================

# Container kosong untuk memberi jarak dari atas
st.write("") 

# --- MULAI CARD UTAMA ---
with st.container():
    st.markdown('<div class="main-card">', unsafe_allow_html=True)

    # --- HEADER LOGO (Menggunakan Kolom) ---
    col_l, col_m, col_r = st.columns([1, 2, 1])
    with col_l:
        st.image("https://upload.wikimedia.org/wikipedia/commons/e/e2/Logo_Kementerian_Hukum_dan_Hak_Asasi_Manusia_RI.png", use_container_width=True)
    with col_r:
        st.image("https://upload.wikimedia.org/wikipedia/commons/7/73/Logo_Pemasyarakatan_Indonesia.png", use_container_width=True)
    
    with col_m:
        # Spacer vertical agar logo seimbang
        st.write("") 
    
    # --- JUDUL APLIKASI ---
    st.markdown("<h1>SISTEM INFORMASI GAJI</h1>", unsafe_allow_html=True)
    st.markdown("<h3>Lapas Kelas IIB Arga Makmur</h3>", unsafe_allow_html=True)
    st.markdown("---") # Garis pemisah tipis

    # --- FORM INPUT ---
    # Ganti bagian ini dengan logika input aplikasi Anda yang lama
    nip_input = st.text_input("🔑 NIP / Username", placeholder="Masukkan NIP Pegawai...")
    
    col_pass, col_bulan = st.columns(2)
    with col_pass:
        password_input = st.text_input("🔒 Password", type="password", placeholder="Kode Akses")
    with col_bulan:
        bulan_list = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
        bulan_pilih = st.selectbox("📅 Periode Bulan", bulan_list)

    st.write("") # Spacer
    
    if st.button("🔍 LIHAT SLIP GAJI"):
        # LOGIKA PROSES DATA DI SINI
        if nip_input and password_input:
            st.success(f"Login Berhasil! Menampilkan data: {nip_input} ({bulan_pilih})")
            # Masukkan kode untuk menampilkan PDF/Data gaji di sini
            
            # Contoh tampilan data sederhana
            st.info("💡 Data slip gaji akan muncul di sini setelah dihubungkan dengan Excel Anda.")
        else:
            st.error("⚠️ Mohon lengkapi NIP dan Password.")

    st.markdown('</div>', unsafe_allow_html=True) # Tutup Main Card

# ==========================================
# 4. FOOTER LUAR
# ==========================================
st.markdown("""
<div class="footer">
    &copy; 2025 Urusan Kepegawaian & Keuangan • Lapas Kelas IIB Arga Makmur<br>
    Kementerian Hukum dan HAM RI Kanwil Bengkulu
</div>
""", unsafe_allow_html=True)
