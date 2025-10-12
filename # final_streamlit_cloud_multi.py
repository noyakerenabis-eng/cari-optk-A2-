# final_streamlit_csv_complete_grouped.py
import streamlit as st
import re
import csv
import io

# === 1. Konfigurasi halaman ===
st.set_page_config(page_title="Pencarian OPTK A1/A2 by Noya", layout="wide")

st.title("🔎 Pencarian OPTK A1 / A2 Berdasarkan Inang / Daerah / Media")
st.markdown("**by: Noya**")
st.markdown("---")

# === 2. Pilihan jenis OPTK ===
jenis_optk = st.selectbox(
    "Pilih jenis OPTK yang ingin dicari:",
    ["A1", "A2"],
    index=1
)

file_map = {"A1": "teks_OPTKA1.txt", "A2": "teks_OPTKA2.txt"}
file_terpilih = file_map[jenis_optk]

# === 3. Baca file sesuai pilihan ===
try:
    with open(file_terpilih, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()
except FileNotFoundError:
    st.error(f"File '{file_terpilih}' tidak ditemukan! Pastikan file ada di folder yang sama.")
    st.stop()

# === 4. Gabungkan baris jadi record ===
records = []
temp = ""
for line in lines:
    line = line.strip()
    if re.match(r"^\d+\.", line):  # awal record baru
        if temp:
            records.append(temp)
        temp = line
    else:
        temp += " " + line
if temp:
    records.append(temp)

st.write(f"📂 Jumlah record dalam {jenis_optk}: {len(records)}")

st.markdown("---")

# === 5. Input pencarian ===
st.subheader("Masukkan kata pencarian")
kata_inang = st.text_input("🪴 Inang / Host (pisahkan koma jika lebih dari satu)")
kata_daerah = st.text_input("📍 Daerah Sebar (pisahkan koma jika lebih dari satu)")
kata_media = st.text_input("📦 Media Pembawa / Pathway (pisahkan koma jika lebih dari satu)")

# === 6. Tombol cari ===
if st.button("🔍 Cari"):
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

    # === 7. Deteksi kategori organisme ===
    kategori_map = {
        "Serangga": ["Coleoptera", "Lepidoptera", "Diptera", "Hemiptera", "Insecta", "beetle", "moth", "fly"],
        "Virus": ["virus", "viroid"],
        "Bakteri": ["bacterium", "bacteria", "Ralstonia", "Xanthomonas", "Erwinia"],
        "Jamur": ["Fusarium", "Phytophthora", "Cercospora", "Colletotrichum", "Puccinia"],
        "Nematoda": ["Meloidogyne", "Heterodera", "Pratylenchus", "nematode"],
        "Gulma": ["weed", "Amaranthus", "Avena", "Cyperus"]
    }

    def deteksi_kategori(teks):
        for kategori, keywords in kategori_map.items():
            for k in keywords:
                if re.search(rf"\b{k}\b", teks, re.IGNORECASE):
                    return kategori
        return "Lainnya"

    # === 8. Tampilkan hasil terkelompok ===
    if hasil:
        st.success(f"Ditemukan {len(hasil)} record pada OPTK {jenis_optk}.")

        hasil_per_kategori = {}
        data_csv = []

        for i, h in enumerate(hasil, start=1):
            kategori = deteksi_kategori(h)
            hasil_per_kategori.setdefault(kategori, []).append(h)

            h_clean = re.sub(r"^\d+\.\s*", "", h)
            h_clean = re.sub(r"--- Halaman \d+ ---", "", h_clean)
            h_clean = re.sub(r"Dokumen ini telah ditandatangani.*", "", h_clean)
            h_clean = h_clean.strip()
            kata_split = h_clean.split()

            target = " ".join(kata_split[:3])
            query_google = target
            google_link = f"https://www.google.com/search?q={query_google.replace(' ', '+')}"

            host = re.search(r"[Hh]ost[:：]\s*([^;]*)", h)
            pathway = re.search(r"[Pp]athway[:：]\s*([^;]*)", h)
            dist = re.search(r"[Dd]istribution[:：]\s*([^;]*)", h)

            data_csv.append({
                "No": i,
                "Target": target,
                "Kategori": kategori,
                "Host": host.group(1).strip() if host else "-",
                "Pathway": pathway.group(1).strip() if pathway else "-",
                "Distribution": dist.group(1).strip() if dist else "-"
            })

        # === 9. Tampilkan per kategori ===
        for kategori, daftar in hasil_per_kategori.items():
            st.markdown(f"### 🧬 {kategori} ({len(daftar)} hasil)")
            for idx, teks in enumerate(daftar, start=1):
                kata_split = teks.split()
                target = " ".join(kata_split[:3])
                link = f"https://www.google.com/search?q={target.replace(' ', '+')}"
                st.markdown(f"- [{target}]({link})", unsafe_allow_html=True)
            st.markdown("---")

        # === 10. Download CSV ===
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=["No", "Target", "Kategori", "Host", "Pathway", "Distribution"])
        writer.writeheader()
        writer.writerows(data_csv)

        st.download_button(
            label=f"💾 Download Hasil OPTK {jenis_optk} (CSV)",
            data=output.getvalue(),
            file_name=f"hasil_OPTKA{jenis_optk}_grup.csv",
            mime="text/csv"
        )

    else:
        st.warning(f"Tidak ditemukan hasil yang cocok pada OPTK {jenis_optk}.")
