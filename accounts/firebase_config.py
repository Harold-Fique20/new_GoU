import pyrebase

config = {
    'apiKey': 'AIzaSyBeBvJvQm9o9tOtzCoMPcs2UeJvnrbO-yM',
    'authDomain': 'gou-adm.firebaseapp.com',
    "databaseURL": 'firebase-adminsdk-3hxpk@gou-adm.iam.gserviceaccount.com',
    'projectId': 'gou-adm',
    'storageBucket': 'gou-adm.appspot.com',
    'messagingSenderId': '909645328534',
    'appId': '1:909645328534:web:ef4322959f52e7a99452b7',
    'measurementId': 'G-1N1SH62VZV',
}
firebase= pyrebase.initialize_app(config)
auth = firebase.auth()
database=firebase.database()
