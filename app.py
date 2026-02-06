import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore, storage
from datetime import datetime
import uuid

# ==================================================
# CONFIGURATION
# ==================================================
ADMIN_USERNAME = "dev"
ADMIN_PASSWORD = "152007poco"

FIREBASE_SERVICE_ACCOUNT = {
  "type": "service_account",
  "project_id": "talent-199e5",
  "private_key_id": "f687fdbe55873a2b8a665edc40408a21e9e288ea",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDUbIiOm6fruwt4\nXowfBM0u/Il6FJiUyBCLdSXqcYXOVlA6/Gwd/5OxAIEo/Tp0rX1xyH3OZv5Njuiu\nwwZt7PTyeBVbhCYsoIwWVGthneynbV2DIiWobQrsGcFp8vaxGOp0jrS+KkauTWpY\nq2QAKlg4VEHQvwttclcTVsatnSsOLtvtA8NUm7AT1SN8sMK14qFquKLfCkaKskBC\n/6z0AqhcF3oBr8kANKxKBWssV9oDQ28J+2Lcq7Q9zLxjNGOJ7weeI4e0HVJAIl0f\n0b+OjLfL/0XxtFABQlUgl4d68BvYbVi8nuNQHInhXZ5DmUD5w8IkLyjsV73ZB8CR\nUBlzjpFPAgMBAAECggEAAYW+As7XYlqgVFGewN6PCk4RpCs/a4DCXmWA18Nn7JjB\nkXKoSbZaHIbyGTubYb7k98RMMCCcpCyo7g7qxGEe4X/+OZfJK3SCth3bxfYH5Kx/\nFfoDYBSL/MsAdl4Hg5eeOPPVR5Ztx3Q5lcuz3azWatNVXdKIsyICWsEHKOZhkR2K\n50xU5jHlmDSatxj47G9K9Z4HGng3IpzM8c9LDyPSU3/h8mYfAknwe0qEgsjnh94o\n4QYHnuCLKX9OsQBiCCtjI6CbqKJFmGkRqcLN4smnrEj2HdnYl0XfDbwQR9BLt8wm\nJCizze5IOACGZeDwN5q6fcH3J2AWa5aAuOolvPzhGQKBgQD/bat0eImNNVN40xQQ\nV/BAg/ELjtEfle5KMt450b2Z+buCXPHVv1X+y8Mgmm3RS4BltOxuA5alLe7pRcMP\n3rxYdjQqRc+Fc29I+HZ19TrHbYIFHLjjIdzlJu1t/0kUmI8nvVzTDuqXhttHDYFm\ncUq6Q+xqSL1Xq1HfN2NWDTaAtwKBgQDU5jorXSLD7IOsBiosuNlBgJf/sBVlSs5X\nEpANk7Njc6HCn08kPv2K3gVbIzXkwtTHZJZDVA9sdSZD4GnXe41RWTwA6qmtCLoD\n109FdgjRR9oSHcOJee63NRAs2Aw5EZzuLBcUpr3GKQ0a3+eDCF26KZc3xtgLVevH\nLizwWG+sKQKBgHSntrVz04ZtQ1kcNb6dGvmsCKt5p2Kgi/rRLpMDim9HEe8g2cYA\nI5tBnjVGsj7zF4nbzlsUQnnf94wMM2ENHcHdAkgIKBXPuZR+/UM0I4svJUGGc54w\nOf1iAO/Ktqq0XjUNE9bEqjlX+s+BiIar2TAmk1ObMvZWJQcn+bM0R58TAoGBALOn\nX7jODBM211nnjdlVVwfeQuWhqjxipsJ1SJgcZklq/zqjgn48pWl0tyJUERtsiW+E\n4wQHwEguh07J5abPfM4Dtg2z9+CrN4UcQKmF1CT+M/gLo8Cz4ww4u+CLo6zYvwuA\nqy1jE0tPwt5FyTAadDUu+Ys4wYC3TZIz1fovNnUZAoGBAM+uer4di9d+qe8N+Sxc\nnl3jEIvgFlLHIGm6DWvaQ/IrBJLQ39vN/qm+SRXnwbEYHSE1NHJK8lFdEvte4167\ns2AgahPiZjG4PLCc6aSdOWyienl8dlUc80G/BUrDCyWiyEG9cX4nPYx5qrPof4qZ\nc/TblbNRQugIConFluGP1O/d\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-fbsvc@talent-199e5.iam.gserviceaccount.com",
  "client_id": "112925563666280259221",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40talent-199e5.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}


STORAGE_BUCKET = "talent-199e5.appspot.com"
PAYMENT_NUMBER = "01000004397"
TOKEN_PACKAGES = {30: 100, 60: 90, 600: 1500}  # tokens: price
CATEGORIES = ["Singing","Acting","Writing","Drawing","Programming","Music","Other"]

# ==================================================
# FIREBASE INIT
# ==================================================
if not firebase_admin._apps:
    cred = credentials.Certificate(FIREBASE_SERVICE_ACCOUNT)
    firebase_admin.initialize_app(cred, {"storageBucket": STORAGE_BUCKET})

db = firestore.client()
bucket = storage.bucket(STORAGE_BUCKET)

# ==================================================
# SESSION STATE DEFAULTS
# ==================================================
if "uid" not in st.session_state:
    st.session_state.uid = None
if "role" not in st.session_state:
    st.session_state.role = None
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ==================================================
# STYLING
# ==================================================
st.markdown("""
<style>
.stApp { background-color:#0b0b10; color:white; }
h1,h2,h3 { color:#c77dff; }
label, p, span { color:white !important; }
button { background:#7b2cbf !important; color:white !important; border-radius:10px; }
input, textarea, select { background:#111 !important; color:white !important; }
</style>
""", unsafe_allow_html=True)

