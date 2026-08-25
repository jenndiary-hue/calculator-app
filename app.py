import streamlit as st
from fpdf import FPDF
from datetime import date
import os

# --- 1. ΕΙΣΑΓΩΓΗ STYLING ΑΠΟ FIGMA (CSS) ---
st.markdown("""
    <style>
    .stApp { background-color: #FAFAFA; }
    h1, h2, h3 { color: #2A3B4C !important; font-family: 'arial', sans-serif; }
    .stButton>button {
        background-color: #E76F51; color: white; border-radius: 8px;        
        padding: 10px 24px; font-weight: bold; border: none; width: 100%;
    }
    .stButton>button:hover { background-color: #D65A3D; color: white; }
    [data-testid="stMetricValue"] { color: #E76F51; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ΣΥΝΑΡΤΗΣΕΙΣ ΥΠΟΛΟΓΙΣΜΩΝ ---
def calculate_bmi(weight_kg, height_cm):
    height_m = height_cm / 100
    bmi = weight_kg / (height_m ** 2)
    if bmi < 18.5: return bmi, "Ελλιποβαρής"
    elif 18.5 <= bmi < 24.9: return bmi, "Φυσιολογικό"
    elif 25 <= bmi < 29.9: return bmi, "Υπέρβαρος/η"
    else: return bmi, "Παχύσαρκος/η"

def calculate_bmr(weight_kg, height_cm, age, gender, formula):
    is_male = (gender == "Άνδρας")
    if formula == "Mifflin-St Jeor":
        return (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + (5 if is_male else -161)
    else:
        if is_male: return 88.362 + (13.397 * weight_kg) + (4.799 * height_cm) - (5.677 * age)
        else: return 447.593 + (9.247 * weight_kg) + (3.098 * height_cm) - (4.330 * age)

def calculate_ibw(height_cm, gender):
    inches_over_5_ft = (height_cm / 2.54) - 60
    if inches_over_5_ft < 0: inches_over_5_ft = 0
    if gender == "Άνδρας": return 50.0 + (2.3 * inches_over_5_ft)
    else: return 45.5 + (2.3 * inches_over_5_ft)

def calculate_healthy_weight_range(height_cm, age):
    height_m = height_cm / 100
    min_bmi = 18.5
    max_bmi = 24.9
    if age > 50:
        min_bmi = 20.0
        max_bmi = 27.0
    elif age > 35:
        min_bmi = 19.0
        max_bmi = 25.5
    return min_bmi * (height_m ** 2), max_bmi * (height_m ** 2)

# --- ΣΥΝΑΡΤΗΣΗ ΔΗΜΙΟΥΡΓΙΑΣ PDF ---
def create_pdf(weight, height, age, gender, pal_desc, bmi, bmi_cat, ibw, min_hw, max_hw, bmr, tdee, goal, target_cals, water, prot, fat, carb):
    pdf = FPDF()
    pdf.add_page()
    
    # Διαβάζει το αρχείο arial.ttf με νέο όνομα 'GreekFont' για να μην μπερδεύεται
    pdf.add_font('GreekFont', '', 'arial.ttf')
    pdf.set_font('GreekFont', '', 16)
        
    pdf.cell(0, 10, "Αναφορά Διατροφικών Αναγκών", ln=True, align="C")
    pdf.set_font('GreekFont', '', 11)
    pdf.cell(0, 10, f"Ημερομηνία: {date.today().strftime('%d/%m/%Y')}", ln=True, align="R")
    pdf.line(10, 25, 200, 25)
    pdf.ln(10)
    
    pdf.set_font('GreekFont', '', 14)
    pdf.cell(0, 10, "1. Προφίλ & Σωματομετρικά", ln=True)
    pdf.set_font('GreekFont', '', 12)
    pdf.cell(0, 8, f"Φύλο: {gender}  |  Ηλικία: {age} ετών  |  Ύψος: {height} cm  |  Βάρος: {weight} kg", ln=True)
    pdf.cell(0, 8, f"Φυσική Δραστηριότητα: {pal_desc}", ln=True)
    pdf.ln(5)
    
    pdf.set_font('GreekFont', '', 14)
    pdf.cell(0, 10, "2. Βασικοί Δείκτες & Ενέργεια", ln=True)
    pdf.set_font('GreekFont', '', 12)
    pdf.cell(0, 8, f"Δείκτης Μάζας Σώματος (BMI): {bmi:.1f} ({bmi_cat})", ln=True)
    pdf.cell(0, 8, f"Ιδανικό Βάρος (Devine): {ibw:.1f} kg", ln=True)
    pdf.cell(0, 8, f"Εύρος Υγιούς Βάρους: Από {min_hw:.1f} kg έως {max_hw:.1f} kg", ln=True)
    pdf.cell(0, 8, f"Βασικός Μεταβολισμός (BMR): {bmr:.0f} kcal", ln=True)
    pdf.cell(0, 8, f"Συνολική Δαπάνη Συντήρησης (TDEE): {tdee:.0f} kcal", ln=True)
    pdf.ln(5)
    
    pdf.set_font('GreekFont', '', 14)
    pdf.cell(0, 10, "3. Διατροφικός Στόχος", ln=True)
    pdf.set_font('GreekFont', '', 12)
    pdf.cell(0, 8, f"Στόχος: {goal}", ln=True)
    pdf.cell(0, 8, f"Προτεινόμενη Πρόσληψη Ενέργειας: {target_cals:.0f} kcal / ημέρα", ln=True)
    pdf.cell(0, 8, f"Στόχος Υδάτωσης: {water:.1f} Λίτρα / ημέρα", ln=True)
    pdf.ln(5)
    
    pdf.set_font('GreekFont', '', 14)
    pdf.cell(0, 10, "4. Κατανομή Μακροθρεπτικών", ln=True)
    pdf.set_font('GreekFont', '', 12)
    pdf.cell(0, 8, f"Πρωτεΐνη: {prot:.0f} g", ln=True)
    pdf.cell(0, 8, f"Λιπαρά: {fat:.0f} g", ln=True)
    pdf.cell(0, 8, f"Υδατάνθρακες: {carb:.0f} g", ln=True)
    
    return bytes(pdf.output())

# --- 3. ΠΕΡΙΒΑΛΛΟΝ ΧΡΗΣΤΗ (UI) ---
st.title("🥑 Υπολογιστής Διατροφικών Αναγκών")

col1, col2 = st.columns(2)

with col1:
    weight = st.number_input("Τωρινό Βάρος (kg)", min_value=30.0, max_value=300.0, value=70.0, step=0.5)
    age = st.number_input("Ηλικία (έτη)", min_value=10, max_value=120, value=30, step=1)
    gender = st.selectbox("Φύλο", ["Γυναίκα", "Άνδρας"])

with col2:
    height = st.number_input("Ύψος (cm)", min_value=100.0, max_value=250.0, value=170.0, step=1.0)
    formula = st.selectbox("Εξίσωση", ["Harris-Benedict", "Mifflin-St Jeor"])

st.divider()

pal = st.slider("Επίπεδο Φυσικής Δραστηριότητας (PAL)", min_value=1.2, max_value=2.4, value=1.55, step=0.05)
if pal < 1.35: pal_desc = "Καθιστική ζωή (ελάχιστη άσκηση)"
elif pal < 1.55: pal_desc = "Ελαφρά δραστήριος (ελαφριά άσκηση)"
elif pal < 1.70: pal_desc = "Μέτρια δραστήριος (μέτρια άσκηση)"
elif pal < 1.90: pal_desc = "Πολύ δραστήριος (σκληρή άσκηση)"
else: pal_desc = "Υπερβολικά δραστήριος"

st.divider()

col_goal, col_macros = st.columns(2)

with col_goal:
    st.subheader("Στόχος")
    goal = st.radio("Επιλογή Στόχου", ["Συντήρηση", "Απώλεια", "Αύξηση"], horizontal=True)
    kg_per_week = 0.0 if goal == "Συντήρηση" else st.slider("Ρυθμός (Κιλά ανά εβδομάδα)", 0.1, 1.5, 0.5, 0.1)

with col_macros:
    st.subheader("Μακροθρεπτικά")
    protein_per_kg = st.slider("Πρωτεΐνη (g ανά κιλό βάρους)", 0.8, 3.0, 1.5, 0.1)
    fat_percent = st.slider("Ποσοστό Λίπους (%)", 15, 50, 30, 1)

st.divider()

# --- 4. ΑΠΟΤΕΛΕΣΜΑΤΑ & ΕΞΑΓΩΓΗ ---
if st.button("Υπολογισμός ➔", key="calc_btn"):
    bmi, bmi_cat = calculate_bmi(weight, height)
    bmr = calculate_bmr(weight, height, age, gender, formula)
    ibw = calculate_ibw(height, gender)
    min_hw, max_hw = calculate_healthy_weight_range(height, age)
    tdee = bmr * pal
    water_liters = weight * 0.035 
    daily_shift = (7700 * kg_per_week) / 7
    
    res_col1, res_col2, res_col3, res_col4 = st.columns(4)
    res_col1.metric("BMI", f"{bmi:.1f}", bmi_cat)
    res_col2.metric("Ιδανικό Βάρος", f"{ibw:.1f} kg")
    res_col3.metric("BMR", f"{bmr:.0f} kcal")
    res_col4.metric("TDEE", f"{tdee:.0f} kcal")
    
    st.info(f"⚖️ **Εύρος Υγιούς Βάρους:** Από **{min_hw:.1f} kg** έως **{max_hw:.1f} kg** (βάσει ύψους και ηλικίας).")
    st.divider()
    
    target_cals = tdee - daily_shift if goal == "Απώλεια" else (tdee + daily_shift if goal == "Αύξηση" else tdee)
    st.success(f"## 🍽️ Θερμίδες: {target_cals:.0f} kcal/ημέρα  |  💧 Νερό: {water_liters:.1f} L/ημέρα")
    st.divider()
    
    protein_grams = weight * protein_per_kg
    fat_grams = (target_cals * (fat_percent / 100)) / 9
    carb_grams = (target_cals - (protein_grams * 4) - (fat_grams * 9)) / 4

    mac_col1, mac_col2, mac_col3 = st.columns(3)
    mac_col1.metric("🥩 Πρωτεΐνη", f"{protein_grams:.0f} g")
    mac_col2.metric("🥑 Λιπαρά", f"{fat_grams:.0f} g")
    mac_col3.metric("🍞 Υδατάνθρακες", f"{carb_grams:.0f} g")
    st.divider()
    
    # Έξυπνος έλεγχος αρχείου!
    if not os.path.exists('arial.ttf'):
        st.error("⚠️ Σφάλμα: Δεν βρέθηκε το αρχείο 'arial.ttf' στο GitHub. Παρακαλώ ανέβασέ το (με μικρά γράμματα) για να λειτουργήσει το PDF!")
    else:
        goal_text = f"{goal} ({kg_per_week}kg/εβδ)" if goal != "Συντήρηση" else "Συντήρηση"
        pdf_data = create_pdf(weight, height, age, gender, pal_desc, bmi, bmi_cat, ibw, min_hw, max_hw, bmr, tdee, goal_text, target_cals, water_liters, protein_grams, fat_grams, carb_grams)
        st.download_button(label="📥 Λήψη Αποτελεσμάτων σε PDF", data=pdf_data, file_name="diet_plan_summary.pdf", mime="application/pdf")
