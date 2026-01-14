import streamlit as st
import pandas as pd
import base64
from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="E-Slip Gaji Lapas Arga Makmur", layout="centered", page_icon="📄")

# --- KONSTANTA ---
FILE_PATH = 'DataGaji.csv'
ADMIN_PASSWORD = "Jaka2505" 

# --- FUNGSI LOAD DATA (Dengan Cache) ---
@st.cache_data
def load_data():
    try:
        # Header ada di baris ke-3 (index 2)
        df = pd.read_csv(FILE_PATH, header=2, dtype=str)
        
        # Hapus baris sampah (jika ada)
        if not df.empty:
            val_cek = str(df.iloc[0]['Nama']).strip()
            if val_cek.isdigit() or len(val_cek) < 2:
                df = df.iloc[1:].reset_index(drop=True)

        # Bersihkan nama kolom
        df.columns = [str(c).strip() for c in df.columns]
        
        # Buat kolom pencarian
        if 'Nama' in df.columns:
            df['Nama_Clean'] = df['Nama'].astype(str).str.strip().str.lower()
        if 'kode akses' in df.columns:
            df['Kode_Clean'] = df['kode akses'].astype(str).str.strip()
            
        return df
    except Exception as e:
        return None

# --- FUNGSI HELPER ---
def parse_duit(val):
    try:
        clean = str(val).replace(',', '').replace('.', '').replace('Rp', '').strip()
        if not clean or clean.lower() == 'nan': return 0
        return int(float(clean))
    except:
        return 0

def format_rupiah(val):
    return f"Rp {val:,}".replace(",", ".")

# --- FUNGSI MEMBUAT PDF ---
def create_pdf(emp, bendahara_name):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=40, bottomMargin=40, leftMargin=50, rightMargin=50)
    elements = []
    styles = getSampleStyleSheet()
    
    # Judul
    title_style = ParagraphStyle(name='TitleHeader', parent=styles['Heading1'], alignment=1, fontSize=14)
    elements.append(Paragraph("SLIP GAJI PEGAWAI", title_style))
    elements.append(Paragraph("LEMBAGA PEMASYARAKATAN KELAS IIB ARGA MAKMUR", 
                              ParagraphStyle(name='Sub', parent=styles['Normal'], alignment=1, fontSize=11)))
    elements.append(Spacer(1, 0.3*inch))
    
    # Info
    info_style = ParagraphStyle(name='InfoBody', parent=styles['Normal'], fontSize=10, leading=14)
    elements.append(Paragraph(f"<b>NAMA :</b> {emp.get('Nama', '-')}", info_style))
    elements.append(Paragraph(f"<b>NIP       :</b> {emp.get('NIP', '-')}", info_style))
    elements.append(Paragraph(f"<b>PERIODE :</b> {datetime.now().strftime('%B %Y').upper()}", info_style))
    elements.append(Spacer(1, 0.15*inch))

    # Data
    inc_items = [
        ('Gaji Pokok', parse_duit(emp.get('Gaji Pokok', 0))),
        ('Tunjangan Kinerja', parse_duit(emp.get('Tunkin', 0))),
        ('Uang Makan', parse_duit(emp.get('Uang Makan', 0)))
    ]
    total_inc = sum(val for _, val in inc_items)

    ded_items_raw = [
        ('Ikapasi', emp.get('Ikapasi', 0)),
        ('Iuran Dharma Wanita', emp.get('Iuran Dharma Wanita', 0)),
        ('Donasi Dharma Wanita', emp.get('Don Dharma Wanita', 0)),
        ('Arisan Dharma Wanita', emp.get('Arisan Dharma Wanita', 0)),
        ('Denda Arisan', emp.get('Denda Arisan', 0)),
        ('Iuran DW Kabupaten', emp.get('Iuran Dw Kabupaten', 0)),
        ('BRI Cabang', emp.get('Bri Cab', 0)),
        ('Simpanan Pokok Koperasi', emp.get('Simpanan Pokok Koperasi', 0)),
        ('Simpanan Wajib Koperasi', emp.get('Simpanan Wajib Koperasi', 0)),
        ('Pinjaman Koperasi', emp.get('Pinjaman Koperasi', 0)),
        ('Kantin', emp.get('Kantin', 0)),
        ('Potongan STAR ASN', emp.get('Potongan STAR ASN', 0)),
        ('Pipas', emp.get('Pipas', 0)),
        ('Iuran Pipas', emp.get('Iuran Pipas', 0)),
        ('Gagal Debit', emp.get('Gagal Debit', 0)),
        ('Lain-Lain', emp.get('Lain-Lian', 0))
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

    # Style
    idx_sub_inc = 1 + len(inc_items) + 1
    idx_sub_ded = idx_sub_inc + 1 + 1 + len(ded_items) + 1 
    
    t = Table(data_tabel, colWidths=[4.2*inch, 2.3*inch])
    t.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('BACKGROUND', (0,0), (-1,0), colors.darkblue),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('ALIGN', (1,1), (1,-1), 'RIGHT'),
        ('FONTNAME', (0,1), (0,1), 'Helvetica-Bold'), 
        ('FONTNAME', (0, idx_sub_inc + 2), (0, idx_sub_inc + 2), 'Helvetica-Bold'),
        ('BACKGROUND', (0, idx_sub_inc), (-1, idx_sub_inc), colors.whitesmoke),
        ('FONTNAME', (0, idx_sub_inc), (-1, idx_sub_inc), 'Helvetica-Bold'),
        ('BACKGROUND', (0, idx_sub_ded), (-1, idx_sub_ded), colors.whitesmoke),
        ('FONTNAME', (0, idx_sub_ded), (-1, idx_sub_ded), 'Helvetica-Bold'),
        ('BACKGROUND', (0,-1), (-1,-1), colors.lightgrey),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,-1), (-1,-1), 11),
        ('TOPPADDING', (0,-1), (-1,-1), 8),
        ('BOTTOMPADDING', (0,-1), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.25, colors.grey),
    ]))
    elements.append(t)
    
    elements.append(Spacer(1, 0.4*inch))
    ttd_content = f"Arga Makmur, {datetime.now().strftime('%d %B %Y')}<br/>Bendahara Pengeluaran<br/><br/><br/><br/><b><u>{bendahara_name}</u></b>"
    elements.append(Paragraph(ttd_content, ParagraphStyle(name='TTD', parent=styles['Normal'], alignment=2, rightIndent=30)))

    doc.build(elements)
    buffer.seek(0)
    return buffer

