-- Posts table: blog articles and long-form content
CREATE TABLE IF NOT EXISTS posts (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  slug        TEXT NOT NULL UNIQUE,
  title       TEXT NOT NULL,
  subtitle    TEXT,
  body_html   TEXT NOT NULL,
  summary     TEXT,
  topic_slug  TEXT,
  author      TEXT DEFAULT 'GreenCompute Editorial',
  status      TEXT DEFAULT 'draft',   -- 'draft' | 'published'
  published_at TEXT,                  -- ISO 8601 string
  created_at  TEXT DEFAULT (datetime('now')),
  updated_at  TEXT DEFAULT (datetime('now'))
);

-- Topics: category taxonomy
CREATE TABLE IF NOT EXISTS topics (
  id        INTEGER PRIMARY KEY AUTOINCREMENT,
  slug      TEXT NOT NULL UNIQUE,
  title     TEXT NOT NULL,
  description TEXT,
  color_hex TEXT DEFAULT '#2d6a4f'
);

-- Contact form submissions
CREATE TABLE IF NOT EXISTS contact_submissions (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  name       TEXT,
  email      TEXT NOT NULL,
  subject    TEXT,
  message    TEXT NOT NULL,
  source_url TEXT,
  created_at TEXT DEFAULT (datetime('now'))
);

-- Seed topics
INSERT OR IGNORE INTO topics (slug, title, description) VALUES
  ('cooling', 'Cooling Technology', 'Liquid cooling, free-air systems, and thermal management'),
  ('energy', 'Energy Sources', 'Nuclear baseload, renewables, and clean power grids'),
  ('regulations', 'Policy & Regulations', 'Government mandates, PUE standards, and ESG frameworks'),
  ('facilities', 'Facility Design', 'Data center construction, location selection, and infrastructure');
