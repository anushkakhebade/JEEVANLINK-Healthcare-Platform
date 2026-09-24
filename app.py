from flask import Flask, render_template, request, redirect, session, jsonify, url_for
import database as db
from datetime import datetime

app = Flask(__name__)
app.secret_key = "jeevanlink-demo-secret"
db.init_database()
db.seed_demo_data()

FACILITIES = [
    "Village A Sub-Centre",
    "Village A Primary Health Centre",
    "Taluka Rural Hospital",
    "District Hospital",
]


def role_required(role):
    return session.get("role") == role


def current_patient():
    return db.get_patient_by_mobile(session.get("user_id", "")) if session.get("role") == "patient" else None


def add_feedback(patient_id, patient_name, facility, rating, feedback, outcome):
    conn = db.get_connection()
    conn.execute("""INSERT INTO feedback (patient_id, patient_name, facility, rating, feedback, outcome)
                    VALUES (?, ?, ?, ?, ?, ?)""",
                 (patient_id, patient_name, facility, rating, feedback, outcome))
    conn.commit()
    row = conn.execute("SELECT * FROM feedback WHERE id = last_insert_rowid()").fetchone()
    conn.close()
    return dict(row)


def all_feedback():
    conn = db.get_connection()
    rows = conn.execute("SELECT * FROM feedback ORDER BY id DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        login_id = (request.form.get("login_id") or "").strip()
        otp = (request.form.get("otp") or "").strip()
        conn = db.get_connection()
        user = conn.execute("SELECT * FROM users WHERE login_id = ?", (login_id,)).fetchone()
        conn.close()
        if not user:
            return render_template("login.html", error="Invalid login ID. Demo IDs: 9876543210, ASHA001, PHC001, RH001, DHO001")
        if otp != "123456":
            return render_template("login.html", error="Invalid OTP. For this prototype, use OTP: 123456")
        session.update(user_id=user["login_id"], role=user["role"], name=user["name"], facility=user["facility"])
        routes = {
            "patient": "patient", "asha": "asha", "phc": "phc",
            "rural_hospital": "rural_hospital", "dho": "dho"
        }
        return redirect(url_for(routes[user["role"]]))
    return render_template("login.html")


@app.route("/patient")
def patient():
    if not role_required("patient"):
        return redirect(url_for("login"))
    p = current_patient()
    appointments = db.get_patient_appointments(p["id"]) if p else []
    referrals = [r for r in db.get_all_referrals() if p and r["patient_id"] == p["id"]]
    today = datetime.now().strftime("%Y-%m-%d")
    return render_template("patient.html", patient=p, appointments=appointments, referrals=referrals, today=today)


@app.route("/patient/book-appointment", methods=["POST"])
def patient_book_appointment():
    if not role_required("patient"):
        return redirect(url_for("login"))
    p = current_patient()
    if not p:
        return "Patient record not found", 404
    appointment_date = (request.form.get("appointment_date") or "").strip()
    appointment_time = (request.form.get("appointment_time") or "").strip()
    facility = request.form.get("facility", "Village A Primary Health Centre")

    # Prevent accidental/past dates in the demo.
    today = datetime.now().strftime("%Y-%m-%d")
    if not appointment_date or appointment_date < today:
        return render_template(
            "patient.html",
            patient=p,
            appointments=db.get_patient_appointments(p["id"]),
            referrals=[r for r in db.get_all_referrals() if r["patient_id"] == p["id"]],
            today=today,
            error="Please select today or a future appointment date."
        )

    appointment = db.create_appointment(
        p["id"], p["name"], p["mobile"],
        facility, appointment_date, appointment_time, "Web"
    )
    return render_template("patient.html", patient=p, appointments=db.get_patient_appointments(p["id"]),
                           referrals=[r for r in db.get_all_referrals() if r["patient_id"] == p["id"]],
                           today=today, booking_success=appointment)


@app.route("/patient/feedback", methods=["GET", "POST"])
def patient_feedback():
    if not role_required("patient"):
        return redirect(url_for("login"))
    p = current_patient()
    if request.method == "POST" and p:
        try:
            rating = max(1, min(5, int(request.form.get("rating", 5))))
        except ValueError:
            rating = 5
        item = add_feedback(p["id"], p["name"], request.form.get("facility"), rating,
                            request.form.get("feedback"), request.form.get("outcome"))
        return render_template("patient_feedback.html", success=True, feedback=item)
    return render_template("patient_feedback.html")


@app.route("/register-patient", methods=["GET", "POST"])
def register_patient():
    if not role_required("asha"):
        return redirect(url_for("login"))
    if request.method == "POST":
        p = db.create_patient(request.form.get("name"), request.form.get("mobile"), request.form.get("age"),
                              request.form.get("village"), request.form.get("symptoms"), session.get("name"),
                              request.form.get("abha_id"))
        return render_template("register_patient.html", success=True, patient=p)
    return render_template("register_patient.html")


@app.route("/create-referral", methods=["GET", "POST"])
def create_referral():
    if not role_required("asha"):
        return redirect(url_for("login"))
    patients = db.get_all_patients()
    if request.method == "POST":
        p = db.get_patient_by_id(request.form.get("patient_id"))
        if not p:
            return render_template("create_referral.html", patients=patients, error="Patient not found.")
        r = db.create_referral(p["id"], p["name"], session.get("facility"), request.form.get("to_facility"),
                               request.form.get("reason"), session.get("name"))
        return render_template("create_referral.html", success=True, referral=r, patients=patients)
    return render_template("create_referral.html", patients=patients)


@app.route("/asha")
def asha():
    if not role_required("asha"):
        return redirect(url_for("login"))
    patients = db.get_all_patients()
    referrals = [r for r in db.get_all_referrals() if r["created_by"] == session.get("name")]
    followups = db.get_followups(session.get("name"))
    return render_template("asha.html", patients_count=len(patients), referral_count=len(referrals),
                           followup_count=sum(f["status"] != "Completed" for f in followups))


@app.route("/asha/followups")
def asha_followups():
    if not role_required("asha"):
        return redirect(url_for("login"))
    return render_template("asha_followups.html", followups=db.get_followups(session.get("name")))


@app.route("/complete-followup/<int:followup_id>", methods=["POST"])
def complete_followup_route(followup_id):
    if not role_required("asha"):
        return "Unauthorized", 403
    db.complete_followup(followup_id)
    return redirect(url_for("asha_followups"))


@app.route("/phc")
def phc():
    if not role_required("phc"):
        return redirect(url_for("login"))
    facility = session.get("facility")
    referrals = [r for r in db.get_all_referrals() if r["to_facility"] == facility]
    appointments = []
    conn = db.get_connection()
    appointments = [dict(r) for r in conn.execute("SELECT * FROM appointments WHERE facility = ? ORDER BY id DESC", (facility,)).fetchall()]
    conn.close()
    medicines = db.get_medicines(facility)
    doctors = db.get_doctors(facility)
    return render_template("phc.html", referrals=referrals, appointments=appointments, medicines=medicines, doctors=doctors,
                           pending_referrals=sum(r["status"] == "Pending" for r in referrals))


@app.route("/phc/referrals")
def phc_referrals():
    if not role_required("phc"):
        return "Unauthorized", 403
    referrals = [r for r in db.get_all_referrals() if r["to_facility"] == session.get("facility")]
    return render_template("phc_referrals.html", referrals=referrals)


@app.route("/update-referral/<int:referral_id>", methods=["POST"])
def update_referral(referral_id):
    if session.get("role") not in {"phc", "rural_hospital", "dho"}:
        return "Unauthorized", 403
    r = next((x for x in db.get_all_referrals() if x["id"] == referral_id), None)
    if not r:
        return "Referral not found", 404
    facility = session.get("facility")
    if session.get("role") == "phc" and r["to_facility"] != facility:
        return "Unauthorized", 403
    status = request.form.get("status")
    if status not in {"Pending", "Arrived", "Completed"}:
        return "Invalid status", 400
    db.update_referral_status(referral_id, status)
    if status == "Completed":
        conn = db.get_connection()
        exists = conn.execute("SELECT id FROM followups WHERE patient_id = ? AND status != 'Completed'", (r["patient_id"],)).fetchone()
        if not exists:
            conn.execute("INSERT INTO followups (patient_id, patient_name, reason, status, asha) VALUES (?, ?, ?, 'Follow-up Required', ?)",
                         (r["patient_id"], r["patient_name"], "Post-referral follow-up", r["created_by"]))
        conn.commit(); conn.close()
    if session.get("role") == "phc":
        return redirect(url_for("phc_referrals"))
    if session.get("role") == "rural_hospital":
        return redirect(url_for("rural_hospital"))
    return redirect(url_for("dho"))


@app.route("/phc/doctors")
def phc_doctors():
    if not role_required("phc"):
        return "Unauthorized", 403
    return render_template("phc_doctors.html", doctors=db.get_doctors(session.get("facility")), facility=session.get("facility"))


@app.route("/phc/doctors/update/<int:doctor_id>", methods=["POST"])
def doctor_status(doctor_id):
    if not role_required("phc"):
        return "Unauthorized", 403
    doctor = next((d for d in db.get_doctors() if d["id"] == doctor_id), None)
    if not doctor or doctor["facility"] != session.get("facility"):
        return "Unauthorized", 403
    status = request.form.get("status")
    if status not in {"On Duty", "On Leave", "Unavailable"}:
        return "Invalid status", 400
    db.update_doctor_status(doctor_id, status)
    return redirect(url_for("phc_doctors"))


@app.route("/phc/medicines")
def phc_medicines():
    if not role_required("phc"):
        return "Unauthorized", 403
    return render_template("phc_medicines.html", medicines=db.get_medicines(session.get("facility")), facility=session.get("facility"))


@app.route("/phc/medicines/update/<int:medicine_id>", methods=["POST"])
def medicine_update(medicine_id):
    if not role_required("phc"):
        return "Unauthorized", 403
    med = next((m for m in db.get_medicines() if m["id"] == medicine_id), None)
    if not med or med["facility"] != session.get("facility"):
        return "Unauthorized", 403
    try: amount = int(request.form.get("amount", 0))
    except ValueError: amount = 0
    if amount < 0: return "Invalid quantity", 400
    if request.form.get("action") == "dispense" and amount > med["quantity"]:
        return "Not enough stock available", 400
    db.update_medicine(medicine_id, request.form.get("action"), amount)
    return redirect(url_for("phc_medicines"))


@app.route("/rural-hospital")
def rural_hospital():
    if not role_required("rural_hospital"):
        return redirect(url_for("login"))
    incoming = [r for r in db.get_all_referrals() if r["to_facility"] == session.get("facility")]
    return render_template("rural_hospital.html", referrals=incoming)


@app.route("/dho")
def dho():
    if not role_required("dho"):
        return "Unauthorized", 403
    referrals = db.get_all_referrals(); followups = db.get_followups(); medicines = db.get_medicines()
    summary = []
    for facility in FACILITIES:
        rs = [r for r in referrals if r["to_facility"] == facility]
        ms = [m for m in medicines if m["facility"] == facility]
        summary.append({"facility": facility, "referrals": len(rs), "pending": sum(r["status"] == "Pending" for r in rs),
                        "completed": sum(r["status"] == "Completed" for r in rs), "medicine_alerts": sum(m["quantity"] <= m["low_stock_limit"] for m in ms)})
    return render_template("dho.html", total_referrals=len(referrals), pending_referrals=sum(r["status"] == "Pending" for r in referrals),
                           arrived_referrals=sum(r["status"] == "Arrived" for r in referrals), completed_referrals=sum(r["status"] == "Completed" for r in referrals),
                           total_followups=len(followups), pending_followups=sum(f["status"] != "Completed" for f in followups),
                           completed_followups=sum(f["status"] == "Completed" for f in followups), total_medicines=len(medicines),
                           low_stock_medicines=sum(0 < m["quantity"] <= m["low_stock_limit"] for m in medicines),
                           out_of_stock_medicines=sum(m["quantity"] == 0 for m in medicines),
                           available_medicines=sum(m["quantity"] > m["low_stock_limit"] for m in medicines),
                           facility_summary=summary, recent_referrals=referrals[-5:][::-1])


@app.route("/dho/feedback")
def dho_feedback():
    if not role_required("dho"):
        return "Unauthorized", 403
    items = all_feedback()
    avg = round(sum(x["rating"] for x in items) / len(items), 1) if items else 0
    return render_template("dho_feedback.html", feedback=items, total_feedback=len(items), average_rating=avg,
                           completed_outcomes=sum(x["outcome"] == "Treatment completed" for x in items))


@app.route("/offline")
def offline_mode():
    if not role_required("asha"):
        return redirect(url_for("login"))
    return render_template("offline.html", name=session.get("name"), facility=session.get("facility"))


@app.route("/offline/sync", methods=["POST"])
def offline_sync():
    if not role_required("asha"):
        return jsonify(success=False, message="Unauthorized"), 403
    payload = request.get_json(silent=True) or {}
    records = payload.get("records", [])
    synced = 0
    created = []
    for rec in records:
        mobile = (rec.get("mobile") or "").strip()
        name = (rec.get("name") or rec.get("patient_name") or "").strip()
        if not mobile or not name:
            continue
        p = db.create_patient(name, mobile, rec.get("age"), rec.get("village", "Offline Village"),
                              rec.get("symptoms") or rec.get("notes", ""), session.get("name"), rec.get("abha_id"))
        created.append(p["id"]); synced += 1
    return jsonify(success=True, message="Offline data synchronized successfully", records_synced=synced,
                   patient_ids=created)


@app.route("/api/patient/lookup")
def api_patient_lookup():
    mobile = (request.args.get("mobile") or "").strip()
    p = db.get_patient_by_mobile(mobile)
    if not p: return jsonify(success=False, message="Patient not found"), 404
    return jsonify(success=True, patient=p, appointments=db.get_patient_appointments(p["id"]))


@app.route("/api/ussd/appointment", methods=["POST"])
def api_ussd_appointment():
    data = request.get_json(silent=True) or request.form
    mobile = (data.get("mobile") or "").strip()
    p = db.get_patient_by_mobile(mobile)
    if not p: return jsonify(success=False, message="Patient not found. Use 9876543210 for demo."), 404
    a = db.create_appointment(p["id"], p["name"], p["mobile"], data.get("facility", "Village A Primary Health Centre"),
                              data.get("appointment_date", "Demo Date"), data.get("appointment_time", "10:00 AM"), "USSD Simulator")
    return jsonify(success=True, appointment=a)


@app.route("/api/ussd/referrals")
def api_ussd_referrals():
    p = db.get_patient_by_mobile(request.args.get("mobile", ""))
    if not p: return jsonify(success=False), 404
    return jsonify(success=True, referrals=[r for r in db.get_all_referrals() if r["patient_id"] == p["id"]])


@app.route("/api/ussd/medicines")
def api_ussd_medicines():
    return jsonify(success=True, medicines=db.get_medicines("Village A Primary Health Centre"))


@app.route("/api/ussd/followups")
def api_ussd_followups():
    p = db.get_patient_by_mobile(request.args.get("mobile", ""))
    if not p: return jsonify(success=False), 404
    return jsonify(success=True, followups=[f for f in db.get_followups() if f["patient_id"] == p["id"]])


@app.route("/ussd")
def ussd():
    return render_template("ussd.html")


@app.route("/ivr")
def ivr():
    return render_template("ivr.html")


@app.route("/logout")
def logout():
    session.clear(); return redirect(url_for("home"))


@app.route("/health")
def health():
    return jsonify(status="success", message="JeevanLink backend is running", database="SQLite")


if __name__ == "__main__":
    app.run(debug=True)