# --- LOGIKA UTAMA ---
def main():
    st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Logo_Pengayoman_Kementerian_Hukum_dan_HAM_RI.png/600px-Logo_Pengayoman_Kementerian_Hukum_dan_HAM_RI.png", width=80)
    menu = st.sidebar.radio("Navigasi", ["Login Pegawai", "Admin Dashboard"])
    
    df = load_data()

    # --- MENU PEGAWAI ---
    if menu == "Login Pegawai":
        st.title("📄 Cetak Slip Gaji Lengkap")
        
        if df is None:
            st.warning("⚠️ Database Gaji belum tersedia. Hubungi Admin.")
            return

        with st.form("login_form"):
            col_a, col_b = st.columns(2)
            with col_a: nama_input = st.text_input("Nama Pegawai")
            with col_b: kode_input = st.text_input("Kode Akses", type="password")
            bendahara_input = st.text_input("Nama Bendahara", "Jaka Suryadinata")
            cari_button = st.form_submit_button("Cari & Tampilkan PDF")

        if cari_button:
            hasil = df[
                (df['Nama_Clean'].str.contains(nama_input.strip().lower(), na=False)) & 
                (df['Kode_Clean'] == kode_input.strip())
            ]

            if not hasil.empty:
                pegawai = hasil.iloc[0]
                st.success(f"Login Sukses: {pegawai['Nama']}")
                
                # Buat PDF
                pdf_file = create_pdf(pegawai, bendahara_input)
                base64_pdf = base64.b64encode(pdf_file.getvalue()).decode('utf-8')
                
                # --- SOLUSI BLOKIR BROWSER ---
                # Menggunakan tag <object> yang lebih aman daripada <iframe>
                # Dan menambahkan tombol download SANGAT JELAS di atasnya
                
                st.info("👇 Jika PDF tidak muncul otomatis, silakan klik tombol Download di bawah ini.")
                
                # Tombol Download Langsung (Pasti berhasil)
                st.download_button(
                    label="📥 DOWNLOAD FILE PDF (KLIK DISINI)",
                    data=pdf_file,
                    file_name=f"Slip_{pegawai['Nama']}.pdf",
                    mime="application/pdf",
                    type="primary" # Tombol berwarna menonjol
                )
                
                # Preview PDF (Menggunakan <object> agar lebih ramah browser)
                pdf_display = f'''
                    <object data="data:application/pdf;base64,{base64_pdf}" type="application/pdf" width="100%" height="800">
                        <p align="center">
                            <b>Browser Anda memblokir pratinjau PDF otomatis.</b><br>
                            Jangan khawatir, silakan klik tombol <b>Download</b> di atas untuk melihat slip gaji Anda.
                        </p>
                    </object>
                '''
                st.markdown(pdf_display, unsafe_allow_html=True)
                
            else:
                st.error("Data tidak ditemukan.")

    # --- MENU ADMIN ---
    elif menu == "Admin Dashboard":
        st.title("⚙️ Admin Dashboard")
        pw = st.sidebar.text_input("Password Admin", type="password")
        
        if pw == ADMIN_PASSWORD:
            st.success("Akses Admin Diterima")
            tab1, tab2 = st.tabs(["📝 Edit Data Manual", "📂 Upload Data Bulan Baru"])
            
            with tab1:
                st.info("Gunakan menu ini untuk mengedit data kecil (salah ketik, dll).")
                if df is not None:
                    cols = [c for c in df.columns if 'Clean' not in c]
                    edited_df = st.data_editor(df[cols], num_rows="dynamic")
                    if st.button("Simpan Perubahan Manual"):
                        try:
                            with open(FILE_PATH, 'r') as f: lines = f.readlines()
                            header = lines[:3]
                            csv = edited_df.to_csv(index=False, header=False)
                            with open(FILE_PATH, 'w') as f: 
                                f.writelines(header)
                                f.write(csv)
                            st.toast("Data manual tersimpan!", icon="✅")
                            load_data.clear()
                            st.rerun() 
                        except Exception as e: st.error(e)
                else:
                    st.error("File database tidak ditemukan.")

            with tab2:
                st.warning("⚠️ Perhatian: Upload file baru akan MENGHAPUS data bulan lama.")
                uploaded_file = st.file_uploader("Pilih File CSV (.csv) Data Gaji", type=['csv'])
                if uploaded_file is not None:
                    if st.button("🚀 Proses & Ganti Database"):
                        try:
                            with open(FILE_PATH, "wb") as f:
                                f.write(uploaded_file.getbuffer())
                            st.success("Sukses! Data gaji bulan baru telah diperbarui.")
                            load_data.clear()
                            st.rerun()
                        except Exception as e:
                            st.error(f"Gagal upload: {e}")

if __name__ == "__main__":
    main()
