import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
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

# ---------------- FIREBASE ----------------
if not firebase_admin._apps:
    firebase_key_dict = json.loads(st.secrets["FIREBASE_KEY_JSON"])
    cred = credentials.Certificate(firebase_key_dict)
    firebase_admin.initialize_app(cred)

db = firestore.client()

# ---------------- SESSION ----------------
if "user" not in st.session_state:
    st.session_state.user = None
    st.session_state.role = None

# ---------------- AUTH ----------------
def login():
    st.subheader("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            st.session_state.user = username
            st.session_state.role = "admin"
            st.rerun()
        user_doc = db.collection("users").document(username).get()
        if user_doc.exists and user_doc.to_dict()["password"] == password:
            st.session_state.user = username
            st.session_state.role = user_doc.to_dict()["role"]
            st.rerun()
        else:
            st.error("Wrong credentials")

def signup():
    st.subheader("Sign Up")
    username = st.text_input("New Username")
    password = st.text_input("New Password", type="password")
    role = st.selectbox("Role", ["skiller", "scout"])
    if st.button("Create Account"):
        if db.collection("users").document(username).get().exists:
            st.error("Username exists")
        else:
            db.collection("users").document(username).set({
                "password": password,
                "role": role,
                "tokens": 30 if role=="skiller" else 0,
                "created": datetime.utcnow(),
                "profile_pic": ""
            })
            st.success("Account created")

# ---------------- SKILLER ----------------
def skiller_dashboard():
    st.header("Skiller Dashboard")
    user_ref = db.collection("users").document(st.session_state.user)
    user_data = user_ref.get().to_dict()

    st.subheader("Upload Profile Picture")
    pic = st.file_uploader("Profile Pic", type=["png","jpg"])
    if pic:
        user_ref.update({"profile_pic": pic.read()})
        st.success("Profile picture updated")

    if st.button("Remove Profile Pic"):
        user_ref.update({"profile_pic": ""})

    st.subheader("New Talent Post (Image/Video required)")
    media = st.file_uploader("Upload Media", type=["jpg","png","mp4"])
    if media and st.button("Post"):
        db.collection("posts").add({
            "user": st.session_state.user,
            "media": media.read(),
            "media_type": media.type,
            "rating": 1,
            "created": datetime.utcnow()
        })
        st.success("Posted successfully")

    st.subheader("Your Posts")
    posts = db.collection("posts").where("user","==",st.session_state.user).stream()
    for p in posts:
        data = p.to_dict()
        col1, col2 = st.columns([3,1])
        with col1: st.write(f"Post ID: {p.id} | Rating: {data['rating']}")
        with col2:
            if st.button(f"Delete {p.id}"):
                db.collection("posts").document(p.id).delete()
                st.experimental_rerun()

    st.subheader("Buy Tokens")
    for name, (price, tokens) in TOKEN_PACKAGES.items():
        with st.expander(f"{name} - {price} EGP"):
            ss = st.file_uploader("Upload payment screenshot", key=name)
            if ss and st.button(f"Submit {name}"):
                db.collection("payments").add({
                    "user": st.session_state.user,
                    "tokens": tokens,
                    "processed": False,
                    "time": datetime.utcnow()
                })
                st.success(f"Send money to {PAYMENT_NUMBER}")

# ---------------- SCOUT ----------------
def scout_dashboard():
    st.header("Scout Dashboard")
    posts = db.collection("posts").stream()
    sorted_posts = sorted(posts, key=lambda p: (p.to_dict().get("rating",0), db.collection("users").document(p.to_dict()["user"]).get().to_dict().get("tokens",0)), reverse=True)
    for p in sorted_posts:
        data = p.to_dict()
        st.write(f"Talent: {data['user']} | Rating: {data['rating']}")
        if st.button(f"⭐ Rate {p.id}"):
            db.collection("posts").document(p.id).update({"rating": data["rating"]+1})

# ---------------- ADMIN ----------------
def admin_panel():
    st.header("Admin Panel")
    st.subheader("Users")
    for u in db.collection("users").stream():
        st.write(u.id, u.to_dict()["role"])
        if st.button(f"Delete {u.id}"):
            db.collection("users").document(u.id).delete()

    st.subheader("Payments")
    for p in db.collection("payments").where("processed","==",False).stream():
        data = p.to_dict()
        if st.button(f"Approve {p.id}"):
            user_ref = db.collection("users").document(data["user"])
            udata = user_ref.get().to_dict()
            user_ref.update({"tokens": udata["tokens"] + data["tokens"]})
            db.collection("payments").document(p.id).update({"processed": True})

# ---------------- ROUTER ----------------
if not st.session_state.user:
    tab1, tab2 = st.tabs(["Login","Sign Up"])
    with tab1: login()
    with tab2: signup()
else:
    if st.session_state.role=="skiller": skiller_dashboard()
    elif st.session_state.role=="scout": scout_dashboard()
    else: admin_panel()
