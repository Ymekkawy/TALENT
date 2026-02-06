import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import tempfile
import json
from datetime import datetime

# ---------------- CONFIG ----------------
st.set_page_config("TALENT HOUSE", layout="wide")

ADMIN_USERNAME = "dev"
ADMIN_PASSWORD = "152007poco"
PAYMENT_NUMBER = "01000004397"

TOKEN_PACKAGES = {
    "30 Tokens": (100, 30),
    "60 Tokens": (90, 60),
    "600 Tokens": (1500, 600)
}

# ---------------- FIREBASE INIT (SAFE) ----------------
if not firebase_admin._apps:
    firebase_dict = {
        "type": "service_account",
        "project_id": st.secrets["FIREBASE_PROJECT_ID"],
        "private_key": st.secrets["FIREBASE_PRIVATE_KEY"],
        "client_email": st.secrets["FIREBASE_CLIENT_EMAIL"],
        "token_uri": "https://oauth2.googleapis.com/token",
    }

    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as f:
        json.dump(firebase_dict, f)
        cred = credentials.Certificate(f.name)

    firebase_admin.initialize_app(cred)

db = firestore.client()

# ---------------- SESSION ----------------
if "user" not in st.session_state:
    st.session_state.user = None
    st.session_state.role = None

# ---------------- AUTH ----------------
def login():
    st.subheader("Login")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if st.button("Login"):
        if u == ADMIN_USERNAME and p == ADMIN_PASSWORD:
            st.session_state.user = u
            st.session_state.role = "admin"
            st.rerun()

        doc = db.collection("users").document(u).get()
        if doc.exists and doc.to_dict()["password"] == p:
            st.session_state.user = u
            st.session_state.role = doc.to_dict()["role"]
            st.rerun()
        else:
            st.error("Wrong credentials")

def signup():
    st.subheader("Sign Up")
    u = st.text_input("New Username")
    p = st.text_input("New Password", type="password")
    role = st.selectbox("Role", ["skiller", "scout"])

    if st.button("Create"):
        if db.collection("users").document(u).get().exists:
            st.error("Username exists")
        else:
            db.collection("users").document(u).set({
                "password": p,
                "role": role,
                "tokens": 30 if role == "skiller" else 0,
                "created": datetime.utcnow()
            })
            st.success("Account created")

# ---------------- SKILLER ----------------
def skiller():
    st.header("Skiller Dashboard")

    st.subheader("New Talent Post (Image/Video)")
    media = st.file_uploader("Upload", type=["jpg", "png", "mp4"])
    if media and st.button("Post"):
        db.collection("posts").add({
            "user": st.session_state.user,
            "rating": 1,
            "created": datetime.utcnow()
        })
        st.success("Posted")

    st.subheader("Buy Tokens")
    for name, (price, tokens) in TOKEN_PACKAGES.items():
        with st.expander(name):
            st.write(f"{price} EGP → {tokens} tokens")
            ss = st.file_uploader("Payment Screenshot", key=name)
            if ss and st.button(f"Submit {name}"):
                db.collection("payments").add({
                    "user": st.session_state.user,
                    "tokens": tokens,
                    "approved": False
                })
                st.success(f"Send to {PAYMENT_NUMBER}")

# ---------------- SCOUT ----------------
def scout():
    st.header("Scout – Discover Talents")
    posts = db.collection("posts").stream()
    for p in posts:
        d = p.to_dict()
        st.write(d["user"], "⭐", d["rating"])
        if st.button(f"Rate {p.id}"):
            db.collection("posts").document(p.id).update({
                "rating": d["rating"] + 1
            })

# ---------------- ADMIN ----------------
def admin():
    st.header("Admin Panel")

    st.subheader("Payments")
    for p in db.collection("payments").where("approved", "==", False).stream():
        d = p.to_dict()
        if st.button(f"Approve {p.id}"):
            uref = db.collection("users").document(d["user"])
            u = uref.get().to_dict()
            uref.update({"tokens": u["tokens"] + d["tokens"]})
            db.collection("payments").document(p.id).update({"approved": True})
            st.success("Approved")

# ---------------- ROUTER ----------------
if not st.session_state.user:
    t1, t2 = st.tabs(["Login", "Sign Up"])
    with t1: login()
    with t2: signup()
else:
    if st.session_state.role == "skiller":
        skiller()
    elif st.session_state.role == "scout":
        scout()
    else:
        admin()
