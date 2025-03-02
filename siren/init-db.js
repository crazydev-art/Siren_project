// init-db.js
db = db.getSiblingDB('siren'); // Switch to the 'siren' database
db.createCollection('test');   // Create the 'test' collection
