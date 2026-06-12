#!/usr/bin/env node
/**
 * Seed de MongoDB para PREVIEWS EFÍMEROS de Neo (datos sintéticos).
 *
 * Copiá este script al repo de la API (api_portal_cliente) e invocalo cuando se levanta el
 * environment de preview del PR (ver docs/neo/README.md → "Previews en Railway").
 *
 * GUARDARRAÍL (criterio de aceptación "previews nunca conectados a bases productivas"):
 *   - Solo corre si NEO_PREVIEW === "true"  (se setea SOLO en environments de preview).
 *   - Aborta si la URL de Mongo apunta a un host/db de la lista de producción
 *     (NEO_PROD_DB_DENYLIST, coma-separada) o si el nombre de la base contiene "prod".
 *   - Marca todo lo insertado con _synthetic:true y origin:"neo-seed".
 *
 * Uso:
 *   MONGO_URL=mongodb://... NEO_PREVIEW=true node seed-mongo.js
 *
 * Requiere el paquete `mongodb` (ver package.json de esta carpeta).
 */
const MONGO_URL = process.env.MONGO_URL || process.env.MONGODB_URI || process.env.DATABASE_URL;
const IS_PREVIEW = String(process.env.NEO_PREVIEW || "").toLowerCase() === "true";
const DENYLIST = (process.env.NEO_PROD_DB_DENYLIST || "")
  .split(",")
  .map((s) => s.trim().toLowerCase())
  .filter(Boolean);

function fail(msg) {
  console.error(`✖ seed abortado: ${msg}`);
  process.exit(1);
}

function assertEphemeral(url) {
  if (!IS_PREVIEW) {
    fail("NEO_PREVIEW !== 'true'. Este seed solo corre en previews efímeros.");
  }
  if (!url) {
    fail("falta MONGO_URL / MONGODB_URI.");
  }
  const lower = url.toLowerCase();
  for (const needle of DENYLIST) {
    if (lower.includes(needle)) {
      fail(`la URL coincide con la denylist de producción ("${needle}").`);
    }
  }
  // Heurística extra: nombre de base que parezca productivo.
  const dbName = dbNameFromUrl(url);
  if (/prod|produccion|producción|live/.test(dbName.toLowerCase())) {
    fail(`el nombre de base "${dbName}" parece productivo.`);
  }
  return dbName;
}

function dbNameFromUrl(url) {
  try {
    // mongodb://host:port/dbname?opts  → dbname
    const afterSlash = url.split("/").pop() || "";
    return decodeURIComponent(afterSlash.split("?")[0] || "preview");
  } catch {
    return "preview";
  }
}

// ── Datos sintéticos (obviamente falsos) ───────────────────────────────────────
const NOW = new Date();
const tag = { _synthetic: true, origin: "neo-seed", seededAt: NOW };

const usuarios = Array.from({ length: 8 }, (_, i) => ({
  ...tag,
  nombre: `Usuario Demo ${i + 1}`,
  email: `demo${i + 1}@preview.local`,
  rol: i === 0 ? "admin" : "cliente",
  activo: true,
}));

const clientes = Array.from({ length: 12 }, (_, i) => ({
  ...tag,
  razonSocial: `Cliente Sintético S.A. ${i + 1}`,
  cuit: `30-0000000${(i % 10)}-${i % 10}`,
  estado: ["activo", "pendiente", "suspendido"][i % 3],
}));

const facturas = Array.from({ length: 20 }, (_, i) => ({
  ...tag,
  numero: `FAC-PRE-${String(1000 + i)}`,
  total: Math.round(1000 + i * 137.5),
  moneda: "ARS",
  pagada: i % 2 === 0,
}));

const COLLECTIONS = { usuarios, clientes, facturas };

async function main() {
  // Guardarraíl PRIMERO, antes de cargar el driver: si no es un preview, ni lo intentamos.
  const dbName = assertEphemeral(MONGO_URL);
  const { MongoClient } = require("mongodb");
  const client = new MongoClient(MONGO_URL);
  await client.connect();
  const db = client.db(dbName);
  console.log(`→ Seed de datos sintéticos en base "${dbName}" (preview)…`);

  for (const [name, docs] of Object.entries(COLLECTIONS)) {
    const col = db.collection(name);
    // Idempotente: borra SOLO lo sintético previo, no toca datos ajenos.
    await col.deleteMany({ origin: "neo-seed" });
    await col.insertMany(docs);
    console.log(`  ✓ ${name}: ${docs.length} documentos`);
  }

  await client.close();
  console.log("✔ Seed completo.");
}

main().catch((err) => fail(err.message));
