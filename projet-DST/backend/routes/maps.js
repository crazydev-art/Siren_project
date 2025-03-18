const express = require("express");
const pool = require("../db");
const router = express.Router();

router.get("/", async (req, res) => {
  const { lat, lon, radius, activity } = req.query;
  console.log("📥 Requête reçue avec :", { lat, lon, radius, activity });

  try {
    let sql = `
      SELECT e.denominationusuelleetablissement, 
             e.activiteprincipaleetablissement, 
             n.nafvfinale AS activite_nom, 
             g.siret, g.x_longitude, g.y_latitude
      FROM geolocalisation g
      JOIN etablissement e ON g.siret = e.siret
      LEFT JOIN nafv2 n ON e.activiteprincipaleetablissement = n.codenaf
      WHERE (g.x_longitude BETWEEN $1 - 0.15 AND $1 + 0.15)
      AND (g.y_latitude BETWEEN $2 - 0.15 AND $2 + 0.15)
    `;

    let values = [parseFloat(lon), parseFloat(lat)];

    // Ajouter le filtre d'activité si fourni
    if (activity) {
      sql += ` AND e.activiteprincipaleetablissement = $3`;
      values.push(activity);
    }

    sql += ` LIMIT 50;`;
	console.log("🔎 Valeurs SQL utilisées :", values);

    const results = await pool.query(sql, values);
	console.log("📊 Résultats SQL renvoyés :", results.rows.length, "entreprises trouvées.");
    res.json(results.rows);

  } catch (error) {
    console.error("❌ Erreur SQL :", error);
    res.status(500).json({ error: "Erreur serveur" });
  }
});

module.exports = router;