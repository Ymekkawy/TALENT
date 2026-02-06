import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import hashlib

# ================== ADMIN ==================
ADMIN_USERNAME = "dev"
ADMIN_PASSWORD = "152007poco"

# ================== PAYMENT ==================
PAYMENT_PHONE = "01000004397"

TOKEN_PACKAGES = {
    30: 100,
    60: 90,
    600: 1500
}

# ================== FIREBASE ==================
firebase_key = {
    "type": "service_account",
    "project_id": "talent-199e5",
    "private_key_id": "05c6f4ed6b67095335bd9e6307d86dfbeefe1414",
    "private_key": """-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCoD3wCp2QU1prJ
8EmhCUbmxSW/gg4XVL+9/hoIB11cGh8SBIylwUd2+1HEfLoVJrGDJnLYSEWV4666
3riITsATuALItPAeLEs95+zM2/mdg5hDN8Kbc1XZn2G36KCETjyX87vyGtLe2dfr
Vo47M6rAccgXSwIVsjvJIGM8CcyEhi05gd7ExQbWSo1Po5GredhvY81ggAVhRiEE
n6c4iY57Qmmfi41X6tW53VhMikIhwz3Vvn5yBuAByk+Y+TXT/4OYda70RvMrd/CL
xeiIZtawXj8zgDwhswSf2usrD1389WbPqULRPJp61I08MbamGLN7nzA0Xkt5W3hL
dEHgopXZAgMBAAECggEAAIOM8LAGrJejK9wfSRFhP9eAXjaYFv3W9Vx77jnMbY7x
xwsMaCg626eqg7pYWVCKeTAhoW6rI80FsyPMa964cKGpdkuIq8GdP7onUQom7YRQ
UyaDcPxaBHXUsAyMUm7MXTAii0LNLiZ7l89YOIuQntEE6jeKVJduM7OC7bjKK7By
9Pj3XzDmv6kDCukRsNb9c11yCG7PzWn5v+CKGV0yLf9YYaAKXnDp5Lurln6K9zYs
Z9Gyh+elHUX5QyvteIUNp+cXsbOo0GSjvfwtL8Uk9z8vUqi5pvMhc2FI8FlVxuVX
VH2u8C5VKFC5g+sDtNtniHhQdR97fKtXajuM4RVVZw==
-----END PRIVATE KEY-----""",
    "client_email": "firebase-adminsdk-fbsvc@talent-199e5.iam.gserviceaccount.com",
    "token_uri": "https://oauth2.googleapis.com/token"
}

if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_key)
    firebase_admin.initialize_app(cred)

db = firestore.client()

# ================== UI ==================
st.set_page_config("TALENT HOUSE", "🔥")
st.markdown("""
<style>
body {background:#0b0614;color:white;}
.stButton button{background:#a855f7;color:white;border-radius:12px;}
</style>
""", unsafe_allow_html=True)

# ================== HELPERS ==================
def hash_pass(p): 
    return hashlib.sha256(p.encode()).hexdigest()

def uid(email):
    return email.replace("@","_").replace(".","_")

# ================== SESSION ==================
if "user" not in st.session_state:
    st.session_state.user = None

# ================== SIGNUP ==================
def signup():
    st.subheader("Sign Up")
    email = st.text_input("Email")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    role = st.selectbox("Role", ["skiller", "scout"])

    if st.button("Create Account"):
        u = uid(email)
        if db.collection("users").document(u).get().exists:
            st.error("User already exists")
            return

        db.collection("users").document(u).set({
            "email": email,
            "username": username,
            "password": hash_pass(password),
            "role": role,
            "tokens": 30 if role == "skiller" else 0,
            "active": True
        })
        st.success("Account created 🔥")
        st.session_state.user = db.collection("users").document(u).get().to_dict()
        st.rerun()

# ================== LOGIN ==================
def login():
    st.subheader("Login")
    user = st.text_input("Email / Admin Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if user == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            st.session_state.user = {"role": "admin", "username": "Admin"}
            st.rerun()

        u = uid(user)
        doc = db.collection("users").document(u).get()
        if not doc.exists:
            st.error("User not found")
            return

        data = doc.to_dict()
        if data["password"] != hash_pass(password):
            st.error("Wrong password")
            return

        if not data["active"]:
            st.error("Account suspended")
            return

        st.session_state.user = data
        st.rerun()

# ================== DASHBOARD ==================
def dashboard():
    user = st.session_state.user
    st.subheader(f"Welcome {user['username']}")

    if st.button("Logout"):
        st.session_state.user = None
        st.rerun()

    # ===== SKILLER =====
    if user["role"] == "skiller":
        st.markdown(f"### Tokens: {user['tokens']}")
        content = st.text_area("Post your talent")
        cat = st.selectbox("Category", ["Music","Writing","Art","General"])

        if st.button("Post"):
            db.collection("posts").add({
                "skiller": uid(user["email"]),
                "content": content,
                "category": cat,
                "rating": 5
            })
            st.success("Posted 🔥")

        st.markdown("---")
        st.markdown(f"### Buy Tokens 💳 (حول على {PAYMENT_PHONE})")
        pack = st.selectbox("Package", list(TOKEN_PACKAGES.keys()))
        phone = st.text_input("Your wallet number")
        shot = st.file_uploader("Upload screenshot")

        if st.button("Submit Payment"):
            if phone and shot:
                db.collection("payments").add({
                    "skiller": uid(user["email"]),
                    "tokens": pack,
                    "amount": TOKEN_PACKAGES[pack],
                    "phone": phone,
                    "approved": False
                })
                st.success("Payment sent for review")

    # ===== SCOUT =====
    elif user["role"] == "scout":
        st.markdown("### Talents")
        for p in db.collection("posts").stream():
            post = p.to_dict()
            st.write(post["content"])
            r = st.slider("Rate",1,10,key=p.id)
            if st.button("Submit",key=f"s{p.id}"):
                new = (post["rating"] + r) / 2
                db.collection("posts").document(p.id).update({"rating": new})
                st.success("Rated 🔥")

    # ===== ADMIN =====
    elif user["role"] == "admin":
        st.markdown("## Admin Panel 👑")

        st.markdown("### Users")
        for u in db.collection("users").stream():
            d = u.to_dict()
            st.write(d["username"], d["role"], "Active:", d["active"])
            if st.button(f"Toggle {u.id}", key=u.id):
                db.collection("users").document(u.id).update({
                    "active": not d["active"]
                })
                st.rerun()

        st.markdown("### Payments")
        for p in db.collection("payments").where("approved","==",False).stream():
            pay = p.to_dict()
            st.write(pay)
            if st.button(f"Approve {p.id}", key=f"a{p.id}"):
                sk = pay["skiller"]
                doc = db.collection("users").document(sk).get()
                tokens_now = doc.to_dict()["tokens"]
                db.collection("users").document(sk).update({
                    "tokens": tokens_now + pay["tokens"]
                })
                db.collection("payments").document(p.id).update({"approved": True})
                st.success("Approved")
                st.rerun()

# ================== MAIN ==================
if st.session_state.user is None:
    tab = st.radio("Menu", ["Login", "Sign Up"])
    login() if tab == "Login" else signup()
else:
    dashboard()
