# 🏥 JeevanLink – Rural Healthcare Continuity Platform

> A connected digital healthcare platform designed to improve healthcare accessibility, referral continuity, and follow-up services for rural and underserved communities.

---

## 📌 Overview

JeevanLink is a rural healthcare continuity platform that connects patients, ASHA workers, Primary Health Centres (PHCs), rural hospitals, and District Health Officers (DHOs) through a unified healthcare workflow.

The platform addresses common rural healthcare challenges such as limited connectivity, difficulty accessing doctors and medicines, fragmented referrals, and lack of follow-up tracking.

JeevanLink follows an **online + offline-first approach** and provides additional access through **USSD and IVR interfaces** for users with limited internet connectivity or basic phones.

---

## 🎯 Problem Statement

Rural and underserved communities may face:

- Limited or unreliable internet connectivity
- Difficulty finding available doctors
- Difficulty checking medicine availability
- Long travel distances to healthcare facilities
- Fragmented referral processes
- Lack of follow-up tracking
- Limited digital literacy
- Poor visibility of healthcare services

These challenges can result in delayed treatment and interrupted patient care.

---

## 💡 Our Solution

JeevanLink creates a connected healthcare journey:

**Patient → ASHA Worker → PHC → Rural Hospital → Follow-up → Medicine → District Monitoring**

The platform allows healthcare stakeholders to track and manage relevant information throughout the patient's healthcare journey.

---

## 🚀 Key Features

### 👤 Patient Portal

- Patient registration and login
- Appointment booking
- Doctor availability
- Medicine availability
- Referral journey tracking
- Follow-up information
- Patient feedback

### 👩‍⚕️ ASHA Worker Portal

- Patient registration
- Symptom recording
- Referral creation
- Offline patient data entry
- Follow-up management
- Data synchronization

### 🏥 PHC Portal

- Referral management
- Referred patient tracking
- Doctor availability management
- Medicine stock management
- Referral status updates

### 🏨 Rural Hospital Portal

- Referred patient management
- Doctor availability
- Medicine availability
- Feedback monitoring
- Escalation monitoring

### 📊 DHO Dashboard

- Patient monitoring
- Referral monitoring
- Follow-up monitoring
- Doctor and service monitoring
- Medicine monitoring
- Facility-level monitoring
- Feedback and escalation monitoring
- Healthcare analytics

### 📱 USSD Support

Provides essential healthcare services through a simulated USSD interface for users with basic phones or limited internet connectivity.

### ☎️ IVR Support

Provides a simulated voice-based interface for users with low digital literacy or limited smartphone access.

### 📴 Offline-First Support

ASHA workers can store patient information locally and synchronize it when internet connectivity becomes available.

---

## 🧩 Technology Stack

| Layer | Technology |
|---|---|
| Frontend | HTML, CSS, JavaScript |
| Backend | Python, Flask |
| Database | SQLite |
| Offline Storage | Browser LocalStorage |
| AI / ML | Python, Scikit-learn |
| Communication | USSD / IVR Simulation |
| Development | VS Code, Anaconda |
| Version Control | Git, GitHub |



## 🏗️ System Architecture

```text
                    ┌────────────────────┐
                    │      Patient       │
                    └─────────┬──────────┘
                              │
                              ▼
                    ┌────────────────────┐
                    │    ASHA Worker     │
                    └─────────┬──────────┘
                              │
                         Referral
                              │
                              ▼
                    ┌────────────────────┐
                    │        PHC         │
                    └─────────┬──────────┘
                              │
                         Referral
                              │
                              ▼
                    ┌────────────────────┐
                    │  Rural Hospital    │
                    └─────────┬──────────┘
                              │
                    Follow-up / Treatment
                              │
                              ▼
                    ┌────────────────────┐
                    │    DHO Dashboard   │
                    └────────────────────┘

       ┌───────────────┐              ┌───────────────┐
       │     USSD      │              │      IVR      │
       └───────┬───────┘              └───────┬───────┘
               │                              │
               └────────── JeevanLink ────────┘



## 📁 Project Structure

```text
JeevanLink-Rural-Healthcare/
│
├── app.py
├── database.py
├── requirements.txt
├── README.md
│
├── templates/
│   ├── login.html
│   ├── patient.html
│   ├── patient_doctors.html
│   ├── patient_medicines.html
│   ├── asha.html
│   ├── asha_followups.html
│   ├── create_referral.html
│   ├── phc.html
│   ├── phc_referrals.html
│   ├── phc_doctors.html
│   ├── phc_medicines.html
│   ├── rural_hospital.html
│   ├── rural_doctors.html
│   ├── rural_medicines.html
│   ├── facility_feedback.html
│   ├── rural_escalations.html
│   ├── dho.html
│   ├── ussd.html
│   └── ivr.html
│
├── static/
│   ├── css/
│   └── js/
│
└── jeevanlink.db

## 🔐 Role-Based Access

JeevanLink provides separate access for different healthcare stakeholders.

| Role | Main Responsibilities |
|---|---|
| Patient | Appointments, doctors, medicines, referrals |
| ASHA Worker | Registration, referrals, follow-ups |
| PHC | Referral, doctor and medicine management |
| Rural Hospital | Patient and facility management |
| DHO | District-level monitoring and analytics |



## 🌐 Accessibility Approach

JeevanLink uses multiple access channels to support users with different levels of connectivity and digital access.


                    JeevanLink
                        │
           ┌────────────┼────────────┐
           │            │            │
         Web          USSD          IVR
           │            │            │
      Smartphone    Basic Phone   Voice Access
           │            │            │
           └────────────┼────────────┘
                        │
                 Healthcare Services


📴 Offline-First Workflow

ASHA workers can collect patient information even when internet connectivity is unavailable.

ASHA Worker
     ↓
Enter Patient Data
     ↓
Store Locally
     ↓
Internet Available?
     ↓
    Yes
     ↓
Synchronize
     ↓
Central Database

This approach helps maintain continuity of data collection in areas with unreliable connectivity.


🔒 Data & Access

The prototype uses role-based access to ensure that users interact with healthcare information relevant to their role and facility.

Authorization is handled by the backend rather than relying only on frontend controls.


## 🧪 Demo Credentials

| Role | Login ID | OTP |
|---|---|---|
| Patient | `9876543210` | `123456` |
| ASHA Worker | `ASHA001` | `123456` |
| PHC | `PHC001` | `123456` |
| Rural Hospital | `RH001` | `123456` |
| DHO | `DHO001` | `123456` |

> These credentials are provided only for demonstration of the JeevanLink prototype.





