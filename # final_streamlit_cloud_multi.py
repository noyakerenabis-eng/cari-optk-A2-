    # final_streamlit_classic_theme.py
import streamlit as st
import re

# Konfigurasi halaman
st.set_page_config(page_title="Pencarian OPTK A2 Berdasarkan Inang/Daerah/Media by Noya", layout="wide")

# CSS tema klasik
st.markdown("""
    <style>
    body {
        background-color: #1800ad;
        background-image: radial-gradient(#1800ad 1px, transparent 1px);
        background-size: 40px 40px;
        font-family: 'Georgia', serif;
        color: #1800ad;
    }
    .stApp {
        background: linear-gradient(180deg, #0097b2, #38b6ff);
    }
    h1 {
        color: #5b4636;
        text-align: center;
        font-size: 2.3em;
        text-shadow: 1px 1px 2px #d2b48c;
        margin-bottom: 0.2em;
    }
    .subtitle {
        text-align: center;
        font-style: italic;
        color: #6e5845;
        margin-bottom: 1.5em;
    }
    .result {
        background-color: #fff9f0;
        border-left: 5px solid #b08b51;
        padding: 10px;
        margin: 8px 0;
        border-radius: 10px;
        transition: all 0.3s ease;
    }
    .result:hover {
        transform: scale(1.02);
        box-shadow: 0 0 10px rgba(176, 139, 81, 0.4);
    }
    a {
        color: #8b4513;
        text-decoration: none;
    }
    a:hover {
        text-decoration: underline;
        color: #a0522d;
    }
    </style>
""", unsafe_allow_html=True)

# Judul & identitas
st.markdown("<h1>Pencarian OPTK A2 Berdasarkan Inang / Daerah / Media</h1>", unsafe_allow_html=True)
st.markdown('<div class="subtitle">by Noya</div>', unsafe_allow_html=True)
st.markdown("---")

# Baca file teks bawaan
try:
    with open("teks_OPTKA2.txt", "r", encoding="utf-8") as f:
        lines = f.read().splitlines()
except FileNotFoundError:
    st.error("File default 'teks_OPTKA2.txt' tidak ditemukan!")
    st.stop()

# Gabungkan baris menjadi record
records = []
temp = ""
for line in lines:
    line = line.strip()
    if re.match(r"^\d+\.", line):
        if temp:
            records.append(temp)
        temp = line
    else:
        temp += " " + line
if temp:
    records.append(temp)

st.write(f"Jumlah record: {len(records)}")

# Input teks
kata_inang = st.text_input("Masukkan kata untuk Inang / Host (pisahkan koma jika lebih dari satu)")
kata_daerah = st.text_input("Masukkan kata untuk Daerah Sebar (pisahkan koma jika lebih dari satu)")
kata_media = st.text_input("Masukkan kata untuk Media Pembawa / Pathway (pisahkan koma jika lebih dari satu)")

# Tombol cari
if st.button("🔍 Cari"):
    # Buat regex dari input multi
    def buat_regex_multi(kata_input):
        if kata_input:
            kata_list = [k.strip() for k in kata_input.split(",") if k.strip()]
            return [re.compile(rf"\b{re.escape(k)}\b", re.IGNORECASE) for k in kata_list]
        return []

    pattern_inang_list = buat_regex_multi(kata_inang)
    pattern_daerah_list = buat_regex_multi(kata_daerah)
    pattern_media_list = buat_regex_multi(kata_media)

    hasil = []
    for rec in records:
        def cocok(pattern_list):
            if not pattern_list:
                return True
            return any(p.search(rec) for p in pattern_list)

        if cocok(pattern_inang_list) and cocok(pattern_daerah_list) and cocok(pattern_media_list):
            hasil.append(rec)

    if hasil:
        st.write(f"✅ Ditemukan {len(hasil)} record. Klik nama untuk melihat di Google:")
        hasil_2kata = []
        for i, h in enumerate(hasil, start=1):
            h_clean = re.sub(r"^\d+\.\s*", "", h)
            h_clean = re.sub(r"--- Halaman \d+ ---", "", h_clean)
            h_clean = re.sub(r"Dokumen ini telah ditandatangani.*", "", h_clean)
            h_clean = h_clean.strip()
            kata_split = h_clean.split()

            # logika hasil dua atau tiga kata
            if kata_split and "[" in kata_split[0]:
                kata1 = kata_split[0]
                kata2 = kata_split[1] if len(kata_split) > 1 else ""
                kata3 = kata_split[2] if len(kata_split) > 2 else ""
                kata_ambil = " ".join([kata1, kata2, kata3])
                query_google = f"{kata2} {kata3}"
            else:
                kata_ambil = " ".join(kata_split[:2])
                query_google = kata_ambil

            hasil_2kata.append(kata_ambil)
            google_link = f"https://www.google.com/search?q={query_google.replace(' ', '+')}"
            st.markdown(
                f'<div class="result"><b>{i}. <a href="{google_link}" target="_blank">{kata_ambil}</a></b></div>',
                unsafe_allow_html=True
            )

        # Tombol download hasil
        csv_content = "Hasil Kata\n" + "\n".join(hasil_2kata)
        st.download_button(
            label="💾 Download CSV",
            data=csv_content,
            file_name="hasil_multi_kata.csv",
            mime="text/csv"
        )
    else:
        st.warning("Tidak ditemukan hasil yang cocok.")






