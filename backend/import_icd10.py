import os
import sqlite3
import csv
from datetime import datetime
import uuid

def setup():
    db_path = os.path.join(os.getcwd(), 'mediclaim.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("Running migrations...")
    try:
        cursor.execute("ALTER TABLE icd_codes ADD COLUMN chapter VARCHAR(200)")
        cursor.execute("ALTER TABLE icd_codes ADD COLUMN created_at DATETIME")
    except sqlite3.OperationalError as e:
        print("Column alter error (might exist):", e)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS claim_icd_recommendations (
        id VARCHAR PRIMARY KEY,
        claim_id VARCHAR NOT NULL,
        diagnosis_text TEXT NOT NULL,
        icd_code VARCHAR(20) NOT NULL,
        confidence FLOAT DEFAULT 0.0,
        source VARCHAR(100) DEFAULT 'FTS5_SEARCH',
        status VARCHAR(50) DEFAULT 'SUGGESTED',
        created_at DATETIME,
        updated_at DATETIME
    )
    """)

    # FTS5 virtual table
    cursor.execute("DROP TABLE IF EXISTS icd_search_fts")
    cursor.execute("""
    CREATE VIRTUAL TABLE icd_search_fts USING fts5(
        code,
        description,
        content='icd_codes',
        content_rowid='rowid'
    )
    """)

    print("Populating dataset...")
    
    # Let's drop existing codes to make it clean
    cursor.execute("DELETE FROM icd_codes")

    mock_icd_codes = [
        ("A15.0", "Tuberculosis of lung, confirmed by sputum microscopy with or without culture", "Infections"),
        ("A37.0", "Whooping cough due to Bordetella pertussis", "Infections"),
        ("B01.9", "Varicella without complication", "Infections"),
        ("B20", "Human immunodeficiency virus [HIV] disease", "Infections"),
        ("C34.90", "Malignant neoplasm of unspecified part of unspecified bronchus or lung", "Neoplasms"),
        ("C50.919", "Malignant neoplasm of unspecified site of unspecified female breast", "Neoplasms"),
        ("C61", "Malignant neoplasm of prostate", "Neoplasms"),
        ("D64.9", "Anemia, unspecified", "Blood"),
        ("E11.9", "Type 2 diabetes mellitus without complications", "Endocrine"),
        ("E03.9", "Hypothyroidism, unspecified", "Endocrine"),
        ("F32.9", "Major depressive disorder, single episode, unspecified", "Mental"),
        ("F41.1", "Generalized anxiety disorder", "Mental"),
        ("G30.9", "Alzheimer's disease, unspecified", "Nervous"),
        ("G43.909", "Migraine, unspecified, not intractable, without status migrainosus", "Nervous"),
        ("H25.9", "Unspecified age-related cataract", "Eye"),
        ("I10", "Essential (primary) hypertension", "Circulatory"),
        ("I21.9", "Acute myocardial infarction, unspecified", "Circulatory"),
        ("I25.10", "Atherosclerotic heart disease of native coronary artery without angina pectoris", "Circulatory"),
        ("I48.91", "Unspecified atrial fibrillation", "Circulatory"),
        ("I50.9", "Heart failure, unspecified", "Circulatory"),
        ("I63.9", "Cerebral infarction, unspecified", "Circulatory"),
        ("J06.9", "Acute upper respiratory infection, unspecified", "Respiratory"),
        ("J18.9", "Pneumonia, unspecified organism", "Respiratory"),
        ("J44.9", "Chronic obstructive pulmonary disease, unspecified", "Respiratory"),
        ("J45.909", "Unspecified asthma, uncomplicated", "Respiratory"),
        ("K21.9", "Gastro-esophageal reflux disease without esophagitis", "Digestive"),
        ("K35.80", "Unspecified acute appendicitis", "Digestive"),
        ("K80.20", "Calculus of gallbladder without cholecystitis without obstruction", "Digestive"),
        ("L03.90", "Cellulitis, unspecified", "Skin"),
        ("M19.90", "Unspecified osteoarthritis, unspecified site", "Musculoskeletal"),
        ("M54.5", "Low back pain", "Musculoskeletal"),
        ("M79.609", "Pain in unspecified limb", "Musculoskeletal"),
        ("M87.051", "Idiopathic aseptic necrosis of right femur", "Musculoskeletal"),
        ("M87.052", "Idiopathic aseptic necrosis of left femur", "Musculoskeletal"),
        ("M87.059", "Idiopathic aseptic necrosis of unspecified femur", "Musculoskeletal"),
        ("M87.9", "Osteonecrosis, unspecified", "Musculoskeletal"),
        ("N18.9", "Chronic kidney disease, unspecified", "Genitourinary"),
        ("N39.0", "Urinary tract infection, site not specified", "Genitourinary"),
        ("O80", "Encounter for full-term uncomplicated delivery", "Pregnancy"),
        ("R07.9", "Chest pain, unspecified", "Symptoms"),
        ("R50.9", "Fever, unspecified", "Symptoms"),
        ("R51.9", "Headache, unspecified", "Symptoms"),
        ("S02.0XXA", "Fracture of vault of skull, initial encounter for closed fracture", "Injuries"),
        ("S82.009A", "Unspecified fracture of unspecified patella, initial encounter for closed fracture", "Injuries"),
        ("T07", "Unspecified multiple injuries", "Injuries"),
        ("Z00.00", "Encounter for general adult medical examination without abnormal findings", "Factors"),
        ("Z01.89", "Encounter for other specified special examinations", "Factors")
    ]

    for code, desc, chapter in mock_icd_codes:
        uid = str(uuid.uuid4())
        cursor.execute("INSERT INTO icd_codes (id, code, description, chapter, is_active, created_at) VALUES (?, ?, ?, ?, ?, ?)", 
                       (uid, code, desc, chapter, True, datetime.utcnow()))
        cursor.execute("INSERT INTO icd_search_fts (rowid, code, description) VALUES (?, ?, ?)", (cursor.lastrowid, code, desc))

    conn.commit()
    print(f"Imported {len(mock_icd_codes)} ICD-10 codes into DB and FTS5 index.")

if __name__ == "__main__":
    setup()
