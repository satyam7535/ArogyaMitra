with open('graph/llm.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace the three recommended_next_steps lines
old_hi = 'recommended_next_steps=f"[प्रारूप - केवल निर्णय समर्थन, कोई दवा खुराक नहीं] {guide_txt}",'
new_hi = 'recommended_next_steps=f"[प्रारूप - केवल निर्णय समर्थन, कोई दवा खुराक नहीं] {guide_txt} सावधानियां: {precautions_str}।",'

old_mr = 'recommended_next_steps=f"[प्रारूप - केवळ निर्णय समर्थन, औषधांचे डोस नाहीत] {guide_txt}",'
new_mr = 'recommended_next_steps=f"[प्रारूप - केवळ निर्णय समर्थन, औषधांचे डोस नाहीत] {guide_txt} काळजी: {precautions_str}।",'

old_en = 'recommended_next_steps=f"[DRAFT - Decision Support Only, not clinically reviewed, no drug dosages] {guide_txt}",'
new_en = 'recommended_next_steps=f"[DRAFT - Decision Support Only, not clinically reviewed, no drug dosages] {guide_txt} Precautions: {precautions_str}.",'

text = text.replace(old_hi, new_hi).replace(old_mr, new_mr).replace(old_en, new_en)

with open('graph/llm.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("Updated recommended_next_steps to include precautions_str")
