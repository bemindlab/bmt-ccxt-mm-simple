import logging


def init_firebase_admin():
    """Initialize the Firebase Admin SDK."""
    try:
        import firebase_admin
        from firebase_admin import credentials

        # Initialize Firebase Admin SDK
        cred = credentials.Certificate("configs/firebase-admin.json")
        firebase_admin.initialize_app(cred)
    except Exception as e:
        logging.error(f"Error initializing Firebase Admin SDK: {e}")
        return None

    return firebase_admin


def get_firestore_client():
    """Get the Firestore client."""
    try:

        from firebase_admin import firestore

        # Get Firestore client
        db = firestore.client()
    except Exception as e:
        logging.error(f"Error getting Firestore client: {e}")
        return None

    return db


def get_firestore_collection(db, collection_name):
    """Get a Firestore collection."""
    try:
        collection = db.collection(collection_name)
    except Exception as e:
        logging.error(f"Error getting Firestore collection: {e}")
        return None

    return collection


def add_document_to_collection(collection, data):
    """Add a document to a Firestore collection."""
    try:
        doc_ref = collection.add(data)
    except Exception as e:
        logging.error(f"Error adding document to Firestore collection: {e}")
        return None

    return doc_ref
