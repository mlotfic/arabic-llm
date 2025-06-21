# from pdf2image import convert_from_path
# import pytesseract
# from PIL import Image

# # Poppler کا درست راستہ
# poppler_path = r"C:\Users\Administrator\Downloads\Release-24.07.0-0\poppler-24.07.0\Library\bin"

# # Tesseract کا درست راستہ
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# # پی ڈی ایف کو امیج میں تبدیل کریں
# images = convert_from_path("C:/Users/Administrator/Desktop/005_1-26.pdf", poppler_path=poppler_path)

# # ہر امیج سے متن نکالیں
# extracted_text = []
# for i, img in enumerate(images):
#     text = pytesseract.image_to_string(img, lang="ara")  # Arabic OCR
#     extracted_text.append(text)
#     print(f"✅ Page {i+1} processed.")

# # پورے متن کو ایک فائل میں محفوظ کریں
# with open("extracted_text.txt", "w", encoding="utf-8") as f:
#     f.write("\n".join(extracted_text))

# print("🎉 Arabic text extracted successfully!")


import re
import pandas as pd

# 🔹 "extracted_text.txt" سے متن پڑھیں
file_path = "extracted_text.txt"
with open(file_path, "r", encoding="utf-8") as file:
    text = file.read()

# 🔹 نئے اور زیادہ اسمارٹ regex پیٹرنز
narrator_pattern = re.compile(r"(\d+)\s*-\s*([\w\sء-ي]+)\s*\*", re.UNICODE)
aliases_pattern = re.compile(r"(المعروف ب|يلقب بـ|أو يسمى) ([\w\sء-ي]+)")
death_year_pattern = re.compile(r"مَاتَ(?: سَنَةَ| فِي حُدُودِ سَنَةِ|: )(\d+)")
birth_year_pattern = re.compile(r"وُلِدَ(?: فِي سَنَةِ|: )(\d+)")
place_pattern = re.compile(r"(البصرة|الكوفة|المدينة|الشام|دمشق|مكة|اليمن|خراسان)")
travel_pattern = re.compile(r"(سافر إلى|رحل إلى|ذهب إلى) ([\w\s،]+)")
memory_changes_pattern = re.compile(r"(كان قويًا في الحفظ قبل|ضعف حفظه بعد) (\d+ ه)")
tadlis_pattern = re.compile(r"(كان معروفًا بالتدليس|مارس التدليس)")
reliability_pattern = re.compile(r"(ثقة|ضعيف|متروك|صدوق|كذاب)")
hadith_id_pattern = re.compile(r"حديث رقم (\d+)")
students_pattern = re.compile(r"(روى عنه|حدث عنه) ([\w\s،]+)")

# 🔹 راویوں کی لسٹ
narrators = []
current_narrator = {}

# 🔹 متن کو لائن بائی لائن پراسیس کریں
lines = text.split("\n")
for line in lines:
    # 🔹 نیا راوی تلاش کریں
    narrator_match = narrator_pattern.search(line)
    if narrator_match:
        if current_narrator:
            narrators.append(current_narrator)  # پچھلے راوی کو محفوظ کریں

        # نیا راوی شامل کریں
        current_narrator = {
            "narrator_id": narrator_match.group(1),
            "full_name": narrator_match.group(2).strip(),
            "aliases": "",
            "birth_year": "",
            "death_year": "",
            "birthplace": "",
            "primary_locations": "",
            "era": "",
            "travel_history": "",
            "did_travel_for_hadith": "No",
            "memory_changes": "",
            "known_tadlis": "No",
            "Scholarly_reliability": "",
            "scholarly_evaluations": "",
            "hadith_id": "",
            "place_id": "",
            "place_name": "",
            "place_type": "",
            "travel_id": "",
            "travel_city": "",
            "year_visited": "",
            "students_and_teachers": "",
        }

    # 🔹 اضافی معلومات تلاش کریں
    if "مَاتَ" in line:
        death_year_match = death_year_pattern.search(line)
        if death_year_match:
            current_narrator["death_year"] = death_year_match.group(1)

    if "وُلِدَ" in line:
        birth_year_match = birth_year_pattern.search(line)
        if birth_year_match:
            current_narrator["birth_year"] = birth_year_match.group(1)

    place_match = place_pattern.search(line)
    if place_match:
        current_narrator["birthplace"] = place_match.group(1)

    travel_match = travel_pattern.search(line)
    if travel_match:
        current_narrator["travel_history"] = travel_match.group(2)
        current_narrator["did_travel_for_hadith"] = "Yes"

    memory_changes_match = memory_changes_pattern.search(line)
    if memory_changes_match:
        current_narrator["memory_changes"] = memory_changes_match.group(1) + " " + memory_changes_match.group(2)

    tadlis_match = tadlis_pattern.search(line)
    if tadlis_match:
        current_narrator["known_tadlis"] = "Yes"

    reliability_match = reliability_pattern.findall(line)
    if reliability_match:
        current_narrator["Scholarly_reliability"] = ", ".join(reliability_match)

    hadith_match = hadith_id_pattern.search(line)
    if hadith_match:
        current_narrator["hadith_id"] = hadith_match.group(1)

    students_match = students_pattern.search(line)
    if students_match:
        current_narrator["students_and_teachers"] = students_match.group(2)

# 🔹 آخری راوی کا اندراج
if current_narrator:
    narrators.append(current_narrator)

# 🔹 ڈیٹا کو ایکسل فائل میں محفوظ کریں
df = pd.DataFrame(narrators)
excel_path = "narrators_updated_data.xlsx"
df.to_excel(excel_path, index=False)

print(f"📂 Data successfully saved in {excel_path}")

