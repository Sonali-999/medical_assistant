import pyrebase

firebaseConfig = {
  "apiKey": "AIzaSyCDD4VWOfdgtXMnqjVQnhJLg_Jlm9psJfM",
  "authDomain": "medical-assistant-d6b7f.firebaseapp.com",
  "projectId": "medical-assistant-d6b7f",
  "storageBucket": "medical-assistant-d6b7f.firebasestorage.app",
  "messagingSenderId": "338252346051",
  "appId": "1:338252346051:web:a81fbdefd8df7d43ece876",
  "measurementId": "G-NN2E1RFNQK",
  "databaseURL": ""
}
firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()