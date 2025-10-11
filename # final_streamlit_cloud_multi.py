# final_streamlit_cloud_multi.py
import streamlit as st
import re

st.set_page_config(page_title="Pencarian OPTK A2 Berdasarkan Inang/Daerah/Media by Noya", layout="wide")
st.title("Pencarian OPTK A2 Berdasarkan Inang/Daerah/Media(multi-kata)")
# =======================
# Aksesori di bawah judul
st.markdown("""
**by:** Noya
---
""")


# 1. Baca file default
# =======================
try:
    with open("teks_OPTKA2.txt", "r", encoding="utf-8") as f:
        lines = f.read().splitlines()
except FileNotFoundError:
    st.error("File default 'teks_OPTKA2.txt' tidak ditemukan!")
    st.stop()

# =======================
# 2. Gabungkan baris menjadi record
# =======================
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

# =======================
# 3. Input multi-kata
# =======================
kata_inang = st.text_input("Masukkan kata untuk Inang / Host (pisahkan koma jika lebih dari satu)")
kata_daerah = st.text_input("Masukkan kata untuk Daerah Sebar (pisahkan koma jika lebih dari satu)")
kata_media = st.text_input("Masukkan kata untuk Media Pembawa / Pathway (pisahkan koma jika lebih dari satu)")

if st.button("Cari"):
    # Fungsi buat list kata regex dari input multi-kata
    def buat_regex_multi(kata_input):
        if kata_input:
            kata_list = [k.strip() for k in kata_input.split(",") if k.strip()]
            return [re.compile(rf"\b{re.escape(k)}\b", re.IGNORECASE) for k in kata_list]
        return []

    pattern_inang_list = buat_regex_multi(kata_inang)
    pattern_daerah_list = buat_regex_multi(kata_daerah)
    pattern_media_list = buat_regex_multi(kata_media)

    # Filter record
    hasil = []
    for rec in records:
        def cocok(pattern_list):
            if not pattern_list:
                return True
            return any(p.search(rec) for p in pattern_list)

        if cocok(pattern_inang_list) and cocok(pattern_daerah_list) and cocok(pattern_media_list):
            hasil.append(rec)

    if hasil:
        st.write(f"Ditemukan {len(hasil)} record. Menampilkan 2 atau 3 kata pertama dari setiap record:")
        hasil_2kata = []
        for i, h in enumerate(hasil, start=1):
            h_clean = re.sub(r"^\d+\.\s*", "", h)
            h_clean = re.sub(r"--- Halaman \d+ ---", "", h_clean)
            h_clean = re.sub(r"Dokumen ini telah ditandatangani.*", "", h_clean)
            h_clean = h_clean.strip()

            kata_split = h_clean.split()
            if kata_split and "[" in kata_split[0]:
                kata1 = kata_split[0]
                kata2 = kata_split[1] if len(kata_split) > 1 else ""
                sisa = kata_split[2:]
                kata3 = ""
                for k in sisa:
                    kata_clean = re.sub(r"^[^\w]+", "", k)
                    if kata_clean.isalpha():
                        kata3 = kata_clean
                        break
                kata_ambil = " ".join([kata1, kata2, kata3])
            else:
                kata_ambil = " ".join(kata_split[:2])

            st.text(f"{i}. {kata_ambil}")
            hasil_2kata.append(kata_ambil)

        # Download CSV
        csv_content = "Hasil Kata\n" + "\n".join(hasil_2kata)
        st.download_button(
            label="Download CSV",
            data=csv_content,
            file_name="hasil_multi_kata.csv",
            mime="text/csv"
        )
    else:
        st.write("Tidak ditemukan hasil yang cocok.")

