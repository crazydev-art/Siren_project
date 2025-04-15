require("dotenv").config();
const express = require("express");
const cors = require("cors");

const app = express();
app.use(cors());
app.use(express.json());

// Import des routes
const searchRoutes = require("./routes/search");
const mapsRoutes = require("./routes/maps");

app.use("/api/search", searchRoutes);
app.use("/api/maps", mapsRoutes);

app.listen(5000, () => {
  console.log("✅ Serveur backend lancé sur http://localhost:5000");
});
