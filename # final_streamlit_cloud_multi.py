# final_streamlit_csv_complete.py
import streamlit as st
import re
import csv
import io

# Konfigurasi halaman
st.set_page_config(page_title="Pencarian OPTK A2 Berdasarkan Inang/Daerah/Media by Noya", layout="wide")

st.title("Pencarian OPTK A2 Berdasarkan Inang / Daerah / Media")
st.markdown("**by: Noya**")
st.markdown("---")

# === 1. Baca file teks bawaan ===
try:
    with open("teks_OPTKA2.txt", "r", encoding="utf-8") as f:
        lines = f.read().splitlines()
except FileNotFoundError:
    st.error("File default 'teks_OPTKA2.txt' tidak ditemukan! Pastikan file ada di folder yang sama dengan app.py")
    st.stop()

# === 2. Gabungkan baris jadi record ===
records = []
temp = ""
for line in lines:
    line = line.strip()
    if re.match(r"^\d+\.", line):  # mulai record baru
        if temp:
            records.append(temp)
        temp = line
    else:
        temp += " " + line
if temp:
    records.append(temp)

st.write(f"Jumlah record: {len(records)}")

# === 3. Input pencarian ===
kata_inang = st.text_input("Masukkan kata untuk Inang / Host (pisahkan koma jika lebih dari satu)")
kata_daerah = st.text_input("Masukkan kata untuk Daerah Sebar (pisahkan koma jika lebih dari satu)")
kata_media = st.text_input("Masukkan kata untuk Media Pembawa / Pathway (pisahkan koma jika lebih dari satu)")

# === 4. Tombol cari ===
if st.button("🔍 Cari"):
    # Fungsi untuk buat regex list
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

    # === 5. Tampilkan hasil ===
    if hasil:
        st.success(f"Ditemukan {len(hasil)} record.")
        hasil_2kata = []
        data_csv = []

        for i, h in enumerate(hasil, start=1):
            h_clean = re.sub(r"^\d+\.\s*", "", h)
            h_clean = re.sub(r"--- Halaman \d+ ---", "", h_clean)
            h_clean = re.sub(r"Dokumen ini telah ditandatangani.*", "", h_clean)
            h_clean = h_clean.strip()
            kata_split = h_clean.split()

            # logika nama OPTK
            if kata_split and "[" in kata_split[0]:
                kata1 = kata_split[0]
                kata2 = kata_split[1] if len(kata_split) > 1 else ""
                kata3 = kata_split[2] if len(kata_split) > 2 else ""
                target = " ".join([kata1, kata2, kata3])
                query_google = f"{kata2} {kata3}"
            else:
                target = " ".join(kata_split[:2])
                query_google = target

            google_link = f"https://www.google.com/search?q={query_google.replace(' ', '+')}"
            st.markdown(f"{i}. [{target}]({google_link})", unsafe_allow_html=True)
            hasil_2kata.append(target)

            # Simulasi parsing (karena teks aslinya tidak rapi)
            host = re.search(r"[Hh]ost[:：]\s*([^;]*)", h)
            pathway = re.search(r"[Pp]athway[:：]\s*([^;]*)", h)
            dist = re.search(r"[Dd]istribution[:：]\s*([^;]*)", h)

            data_csv.append({
                "No": i,
                "Target": target,
                "Host": host.group(1).strip() if host else "-",
                "Pathway": pathway.group(1).strip() if pathway else "-",
                "Distribution": dist.group(1).strip() if dist else "-"
            })
  # === 6. Download CSV ===
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=["No", "Target", "Host", "Pathway", "Distribution"])
        writer.writeheader()
        writer.writerows(data_csv)

        st.download_button(
            label="💾 Download CSV Lengkap",
            data=output.getvalue(),
            file_name="hasil_lengkap.csv",
            mime="text/csv"
        )

    else:
        st.warning("Tidak ditemukan hasil yang cocok.")
       # === Tombol Download hasil pencarian ===