# ==================================================
# LOGIN / SIGNUP FUNCTIONS
# ==================================================
def login(username, password):
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        st.session_state.uid = "ADMIN"
        st.session_state.role = "admin"
        return True

    users = db.collection("users").where("username","==",username).stream()
    for u in users:
        d = u.to_dict()
        if d["password"] == password and not d.get("banned", False):
            st.session_state.uid = u.id
            st.session_state.role = d["role"]
            return True

    st.session_state.uid = None
    st.session_state.role = None
    return False

def signup(username, password, role):
    db.collection("users").add({
        "username": username,
        "password": password,
        "role": role,
        "tokens": 30 if role=="skiller" else 0,
        "banned": False,
        "created": datetime.utcnow()
    })

# ==================================================
# LOGIN / SIGNUP UI
# ==================================================
if not st.session_state.logged_in:
    st.title("TALENT HOUSE")
    tab1, tab2 = st.tabs(["Login","Sign Up"])

    with tab1:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Login"):
            success = login(u,p)
            if success:
                st.session_state.logged_in = True
                st.experimental_rerun()
            else:
                st.error("Invalid credentials or banned user.")

    with tab2:
        u = st.text_input("New Username")
        p = st.text_input("New Password", type="password")
        r = st.selectbox("Role", ["skiller","scout"])
        if st.button("Create Account"):
            signup(u,p,r)
            st.success("Account created successfully.")
    st.stop()

# ==================================================
# ADMIN PANEL
# ==================================================
if st.session_state.role=="admin":
    st.title("Admin Dashboard")

    st.subheader("Users")
    for u in db.collection("users").stream():
        d = u.to_dict()
        col1,col2,col3 = st.columns([3,2,2])
        col1.write(f"{d['username']} ({d['role']})")
        col2.write(f"Tokens: {d.get('tokens',0)}")
        if col3.button("BAN",key=u.id):
            db.collection("users").document(u.id).update({"banned":True})

    st.subheader("Posts – Admin Ratings")
    for p in db.collection("posts").stream():
        d = p.to_dict()
        if d["media_url"].endswith(("mp4")):
            st.video(d["media_url"])
        else:
            st.image(d["media_url"])
        st.write(d.get("description",""))
        rating = st.slider("Admin Rating",0,10,d.get("admin_rating",0),key=f"admin_{p.id}")
        if st.button("Save Rating",key=f"save_{p.id}"):
            db.collection("posts").document(p.id).update({"admin_rating":rating})

    st.subheader("Payment Requests")
    for r in db.collection("payments").stream():
        d = r.to_dict()
        st.write(f"User: {d['user']} | Tokens: {d['tokens']} | Price: {d['price']} EGP")
        st.image(d["screenshot"])
        if st.button("Approve",key=r.id):
            db.collection("users").document(d["user"]).update({"tokens":firestore.Increment(d["tokens"])})
            db.collection("payments").document(r.id).delete()
    st.stop()

# ==================================================
# SKILLER PANEL
# ==================================================
if st.session_state.role=="skiller":
    st.title("Skiller Panel")
    media = st.file_uploader("Upload Image or Video", type=["png","jpg","mp4"])
    desc = st.text_area("Description (optional)")
    cat = st.selectbox("Category", CATEGORIES)

    if st.button("Post Talent") and media:
        pid = str(uuid.uuid4())
        blob = bucket.blob(pid)
        blob.upload_from_file(media)
        blob.make_public()
        db.collection("posts").add({
            "user": st.session_state.uid,
            "media_url": blob.public_url,
            "description": desc,
            "category": cat,
            "admin_rating": 0,
            "created": datetime.utcnow()
        })

    st.subheader("Buy Tokens")
    pack = st.selectbox("Choose Package", list(TOKEN_PACKAGES.keys()))
    proof = st.file_uploader("Payment Screenshot", type=["png","jpg"])
    if st.button("Send Payment") and proof:
        rid = str(uuid.uuid4())
        b = bucket.blob(f"payments/{rid}")
        b.upload_from_file(proof)
        b.make_public()
        db.collection("payments").add({
            "user": st.session_state.uid,
            "tokens": pack,
            "price": TOKEN_PACKAGES[pack],
            "screenshot": b.public_url,
            "number": PAYMENT_NUMBER,
            "created": datetime.utcnow()
        })

# ==================================================
# SCOUT PANEL
# ==================================================
if st.session_state.role == "scout":
    st.title("Scout Panel")
    flt = st.selectbox("Filter by Category", ["All"] + CATEGORIES)

    for p in db.collection("posts").order_by("admin_rating", direction=firestore.Query.DESCENDING).stream():
        d = p.to_dict()
        if flt != "All" and d["category"] != flt:
            continue

        if d["media_url"].endswith(("mp4")):
            st.video(d["media_url"])
        else:
            st.image(d["media_url"])

        st.write(d.get("description",""))
        st.write(f"Category: {d['category']}")

        key_name = f"scout_rating_{p.id}"
        if key_name not in st.session_state:
            st.session_state[key_name] = 0

        score = st.slider("Your Rating", 0, 10, st.session_state[key_name], key=key_name)
        st.session_state[key_name] = score

        if st.button("Submit Rating", key=f"rate_{p.id}"):
            db.collection("posts").document(p.id).update({"scout_rating": score})
            st.success("Rating submitted!")
