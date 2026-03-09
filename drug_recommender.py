# ─── drug_recommender.py ──────────────────────────────────────────────────────
# OTC Drug Recommendation System
# Recommends only common over-the-counter medications.
# Never suggests prescription drugs. Always includes a medical disclaimer.
# ──────────────────────────────────────────────────────────────────────────────

# ── Knowledge Base ────────────────────────────────────────────────────────────
drug_database = {
    "fever": [
        {"drug": "Paracetamol (Acetaminophen)", "use": "Reduces fever and relieves mild to moderate pain",
         "dosage": "500–1000 mg every 4–6 hours (max 4 g/day)", "side_effects": "Nausea, rash (rare), liver stress with overdose"},
        {"drug": "Ibuprofen", "use": "Reduces fever and inflammation",
         "dosage": "200–400 mg every 6–8 hours with food (max 1200 mg/day OTC)", "side_effects": "Stomach irritation, heartburn, dizziness"},
    ],
    "headache": [
        {"drug": "Paracetamol (Acetaminophen)", "use": "Relieves tension headaches and mild pain",
         "dosage": "500–1000 mg every 4–6 hours (max 4 g/day)", "side_effects": "Nausea, rash (rare)"},
        {"drug": "Aspirin", "use": "Relieves headache and mild inflammation",
         "dosage": "325–650 mg every 4–6 hours with water (max 4 g/day)", "side_effects": "Stomach upset, bleeding risk — avoid in children"},
        {"drug": "Ibuprofen", "use": "Reduces headache pain and inflammation",
         "dosage": "200–400 mg every 6–8 hours with food", "side_effects": "Stomach irritation, heartburn"},
    ],
    "cold": [
        {"drug": "Paracetamol (Acetaminophen)", "use": "Reduces fever and body aches associated with cold",
         "dosage": "500–1000 mg every 4–6 hours", "side_effects": "Nausea, rash (rare)"},
        {"drug": "Cetirizine", "use": "Relieves runny nose and sneezing",
         "dosage": "10 mg once daily", "side_effects": "Drowsiness, dry mouth, fatigue"},
        {"drug": "Dextromethorphan (DXM)", "use": "Suppresses cough",
         "dosage": "10–20 mg every 4 hours or 30 mg every 6–8 hours (max 120 mg/day)", "side_effects": "Dizziness, nausea, drowsiness"},
        {"drug": "Pseudoephedrine", "use": "Relieves nasal congestion",
         "dosage": "60 mg every 4–6 hours (max 240 mg/day)", "side_effects": "Insomnia, increased heart rate, dry mouth"},
    ],
    "cough": [
        {"drug": "Dextromethorphan (DXM)", "use": "Suppresses dry cough",
         "dosage": "10–20 mg every 4 hours (max 120 mg/day)", "side_effects": "Dizziness, nausea, drowsiness"},
        {"drug": "Guaifenesin", "use": "Loosens chest congestion (expectorant)",
         "dosage": "200–400 mg every 4 hours with plenty of fluids (max 2400 mg/day)", "side_effects": "Nausea, vomiting, dizziness"},
        {"drug": "Honey + Warm Water", "use": "Natural soothing agent for sore throat and cough",
         "dosage": "1–2 teaspoons in warm water as needed", "side_effects": "None (avoid in children under 1 year)"},
    ],
    "allergy": [
        {"drug": "Cetirizine", "use": "Relieves allergy symptoms — sneezing, runny nose, itchy eyes",
         "dosage": "10 mg once daily", "side_effects": "Drowsiness, dry mouth, fatigue"},
        {"drug": "Loratadine", "use": "Non-drowsy antihistamine for allergy relief",
         "dosage": "10 mg once daily", "side_effects": "Headache, dry mouth, rare drowsiness"},
        {"drug": "Fexofenadine", "use": "Non-drowsy allergy relief",
         "dosage": "120 mg once daily or 180 mg once daily", "side_effects": "Headache, nausea, dizziness"},
    ],
    "sore throat": [
        {"drug": "Benzocaine Lozenges", "use": "Numbs and soothes sore throat pain",
         "dosage": "1 lozenge every 2 hours as needed (max 8/day)", "side_effects": "Numbness in mouth, rare allergic reaction"},
        {"drug": "Paracetamol (Acetaminophen)", "use": "Reduces throat pain and fever",
         "dosage": "500–1000 mg every 4–6 hours", "side_effects": "Nausea, rash (rare)"},
        {"drug": "Ibuprofen", "use": "Reduces throat inflammation and pain",
         "dosage": "200–400 mg every 6–8 hours with food", "side_effects": "Stomach irritation"},
    ],
    "stomach pain": [
        {"drug": "Antacids (Calcium Carbonate)", "use": "Neutralises stomach acid, relieves heartburn and indigestion",
         "dosage": "500–1500 mg as needed after meals (max per label)", "side_effects": "Constipation, gas"},
        {"drug": "Omeprazole (OTC)", "use": "Reduces stomach acid for persistent heartburn",
         "dosage": "20 mg once daily before meals for up to 14 days", "side_effects": "Headache, diarrhoea, nausea"},
        {"drug": "Simethicone", "use": "Relieves gas and bloating",
         "dosage": "40–125 mg after meals and at bedtime", "side_effects": "Minimal — occasional loose stools"},
    ],
    "diarrhea": [
        {"drug": "Loperamide (Imodium)", "use": "Slows intestinal movement to reduce diarrhoea",
         "dosage": "4 mg initially, then 2 mg after each loose stool (max 8 mg/day OTC)", "side_effects": "Constipation, dizziness, dry mouth"},
        {"drug": "Oral Rehydration Salts (ORS)", "use": "Replaces fluids and electrolytes lost during diarrhoea",
         "dosage": "1 sachet dissolved in 200 ml water after each loose stool", "side_effects": "None when used correctly"},
    ],
    "nausea": [
        {"drug": "Dimenhydrinate (Dramamine)", "use": "Relieves nausea, vomiting, and motion sickness",
         "dosage": "50–100 mg every 4–6 hours (max 400 mg/day)", "side_effects": "Drowsiness, dry mouth, blurred vision"},
        {"drug": "Ginger (Supplement/Tea)", "use": "Natural remedy for nausea and upset stomach",
         "dosage": "250 mg capsule 4 times daily or ginger tea as needed", "side_effects": "Mild heartburn in high doses"},
    ],
    "acne": [
        {"drug": "Benzoyl Peroxide (2.5–5%)", "use": "Kills acne-causing bacteria on skin",
         "dosage": "Apply thin layer to affected area once or twice daily after washing", "side_effects": "Dryness, redness, peeling — reduce frequency if irritation occurs"},
        {"drug": "Salicylic Acid (0.5–2%)", "use": "Unclogs pores and reduces blackheads and whiteheads",
         "dosage": "Apply to affected area 1–3 times daily", "side_effects": "Skin irritation, dryness, peeling"},
        {"drug": "Adapalene 0.1% Gel (OTC)", "use": "Reduces acne by normalising skin cell turnover",
         "dosage": "Apply a thin layer once daily at night to clean, dry skin", "side_effects": "Dryness, redness, sun sensitivity — use SPF daily"},
    ],
    "rash": [
        {"drug": "Hydrocortisone Cream 1%", "use": "Reduces mild skin inflammation, redness and itching",
         "dosage": "Apply thin layer to affected area 2–3 times daily for up to 7 days", "side_effects": "Skin thinning with prolonged use"},
        {"drug": "Calamine Lotion", "use": "Soothes itching from rashes, insect bites, and poison ivy",
         "dosage": "Apply to affected area 3–4 times daily as needed", "side_effects": "Minimal — skin dryness"},
        {"drug": "Cetirizine", "use": "Reduces itching caused by allergic skin reactions",
         "dosage": "10 mg once daily", "side_effects": "Drowsiness, dry mouth"},
    ],
    "blisters": [
        {
            "drug": "Petroleum Jelly (Vaseline)",
            "use": "Protects blistered skin and prevents dryness while healing",
            "dosage": "Apply thin layer 2–3 times daily",
            "side_effects": "Minimal — may clog pores if overused"
        },
        {
            "drug": "Hydrocolloid Blister Bandage",
            "use": "Protects blister and promotes faster healing",
            "dosage": "Apply over clean blister until healed",
            "side_effects": "Rare skin irritation"
        }
    ],

    "fungal infection": [
        {
            "drug": "Clotrimazole Cream 1%",
            "use": "Treats fungal skin infections such as ringworm and athlete’s foot",
            "dosage": "Apply twice daily for 2–4 weeks",
            "side_effects": "Mild burning or irritation"
        },
        {
            "drug": "Miconazole Cream",
            "use": "Antifungal medication for skin infections",
            "dosage": "Apply twice daily to affected area",
            "side_effects": "Redness or irritation"
        }
    ],

    "athlete's foot": [
        {
            "drug": "Terbinafine Cream 1%",
            "use": "Treats fungal infections of the feet",
            "dosage": "Apply once daily for 1–2 weeks",
            "side_effects": "Mild itching or redness"
        }
    ],

    "sunburn": [
        {
            "drug": "Aloe Vera Gel",
            "use": "Soothes sunburned skin and reduces irritation",
            "dosage": "Apply 2–3 times daily",
            "side_effects": "Rare allergic reaction"
        },
        {
            "drug": "Hydrocortisone Cream 1%",
            "use": "Reduces inflammation and redness",
            "dosage": "Apply thin layer twice daily",
            "side_effects": "Skin thinning if overused"
        }
    ],
    "muscle pain": [
        {"drug": "Ibuprofen", "use": "Reduces muscle inflammation and pain",
         "dosage": "200–400 mg every 6–8 hours with food (max 1200 mg/day OTC)", "side_effects": "Stomach irritation, heartburn"},
        {"drug": "Diclofenac Gel (OTC)", "use": "Topical anti-inflammatory for localised muscle and joint pain",
         "dosage": "Apply 2–4 g to affected area 3–4 times daily", "side_effects": "Mild skin irritation at application site"},
        {"drug": "Naproxen Sodium", "use": "Longer-acting NSAID for muscle aches",
         "dosage": "220 mg every 8–12 hours with food (max 440 mg/day OTC)", "side_effects": "Stomach upset, dizziness, fluid retention"},
    ],
    "eye irritation": [
        {"drug": "Artificial Tears (Carboxymethylcellulose)", "use": "Lubricates dry, irritated eyes",
         "dosage": "1–2 drops in each eye as needed", "side_effects": "Mild temporary blurring"},
        {"drug": "Ketotifen Eye Drops (OTC)", "use": "Relieves itchy, red eyes from allergies",
         "dosage": "1 drop in each affected eye twice daily (every 8–12 hours)", "side_effects": "Mild stinging, headache"},
    ],
    "insomnia": [
        {"drug": "Diphenhydramine (Benadryl / ZzzQuil)", "use": "OTC sleep aid — causes sedation",
         "dosage": "25–50 mg at bedtime (max 7 days continuous use)", "side_effects": "Morning grogginess, dry mouth, urinary retention — avoid in elderly"},
        {"drug": "Melatonin", "use": "Regulates sleep-wake cycle for mild insomnia or jet lag",
         "dosage": "0.5–5 mg 30 minutes before bedtime", "side_effects": "Drowsiness, headache, dizziness"},
    ],
    "constipation": [
        {"drug": "Bisacodyl (Dulcolax)", "use": "Stimulant laxative for short-term constipation relief",
         "dosage": "5–10 mg orally at bedtime (results in 6–12 hours)", "side_effects": "Abdominal cramps, diarrhoea — do not use daily"},
        {"drug": "Psyllium Husk (Metamucil)", "use": "Fibre supplement that softens stool",
         "dosage": "1 teaspoon in 8 oz water 1–3 times daily with plenty of fluids", "side_effects": "Bloating, gas — drink plenty of water"},
        {"drug": "Polyethylene Glycol 3350 (MiraLAX)", "use": "Osmotic laxative — draws water into stool",
         "dosage": "17 g (1 capful) dissolved in 8 oz beverage once daily for up to 7 days", "side_effects": "Bloating, cramping, nausea"},
    ],
    "eczema": [
        {"drug": "Hydrocortisone Cream 1%", "use": "Reduces inflammation, redness and itching in eczema flare-ups",
         "dosage": "Apply thin layer to affected area 2-3 times daily for up to 7 days", "side_effects": "Skin thinning with prolonged use -- do not use on face long-term"},
        {"drug": "Cetirizine", "use": "Oral antihistamine to relieve itch associated with eczema",
         "dosage": "10 mg once daily", "side_effects": "Drowsiness, dry mouth, fatigue"},
        {"drug": "Emollient / Moisturiser (e.g. CeraVe, Eucerin)", "use": "Restores skin barrier, prevents dryness and flare-ups",
         "dosage": "Apply generously 2-3 times daily especially after bathing", "side_effects": "Rarely skin irritation -- patch test first"},
        {"drug": "Calamine Lotion", "use": "Soothes itching and weeping eczema patches",
         "dosage": "Apply to affected area 3-4 times daily as needed", "side_effects": "Minimal -- skin dryness"},
    ],

    "psoriasis": [
        {"drug": "Coal Tar Shampoo / Cream (OTC)", "use": "Reduces scaling, itching and inflammation in psoriasis",
         "dosage": "Apply shampoo 2-3 times per week; cream once or twice daily to plaques", "side_effects": "Skin irritation, photosensitivity, strong odour"},
        {"drug": "Salicylic Acid (2-6%)", "use": "Softens and removes psoriatic scales",
         "dosage": "Apply to plaques once or twice daily", "side_effects": "Skin irritation, dryness -- avoid broken skin"},
        {"drug": "Hydrocortisone Cream 1%", "use": "Mild steroid to reduce redness and inflammation",
         "dosage": "Apply thin layer 1-2 times daily for up to 7 days", "side_effects": "Skin thinning with prolonged use"},
        {"drug": "Emollient / Moisturiser", "use": "Keeps skin hydrated and reduces plaque severity",
         "dosage": "Apply liberally several times daily especially after bathing", "side_effects": "Minimal -- rare irritation"},
    ],

    "ringworm": [
        {"drug": "Clotrimazole Cream 1%", "use": "Antifungal -- treats ringworm (tinea corporis) skin infection",
         "dosage": "Apply twice daily for 2-4 weeks until fully cleared", "side_effects": "Mild burning, redness or irritation at site"},
        {"drug": "Terbinafine Cream 1%", "use": "Kills fungus causing ringworm -- faster acting than clotrimazole",
         "dosage": "Apply once or twice daily for 1-2 weeks", "side_effects": "Mild itching or redness"},
        {"drug": "Miconazole Cream", "use": "Antifungal for ringworm and other skin fungal infections",
         "dosage": "Apply twice daily to affected area", "side_effects": "Redness or irritation"},
    ],

    "conjunctivitis": [
        {"drug": "Ketotifen Eye Drops (OTC)", "use": "Relieves itching and redness from allergic conjunctivitis",
         "dosage": "1 drop in each affected eye twice daily (every 8-12 hours)", "side_effects": "Mild stinging, headache, dry eye"},
        {"drug": "Artificial Tears (Carboxymethylcellulose)", "use": "Lubricates and flushes irritants from the eye",
         "dosage": "1-2 drops in each eye as needed throughout the day", "side_effects": "Mild temporary blurring"},
        {"drug": "Saline Eye Wash", "use": "Gently rinses eye to remove discharge and irritants",
         "dosage": "Flush eye for 1-2 minutes as needed", "side_effects": "None when used correctly"},
    ],

    "stye": [
        {"drug": "Warm Compress", "use": "Applies heat to bring stye to a head and promote drainage",
         "dosage": "Hold warm (not hot) damp cloth against closed eyelid for 10-15 mins, 3-4 times daily", "side_effects": "None -- avoid if skin is broken"},
        {"drug": "Artificial Tears (Carboxymethylcellulose)", "use": "Soothes eye irritation and discomfort caused by stye",
         "dosage": "1-2 drops in affected eye as needed", "side_effects": "Mild temporary blurring"},
        {"drug": "Ibuprofen", "use": "Reduces pain and swelling around the stye",
         "dosage": "200-400 mg every 6-8 hours with food", "side_effects": "Stomach irritation, heartburn"},
    ],

    "mouth ulcer": [
        {"drug": "Benzocaine Gel (OTC)", "use": "Numbs the ulcer and provides fast pain relief",
         "dosage": "Apply small amount directly to ulcer up to 4 times daily", "side_effects": "Temporary numbness, rare allergic reaction"},
        {"drug": "Chlorhexidine Mouthwash (OTC)", "use": "Antiseptic rinse that prevents infection and speeds healing",
         "dosage": "Rinse with 10 ml for 1 minute twice daily after brushing", "side_effects": "Tooth staining with long-term use, altered taste"},
        {"drug": "Bonjela (Choline Salicylate Gel)", "use": "Reduces inflammation and relieves pain of mouth ulcers",
         "dosage": "Apply to ulcer every 3 hours as needed -- not for children under 16", "side_effects": "Mild burning sensation on application"},
        {"drug": "Vitamin B12 / B-complex Supplement", "use": "Recurrent mouth ulcers may be linked to B12 deficiency -- supplementation can reduce frequency",
         "dosage": "1 tablet daily as directed on label", "side_effects": "Minimal -- excess B12 is excreted in urine"},
    ],

    "alopecia": [
        {"drug": "Minoxidil 2% / 5% Solution or Foam (OTC)", "use": "Stimulates hair follicles and slows hair loss -- most evidence-backed OTC treatment",
         "dosage": "Apply 1 ml (2%) or half capful foam (5%) to dry scalp twice daily -- results in 3-6 months", "side_effects": "Scalp irritation, initial shedding (weeks 2-4), unwanted facial hair if solution spreads"},
        {"drug": "Biotin (Vitamin B7) Supplement", "use": "Supports keratin production -- often recommended for hair thinning",
         "dosage": "2.5-5 mg once daily with food", "side_effects": "Minimal -- may interfere with lab test results at high doses"},
        {"drug": "Zinc Supplement", "use": "Zinc deficiency is linked to hair loss -- supplementation may help",
         "dosage": "25-50 mg once daily with food", "side_effects": "Nausea if taken on empty stomach, metallic taste"},
        {"drug": "Ketoconazole Shampoo 1% (OTC)", "use": "Antifungal shampoo that may reduce scalp inflammation contributing to hair loss",
         "dosage": "Use 2-3 times per week, leave on scalp for 3-5 minutes before rinsing", "side_effects": "Scalp dryness or irritation"},
    ],

    "cavity": [
        {"drug": "Fluoride Toothpaste (1000-1450 ppm)", "use": "Remineralises early enamel decay and prevents cavity progression",
         "dosage": "Brush twice daily for 2 minutes -- do not rinse mouth with water immediately after", "side_effects": "Dental fluorosis if swallowed in large amounts (children)"},
        {"drug": "Clove Oil (Eugenol)", "use": "Natural analgesic -- temporarily relieves toothache from cavities",
         "dosage": "Apply 1-2 drops to a cotton ball and press against aching tooth for a few minutes", "side_effects": "Gum irritation if used undiluted frequently"},
        {"drug": "Ibuprofen", "use": "Reduces toothache pain and dental inflammation",
         "dosage": "200-400 mg every 6-8 hours with food", "side_effects": "Stomach irritation, heartburn"},
        {"drug": "Benzocaine Gel (OTC)", "use": "Topical numbing gel for temporary toothache relief",
         "dosage": "Apply small amount to affected gum/tooth area up to 4 times daily", "side_effects": "Temporary numbness, avoid swallowing"},
    ],
}

