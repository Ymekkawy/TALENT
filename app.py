import streamlit as st
from PIL import Image
import firebase_admin
from firebase_admin import credentials, firestore, storage
import base64
import uuid
import datetime

# -------------------- Firebase setup --------------------
firebase_key_dict = {
    "type": "service_account",
    "project_id": "talent-199e5",
    "private_key_id": "f687fdbe55873a2b8a665edc40408a21e9e288ea",
    "private_key": """-----BEGIN PRIVATE KEY-----
MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDUbIiOm6fruwt4
XowfBM0u/Il6FJiUyBCLdSXqcYXOVlA6/Gwd/5OxAIEo/Tp0rX1xyH3OZv5Njuiu
wwZt7PTyeBVbhCYsoIwWVGthneynbV2DIiWobQrsGcFp8vaxGOp0jrS+KkauTWpY
q2QAKlg4VEHQvwttclcTVsatnSsOLtvtA8NUm7AT1SN8sMK14qFquKLfCkaKskBC
/6z0AqhcF3oBr8kANKxKBWssV9oDQ28J+2Lcq7Q9zLxjNGOJ7weeI4e0HVJAIl0f
0b+OjLfL/0XxtFABQlUgl4d68BvYbVi8nuNQHInhXZ5DmUD5w8IkLyjsV73ZB8CR
UBlzjpFPAgMBAAECggEAAYW+As7XYlqgVFGewN6PCk4RpCs/a4DCXmWA18Nn7JjB
kXKoSbZaHIbyGTubYb7k98RMMCCcpCyo7g7qxGEe4X/+OZfJK3SCth3bxfYH5Kx/
FfoDYBSL/MsAdl4Hg5eeOPPVR5Ztx3Q5lcuz3azWatNVXdKIsyICWsEHKOZhkR2K
50xU5jHlmDSatxj47G9K9Z4HGng3IpzM8c9LDyPSU3/h8mYfAknwe0qEgsjnh94o
4QYHnuCLKX9OsQBiCCtjI6CbqKJFmGkRqcLN4smnrEj2HdnYl0XfDbwQR9BLt8wm
JCizze5IOACGZeDwN5q6fcH3J2AWa5aAuOolvPzhGQKBgQD/bat0eImNNVN40xQQ
V/BAg/ELjtEfle5KMt450b2Z+buCXPHVv1X+y8Mgmm3RS4BltOxuA5alLe7pRcMP
3rxYdjQqRc+Fc29I+HZ19TrHbYIFHLjjIdzlJu1t/0kUmI8nvVzTDuqXhttHDYFm
cUq6Q+xqSL1Xq1HfN2NWDTaAtwKBgQDU5jorXSLD7IOsBiosuNlBgJf/sBVlSs5X
EpANk7Njc6HCn08kPv2K3gVbIzXkwtTHZJZDVA9sdSZD4GnXe41RWTwA6qmtCLoD
109FdgjRR9oSHcOJee63NRAs2Aw5EZzuLBcUpr3GKQ0a3+eDCF26KZc3xtgLVevH
LizwWG+sKQKBgHSntrVz04ZtQ1kcNb6dGvmsCKt5p2Kgi/rRLpMDim9HEe8g2cYA
I5tBnjVGsj7zF4nbzlsUQnnf94wMM2ENHcHdAkgIKBXPuZR+/UM0I4svJUGGc54w
Of1iAO/Ktqq0XjUNE9bEqjlX+s+BiIar2TAmk1ObMvZWJQcn+bM0R58TAoGBALOn
X7jODBM211nnjdlVVwfeQuWhqjxipsJ1SJgcZklq/zqjgn48pWl0tyJUERtsiW+E
4wQHwEguh07J5abPfM4Dtg2z9+CrN4UcQKmF1CT+M/gLo8Cz4ww4u+CLo6zYvwuA
qy1jE0tPwt5FyTAadDUu+Ys4wYC3TZIz1fovNnUZAoGBAM+uer4di9d+qe8N+Sxc
nl3jEIvgFlLHIGm6DWvaQ/IrBJLQ39vN/qm+SRXnwbEYHSE1NHJK8lFdEvte4167
s2AgahPiZjG4PLCc6aSdOWyienl8dlUc80G/BUrDCyWiyEG9cX4nPYx5qrPof4qZ
c/TblbNRQugIConFluGP1O/d
-----END PRIVATE KEY-----""",
    "client_email": "firebase-adminsdk-fbsvc@talent-199e5.iam.gserviceaccount.com",
    "client_id": "112925563666280259221",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40talent-199e5.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"
}

