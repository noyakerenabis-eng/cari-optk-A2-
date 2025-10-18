import streamlit as st
import re
import csv
import io

# === 1. Konfigurasi halaman ===
st.set_page_config(page_title="Daftar OPTK & Kategori", layout="wide")

st.title("📋 Daftar OPTK & Kategori")
st.markdown("**Simplified version by Noya**")
st.markdown("---")

# === 2. Pilih file A1 / A2 ===
jenis_optk = st.selectbox("Pilih jenis OPTK:", ["A1", "A2"], index=1)
file_map = {"A1": "teks_OPTKA1.txt", "A2": "teks_OPTKA2.txt"}
file_terpilih = file_map[jenis_optk]

# === 3. Baca file ===
try:
    with open(file_terpilih, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()
except FileNotFoundError:
    st.error(f"File '{file_terpilih}' tidak ditemukan!")
    st.stop()

# === 4. Gabungkan baris menjadi record ===
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

st.write(f"📂 Jumlah record: {len(records)}")
st.markdown("---")

# === 5. Input pencarian (opsional) ===
kata_cari = st.text_input("🔎 Filter kata (optional, pisahkan koma jika lebih dari satu)")

def buat_regex_multi(kata_input):
    if kata_input:
        kata_list = [k.strip() for k in kata_input.split(",") if k.strip()]
        return [re.compile(rf"\b{re.escape(k)}\b", re.IGNORECASE) for k in kata_list]
    return []

pattern_list = buat_regex_multi(kata_cari)

# === 6. Kategori default (regex sederhana) ===
kategori_optk = {
    "Serangga": ["Coleoptera", "Lepidoptera", "Diptera", "Insecta", "beetle", "borer", "fly"],
    "Virus": ["virus", "viroid", "begomovirus", "tospovirus"],
    "Bakteri": ["bacterium", "bacteria", "Ralstonia", "Phytoplasma"],
    "Jamur": ["Fusarium", "Phytophthora", "Cercospora", "Colletotrichum", "Rhizoctonia"],
    "Nematoda": ["Meloidogyne", "Heterodera", "Pratylenchus"],
    "Tungau": ["Acarina", "mite"],
    "Gulma": ["weed", "Amaranthus", "Cyperus", "Mikania"],
    "Siput": ["Achatina", "snail", "slug"]
}

def deteksi_kategori(teks):
    for kategori, kata_list in kategori_optk.items():
        for kata in kata_list:
            if re.search(rf"\b{kata}\b", teks, re.IGNORECASE):
                return kategori
    return "Lainnya"

# === 7. Proses record ===
hasil_list = []
for rec in records:
    if pattern_list and not any(p.search(rec) for p in pattern_list):
        continue
    h_clean = re.sub(r"^\d+\.\s*", "", rec)
    h_clean = re.sub(r"--- Halaman \d+ ---", "", h_clean)
    h_clean = re.sub(r"Dokumen ini telah ditandatangani.*", "", h_clean)
    h_clean = h_clean.strip()
    target = " ".join(h_clean.split()[:3])
    kategori = deteksi_kategori(h_clean)
    hasil_list.append({"Nama/Target": target, "Kategori": kategori})

# === 8. Tampilkan tabel ===
if hasil_list:
    st.write("### Hasil Daftar OPTK & Kategori")
    st.table(hasil_list)

    # Download CSV
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=["Nama/Target", "Kategori"])
    writer.writeheader()
    writer.writerows(hasil_list)

    st.download_button(
        label="💾 Download CSV",
        data=output.getvalue(),
        file_name=f"daftar_OPTKA{jenis_optk}.csv",
        mime="text/csv"
    )
else:
    st.warning("Tidak ada record yang cocok.")
