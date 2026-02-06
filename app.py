import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore, storage
from datetime import datetime
import uuid

# ===========================
# CONFIG
# ===========================
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
TOKEN_PACKAGES = {30: 100, 60: 90, 600: 1500}
CATEGORIES = ["Singing","Acting","Writing","Drawing","Programming","Music","Other"]

# ===========================
# FIREBASE INIT
# ===========================
if not firebase_admin._apps:
    cred = credentials.Certificate(FIREBASE_SERVICE_ACCOUNT)
    firebase_admin.initialize_app(cred, {"storageBucket": STORAGE_BUCKET})

db = firestore.client()
bucket = storage.bucket(STORAGE_BUCKET)

# ===========================
# SESSION STATE DEFAULTS
# ===========================
for key in ["uid","role","logged_in"]:
    if key not in st.session_state:
        st.session_state[key] = None if key!="logged_in" else False

# ===========================
# STYLING
# ===========================
st.markdown("""
<style>
.stApp { background-color:#0b0b10; color:white; }
h1,h2,h3 { color:#c77dff; }
label, p, span { color:white !important; }
button { background:#7b2cbf !important; color:white !important; border-radius:10px; }
input, textarea, select { background:#111 !important; color:white !important; }
</style>
""", unsafe_allow_html=True)

# ===========================
# FUNCTIONS
# ===========================
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

# ===========================
# LOGIN / SIGNUP UI
# ===========================
if not st.session_state.logged_in:
    st.title("TALENT HOUSE")
    tab1, tab2 = st.tabs(["Login","Sign Up"])
    with tab1:
        u = st.text_input("Username", key="login_user")
        p = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            if login(u,p):
                st.session_state.logged_in = True
                st.experimental_rerun()  # ✅ rerun safe after session_state set
            else:
                st.error("Invalid credentials or banned user.")
    with tab2:
        u = st.text_input("New Username", key="signup_user")
        p = st.text_input("New Password", type="password", key="signup_pass")
        r = st.selectbox("Role", ["skiller","scout"], key="signup_role")
        if st.button("Create Account"):
            signup(u,p,r)
            st.success("Account created successfully.")
    st.stop()

# ===========================
# ADMIN PANEL
# ===========================
if st.session_state.role=="admin":
    st.title("Admin Dashboard")
    st.subheader("Users")
    for u in db.collection("users").stream():
        d = u.to_dict()
        col1,col2,col3 = st.co
