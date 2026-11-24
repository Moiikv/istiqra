// Express server: serves /public and a small JSON API.
// Later: replace readJson() with database queries and add POST routes (contact form, admin, ...).
const express = require("express");
const fs = require("fs");
const path = require("path");

const app = express();
app.use(express.json());

const DATA_DIR = path.join(__dirname, "public", "data");
const readJson = (name) => JSON.parse(fs.readFileSync(path.join(DATA_DIR, name), "utf8"));

app.get("/api/portfolio", (req, res) => res.json(readJson("portfolio.json")));
app.get("/api/projects/olist", (req, res) => res.json(readJson("olist.json")));
app.get("/api/olist", (req, res) => res.json(readJson("olist.json")));
app.get("/api/projects/:id", (req, res) => { const id = String(req.params.id); if (!/^[a-z0-9_]+$/.test(id) || !fs.existsSync(path.join(DATA_DIR, id + ".json"))) return res.status(404).json({ error: "not found" }); res.json(readJson(id + ".json")); });
app.get("/api/olist-profile", (req, res) => res.json(readJson("olist_profile.json")));

app.use(express.static(path.join(__dirname, "public"), { extensions: ["html"] }));

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Istiqra running on http://localhost:${PORT}`));
