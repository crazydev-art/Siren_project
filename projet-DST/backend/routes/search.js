const express = require("express");
const pool = require("../db");
const router = express.Router();

router.get("/", async (req, res) => {
  let { query, type } = req.query;

  if (!query) {
    return res.status(400).json({ error: "Veuillez entrer un terme de recherche." });
  }

  console.log("🔍 Requête reçue avec :", { query, type });

  try {
    let sql = `
      SELECT u.siren, u.denominationunitelegale, 
             e.siret, 
             TRIM(REPLACE(e.activiteprincipaleetablissement, ' ', '')) AS activiteprincipaleetablissement, 
             a.libellecommuneetablissement, 
             n.nafvfinale AS activite_nom
      FROM unitelegale u
      LEFT JOIN etablissement e ON TRIM(u.siren) = TRIM(e.siren)
      LEFT JOIN staging_adresse a ON TRIM(e.siret) = TRIM(a.siret)
      LEFT JOIN nafv2 n ON TRIM(e.activiteprincipaleetablissement) = TRIM(n.codenaf)
    `;

    let values = [];

    if (type === "siren") {
      sql += ` WHERE u.siren LIKE $1 OR e.siret LIKE $1`;
      values.push(`%${query}%`);
    } else if (type === "name") {
      sql += ` WHERE u.denominationunitelegale ILIKE $1 OR e.denominationusuelleetablissement ILIKE $1`;
      values.push(`%${query}%`);
    } else if (type === "activity") {
      query = query.replace("/", ".").trim(); // 🔥 Remplacement et suppression d'espaces
      sql += `
        WHERE TRIM(REPLACE(e.activiteprincipaleetablissement, ' ', '')) ILIKE $1
        OR TRIM(REPLACE(n.codenaf, ' ', '')) ILIKE $1
        OR n.nafvfinale ILIKE $1
      `;
      values.push(`%${query}%`);
    }

    sql += ` LIMIT 20;`;

    console.log("🔎 Requête SQL exécutée :", sql);
    console.log("🔎 Valeurs utilisées :", values);

    const results = await pool.query(sql, values);
    console.log("📊 Résultats SQL renvoyés :", results.rows.length, "entreprises trouvées.");
    console.log("📊 Données brutes retournées par PostgreSQL :", results.rows);

    res.json(results.rows);
  } catch (error) {
    console.error("❌ Erreur SQL :", error);
    res.status(500).json({ error: "Erreur serveur" });
  }
});

module.exports = router;