cred = credentials.Certificate(firebase_key_dict)
firebase_admin.initialize_app(cred, {'storageBucket': 'talent-199e5.appspot.com'})
db = firestore.client()
bucket = storage.bucket()

# -------------------- Session State --------------------
if 'role' not in st.session_state:
    st.session_state['role'] = None
if 'username' not in st.session_state:
    st.session_state['username'] = None

# -------------------- Design --------------------
st.set_page_config(page_title="TALENT HOUSE", page_icon="🎤", layout="wide", initial_sidebar_state="expanded")
st.markdown("""
    <style>
    body {background-color: #0a0a0a; color: #fff; font-family: 'Arial';}
    .stButton>button {background-color:#8a2be2;color:#fff;border-radius:10px;padding:10px 20px;}
    .stTextInput>div>input {background-color:#1c1c1c;color:#fff;}
    .stFileUploader>div>input {background-color:#1c1c1c;color:#fff;}
    </style>
""", unsafe_allow_html=True)

# -------------------- Login --------------------
st.title("TALENT HOUSE Login")

username = st.text_input("Username")
password = st.text_input("Password", type="password")

if st.button("Login"):
    if username == "dev" and password == "152007poco":
        st.session_state['role'] = "admin"
        st.session_state['username'] = "dev"
        st.success("Logged in as Admin!")
    elif username and password:
        # check Firestore users collection
        user_doc = db.collection("users").document(username).get()
        if user_doc.exists and user_doc.to_dict()['password'] == password:
            st.session_state['role'] = user_doc.to_dict()['role']
            st.session_state['username'] = username
            st.success(f"Logged in as {st.session_state['role'].capitalize()}")
        else:
            st.error("Invalid credentials!")

# -------------------- Admin Dashboard --------------------
if st.session_state['role'] == "admin":
    st.header("Admin Dashboard")
    st.subheader("Users")
    users = db.collection("users").stream()
    for user in users:
        u = user.to_dict()
        st.write(f"{u['username']} - {u['role']} - Tokens: {u.get('tokens',0)}")
        if st.button(f"Ban {u['username']}"):
            db.collection("users").document(u['username']).update({"banned": True})

    st.subheader("Payment Requests")
    payments = db.collection("payments").stream()
    for pay in payments:
        p = pay.to_dict()
        st.write(f"User: {p['skiller_id']} Amount: {p['amount']}")
        st.image(p['screenshot'])
        if st.button(f"Approve {p['skiller_id']}"):
            db.collection("users").document(p['skiller_id']).update({"tokens": p['amount']//10}) # example
            db.collection("payments").document(pay.id).update({"status":"approved"})

# -------------------- Skiller / Scout --------------------
if st.session_state['role'] in ["skiller","scout"]:
    st.header(f"{st.session_state['role'].capitalize()} Dashboard")
    if st.session_state['role'] == "skiller":
        st.subheader("Upload your talent")
        uploaded_file = st.file_uploader("Image or Video", type=["png","jpg","jpeg","mp4"])
        category = st.selectbox("Category", ["Singing","Writing","General","Other"])
        description = st.text_area("Description (optional)")
        if uploaded_file:
            blob = bucket.blob(f"{uuid.uuid4()}_{uploaded_file.name}")
            blob.upload_from_file(uploaded_file)
            url = blob.public_url
            db.collection("posts").add({
                "user": st.session_state['username'],
                "file_url": url,
                "category": category,
                "description": description,
                "timestamp": datetime.datetime.now(),
                "rating": 0
            })
            st.success("Talent uploaded!")
    elif st.session_state['role'] == "scout":
        st.subheader("Talent Feed")
        posts = db.collection("posts").order_by("rating", direction=firestore.Query.DESCENDING).stream()
        for post in posts:
            p = post.to_dict()
            st.write(f"Category: {p['category']} | Description: {p.get('description','')}")
            if p['file_url'].endswith(("png","jpg","jpeg")):
                st.image(p['file_url'])
            else:
                st.video(p['file_url'])
            rating = st.slider(f"Rate {p['user']}", 0, 5, 0)
            if st.button(f"Submit Rating for {p['user']}"):
                db.collection("posts").document(post.id).update({"rating": rating})