# Keyword → canonical condition mapping for flexible matching
_SYNONYM_MAP = {
    "temperature": "fever", "high temperature": "fever", "pyrexia": "fever",
    "flu": "cold", "common cold": "cold", "runny nose": "cold", "sneezing": "cold",
    "congestion": "cold", "stuffy nose": "cold",
    "coughing": "cough", "dry cough": "cough", "wet cough": "cough", "chest cough": "cough",
    "migraine": "headache", "head pain": "headache", "tension headache": "headache",
    "allergies": "allergy", "hay fever": "allergy", "allergic": "allergy", "hives": "allergy",
    "throat": "sore throat", "throat pain": "sore throat", "pharyngitis": "sore throat",
    "tummy": "stomach pain", "stomach ache": "stomach pain", "abdomen": "stomach pain",
    "heartburn": "stomach pain", "indigestion": "stomach pain", "acid reflux": "stomach pain",
    "loose stool": "diarrhea", "loose motion": "diarrhea", "diarrhoea": "diarrhea",
    "vomiting": "nausea", "vomit": "nausea", "motion sickness": "nausea",
    "pimples": "acne", "breakout": "acne", "blemishes": "acne", "blackheads": "acne",
    "skin rash": "rash", "itching": "rash", "itchy skin": "rash", "eczema": "rash",
    "body ache": "muscle pain", "muscle ache": "muscle pain", "joint pain": "muscle pain",
    "myalgia": "muscle pain", "soreness": "muscle pain",
    "red eye": "eye irritation", "dry eye": "eye irritation", "itchy eye": "eye irritation",
    "conjunctivitis": "eye irritation",
    "sleeplessness": "insomnia", "can't sleep": "insomnia", "sleep": "insomnia",
    "no sleep": "insomnia",
    "hard stool": "constipation", "no bowel": "constipation",
    "blister": "blisters",
    "skin blister": "blisters",
    "fluid filled bump": "blisters",

    "fungal": "fungal infection",
    "ringworm": "fungal infection",
    "tinea": "fungal infection",
    "athlete foot": "athlete's foot",
    "itchy circular rash": "fungal infection",
    "scaly rash": "fungal infection",
    "skin fungus": "fungal infection",

    "sun burn": "sunburn",
    "burn from sun": "sunburn",

    "dermatitis": "eczema", "atopic": "eczema", "itchy patches": "eczema",
    "dry itchy skin": "eczema", "skin inflammation": "eczema",

    "plaque": "psoriasis", "scaly skin": "psoriasis", "silver scales": "psoriasis",
    "skin plaques": "psoriasis", "thick skin patches": "psoriasis",

    "tinea corporis": "ringworm", "circular rash": "ringworm",
    "ring shaped rash": "ringworm", "worm rash": "ringworm",

    "pink eye": "conjunctivitis", "red eye discharge": "conjunctivitis",
    "eye discharge": "conjunctivitis", "sticky eye": "conjunctivitis",
    "watery eye": "conjunctivitis", "eye infection": "conjunctivitis",

    "eyelid bump": "stye", "eye bump": "stye", "eyelid swelling": "stye",
    "hordeolum": "stye", "eyelid pimple": "stye",

    "canker sore": "mouth ulcer", "oral ulcer": "mouth ulcer",
    "mouth sore": "mouth ulcer", "aphthous": "mouth ulcer",
    "ulcer in mouth": "mouth ulcer", "painful mouth": "mouth ulcer",

    "hair loss": "alopecia", "baldness": "alopecia", "thinning hair": "alopecia",
    "hair fall": "alopecia", "hair thinning": "alopecia",
    "patchy hair loss": "alopecia", "receding hairline": "alopecia",

    "tooth decay": "cavity", "tooth pain": "cavity", "toothache": "cavity",
    "dental cavity": "cavity", "tooth cavity": "cavity", "tooth ache": "cavity",
    "decayed tooth": "cavity", "tooth hole": "cavity",
}

