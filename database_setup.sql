-- ============================================================
-- GestRes Pro — Base de données PostgreSQL
-- BTS SIO SLAM — CAMARA Ibrahim — 2026
-- ============================================================
-- Architecture client-serveur, schéma complet :
--   1. Création de l'utilisateur dédié et de la base
--   2. Schéma relationnel avec contraintes d'intégrité
--   3. Index de performance
--   4. Vues métier (tableaux de bord, rapports)
--   5. Fonctions PL/pgSQL (RGPD, statistiques)
--   6. Triggers (audit automatique, cohérence des statuts)
--   7. Données initiales (rôles, super administrateur)
-- ============================================================


-- ============================================================
-- ÉTAPE 1 — UTILISATEUR ET BASE
-- (à exécuter en tant que superuser PostgreSQL)
-- ============================================================

-- Supprimer si re-création complète
-- DROP DATABASE IF EXISTS gestres_pro;
-- DROP USER IF EXISTS gestres_user;

CREATE USER gestres_user
    WITH PASSWORD 'GestRes2026!Secure'
    NOSUPERUSER
    NOCREATEDB
    NOCREATEROLE
    LOGIN;

CREATE DATABASE gestres_pro
    OWNER     gestres_user
    ENCODING  'UTF8'
    LC_COLLATE 'fr_FR.UTF-8'
    LC_CTYPE   'fr_FR.UTF-8'
    TEMPLATE  template0
    CONNECTION LIMIT 50;

COMMENT ON DATABASE gestres_pro IS
    'GestRes Pro — Gestion des ressources entreprise — BTS SIO SLAM 2026';

-- Se connecter à gestres_pro avant d'exécuter la suite :
-- \c gestres_pro

GRANT CONNECT ON DATABASE gestres_pro TO gestres_user;


-- ============================================================
-- ÉTAPE 2 — TABLES
-- ============================================================

-- ------------------------------------------------------------
-- 2.1  Rôles utilisateurs
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS roles (
    id          SERIAL       PRIMARY KEY,
    name        VARCHAR(50)  NOT NULL UNIQUE,
    permissions TEXT,
    CONSTRAINT chk_roles_name CHECK (name IN ('super_admin', 'admin', 'employee'))
);

COMMENT ON TABLE  roles IS 'Rôles système : super_admin, admin, employee';
COMMENT ON COLUMN roles.permissions IS 'JSON : liste des permissions accordées';


-- ------------------------------------------------------------
-- 2.2  Entreprises (espaces cloisonnés)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS companies (
    id         SERIAL        PRIMARY KEY,
    name       VARCHAR(100)  NOT NULL,
    siret      VARCHAR(14)   UNIQUE,
    address    TEXT,
    created_at TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    is_active  BOOLEAN       NOT NULL DEFAULT TRUE,
    CONSTRAINT chk_companies_siret CHECK (siret IS NULL OR siret ~ '^\d{14}$')
);

COMMENT ON TABLE companies IS 'Espaces entreprise cloisonnés';


-- ------------------------------------------------------------
-- 2.3  Utilisateurs
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id            SERIAL        PRIMARY KEY,
    email         VARCHAR(100)  NOT NULL UNIQUE,
    password_hash VARCHAR(255)  NOT NULL,
    first_name    VARCHAR(50),
    last_name     VARCHAR(50),
    role_id       INTEGER       NOT NULL REFERENCES roles(id),
    company_id    INTEGER       REFERENCES companies(id),
    is_active     BOOLEAN       NOT NULL DEFAULT TRUE,
    created_at    TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    last_login    TIMESTAMPTZ,
    CONSTRAINT chk_users_email CHECK (email ~ '^[^@]+@[^@]+\.[^@]+$')
);

COMMENT ON TABLE  users IS 'Utilisateurs de l''application';
COMMENT ON COLUMN users.password_hash IS 'Mot de passe haché bcrypt (12 rounds)';


