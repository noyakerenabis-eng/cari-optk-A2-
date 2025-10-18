# final_streamlit_csv_group_by_range.py
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

# === 3. Baca file ===
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

    # === Fungsi bantu ===
    def buat_regex_multi(kata_input):
        if kata_input:
            kata_list = [k.strip() for k in kata_input.split(",") if k.strip()]
            return [re.compile(rf"\b{re.escape(k)}\b", re.IGNORECASE) for k in kata_list]
        return []

    def cocok(pattern_list, teks):
        if not pattern_list:
            return True
        return any(p.search(teks) for p in pattern_list)

    # === Buat pola regex ===
    pattern_inang = buat_regex_multi(kata_inang)
    pattern_daerah = buat_regex_multi(kata_daerah)
    pattern_media = buat_regex_multi(kata_media)

    # === 7. Tentukan kategori berdasarkan baris ===
    kategori_map = {}
    if jenis_optk == "A1":
        kategori_map = {
            "Serangga": (2, 237),
            "Tungau": (239, 262),
            "Keong": (264, 278),
            "Siput": (280, 293),
            "Nematoda": (295, 360),
            "Gulma parasitik": (362, 392),
            "Gulma non parasitik": (398, 404),
            "Cendawan": (406, 538),
            "Bakteri": (540, 594),
            "Mollicute": (596, 610),
            "Virus": (612, 732),
            "Viroid": (733, 739)
        }
    else:  # A2
        kategori_map = {
            "Serangga": (2, 50),
            "Tungau": (52, 58),
            "Keong": (60, 61),
            "Nematoda": (63, 72),
            "Gulma non parasitik": (74, 77),
            "Cendawan": (79, 108),
            "Bakteri": (110, 123),
            "Virus": (125, 136),
            "Viroid": (138, 138)
        }

    def kategori_by_index(index):
        no = index + 2  # karena record pertama mulai dari no.2
        for kategori, (start, end) in kategori_map.items():
            if start <= no <= end:
                return kategori
        return "Tidak Terklasifikasi"

    # === 8. Filter hasil berdasarkan input ===
    hasil = []
    for rec in records:
        if cocok(pattern_inang, rec) and cocok(pattern_daerah, rec) and cocok(pattern_media, rec):
            hasil.append(rec)

    # === 9. Output ===
    if hasil:
        st.success(f"Ditemukan {len(hasil)} record pada OPTK {jenis_optk}.")
        hasil_per_kategori = {}
        data_csv = []

        for i, h in enumerate(hasil, start=1):
            kategori = kategori_by_index(records.index(h))
            hasil_per_kategori.setdefault(kategori, []).append(h)

            h_clean = re.sub(r"^\d+\.\s*", "", h).strip()
            kata_split = h_clean.split()
            target = " ".join(kata_split[:3])
            google_link = f"https://www.google.com/search?q={target.replace(' ', '+')}"

            host = re.search(r"[Hh]ost[:：]\s*([^;]*)", h)
            pathway = re.search(r"[Pp]athway[:：]\s*([^;]*)", h)
            dist = re.search(r"[Dd]istribution[:：]\s*([^;]*)", h)

            data_csv.append({
                "No": i,
                "Target": target,
                "Kategori": kategori,
                "Host": host.group(1).strip() if host else "-",
                "Pathway": pathway.group(1).strip() if pathway else "-",
                "Distribution": dist.group(1).strip() if dist else "-",
                "Google": google_link
            })

        for kategori, daftar in hasil_per_kategori.items():
            st.markdown(f"### 🧬 {kategori} ({len(daftar)} hasil)")
            for teks in daftar:
                kata_split = teks.split()
                target = " ".join(kata_split[:3])
                link = f"https://www.google.com/search?q={target.replace(' ', '+')}"
                st.markdown(f"- [{target}]({link})", unsafe_allow_html=True)
            st.markdown("---")

        # === 10. Download CSV ===
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=["No", "Target", "Kategori", "Host", "Pathway", "Distribution", "Google"])
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
