import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import hashlib

# ================== Firebase Init ==================
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_key.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

# ================== Streamlit Config ==================
st.set_page_config(page_title="TALENT HOUSE", page_icon="🔥")
st.markdown("""
<style>
body { background-color:#0a041a; color:white; }
.stButton button { background:#a855f7; color:white; }
textarea, input, select { background:#14082f; color:white; border:1px solid #a855f7; }
</style>
""", unsafe_allow_html=True)

# ================== Session ==================
if "user" not in st.session_state:
    st.session_state.user = None

# ================== Helpers ==================
def hash_pass(p):
    return hashlib.sha256(p.encode()).hexdigest()

def uid_from_email(email):
    return email.replace("@", "_").replace(".", "_")

# ================== Signup ==================
def signup():
    st.subheader("Sign Up")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    username = st.text_input("Username")
    role = st.selectbox("Role", ["scout", "skiller"])

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
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
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

    # -------- Logout ---------
    if st.button("Logout"):
        st.session_state.user = None
        st.rerun()

    # ================== Skiller ==================
    if role == "skiller":
        st.markdown(f"### Your Tokens: {user['tokens']} (30 Tokens = 100 جنيه بداية)")
        st.markdown("### Post Your Talent 🎤🎨✍️")
        category = st.selectbox("Category", ["Music", "Writing", "Art", "General"])
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
        st.markdown("### Purchase Tokens 💳")
        st.write("اختر باقة التوكنز:")
        packages = {
            "30 Tokens = 100 جنيه": 30,
            "60 Tokens = 180 جنيه": 60,
            "600 Tokens = 1500 جنيه": 600
        }
        selected_package = st.selectbox("Choose Token Package", list(packages.keys()))
        tokens_to_add = packages[selected_package]

        phone = st.text_input("Vodafone Cash / InstaPay Number")
        screenshot = st.file_uploader("Upload Screenshot of Transfer", type=["png","jpg","jpeg"])

        if st.button("Submit Payment"):
            if phone and screenshot:
                db.collection("payments").add({
                    "skiller_id": uid_from_email(user["email"]),
                    "phone": phone,
                    "screenshot": screenshot.name,
                    "processed": False,
                    "tokens_to_add": tokens_to_add
                })
                st.success(f"Payment Submitted! {tokens_to_add} Tokens will be added after Admin approval.")
            else:
                st.error("Please enter phone number and upload screenshot.")

    # ================== Scout ==================
    elif role == "scout":
        st.markdown("### View Talents 🎯")
        category_filter = st.selectbox("Filter Category", ["All", "Music", "Writing", "Art", "General"])
        posts = db.collection("posts").stream()

        for p in posts:
            post = p.to_dict()
            if category_filter != "All" and post["category"] != category_filter:
                continue

            st.markdown(f"**Category:** {post['category']}")
            st.write(post["content"])
            st.write(f"⭐ Total Rating: {post['total_rating']}")

            rating = st.slider("Your Rating", 1, 10, key=p.id)
            if st.button("Submit Rating", key=f"rate{p.id}"):
                db.collection("ratings").add({
                    "scout_id": uid_from_email(user["email"]),
                    "post_id": p.id,
                    "value": rating
                })
                # إضافة token للSkiller
                skiller_id = post["skiller_id"]
                skiller_doc = db.collection("users").document(skiller_id).get()
                if skiller_doc.exists:
                    skiller_data = skiller_doc.to_dict()
                    new_tokens = skiller_data.get("tokens",0) + 1
                    db.collection("users").document(skiller_id).update({"tokens": new_tokens})

                new_total = (post["total_rating"] + rating)/2
                db.collection("posts").document(p.id).update({"total_rating": new_total})
                st.success("Rated 🔥")
                st.rerun()

    # ================== Admin ==================
    elif role == "admin":
        st.markdown("### Admin Panel 👑")
        users = db.collection("users").stream()
        for u in users:
            udata = u.to_dict()
            st.write(f"{udata['username']} ({udata['role']}) - Active: {udata['active']} - Tokens: {udata.get('tokens',0)}")
            if st.button(f"Toggle Active {u.id}", key=u.id):
                db.collection("users").document(u.id).update({
                    "active": not udata["active"]
                })
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
                    db.collection("users").document(pay['skiller_id']).update({
                        "tokens": skiller_data.get("tokens",0) + pay["tokens_to_add"]
                    })
                db.collection("payments").document(p.id).update({"processed": True})
                st.success(f"Payment Approved: {pay['tokens_to_add']} Tokens added")
                st.rerun()

# ================== Main ==================
if st.session_state.user is None:
    choice = st.radio("Menu", ["Login", "Sign Up"])
    if choice == "Login":
        login()
    else:
        signup()
else:
    dashboard()
