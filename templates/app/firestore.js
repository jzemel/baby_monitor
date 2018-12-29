firebase.initializeApp({
	apiKey: "AIzaSyAF0vHKLHxCy9WGbJfTqf2yhCJuuwsWcHw",
	authDomain: "babypi-jz.firebaseapp.com",
	projectId: "babypi-jz"
});

// Initialize Cloud Firestore through Firebase
var db = firebase.firestore();

// Disable deprecated features
db.settings({
  timestampsInSnapshots: true
});

print(db.collection("tlm").get());