# Severity thresholds
_SEVERE_KEYWORDS = [
    "severe", "critical", "extreme", "unbearable", "chest pain", "difficulty breathing",
    "shortness of breath", "unconscious", "unresponsive", "blood", "bleeding",
    "paralysis", "stroke", "heart attack", "seizure", "anaphylaxis",
]


# ── Core Functions ─────────────────────────────────────────────────────────────

def recommend_drugs(disease_or_symptoms: str, severity: str = "Mild") -> str:
    """
    Match input text against drug_database and return formatted HTML cards.
    Always OTC only. Always includes a disclaimer. Warns if severe.
    """
    if not disease_or_symptoms or not disease_or_symptoms.strip():
        return ""

    text_lower = disease_or_symptoms.lower().strip()

    # Severity override check
    is_severe = (
        severity == "Severe" or
        any(kw in text_lower for kw in _SEVERE_KEYWORDS)
    )

    # Find matching conditions
    matched_conditions = []
    for condition in drug_database:
        if condition in text_lower:
            if condition not in matched_conditions:
                matched_conditions.append(condition)

    for synonym, canonical in _SYNONYM_MAP.items():
        if synonym in text_lower and canonical not in matched_conditions:
            matched_conditions.append(canonical)

    if not matched_conditions:
        return _no_match_html(disease_or_symptoms, is_severe)

    return format_drug_response(matched_conditions, disease_or_symptoms, severity, is_severe)


