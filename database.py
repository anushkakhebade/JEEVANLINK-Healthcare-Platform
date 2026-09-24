import sqlite3
from pathlib import Path

# Database file will be created inside JeevanLink folder
DB_PATH = Path(__file__).parent / "jeevanlink.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    conn = get_connection()
    cursor = conn.cursor()

    # =========================
    # USERS
    # =========================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            login_id TEXT UNIQUE NOT NULL,
            role TEXT NOT NULL,
            name TEXT NOT NULL,
            facility TEXT
        )
    """)

    # =========================
    # PATIENTS
    # =========================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            mobile TEXT UNIQUE,
            abha_id TEXT,
            age INTEGER,
            village TEXT,
            symptoms TEXT,
            asha TEXT
        )
    """)

    # =========================
    # REFERRALS
    # =========================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS referrals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            patient_name TEXT NOT NULL,
            from_facility TEXT,
            to_facility TEXT,
            reason TEXT,
            status TEXT DEFAULT 'Pending',
            created_by TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES patients(id)
        )
    """)

    # =========================
    # APPOINTMENTS
    # =========================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            patient_name TEXT NOT NULL,
            mobile TEXT,
            facility TEXT,
            appointment_date TEXT,
            appointment_time TEXT,
            status TEXT DEFAULT 'Booked',
            source TEXT DEFAULT 'Web',
            FOREIGN KEY (patient_id) REFERENCES patients(id)
        )
    """)

    # =========================
    # DOCTORS
    # =========================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS doctors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            department TEXT,
            facility TEXT,
            timing TEXT,
            status TEXT DEFAULT 'On Duty'
        )
    """)

    # =========================
    # MEDICINES
    # =========================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS medicines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            facility TEXT,
            quantity INTEGER DEFAULT 0,
            unit TEXT,
            low_stock_limit INTEGER DEFAULT 30
        )
    """)

    # =========================
    # FOLLOWUPS
    # =========================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS followups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            patient_name TEXT NOT NULL,
            reason TEXT,
            status TEXT DEFAULT 'Follow-up Required',
            asha TEXT,
            FOREIGN KEY (patient_id) REFERENCES patients(id)
        )
    """)

    # =========================
    # FEEDBACK
    # =========================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            patient_name TEXT,
            facility TEXT,
            rating INTEGER,
            feedback TEXT,
            outcome TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES patients(id)
        )
    """)

    conn.commit()
    conn.close()


# =========================
# PATIENT FUNCTIONS
# =========================

def get_all_patients():
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM patients ORDER BY id"
    ).fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_patient_by_id(patient_id):
    conn = get_connection()

    row = conn.execute(
        "SELECT * FROM patients WHERE id = ?",
        (patient_id,)
    ).fetchone()

    conn.close()

    return dict(row) if row else None


def get_patient_by_mobile(mobile):
    conn = get_connection()

    row = conn.execute(
        "SELECT * FROM patients WHERE mobile = ?",
        (mobile,)
    ).fetchone()

    conn.close()

    return dict(row) if row else None