-- ------------------------------------------------------------
-- 2.4  Types de ressources (configurables par entreprise)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS resource_types (
    id            SERIAL        PRIMARY KEY,
    company_id    INTEGER       NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    name          VARCHAR(100)  NOT NULL,
    description   TEXT,
    custom_fields TEXT
);

COMMENT ON TABLE  resource_types IS 'Catégories de ressources définies par l''entreprise';
COMMENT ON COLUMN resource_types.custom_fields IS 'JSON : champs personnalisés du type de ressource';


-- ------------------------------------------------------------
-- 2.5  Ressources (équipements, comptes, véhicules…)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS resources (
    id               SERIAL       PRIMARY KEY,
    company_id       INTEGER      NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    resource_type_id INTEGER      NOT NULL REFERENCES resource_types(id),
    name             VARCHAR(100) NOT NULL,
    serial_number    VARCHAR(100) UNIQUE,
    status           VARCHAR(20)  NOT NULL DEFAULT 'available',
    custom_data      TEXT,
    purchase_date    DATE,
    end_of_life_date DATE,
    created_at       TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_resources_status
        CHECK (status IN ('available', 'assigned', 'maintenance', 'retired')),
    CONSTRAINT chk_resources_dates
        CHECK (end_of_life_date IS NULL OR purchase_date IS NULL
               OR end_of_life_date >= purchase_date)
);

COMMENT ON TABLE  resources IS 'Ressources physiques et numériques';
COMMENT ON COLUMN resources.status IS
    'available | assigned | maintenance | retired';
COMMENT ON COLUMN resources.custom_data IS
    'JSON : données spécifiques au type de ressource';


-- ------------------------------------------------------------
-- 2.6  Affectations (ressource ↔ utilisateur)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS assignments (
    id          SERIAL       PRIMARY KEY,
    resource_id INTEGER      NOT NULL REFERENCES resources(id),
    user_id     INTEGER      NOT NULL REFERENCES users(id),
    assigned_by INTEGER      NOT NULL REFERENCES users(id),
    start_date  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    end_date    TIMESTAMPTZ,
    status      VARCHAR(20)  NOT NULL DEFAULT 'active',
    notes       TEXT,
    CONSTRAINT chk_assignments_status
        CHECK (status IN ('active', 'returned', 'cancelled')),
    CONSTRAINT chk_assignments_dates
        CHECK (end_date IS NULL OR end_date >= start_date)
);

COMMENT ON TABLE assignments IS 'Affectations de ressources aux utilisateurs';


-- ------------------------------------------------------------
-- 2.7  Contrats (générés à chaque affectation)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS contracts (
    id             SERIAL        PRIMARY KEY,
    assignment_id  INTEGER       NOT NULL REFERENCES assignments(id) ON DELETE CASCADE,
    content        TEXT          NOT NULL,
    content_hash   VARCHAR(64)   NOT NULL,
    generated_at   TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    signed_at      TIMESTAMPTZ,
    signature_hash VARCHAR(64),
    pdf_path       VARCHAR(255),
    CONSTRAINT chk_contracts_hash_length CHECK (LENGTH(content_hash) = 64),
    CONSTRAINT chk_contracts_signature
        CHECK ((signed_at IS NULL) = (signature_hash IS NULL))
);

COMMENT ON TABLE  contracts IS 'Contrats générés pour les affectations';
COMMENT ON COLUMN contracts.content_hash IS 'SHA-256 du contenu — intégrité RGPD';


