import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("/home/suraj/Downloads/car-parking-83ea3-firebase-adminsdk-6ookb-ec3c13f53e.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

def update_parking(label, hasVehicle):

    docs = db.collection('parkdata').stream()

    for doc in docs:
        data = doc.to_dict()
        if data["label"] == label:
            doc_ref = db.collection('parkdata').document(doc.id)
            doc_ref.update({"hasVehicle": hasVehicle})