def format_drug_response(matched_conditions: list, query: str, severity: str, is_severe: bool) -> str:
    """
    Build the full HTML output: severity warning, drug cards per condition, disclaimer.
    """
    html = ""

    # Severe warning banner
    if is_severe:
        html += """
        <div style="background:#fef2f2;border:2px solid #ef4444;border-radius:12px;padding:1rem 1.25rem;
                    margin-bottom:1.25rem;display:flex;align-items:flex-start;gap:0.75rem;">
            <span style="font-size:1.4rem;line-height:1;">⚠️</span>
            <div>
                <div style="color:#b91c1c;font-weight:800;font-size:0.95rem;margin-bottom:0.2rem;">
                    Symptoms appear serious — Please consult a doctor immediately
                </div>
                <div style="color:#dc2626;font-size:0.84rem;line-height:1.6;">
                    The severity of your symptoms may require professional evaluation.
                    OTC medications listed below are for informational reference only and are not a substitute for emergency care.
                </div>
            </div>
        </div>"""

    # Matched query summary
    conditions_text = ", ".join(c.title() for c in matched_conditions)
    html += f"""
    <div style="background:var(--accent-light);border:1px solid var(--border);border-radius:10px;
                padding:0.9rem 1.2rem;margin-bottom:1.25rem;display:flex;align-items:center;gap:0.75rem;">
        <span style="font-size:1.2rem;">🔍</span>
        <div>
            <span style="color:var(--text-muted);font-size:0.72rem;font-weight:700;text-transform:uppercase;
                          letter-spacing:0.08em;">Matched Condition(s)</span>
            <div style="color:var(--text-primary);font-weight:700;font-size:0.95rem;">{conditions_text}</div>
            <div style="color:var(--text-muted);font-size:0.78rem;">Severity: <strong>{severity}</strong></div>
        </div>
    </div>"""

    # Drug cards per matched condition
    for condition in matched_conditions:
        drugs = drug_database.get(condition, [])
        if not drugs:
            continue

        html += f"""
        <div style="margin-bottom:1.5rem;">
            <div style="font-size:0.78rem;font-weight:700;text-transform:uppercase;letter-spacing:0.09em;
                        color:var(--text-muted);padding-bottom:0.6rem;border-bottom:1px solid var(--border);
                        margin-bottom:1rem;display:flex;align-items:center;gap:0.5rem;">
                <span style="display:inline-flex;align-items:center;justify-content:center;
                              width:22px;height:22px;background:var(--accent-light);border-radius:5px;
                              font-size:0.75rem;">💊</span>
                Recommended OTC Medicines — {condition.title()}
            </div>
            <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:0.875rem;">"""

        for drug in drugs:
            html += f"""
                <div style="background:var(--bg-surface);border:1px solid var(--border);border-radius:11px;
                            padding:1.1rem 1.25rem;box-shadow:var(--card-shadow);
                            transition:box-shadow 0.18s ease;border-top:3px solid var(--accent);">
                    <div style="display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:0.65rem;">
                        <div style="font-size:0.95rem;font-weight:800;color:var(--text-primary);line-height:1.3;">
                            {drug['drug']}
                        </div>
                    </div>
                    <div style="margin-bottom:0.5rem;">
                        <span style="font-size:0.67rem;font-weight:700;text-transform:uppercase;letter-spacing:0.07em;
                                     color:var(--accent);">Purpose</span>
                        <div style="color:var(--text-secondary);font-size:0.84rem;margin-top:0.15rem;line-height:1.5;">
                            {drug['use']}
                        </div>
                    </div>
                    <div style="margin-bottom:0.5rem;">
                        <span style="font-size:0.67rem;font-weight:700;text-transform:uppercase;letter-spacing:0.07em;
                                     color:#059669;">Dosage</span>
                        <div style="color:var(--text-secondary);font-size:0.84rem;margin-top:0.15rem;line-height:1.5;
                                    background:#f0fdf4;border-radius:6px;padding:0.4rem 0.6rem;
                                    border-left:3px solid #34d399;">
                            {drug['dosage']}
                        </div>
                    </div>
                    <div>
                        <span style="font-size:0.67rem;font-weight:700;text-transform:uppercase;letter-spacing:0.07em;
                                     color:#d97706;">Side Effects</span>
                        <div style="color:var(--text-secondary);font-size:0.84rem;margin-top:0.15rem;line-height:1.5;
                                    background:#fffbeb;border-radius:6px;padding:0.4rem 0.6rem;
                                    border-left:3px solid #fbbf24;">
                            {drug['side_effects']}
                        </div>
                    </div>
                </div>"""

        html += "</div></div>"  # close grid + condition section

    # Medical disclaimer
    html += """
    <div style="background:#f8fafc;border:1.5px solid #e2e8f0;border-radius:10px;
                padding:1rem 1.25rem;margin-top:0.5rem;display:flex;align-items:flex-start;gap:0.75rem;">
        <span style="font-size:1.2rem;line-height:1.4;">⚕️</span>
        <div>
            <div style="color:var(--text-primary);font-weight:700;font-size:0.84rem;margin-bottom:0.3rem;">
                Medical Disclaimer
            </div>
            <div style="color:var(--text-muted);font-size:0.8rem;line-height:1.7;">
                These recommendations are generated by an AI system based on a general knowledge base
                and are intended for <strong>informational purposes only</strong>.
                They are <strong>not a substitute</strong> for professional medical advice, diagnosis, or treatment.
                Always read the full product label and consult a qualified healthcare professional before
                taking any medication, especially if you are pregnant, breastfeeding, have existing health
                conditions, or are taking other medicines.
            </div>
        </div>
    </div>"""

    return html