def create_patient(name, mobile, age, village, symptoms, asha, abha_id=None):

    conn = get_connection()

    existing = conn.execute(
        "SELECT * FROM patients WHERE mobile = ?",
        (mobile,)
    ).fetchone()

    if existing:
        conn.close()
        return dict(existing)

    cursor = conn.execute("""
        INSERT INTO patients
        (name, mobile, age, village, symptoms, asha, abha_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        name,
        mobile,
        age,
        village,
        symptoms,
        asha,
        abha_id
    ))

    patient_id = cursor.lastrowid

    conn.commit()

    row = conn.execute(
        "SELECT * FROM patients WHERE id = ?",
        (patient_id,)
    ).fetchone()

    conn.close()

    return dict(row)


# =========================
# REFERRAL FUNCTIONS
# =========================

def get_all_referrals():
    conn = get_connection()

    rows = conn.execute(
        "SELECT * FROM referrals ORDER BY id"
    ).fetchall()

    conn.close()

    return [dict(row) for row in rows]


def create_referral(
    patient_id,
    patient_name,
    from_facility,
    to_facility,
    reason,
    created_by
):

    conn = get_connection()

    cursor = conn.execute("""
        INSERT INTO referrals
        (
            patient_id,
            patient_name,
            from_facility,
            to_facility,
            reason,
            status,
            created_by
        )
        VALUES (?, ?, ?, ?, ?, 'Pending', ?)
    """, (
        patient_id,
        patient_name,
        from_facility,
        to_facility,
        reason,
        created_by
    ))

    referral_id = cursor.lastrowid

    conn.commit()

    row = conn.execute(
        "SELECT * FROM referrals WHERE id = ?",
        (referral_id,)
    ).fetchone()

    conn.close()

    return dict(row)


def update_referral_status(referral_id, status):
    conn = get_connection()

    conn.execute("""
        UPDATE referrals
        SET status = ?
        WHERE id = ?
    """, (
        status,
        referral_id
    ))

    conn.commit()

    row = conn.execute(
        "SELECT * FROM referrals WHERE id = ?",
        (referral_id,)
    ).fetchone()

    conn.close()

    return dict(row) if row else None


# =========================
# APPOINTMENT FUNCTIONS
# =========================

def create_appointment(
    patient_id,
    patient_name,
    mobile,
    facility,
    appointment_date,
    appointment_time,
    source="Web"
):

    conn = get_connection()

    cursor = conn.execute("""
        INSERT INTO appointments
        (
            patient_id,
            patient_name,
            mobile,
            facility,
            appointment_date,
            appointment_time,
            status,
            source
        )
        VALUES (?, ?, ?, ?, ?, ?, 'Booked', ?)
    """, (
        patient_id,
        patient_name,
        mobile,
        facility,
        appointment_date,
        appointment_time,
        source
    ))

    appointment_id = cursor.lastrowid

    conn.commit()

    row = conn.execute(
        "SELECT * FROM appointments WHERE id = ?",
        (appointment_id,)
    ).fetchone()

    conn.close()

    return dict(row)


def get_patient_appointments(patient_id):
    conn = get_connection()

    rows = conn.execute("""
        SELECT *
        FROM appointments
        WHERE patient_id = ?
        ORDER BY id DESC
    """, (
        patient_id,
    )).fetchall()

    conn.close()

    return [dict(row) for row in rows]


# =========================
# DOCTOR FUNCTIONS
# =========================

def get_doctors(facility=None):

    conn = get_connection()

    if facility:
        rows = conn.execute("""
            SELECT *
            FROM doctors
            WHERE facility = ?
            ORDER BY id
        """, (facility,)).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM doctors ORDER BY id"
        ).fetchall()

    conn.close()

    return [dict(row) for row in rows]


def update_doctor_status(doctor_id, status):

    conn = get_connection()

    conn.execute("""
        UPDATE doctors
        SET status = ?
        WHERE id = ?
    """, (
        status,
        doctor_id
    ))

    conn.commit()
    conn.close()


# =========================
# MEDICINE FUNCTIONS
# =========================

def get_medicines(facility=None):

    conn = get_connection()

    if facility:
        rows = conn.execute("""
            SELECT *
            FROM medicines
            WHERE facility = ?
            ORDER BY id
        """, (facility,)).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM medicines ORDER BY id"
        ).fetchall()

    conn.close()

    return [dict(row) for row in rows]


def update_medicine(medicine_id, action, amount):

    conn = get_connection()

    medicine = conn.execute("""
        SELECT *
        FROM medicines
        WHERE id = ?
    """, (medicine_id,)).fetchone()

    if not medicine:
        conn.close()
        return None

    current_quantity = medicine["quantity"]

    if action == "add":
        new_quantity = current_quantity + amount

    elif action == "dispense":
        if amount > current_quantity:
            conn.close()
            return None

        new_quantity = current_quantity - amount

    else:
        conn.close()
        return None

    conn.execute("""
        UPDATE medicines
        SET quantity = ?
        WHERE id = ?
    """, (
        new_quantity,
        medicine_id
    ))

    conn.commit()

    row = conn.execute("""
        SELECT *
        FROM medicines
        WHERE id = ?
    """, (medicine_id,)).fetchone()

    conn.close()

    return dict(row)


# =========================
# FOLLOW-UP FUNCTIONS
# =========================

def get_followups(asha=None):

    conn = get_connection()

    if asha:
        rows = conn.execute("""
            SELECT *
            FROM followups
            WHERE asha = ?
            ORDER BY id DESC
        """, (asha,)).fetchall()

    else:
        rows = conn.execute("""
            SELECT *
            FROM followups
            ORDER BY id DESC
        """).fetchall()

    conn.close()

    return [dict(row) for row in rows]


def complete_followup(followup_id):

    conn = get_connection()

    conn.execute("""
        UPDATE followups
        SET status = 'Completed'
        WHERE id = ?
    """, (
        followup_id,
    ))

    conn.commit()
    conn.close()


# =========================
# DATABASE SEEDING
# =========================

def seed_demo_data():

    conn = get_connection()

    # USERS
    users = [
        (
            "9876543210",
            "patient",
            "Demo Patient",
            "Village A"
        ),
        (
            "ASHA001",
            "asha",
            "Demo ASHA Worker",
            "Village A Sub-Centre"
        ),
        (
            "PHC001",
            "phc",
            "Demo PHC Staff",
            "Village A Primary Health Centre"
        ),
        (
            "RH001",
            "rural_hospital",
            "Demo Rural Hospital Staff",
            "Taluka Rural Hospital"
        ),
        (
            "DHO001",
            "dho",
            "Demo DHO",
            "District Health Office"
        )
    ]

    for user in users:
        conn.execute("""
            INSERT OR IGNORE INTO users
            (login_id, role, name, facility)
            VALUES (?, ?, ?, ?)
        """, user)

    # PATIENT
    existing_patient = conn.execute(
        "SELECT id FROM patients WHERE mobile = ?",
        ("9876543210",)
    ).fetchone()

    if not existing_patient:

        cursor = conn.execute("""
            INSERT INTO patients
            (name, mobile, age, village, symptoms, asha)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            "Demo Patient",
            "9876543210",
            35,
            "Village A",
            "Fever and weakness",
            "Demo ASHA Worker"
        ))

        patient_id = cursor.lastrowid

        # REFERRAL
        conn.execute("""
            INSERT INTO referrals
            (
                patient_id,
                patient_name,
                from_facility,
                to_facility,
                reason,
                status,
                created_by
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            patient_id,
            "Demo Patient",
            "Village A Sub-Centre",
            "Village A Primary Health Centre",
            "Fever and weakness",
            "Pending",
            "Demo ASHA Worker"
        ))

        # FOLLOW-UP
        conn.execute("""
            INSERT INTO followups
            (
                patient_id,
                patient_name,
                reason,
                status,
                asha
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            patient_id,
            "Demo Patient",
            "Patient has not reached the PHC after referral",
            "Follow-up Required",
            "Demo ASHA Worker"
        ))

        # FEEDBACK
        conn.execute("""
            INSERT INTO feedback
            (
                patient_id,
                patient_name,
                facility,
                rating,
                feedback,
                outcome
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            patient_id,
            "Demo Patient",
            "Village A Primary Health Centre",
            4,
            "Good service and helpful staff.",
            "Treatment completed"
        ))

    # DOCTORS
    doctor_count = conn.execute(
        "SELECT COUNT(*) FROM doctors"
    ).fetchone()[0]

    if doctor_count == 0:

        doctors = [
            (
                "Dr. Priya Sharma",
                "General Medicine",
                "Village A Primary Health Centre",
                "09:00 AM - 02:00 PM",
                "On Duty"
            ),
            (
                "Dr. Rahul Patil",
                "Pediatrics",
                "Village A Primary Health Centre",
                "10:00 AM - 04:00 PM",
                "On Duty"
            ),
            (
                "Dr. Sneha Deshmukh",
                "Gynecology",
                "Village A Primary Health Centre",
                "09:00 AM - 01:00 PM",
                "On Leave"
            )
        ]

        conn.executemany("""
            INSERT INTO doctors
            (
                name,
                department,
                facility,
                timing,
                status
            )
            VALUES (?, ?, ?, ?, ?)
        """, doctors)

    # MEDICINES
    medicine_count = conn.execute(
        "SELECT COUNT(*) FROM medicines"
    ).fetchone()[0]

    if medicine_count == 0:

        medicines = [
            (
                "Paracetamol",
                "Village A Primary Health Centre",
                240,
                "tablets",
                50
            ),
            (
                "ORS",
                "Village A Primary Health Centre",
                180,
                "packets",
                40
            ),
            (
                "Amoxicillin",
                "Village A Primary Health Centre",
                18,
                "tablets",
                30
            ),
            (
                "Iron Tablets",
                "Village A Primary Health Centre",
                0,
                "tablets",
                30
            )
        ]

        conn.executemany("""
            INSERT INTO medicines
            (
                name,
                facility,
                quantity,
                unit,
                low_stock_limit
            )
            VALUES (?, ?, ?, ?, ?)
        """, medicines)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_database()
    seed_demo_data()

    print("===================================")
    print("JeevanLink Database Ready")
    print("===================================")
    print(f"Database: {DB_PATH}")