-- ------------------------------------------------------------
-- 2.8  Journal d'audit applicatif
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS audit_logs (
    id         SERIAL       PRIMARY KEY,
    user_id    INTEGER      REFERENCES users(id) ON DELETE SET NULL,
    action     VARCHAR(50)  NOT NULL,
    table_name VARCHAR(50),
    record_id  INTEGER,
    old_values TEXT,
    new_values TEXT,
    ip_address VARCHAR(45),
    created_at TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE audit_logs IS 'Traçabilité des actions utilisateurs (applicatif)';


-- ------------------------------------------------------------
-- 2.9  Sessions authentifiées
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS sessions (
    id         SERIAL       PRIMARY KEY,
    user_id    INTEGER      NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(64)  NOT NULL,
    created_at TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ  NOT NULL,
    CONSTRAINT chk_sessions_expiry CHECK (expires_at > created_at)
);

COMMENT ON TABLE sessions IS 'Sessions actives des utilisateurs connectés';


-- ------------------------------------------------------------
-- 2.10  Journal de modifications bas niveau (triggers PostgreSQL)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS journal_modifications (
    id          BIGSERIAL    PRIMARY KEY,
    table_name  VARCHAR(50)  NOT NULL,
    operation   VARCHAR(10)  NOT NULL,
    record_id   INTEGER,
    old_data    JSONB,
    new_data    JSONB,
    pg_user     VARCHAR(100) NOT NULL DEFAULT current_user,
    app_user_id INTEGER,
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_journal_operation CHECK (operation IN ('INSERT', 'UPDATE', 'DELETE'))
);

COMMENT ON TABLE journal_modifications IS
    'Audit bas niveau déclenché par triggers PostgreSQL';


-- ============================================================
-- ÉTAPE 3 — INDEX DE PERFORMANCE
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_users_email         ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_company        ON users(company_id);
CREATE INDEX IF NOT EXISTS idx_users_role           ON users(role_id);
CREATE INDEX IF NOT EXISTS idx_resources_company    ON resources(company_id);
CREATE INDEX IF NOT EXISTS idx_resources_status     ON resources(status);
CREATE INDEX IF NOT EXISTS idx_assignments_resource ON assignments(resource_id);
CREATE INDEX IF NOT EXISTS idx_assignments_user     ON assignments(user_id);
CREATE INDEX IF NOT EXISTS idx_assignments_status   ON assignments(status);
CREATE INDEX IF NOT EXISTS idx_audit_logs_user      ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_date      ON audit_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_sessions_user        ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_expires     ON sessions(expires_at);
CREATE INDEX IF NOT EXISTS idx_journal_table        ON journal_modifications(table_name, created_at);


-- ============================================================
-- ÉTAPE 4 — VUES MÉTIER
-- ============================================================

-- Vue 1 : ressources disponibles avec leur type et leur entreprise
CREATE OR REPLACE VIEW v_ressources_disponibles AS
SELECT
    r.id,
    r.name                  AS ressource,
    rt.name                 AS type_ressource,
    c.name                  AS entreprise,
    r.serial_number,
    r.purchase_date,
    r.end_of_life_date,
    r.created_at
FROM resources r
JOIN resource_types rt ON rt.id = r.resource_type_id
JOIN companies      c  ON c.id  = r.company_id
WHERE r.status = 'available'
  AND c.is_active = TRUE;

COMMENT ON VIEW v_ressources_disponibles IS
    'Ressources disponibles à l''affectation, par entreprise';


-- Vue 2 : affectations actives avec tous les détails
CREATE OR REPLACE VIEW v_affectations_actives AS
SELECT
    a.id                                   AS affectation_id,
    r.name                                 AS ressource,
    rt.name                                AS type_ressource,
    (u.first_name || ' ' || u.last_name)   AS utilisateur,
    u.email                                AS email_utilisateur,
    (adm.first_name || ' ' || adm.last_name) AS affecte_par,
    a.start_date,
    a.end_date,
    NOW() - a.start_date                   AS duree_actuelle,
    c.name                                 AS entreprise,
    a.notes
FROM assignments a
JOIN resources    r   ON r.id   = a.resource_id
JOIN resource_types rt ON rt.id = r.resource_type_id
JOIN users        u   ON u.id   = a.user_id
JOIN users        adm ON adm.id = a.assigned_by
JOIN companies    c   ON c.id   = r.company_id
WHERE a.status = 'active';

COMMENT ON VIEW v_affectations_actives IS
    'Affectations en cours avec détails ressource, utilisateur et entreprise';


-- Vue 3 : tableau de bord par entreprise
CREATE OR REPLACE VIEW v_tableau_de_bord AS
SELECT
    c.id                                              AS company_id,
    c.name                                            AS entreprise,
    COUNT(DISTINCT u.id)                              AS nb_utilisateurs_actifs,
    COUNT(DISTINCT r.id)                              AS nb_ressources_total,
    COUNT(DISTINCT r.id) FILTER (WHERE r.status = 'available')   AS nb_disponibles,
    COUNT(DISTINCT r.id) FILTER (WHERE r.status = 'assigned')    AS nb_affectees,
    COUNT(DISTINCT r.id) FILTER (WHERE r.status = 'maintenance') AS nb_maintenance,
    COUNT(DISTINCT a.id) FILTER (WHERE a.status = 'active')      AS nb_affectations_actives,
    COUNT(DISTINCT ct.id) FILTER (WHERE ct.signed_at IS NOT NULL) AS nb_contrats_signes
FROM companies c
LEFT JOIN users        u  ON u.company_id  = c.id  AND u.is_active = TRUE
LEFT JOIN resources    r  ON r.company_id  = c.id
LEFT JOIN assignments  a  ON a.resource_id = r.id
LEFT JOIN contracts    ct ON ct.assignment_id = a.id
WHERE c.is_active = TRUE
GROUP BY c.id, c.name;

COMMENT ON VIEW v_tableau_de_bord IS
    'Statistiques agrégées par entreprise pour le tableau de bord';


-- Vue 4 : historique complet d'une ressource
CREATE OR REPLACE VIEW v_historique_ressources AS
SELECT
    r.id                                            AS resource_id,
    r.name                                          AS ressource,
    c.name                                          AS entreprise,
    a.id                                            AS affectation_id,
    a.start_date,
    a.end_date,
    a.status                                        AS statut_affectation,
    (u.first_name || ' ' || u.last_name)            AS utilisateur,
    u.email,
    ct.generated_at                                 AS contrat_genere_le,
    ct.signed_at                                    AS contrat_signe_le
FROM resources r
JOIN companies    c  ON c.id  = r.company_id
JOIN assignments  a  ON a.resource_id = r.id
JOIN users        u  ON u.id  = a.user_id
LEFT JOIN contracts ct ON ct.assignment_id = a.id
ORDER BY r.id, a.start_date DESC;

COMMENT ON VIEW v_historique_ressources IS
    'Historique complet de toutes les affectations par ressource';


-- Vue 5 : activité récente des utilisateurs (30 derniers jours)
CREATE OR REPLACE VIEW v_activite_utilisateurs AS
SELECT
    u.id,
    (u.first_name || ' ' || u.last_name) AS utilisateur,
    u.email,
    r.name                               AS role,
    c.name                               AS entreprise,
    u.last_login,
    COUNT(al.id)                         AS nb_actions_30j,
    MAX(al.created_at)                   AS derniere_action
FROM users u
JOIN roles    r  ON r.id = u.role_id
LEFT JOIN companies c  ON c.id  = u.company_id
LEFT JOIN audit_logs al ON al.user_id = u.id
                       AND al.created_at >= NOW() - INTERVAL '30 days'
WHERE u.is_active = TRUE
GROUP BY u.id, u.first_name, u.last_name, u.email, r.name, c.name, u.last_login;

COMMENT ON VIEW v_activite_utilisateurs IS
    'Activité des utilisateurs actifs sur les 30 derniers jours';


-- ============================================================
-- ÉTAPE 5 — FONCTIONS PL/pgSQL
-- ============================================================

-- Fonction 1 : anonymisation RGPD (droit à l'oubli)
CREATE OR REPLACE FUNCTION fn_anonymize_user(p_user_id INTEGER)
RETURNS VOID
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM users WHERE id = p_user_id) THEN
        RAISE EXCEPTION 'Utilisateur % introuvable', p_user_id;
    END IF;

    UPDATE users
    SET
        email         = 'anonyme_' || p_user_id || '@supprime.local',
        first_name    = 'Anonyme',
        last_name     = 'Supprimé',
        password_hash = 'ANONYMIZED',
        is_active     = FALSE,
        last_login    = NULL
    WHERE id = p_user_id;

    -- Purger les sessions
    DELETE FROM sessions WHERE user_id = p_user_id;

    -- Tracer l'anonymisation
    INSERT INTO journal_modifications(table_name, operation, record_id, pg_user)
    VALUES ('users', 'DELETE', p_user_id, current_user);

    RAISE NOTICE 'Utilisateur % anonymisé (RGPD)', p_user_id;
END;
$$;

COMMENT ON FUNCTION fn_anonymize_user IS
    'Anonymise les données personnelles d''un utilisateur (droit à l''oubli RGPD)';


-- Fonction 2 : purge des sessions expirées
CREATE OR REPLACE FUNCTION fn_purge_sessions_expirees()
RETURNS INTEGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_count INTEGER;
BEGIN
    DELETE FROM sessions
    WHERE expires_at < NOW()
    RETURNING COUNT(*) INTO v_count;

    RETURN COALESCE(v_count, 0);
END;
$$;

COMMENT ON FUNCTION fn_purge_sessions_expirees IS
    'Supprime les sessions expirées, retourne le nombre supprimé';


-- Fonction 3 : statistiques d'une entreprise
CREATE OR REPLACE FUNCTION fn_stats_entreprise(p_company_id INTEGER)
RETURNS TABLE (
    indicateur  TEXT,
    valeur      TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 'Ressources totales'::TEXT,        COUNT(r.id)::TEXT
      FROM resources r WHERE r.company_id = p_company_id
    UNION ALL
    SELECT 'Ressources disponibles',          COUNT(r.id)::TEXT
      FROM resources r WHERE r.company_id = p_company_id AND r.status = 'available'
    UNION ALL
    SELECT 'Affectations actives',            COUNT(a.id)::TEXT
      FROM assignments a
      JOIN resources r ON r.id = a.resource_id
     WHERE r.company_id = p_company_id AND a.status = 'active'
    UNION ALL
    SELECT 'Contrats signés (total)',         COUNT(ct.id)::TEXT
      FROM contracts ct
      JOIN assignments a ON a.id = ct.assignment_id
      JOIN resources   r ON r.id = a.resource_id
     WHERE r.company_id = p_company_id AND ct.signed_at IS NOT NULL
    UNION ALL
    SELECT 'Utilisateurs actifs',             COUNT(u.id)::TEXT
      FROM users u
     WHERE u.company_id = p_company_id AND u.is_active = TRUE;
END;
$$;

COMMENT ON FUNCTION fn_stats_entreprise IS
    'Retourne les indicateurs clés pour une entreprise donnée';


-- Fonction 4 : vérifier les ressources en fin de vie
CREATE OR REPLACE FUNCTION fn_ressources_fin_de_vie(p_jours INTEGER DEFAULT 90)
RETURNS TABLE (
    id               INTEGER,
    name             VARCHAR,
    entreprise       VARCHAR,
    end_of_life_date DATE,
    jours_restants   INTEGER,
    status           VARCHAR
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        r.id,
        r.name,
        c.name,
        r.end_of_life_date,
        (r.end_of_life_date - CURRENT_DATE)::INTEGER,
        r.status
    FROM resources r
    JOIN companies c ON c.id = r.company_id
    WHERE r.end_of_life_date IS NOT NULL
      AND r.end_of_life_date <= CURRENT_DATE + p_jours
      AND r.status != 'retired'
    ORDER BY r.end_of_life_date;
END;
$$;

COMMENT ON FUNCTION fn_ressources_fin_de_vie IS
    'Retourne les ressources arrivant à fin de vie dans les N prochains jours';


-- ============================================================
-- ÉTAPE 6 — TRIGGERS
-- ============================================================

-- Trigger 1 : audit générique sur tables sensibles
CREATE OR REPLACE FUNCTION fn_trigger_audit()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO journal_modifications(table_name, operation, record_id, new_data)
        VALUES (TG_TABLE_NAME, 'INSERT', NEW.id, row_to_json(NEW)::JSONB);
        RETURN NEW;

    ELSIF TG_OP = 'UPDATE' THEN
        IF row(OLD.*) IS DISTINCT FROM row(NEW.*) THEN
            INSERT INTO journal_modifications(table_name, operation, record_id, old_data, new_data)
            VALUES (TG_TABLE_NAME, 'UPDATE', NEW.id,
                    row_to_json(OLD)::JSONB,
                    row_to_json(NEW)::JSONB);
        END IF;
        RETURN NEW;

    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO journal_modifications(table_name, operation, record_id, old_data)
        VALUES (TG_TABLE_NAME, 'DELETE', OLD.id, row_to_json(OLD)::JSONB);
        RETURN OLD;
    END IF;

    RETURN NULL;
END;
$$;

-- Appliquer le trigger d'audit sur les tables sensibles
CREATE OR REPLACE TRIGGER trg_audit_users
    AFTER INSERT OR UPDATE OR DELETE ON users
    FOR EACH ROW EXECUTE FUNCTION fn_trigger_audit();

CREATE OR REPLACE TRIGGER trg_audit_resources
    AFTER INSERT OR UPDATE OR DELETE ON resources
    FOR EACH ROW EXECUTE FUNCTION fn_trigger_audit();

CREATE OR REPLACE TRIGGER trg_audit_assignments
    AFTER INSERT OR UPDATE OR DELETE ON assignments
    FOR EACH ROW EXECUTE FUNCTION fn_trigger_audit();

CREATE OR REPLACE TRIGGER trg_audit_companies
    AFTER INSERT OR UPDATE OR DELETE ON companies
    FOR EACH ROW EXECUTE FUNCTION fn_trigger_audit();


-- Trigger 2 : mise à jour automatique du statut de la ressource
CREATE OR REPLACE FUNCTION fn_trigger_resource_status()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    -- Nouvelle affectation active → ressource passe à 'assigned'
    IF TG_OP = 'INSERT' AND NEW.status = 'active' THEN
        UPDATE resources SET status = 'assigned' WHERE id = NEW.resource_id;

    -- Retour ou annulation → ressource redevient 'available'
    ELSIF TG_OP = 'UPDATE'
          AND OLD.status = 'active'
          AND NEW.status IN ('returned', 'cancelled')
    THEN
        -- Vérifier qu'aucune autre affectation active n'utilise la ressource
        IF NOT EXISTS (
            SELECT 1 FROM assignments
            WHERE resource_id = NEW.resource_id
              AND status = 'active'
              AND id != NEW.id
        ) THEN
            UPDATE resources SET status = 'available' WHERE id = NEW.resource_id;
        END IF;
        -- Enregistrer la date de fin si non renseignée
        IF NEW.end_date IS NULL THEN
            NEW.end_date := NOW();
        END IF;
    END IF;

    RETURN NEW;
END;
$$;

CREATE OR REPLACE TRIGGER trg_resource_status
    BEFORE INSERT OR UPDATE ON assignments
    FOR EACH ROW EXECUTE FUNCTION fn_trigger_resource_status();


-- Trigger 3 : interdire l'affectation d'une ressource non disponible
CREATE OR REPLACE FUNCTION fn_trigger_check_availability()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_status VARCHAR(20);
BEGIN
    IF TG_OP = 'INSERT' AND NEW.status = 'active' THEN
        SELECT status INTO v_status FROM resources WHERE id = NEW.resource_id;
        IF v_status != 'available' THEN
            RAISE EXCEPTION
                'Ressource % non disponible (statut actuel : %)',
                NEW.resource_id, v_status;
        END IF;
    END IF;
    RETURN NEW;
END;
$$;

CREATE OR REPLACE TRIGGER trg_check_availability
    BEFORE INSERT ON assignments
    FOR EACH ROW EXECUTE FUNCTION fn_trigger_check_availability();


-- Trigger 4 : horodatage automatique à la connexion
CREATE OR REPLACE FUNCTION fn_trigger_session_created()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE users SET last_login = NOW() WHERE id = NEW.user_id;
    RETURN NEW;
END;
$$;

CREATE OR REPLACE TRIGGER trg_session_created
    AFTER INSERT ON sessions
    FOR EACH ROW EXECUTE FUNCTION fn_trigger_session_created();


-- ============================================================
-- ÉTAPE 7 — DROITS D'ACCÈS (gestres_user)
-- ============================================================

GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES    IN SCHEMA public TO gestres_user;
GRANT USAGE, SELECT                  ON ALL SEQUENCES IN SCHEMA public TO gestres_user;
GRANT EXECUTE                        ON ALL FUNCTIONS IN SCHEMA public TO gestres_user;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES    TO gestres_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT USAGE, SELECT                  ON SEQUENCES TO gestres_user;


-- ============================================================
-- ÉTAPE 8 — DONNÉES INITIALES
-- ============================================================

-- Rôles système
INSERT INTO roles (name, permissions) VALUES
    ('super_admin', '["all"]'),
    ('admin',       '["view_resources","manage_resources","view_users","manage_users","view_logs","generate_contracts","view_assignments","manage_assignments"]'),
    ('employee',    '["view_own_resources","view_own_assignments","sign_contracts","view_own_history"]')
ON CONFLICT (name) DO NOTHING;

-- Super administrateur par défaut
-- Mot de passe : Admin2026! (haché bcrypt — à changer à la première connexion)
INSERT INTO users (email, password_hash, first_name, last_name, role_id, is_active)
SELECT
    'admin@gestres.local',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TiGILbGXwXfq0bGFhNJBQ3DK4Y4.',
    'Super',
    'Admin',
    r.id,
    TRUE
FROM roles r
WHERE r.name = 'super_admin'
ON CONFLICT (email) DO NOTHING;


-- ============================================================
-- VÉRIFICATION FINALE
-- ============================================================

DO $$
DECLARE
    v_tables   INTEGER;
    v_triggers INTEGER;
    v_views    INTEGER;
    v_funcs    INTEGER;
BEGIN
    SELECT COUNT(*) INTO v_tables
      FROM information_schema.tables
     WHERE table_schema = 'public' AND table_type = 'BASE TABLE';

    SELECT COUNT(*) INTO v_triggers
      FROM information_schema.triggers
     WHERE trigger_schema = 'public';

    SELECT COUNT(*) INTO v_views
      FROM information_schema.views
     WHERE table_schema = 'public';

    SELECT COUNT(*) INTO v_funcs
      FROM information_schema.routines
     WHERE routine_schema = 'public' AND routine_type = 'FUNCTION';

    RAISE NOTICE '=== GestRes Pro — Initialisation réussie ===';
    RAISE NOTICE 'Tables   : %', v_tables;
    RAISE NOTICE 'Vues     : %', v_views;
    RAISE NOTICE 'Fonctions: %', v_funcs;
    RAISE NOTICE 'Triggers : %', v_triggers;
    RAISE NOTICE '============================================';
END;
$$;