def _no_match_html(query: str, is_severe: bool) -> str:
    warning = ""
    if is_severe:
        warning = """
        <div style="background:#fef2f2;border:2px solid #ef4444;border-radius:12px;padding:1rem 1.25rem;
                    margin-bottom:1rem;display:flex;gap:0.75rem;">
            <span style="font-size:1.3rem;">⚠️</span>
            <div style="color:#b91c1c;font-weight:700;font-size:0.9rem;">
                Symptoms appear serious — Please consult a doctor immediately.
            </div>
        </div>"""

    return f"""{warning}
    <div style="background:var(--bg-surface);border:1px solid var(--border);border-radius:12px;
                padding:2.5rem 2rem;text-align:center;">
        <div style="font-size:2rem;margin-bottom:0.75rem;">🔍</div>
        <div style="color:var(--text-primary);font-weight:700;font-size:1rem;margin-bottom:0.5rem;">
            No direct match found for "{query}"
        </div>
        <div style="color:var(--text-muted);font-size:0.855rem;line-height:1.7;max-width:420px;margin:0 auto;">
            Try entering a more specific condition such as:
            <em>fever, cold, cough, allergy, headache, acne, rash, stomach pain, muscle pain,
            nausea, diarrhea, sore throat, eye irritation, insomnia, constipation</em>.
        </div>
    </div>
    <div style="background:#f8fafc;border:1.5px solid #e2e8f0;border-radius:10px;
                padding:1rem 1.25rem;margin-top:1rem;display:flex;gap:0.75rem;">
        <span style="font-size:1.1rem;">⚕️</span>
        <div style="color:var(--text-muted);font-size:0.8rem;line-height:1.7;">
            <strong>Disclaimer:</strong> Always consult a qualified healthcare professional for a proper diagnosis and treatment plan.
        </div>
    </div>"""

def get_drug_list(condition):
    """
    Extract structured drug list from free-text condition/symptom input.
    Uses the same fuzzy + synonym matching as recommend_drugs() so that
    inputs like 'i have headache' or a full diagnosis string all work correctly.
    Returns a flat list of dicts with name/dosage/purpose/side_effects.
    """
    if not condition or not condition.strip():
        return []

    text_lower = condition.lower().strip()

    # Step 1: direct condition-name matches
    matched_conditions = []
    for cond in drug_database:
        if cond in text_lower and cond not in matched_conditions:
            matched_conditions.append(cond)

    # Step 2: synonym / keyword matches
    for synonym, canonical in _SYNONYM_MAP.items():
        if synonym in text_lower and canonical not in matched_conditions:
            matched_conditions.append(canonical)

    # Step 3: collect drugs from every matched condition
    drugs = []
    seen = set()
    for cond in matched_conditions:
        for d in drug_database.get(cond, []):
            key = d["drug"]
            if key not in seen:          # deduplicate across conditions
                seen.add(key)
                drugs.append({
                    "name":         d["drug"],
                    "dosage":       d["dosage"],
                    "purpose":      d["use"],
                    "side_effects": d["side_effects"]
                })

    return drugs