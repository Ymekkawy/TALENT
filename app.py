import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import hashlib

# ================== Admin Credentials ==================
ADMIN_USERNAME = "dev"
ADMIN_PASSWORD = "152007poco"

# ================== Payment Info ==================
PAYMENT_PHONE = "01000004397"

TOKEN_PACKAGES = {
    30: 100,
    60: 180,
    600: 1500
}

# ================== Firebase Secret ==================
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
VH2u8C5VKFC5g+sDtNtniHhQdR97fKtXajuM4RVVZwKBgQDfoh+qJ4zayoMnr5qU
DMJoNq+AoYoVuQXU4LDxv8fyk5lt3hru/LsT4KM2PRWeYQGQ5I6gQMpyr8ROq/ri
hv1PQXt+c1x2ja9+VqLMHhldMpNQ3Qy03BDEegovjHl9Ge0856lBiVKHtXrgrZSc
0J3i21eU9J9EZOnpSkonNxNYpwKBgQDAYlKl+FrQIM8WPAiBrOShzc9CCuMuv3WI
BFXK0OH85BRg7hxhjkf1Hdj8ltjnog90UKgBDSuCyaSDC/qYSG992mLScWr/tR8S
zWhNqvZNV9ewJtZ+P3Pj8KOu9QkesXvYXBhMHjDl3mmTUj+cuwHN4GvlNlAG9QI8
cGx2izHtfwKBgQCWwn/gQLtnQAC8/1gRGKzyfnNAHyas0EfLJBKFVwmfUbusYn/7
vusLUnQU+4cYd0ML/9ja1fLk7/NCKhR/JAueo4FyVKjvz0KQxC0Jt/zXZGIFsI+B
WZ4AJlm5hlTcbl8NoQrsgHvfuwt0bfBy6vyVU9MuOt8nx3QdbpSg7TMgnwKBgEUg
DwpLnnXCFCatE3FkqhHpXVshhle5u4VP6XOiclDnstrRM6lp8jkErH61xOIVvO/S
O0uFa+jmgxIDL9ufy0+xNGjhD80pSyz6WUvu7ekEcx98FP3v1rhEMsweh1Rb+V/Y
V3KiNneh3tVsbCbomtFaneoSBdc6Gb+VtaMyiJIJAoGAXU79VmCVxQnr6Pa2SDAH
0VqVYTWq2DxwGiizSLgErIiGe5ZU1XtB04nM/uLeNKeA/RpaPBJlH5eHi6Mu4zTD
aISKgiUOwXlInSe4bsK0FALkvvss50W5IVgjbHabyws16TrIO1uh3Iexcymu2YMG
vZjdgVbWjFG5GrLLBM5N8eE=
-----END PRIVATE KEY-----""",
  "client_email": "firebase-adminsdk-fbsvc@talent-199e5.iam.gserviceaccount.com",
  "client_id": "112925563666280259221",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token"
}

if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_key)
    firebase_admin.initialize_app(cred)

db = firestore.client()

# ================== Streamlit Config ==================
st.set_page_config(page_title="TALENT HOUSE", page_icon="🔥")
st.markdown("""
<style>
body { background-color:#0a041a; color:white; }
.stButton button { background:#a855f7; color:white; border-radius:12px; }
textarea, input, select { background:#14082f; color:white; border:1px solid #a855f7; border-radius:5px; }
</style>
""", unsafe_allow_html=True)

# ================== Session ==================
if "user" not in st.session_state:
    st.session_state.user = None

# ================== Helpers ==================
def hash_pass(p):
    return hashlib.sha256(p.encode()).hexdigest()

def uid_from_email(email):
    return email.replace("@","_").replace(".","_")

# ================== Signup ==================
def signup():
    st.subheader("Sign Up")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    username = st.text_input("Username")
    role = st.selectbox("Role", ["scout","skiller"])
    if st.button("Create Account"):
        uid = uid_from_email(email)
        doc = db.collection("users").document(uid).get()
        if doc.exists:
            st.error("User already exists")
        else:
            tokens = 30 if role=="skiller" else 0
            db.collection("users").document(uid).set({
                "email": email,
                "password": hash_pass(password),
                "username": username,
                "role": role,
                "tokens": tokens,
                "active": True
            })
            st.success("Account created 🔥")
            st.session_state.user = db.collection("users").document(uid).get().to_dict()
            st.rerun()

# ================== Login ==================
def login():
    st.subheader("Login")
    email = st.text_input("Email or Admin Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        # Check Admin
        if email == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            st.session_state.user = {"role":"admin","username":"Admin"}
            st.success("Admin logged in 🔥")
            st.rerun()
        else:
            uid = uid_from_email(email)
            doc = db.collection("users").document(uid).get()
            if doc.exists:
                user = doc.to_dict()
                if user["password"] == hash_pass(password):
                    if not user["active"]:
                        st.error("Your account is inactive")
                        return
                    st.session_state.user = user
                    st.success("Logged in 🔥")
                    st.rerun()
                else:
                    st.error("Wrong password")
            else:
                st.error("User not found")

# ================== Dashboard ==================
def dashboard():
    user = st.session_state.user
    st.subheader(f"Welcome {user['username']} ({user['role']})")
    role = user["role"]

    if st.button("Logout"):
        st.session_state.user = None
        st.rerun()

    # ===== Skiller =====
    if role == "skiller":
        st.markdown(f"### Your Tokens: {user.get('tokens',0)} (30 Tokens = 100 جنيه البداية)")
        st.markdown("### Post Your Talent 🎤🎨✍️")
        category = st.selectbox("Category",["Music","Writing","Art","General"])
        content = st.text_area("Describe your talent")
        if st.button("Post Talent"):
            db.collection("posts").add({
                "skiller_id": uid_from_email(user["email"]),
                "category": category,
                "content": content,
                "developer_rating": 5,
                "total_rating": 5
            })
            st.success("Talent Posted 🔥")
            st.rerun()

        st.markdown("---")
        st.markdown(f"### Purchase Tokens 💳 (حول المبلغ على: {PAYMENT_PHONE})")
        package_keys = list(TOKEN_PACKAGES.keys())
        package_values = list(TOKEN_PACKAGES.values())
        selected_idx = st.selectbox("Select Package", range(len(package_keys)), format_func=lambda x: f"{package_keys[x]} جنيه {package_values[x]} tokens")
        phone = st.text_input("Vodafone Cash / InstaPay Number")
        screenshot = st.file_uploader("Upload Screenshot of Transfer", type=["png","jpg","jpeg"])
        if st.button("Submit Payment"):
            if phone and screenshot:
                db.collection("payments").add({
                    "skiller_id": uid_from_email(user["email"]),
                    "phone": phone,
                    "screenshot": screenshot.name,
                    "processed": False,
                    "tokens_to_add": package_values[selected_idx]
                })
                st.success(f"Payment submitted! {package_values[selected_idx]} tokens will be added after admin approval.")
            else:
                st.error("Enter phone and screenshot!")

    # ===== Scout =====
    elif role == "scout":
        st.markdown("### View Talents 🎯")
        cat_filter = st.selectbox("Filter Category",["All","Music","Writing","Art","General"])
        posts = db.collection("posts").stream()
        for p in posts:
            post = p.to_dict()
            if cat_filter != "All" and post["category"] != cat_filter:
                continue
            st.markdown(f"**Category:** {post['category']}")
            st.write(post["content"])
            st.write(f"⭐ Total Rating: {post['total_rating']}")
            rating = st.slider("Your Rating",1,10,key=p.id)
            if st.button("Submit Rating",key=f"rate{p.id}"):
                db.collection("ratings").add({
                    "scout_id": uid_from_email(user.get("email","scout")),
                    "post_id": p.id,
                    "value": rating
                })
                skiller_id = post["skiller_id"]
                skiller_doc = db.collection("users").document(skiller_id).get()
                if skiller_doc.exists:
                    skiller_data = skiller_doc.to_dict()
                    new_tokens = skiller_data.get("tokens",0)+1
                    db.collection("users").document(skiller_id).update({"tokens": new_tokens})
                new_total = (post["total_rating"]+rating)/2
                db.collection("posts").document(p.id).update({"total_rating": new_total})
                st.success("Rated 🔥")
                st.rerun()

    # ===== Admin =====
    elif role == "admin":
        st.markdown("### Admin Panel 👑")
        users = db.collection("users").stream()
        for u in users:
            udata = u.to_dict()
            st.write(f"{udata['username']} ({udata['role']}) - Active: {udata['active']} - Tokens: {udata.get('tokens',0)}")
            if st.button(f"Toggle Active {u.id}",key=u.id):
                db.collection("users").document(u.id).update({"active": not udata["active"]})
                st.success(f"{udata['username']} status toggled")
                st.rerun()

        st.markdown("---")
        st.markdown("### Pending Payments")
        payments = db.collection("payments").where("processed","==",False).stream()
        for p in payments:
            pay = p.to_dict()
            st.write(f"{pay['skiller_id']} sent payment to {pay['phone']} - Screenshot: {pay['screenshot']} - Tokens: {pay['tokens_to_add']}")
            if st.button(f"Approve Payment {p.id}", key=p.id):
                skiller_doc = db.collection("users").document(pay['skiller_id']).get()
                if skiller_doc.exists:
                    skiller_data = skiller_doc.to_dict()
                    db.collection("users"].document(pay['skiller_id']).update({
                        "tokens": skiller_data.get("tokens",0) + pay["tokens_to_add"]
                    })
                db.collection("payments").document(p.id).update({"processed": True})
                st.success(f"Payment Approved: {pay['tokens_to_add']} Tokens added")
                st.rerun()

# ================== Main ==================
if st.session_state.user is None:
    choice = st.radio("Menu",["Login","Sign Up"])
    if choice=="Login":
        login()
    else:
        signup()
else:
    dashboard()
