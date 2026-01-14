import streamlit as st
import pandas as pd
import base64
from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

# ==========================================
# 1. KONFIGURASI HALAMAN & CSS
# ==========================================
st.set_page_config(
    page_title="E-Slip Gaji | Lapas Arga Makmur", 
    layout="wide", # Layout lebar agar lebih modern
    page_icon="🏛️"
)

FILE_PATH = 'DataGaji.csv'
ADMIN_PASSWORD = "admin123" 

# --- CUSTOM CSS (UNTUK MEMPERCANTIK TAMPILAN) ---
st.markdown("""
<style>
    /* Mengubah warna background utama menjadi abu-abu sangat muda (profesional) */
    .stApp {
        background-color: #f5f7f9;
    }
    
    /* Style untuk Header */
    .header-container {
        background-color: #1a237e; /* Biru Tua Institusi */
        padding: 2rem;
        border-radius: 0 0 20px 20px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .header-title {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
    }
    .header-subtitle {
        font-size: 1.2rem;
        font-weight: 300;
        opacity: 0.9;
    }
    
    /* Style untuk Card (Kotak Putih) */
    .card-box {
        background-color: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        border: 1px solid #e0e0e0;
    }
    
    /* Footer */
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: white;
        color: #666;
        text-align: center;
        padding: 10px;
        border-top: 1px solid #eee;
        font-size: 0.8rem;
    }
    
    /* Mempercantik Tombol */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3em;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. FUNGSI BACKEND (LOGIKA SAMA, HANYA FORMAT PDF DIRAFIKAN)
# ==========================================

@st.cache_data
def load_data():
    try:
        df = pd.read_csv(FILE_PATH, header=2, dtype=str)
        if not df.empty:
            val_cek = str(df.iloc[0]['Nama']).strip()
            if val_cek.isdigit() or len(val_cek) < 2:
                df = df.iloc[1:].reset_index(drop=True)
        df.columns = [str(c).strip() for c in df.columns]
        if 'Nama' in df.columns:
            df['Nama_Clean'] = df['Nama'].astype(str).str.strip().str.lower()
        if 'kode akses' in df.columns:
            df['Kode_Clean'] = df['kode akses'].astype(str).str.strip()
        return df
    except Exception as e:
        return None

def parse_duit(val):
    try:
        clean = str(val).replace(',', '').replace('.', '').replace('Rp', '').strip()
        if not clean or clean.lower() == 'nan': return 0
        return int(float(clean))
    except:
        return 0

def format_rupiah(val):
    return f"Rp {val:,}".replace(",", ".")

def create_pdf(emp, bendahara_name):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=40, bottomMargin=40, leftMargin=50, rightMargin=50)
    elements = []
    styles = getSampleStyleSheet()
    
    # Header PDF yang lebih rapi
    title_style = ParagraphStyle(name='TitleHeader', parent=styles['Heading1'], alignment=1, fontSize=16, spaceAfter=2)
    sub_style = ParagraphStyle(name='Sub', parent=styles['Normal'], alignment=1, fontSize=12, spaceAfter=20)
    
    elements.append(Paragraph("SLIP GAJI PEGAWAI", title_style))
    elements.append(Paragraph("LEMBAGA PEMASYARAKATAN KELAS IIB ARGA MAKMUR", sub_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Info
    info_style = ParagraphStyle(name='InfoBody', parent=styles['Normal'], fontSize=11, leading=16)
    elements.append(Paragraph(f"<b>NAMA :</b> {emp.get('Nama', '-')}", info_style))
    elements.append(Paragraph(f"<b>NIP       :</b> {emp.get('NIP', '-')}", info_style))
    elements.append(Paragraph(f"<b>PERIODE :</b> {datetime.now().strftime('%B %Y').upper()}", info_style))
    elements.append(Spacer(1, 0.2*inch))

    # Data Items
    inc_items = [('Gaji Pokok', parse_duit(emp.get('Gaji Pokok', 0))), ('Tunjangan Kinerja', parse_duit(emp.get('Tunkin', 0))), ('Uang Makan', parse_duit(emp.get('Uang Makan', 0)))]
    total_inc = sum(val for _, val in inc_items)

    ded_items_raw = [
        ('Ikapasi', emp.get('Ikapasi', 0)), ('Iuran Dharma Wanita', emp.get('Iuran Dharma Wanita', 0)),
        ('Donasi Dharma Wanita', emp.get('Don Dharma Wanita', 0)), ('Arisan Dharma Wanita', emp.get('Arisan Dharma Wanita', 0)),
        ('Denda Arisan', emp.get('Denda Arisan', 0)), ('Iuran DW Kabupaten', emp.get('Iuran Dw Kabupaten', 0)),
        ('BRI Cabang', emp.get('Bri Cab', 0)), ('Simpanan Pokok Koperasi', emp.get('Simpanan Pokok Koperasi', 0)),
        ('Simpanan Wajib Koperasi', emp.get('Simpanan Wajib Koperasi', 0)), ('Pinjaman Koperasi', emp.get('Pinjaman Koperasi', 0)),
        ('Kantin', emp.get('Kantin', 0)), ('Potongan STAR ASN', emp.get('Potongan STAR ASN', 0)),
        ('Pipas', emp.get('Pipas', 0)), ('Iuran Pipas', emp.get('Iuran Pipas', 0)),
        ('Gagal Debit', emp.get('Gagal Debit', 0)), ('Lain-Lain', emp.get('Lain-Lian', 0))
    ]
    ded_items = [(lbl, parse_duit(val)) for lbl, val in ded_items_raw]
    total_ded = sum(val for _, val in ded_items)
    take_home_pay = total_inc - total_ded

    # Tabel
    data_tabel = [['URAIAN', 'JUMLAH (IDR)'], ['PENGHASILAN', '']]
    for lbl, val in inc_items: data_tabel.append([f"  - {lbl}", format_rupiah(val)])
    data_tabel.append(['TOTAL PENGHASILAN', format_rupiah(total_inc)])
    data_tabel.append(['', ''])
    data_tabel.append(['POTONGAN', ''])
    for lbl, val in ded_items: data_tabel.append([f"  - {lbl}", format_rupiah(val)])
    data_tabel.append(['TOTAL POTONGAN', format_rupiah(total_ded)])
    data_tabel.append(['', ''])
    data_tabel.append(['GAJI BERSIH (DITERIMA)', format_rupiah(take_home_pay)])

    idx_sub_inc = 1 + len(inc_items) + 1
    idx_sub_ded = idx_sub_inc + 1 + 1 + len(ded_items) + 1 
    
    t = Table(data_tabel, colWidths=[4.2*inch, 2.3*inch])
    t.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'), ('FONTSIZE', (0,0), (-1,-1), 10),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1a237e")), ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'), ('ALIGN', (0,0), (-1,0), 'CENTER'), ('ALIGN', (1,1), (1,-1), 'RIGHT'),
        ('FONTNAME', (0,1), (0,1), 'Helvetica-Bold'), ('FONTNAME', (0, idx_sub_inc + 2), (0, idx_sub_inc + 2), 'Helvetica-Bold'),
        ('BACKGROUND', (0, idx_sub_inc), (-1, idx_sub_inc), colors.whitesmoke), ('FONTNAME', (0, idx_sub_inc), (-1, idx_sub_inc), 'Helvetica-Bold'),
        ('BACKGROUND', (0, idx_sub_ded), (-1, idx_sub_ded), colors.whitesmoke), ('FONTNAME', (0, idx_sub_ded), (-1, idx_sub_ded), 'Helvetica-Bold'),
        ('BACKGROUND', (0,-1), (-1,-1), colors.lightgrey), ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
        ('TOPPADDING', (0,-1), (-1,-1), 10), ('BOTTOMPADDING', (0,-1), (-1,-1), 10), ('GRID', (0,0), (-1,-1), 0.25, colors.grey),
    ]))
    elements.append(t)
    
    elements.append(Spacer(1, 0.5*inch))
    ttd_content = f"Arga Makmur, {datetime.now().strftime('%d %B %Y')}<br/>Bendahara Pengeluaran<br/><br/><br/><br/><b><u>{bendahara_name}</u></b>"
    elements.append(Paragraph(ttd_content, ParagraphStyle(name='TTD', parent=styles['Normal'], alignment=2, rightIndent=30)))

    doc.build(elements)
    buffer.seek(0)
    return buffer

# ==========================================
# 3. USER INTERFACE (FRONTEND MODERN)
# ==========================================
def main():
    # --- HEADER VISUAL ---
    st.markdown("""
        <div class="header-container">
            <h1 class="header-title">E-SLIP GAJI</h1>
            <p class="header-subtitle">LEMBAGA PEMASYARAKATAN KELAS IIB ARGA MAKMUR</p>
        </div>
    """, unsafe_allow_html=True)

    # Sidebar Navigasi yang Bersih
    with st.sidebar:
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Logo_Pengayoman_Kementerian_Hukum_dan_HAM_RI.png/600px-Logo_Pengayoman_Kementerian_Hukum_dan_HAM_RI.png", width=100)
        st.markdown("### Menu Aplikasi")
        menu = st.radio("", ["🏠 Beranda Login", "⚙️ Admin Panel"])
        st.markdown("---")
        st.caption("© 2026 Lapas Arga Makmur")

    df = load_data()

    # --- HALAMAN 1: LOGIN (CARD DESIGN) ---
    if menu == "🏠 Beranda Login":
        # Membuat Layout Kolom agar Login Box di Tengah
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown('<div class="card-box">', unsafe_allow_html=True)
            st.markdown("### 🔐 Akses Pegawai")
            st.write("Masukkan identitas Anda untuk mengunduh slip gaji.")
            
            if df is None:
                st.error("⚠️ Sistem sedang maintenance (Database belum siap).")
            else:
                with st.form("login_form"):
                    nama_input = st.text_input("Nama Lengkap", placeholder="Contoh: AGUS SALIM")
                    kode_input = st.text_input("Kode Akses", type="password", placeholder="Masukkan kode unik Anda")
                    st.write("") # Spacer
                    bendahara_input = st.text_input("Nama Bendahara (Untuk TTD)", "BUDI SANTOSO, S.E.")
                    st.write("") # Spacer
                    cari_button = st.form_submit_button("Cek Slip Gaji Saya")

                if cari_button:
                    # Proses Pencarian
                    hasil = df[
                        (df['Nama_Clean'].str.contains(nama_input.strip().lower(), na=False)) & 
                        (df['Kode_Clean'] == kode_input.strip())
                    ]

                    if not hasil.empty:
                        pegawai = hasil.iloc[0]
                        st.success(f"✅ Login Berhasil! Halo, {pegawai['Nama']}")
                        
                        # Generate PDF
                        pdf_file = create_pdf(pegawai, bendahara_input)
                        base64_pdf = base64.b64encode(pdf_file.getvalue()).decode('utf-8')
                        
                        st.markdown("---")
                        
                        # Tombol Download Besar
                        col_dl1, col_dl2 = st.columns([1,1])
                        with col_dl1:
                            st.download_button(
                                label="📥 DOWNLOAD PDF SEKARANG",
                                data=pdf_file,
                                file_name=f"SlipGaji_{pegawai['Nama']}.pdf",
                                mime="application/pdf",
                                type="primary",
                                use_container_width=True
                            )
                        
                        # Preview PDF
                        pdf_display = f'''
                            <object data="data:application/pdf;base64,{base64_pdf}" type="application/pdf" width="100%" height="600">
                                <div style="text-align:center; padding:20px; border:1px solid #ccc; background:#f9f9f9;">
                                    <p>⚠️ Browser Anda tidak mendukung pratinjau PDF.</p>
                                </div>
                            </object>
                        '''
                        st.markdown(pdf_display, unsafe_allow_html=True)
                    else:
                        st.error("❌ Login Gagal. Nama atau Kode Akses tidak ditemukan.")
            
            st.markdown('</div>', unsafe_allow_html=True) # Tutup Card

    # --- HALAMAN 2: ADMIN PANEL ---
    elif menu == "⚙️ Admin Panel":
        col1, col2, col3 = st.columns([1, 4, 1])
        with col2:
            st.markdown('<div class="card-box">', unsafe_allow_html=True)
            st.markdown("### 🛠️ Pengaturan Administrator")
            
            pw = st.text_input("Password Admin", type="password")
            
            if pw == ADMIN_PASSWORD:
                st.success("Akses Diberikan")
                
                tab1, tab2 = st.tabs(["📝 Edit Data", "📂 Update Bulan Baru"])
                
                with tab1:
                    st.info("Klik dua kali pada sel tabel untuk mengedit data.")
                    if df is not None:
                        cols_view = [c for c in df.columns if 'Clean' not in c]
                        edited_df = st.data_editor(df[cols_view], num_rows="dynamic", use_container_width=True)
                        
                        if st.button("Simpan Perubahan", type="primary"):
                            try:
                                with open(FILE_PATH, 'r') as f: lines = f.readlines()
                                header_lines = lines[:3]
                                csv_data = edited_df.to_csv(index=False, header=False)
                                with open(FILE_PATH, 'w') as f: 
                                    f.writelines(header_lines)
                                    f.write(csv_data)
                                st.toast("Data tersimpan!", icon="✅")
                                load_data.clear()
                                st.rerun() 
                            except Exception as e: st.error(f"Error: {e}")
                
                with tab2:
                    st.warning("⚠️ Upload file CSV baru akan menimpa data bulan sebelumnya.")
                    uploaded_file = st.file_uploader("Upload File CSV", type=['csv'])
                    if uploaded_file is not None:
                        if st.button("Proses Upload", type="primary"):
                            try:
                                with open(FILE_PATH, "wb") as f:
                                    f.write(uploaded_file.getbuffer())
                                st.success("Database berhasil diperbarui!")
                                load_data.clear()
                                st.rerun()
                            except Exception as e:
                                st.error(f"Gagal: {e}")
            elif pw:
                st.error("Password Salah")
            
            st.markdown('</div>', unsafe_allow_html=True)

    # --- FOOTER ---
    st.markdown('<div class="footer">Sistem Informasi Penggajian - Lapas Kelas IIB Arga Makmur &copy; 2026</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
