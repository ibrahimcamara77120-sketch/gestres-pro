from datetime import datetime, timedelta

from src.models.base import init_db, get_session
from src.models.user import Role
from src.controllers.auth_controller import AuthController
from src.controllers.company_controller import company_controller
from src.controllers.user_controller import user_controller
from src.controllers.resource_controller import resource_controller
from src.controllers.assignment_controller import assignment_controller
from src.controllers.contract_controller import contract_controller


def sep(title=""):
    print(f"\n{'─'*55}")
    if title:
        print(f"  {title}")
        print(f"{'─'*55}")


def ok(msg):  print(f"  ✅  {msg}")
def err(msg): print(f"  ❌  {msg}")
def info(msg):print(f"  ℹ   {msg}")


def run():
    sep("0. Initialisation de la base de données")
    init_db()
    ok("Base initialisée")

    sep("1. Super-administrateur")
    auth = AuthController()
    ok_flag, msg = auth.create_initial_super_admin(
        email="superadmin@gestres.test",
        password="SuperAdmin1!",
        first_name="Super",
        last_name="Admin"
    )
    if ok_flag:
        ok(f"Super-admin créé")
    else:
        info(f"Super-admin : {msg}")

    auth.login("superadmin@gestres.test", "SuperAdmin1!")

    sep("2. Création de la société test")
    ok_flag, msg, company_id = company_controller.create_company(
        name="[SOCIÉTÉ TEST] CleanPro Services",
        siret="73282932000074",
        address="12 rue des Lilas, 75013 Paris"
    )
    if ok_flag:
        ok(f"Société créée     → ID {company_id}  |  SIRET 732 829 320 00074")
    else:
        info(f"Société : {msg}")
        with get_session() as session:
            from src.models.company import Company
            c = session.query(Company).filter_by(siret="73282932000074").first()
            company_id = c.id if c else None

    sep("3. Création des utilisateurs")

    with get_session() as session:
        admin_role  = session.query(Role).filter_by(name="admin").first()
        emp_role    = session.query(Role).filter_by(name="employee").first()
        admin_rid   = admin_role.id  if admin_role  else None
        emp_rid     = emp_role.id    if emp_role    else None

    users_data = [
        ("responsable@cleanpro.test", "Responsable1!", "Marie",   "Dupont",   admin_rid, "Responsable d'agence (admin)"),
        ("employe1@cleanpro.test",    "Employe001!",   "Karim",   "Benali",   emp_rid,   "Agent de nettoyage"),
        ("employe2@cleanpro.test",    "Employe002!",   "Fatou",   "Diallo",   emp_rid,   "Agente de nettoyage"),
        ("employe3@cleanpro.test",    "Employe003!",   "Lucas",   "Martin",   emp_rid,   "Agent polyvalent"),
        ("employe4@cleanpro.test",    "Employe004!",   "Amina",   "Traore",   emp_rid,   "Agente de nettoyage"),
    ]

    user_ids = {}
    for email, pwd, fn, ln, rid, desc in users_data:
        ok_flag, msg, uid = user_controller.create_user(
            email=email, password=pwd,
            first_name=fn, last_name=ln,
            role_id=rid, company_id=company_id
        )
        if ok_flag:
            ok(f"{fn} {ln} ({desc})  → ID {uid}")
            user_ids[email] = uid
        else:
            info(f"{fn} {ln} : {msg}")
            with get_session() as session:
                from src.models.user import User
                u = session.query(User).filter_by(email=email).first()
                if u:
                    user_ids[email] = u.id

    sep("4. Types de ressources (matériel de nettoyage)")

    types_data = [
        ("Balai",          "Balais à franges, balais à brosse, balais plats",
         [{"name": "modele", "type": "text", "required": False},
          {"name": "longueur_manche_cm", "type": "number", "required": False}]),

        ("Serpillère",     "Serpillères et têtes de vadrouille",
         [{"name": "matiere", "type": "text", "required": False},
          {"name": "capacite_absorption", "type": "text", "required": False}]),

        ("Essuie-tout",    "Rouleaux et feuilles essuie-tout professionnels",
         [{"name": "nb_feuilles", "type": "number", "required": False},
          {"name": "couleur", "type": "text", "required": False}]),

        ("Seau & Chariot", "Seaux de nettoyage et chariots porte-seau avec essoreuse",
         [{"name": "capacite_litres", "type": "number", "required": False},
          {"name": "avec_essoreuse", "type": "boolean", "required": False}]),

        ("Produit nettoyant", "Produits détergents, désinfectants et dégraissants",
         [{"name": "reference_produit", "type": "text", "required": True},
          {"name": "dangereux", "type": "boolean", "required": False},
          {"name": "date_peremption", "type": "text", "required": False}]),

        ("Équipement de protection", "Gants, masques, tabliers, lunettes de protection",
         [{"name": "taille", "type": "text", "required": False},
          {"name": "norme", "type": "text", "required": False}]),

        ("Aspirateur",     "Aspirateurs industriels et aspirateurs à eau",
         [{"name": "puissance_watts", "type": "number", "required": False},
          {"name": "type_filtre", "type": "text", "required": False}]),
    ]

    type_ids = {}
    for name, desc, fields in types_data:
        ok_flag, msg, tid = resource_controller.create_resource_type(
            company_id=company_id, name=name,
            description=desc, custom_fields=fields
        )
        if ok_flag:
            ok(f"Type '{name}'  → ID {tid}")
            type_ids[name] = tid
        else:
            info(f"Type '{name}' : {msg}")
            with get_session() as session:
                from src.models.resource_type import ResourceType
                rt = session.query(ResourceType).filter_by(
                    name=name, company_id=company_id
                ).first()
                if rt:
                    type_ids[name] = rt.id

    sep("5. Création des ressources matérielles")

    resources_data = [
        ("Balai",          "Balai à franges 130cm",       "BAL-001", {"modele": "Franges coton", "longueur_manche_cm": 130}),
        ("Balai",          "Balai à brosse sol dur",      "BAL-002", {"modele": "Brosse PVC", "longueur_manche_cm": 120}),
        ("Balai",          "Balai plat microfibre",       "BAL-003", {"modele": "Plat microfibre", "longueur_manche_cm": 140}),
        ("Serpillère",     "Serpillère coton 400g",       "SER-001", {"matiere": "Coton", "capacite_absorption": "400g/m²"}),
        ("Serpillère",     "Tête vadrouille microfibre",  "SER-002", {"matiere": "Microfibre", "capacite_absorption": "600g/m²"}),
        ("Serpillère",     "Serpillère frange bleu",      "SER-003", {"matiere": "Rayonne", "capacite_absorption": "350g/m²"}),
        ("Essuie-tout",    "Rouleau essuie-tout x6",      "EST-001", {"nb_feuilles": 180, "couleur": "Blanc"}),
        ("Essuie-tout",    "Rouleau essuie-tout x12",     "EST-002", {"nb_feuilles": 360, "couleur": "Blanc"}),
        ("Seau & Chariot", "Chariot de nettoyage 25L",    "CHR-001", {"capacite_litres": 25, "avec_essoreuse": True}),
        ("Seau & Chariot", "Seau double compartiment",   "CHR-002", {"capacite_litres": 20, "avec_essoreuse": False}),
        ("Seau & Chariot", "Chariot pro essoreuse 30L",   "CHR-003", {"capacite_litres": 30, "avec_essoreuse": True}),
        ("Produit nettoyant", "Détergent sol toutes surfaces",  "PRD-001", {"reference_produit": "DETSOL-500", "dangereux": False, "date_peremption": "12/2026"}),
        ("Produit nettoyant", "Désinfectant multi-usage",       "PRD-002", {"reference_produit": "DESIN-200", "dangereux": True,  "date_peremption": "06/2026"}),
        ("Produit nettoyant", "Dégraissant sanitaires",         "PRD-003", {"reference_produit": "DEGR-100", "dangereux": True,  "date_peremption": "09/2026"}),
        ("Équipement de protection", "Gants nitrile taille M",  "EPI-001", {"taille": "M", "norme": "EN 374"}),
        ("Équipement de protection", "Gants nitrile taille L",  "EPI-002", {"taille": "L", "norme": "EN 374"}),
        ("Équipement de protection", "Tablier imperméable",     "EPI-003", {"taille": "Unique", "norme": "EN 13034"}),
        ("Équipement de protection", "Lunettes de protection",  "EPI-004", {"taille": "Unique", "norme": "EN 166"}),
        ("Aspirateur",     "Aspirateur industriel 1400W",  "ASP-001", {"puissance_watts": 1400, "type_filtre": "HEPA 13"}),
        ("Aspirateur",     "Aspirateur eau & poussières", "ASP-002", {"puissance_watts": 1200, "type_filtre": "Standard"}),
    ]

    resource_ids = {}
    for type_name, name, serial, custom in resources_data:
        tid = type_ids.get(type_name)
        if not tid:
            err(f"Type introuvable pour '{name}'")
            continue
        ok_flag, msg, rid = resource_controller.create_resource(
            company_id=company_id, resource_type_id=tid,
            name=name, serial_number=serial, custom_data=custom
        )
        if ok_flag:
            ok(f"Ressource '{name}'  [{serial}]  → ID {rid}")
            resource_ids[serial] = rid
        else:
            info(f"Ressource '{name}' : {msg}")
            with get_session() as session:
                from src.models.resource import Resource
                r = session.query(Resource).filter_by(serial_number=serial).first()
                if r:
                    resource_ids[serial] = r.id

    sep("6. Affectations de ressources aux agents")

    emp1 = user_ids.get("employe1@cleanpro.test")
    emp2 = user_ids.get("employe2@cleanpro.test")
    emp3 = user_ids.get("employe3@cleanpro.test")
    emp4 = user_ids.get("employe4@cleanpro.test")

    today = datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)

    assignments_data = [
        ("BAL-001", emp1, 30, "Balai de Karim"),
        ("SER-001", emp1, 30, "Serpillère de Karim"),
        ("EPI-001", emp1, 30, "Gants M de Karim"),
        ("BAL-002", emp2, 20, "Balai de Fatou"),
        ("SER-002", emp2, 20, "Serpillère de Fatou"),
        ("EPI-002", emp2, 20, "Gants L de Fatou"),
        ("CHR-001", emp3, 15, "Chariot de Lucas"),
        ("PRD-001", emp3, 15, "Détergent de Lucas"),
        ("EPI-003", emp3, 15, "Tablier de Lucas"),
        ("ASP-001", emp4,  7, "Aspirateur d'Amina"),
        ("EPI-004", emp4,  7, "Lunettes d'Amina"),
    ]

    assignment_ids = {}
    for serial, uid, days_ago, desc in assignments_data:
        rid = resource_ids.get(serial)
        if not rid or not uid:
            err(f"Données manquantes pour {desc}")
            continue
        start = today - timedelta(days=days_ago)
        ok_flag, msg, aid = assignment_controller.create_assignment(
            resource_id=rid, user_id=uid, start_date=start,
            notes=f"[TEST] {desc}"
        )
        if ok_flag:
            ok(f"{desc}  → affectation ID {aid}")
            assignment_ids[serial] = aid
        else:
            info(f"{desc} : {msg}")

    sep("7. Génération d'un contrat (Karim / Balai BAL-001)")

    aid_bal = assignment_ids.get("BAL-001")
    if aid_bal:
        ok_flag, msg, cid = contract_controller.generate_contract(
            assignment_id=aid_bal,
            objet="Mise à disposition d'un balai à franges professionnel 130cm pour l'exécution des missions de nettoyage assignées à l'agent.",
            conditions=(
                "1. La ressource est confiée à titre personnel et ne peut être prêtée à un tiers.\n"
                "2. L'agent s'engage à utiliser le matériel conformément aux instructions d'utilisation.\n"
                "3. Tout dommage ou perte doit être signalé immédiatement au responsable d'agence.\n"
                "4. La ressource doit être restituée propre et en bon état en fin de mission."
            ),
            notes="[SOCIÉTÉ TEST] — Contrat généré automatiquement dans le cadre de la démonstration GestRes Pro."
        )
        if ok_flag:
            ok(f"Contrat généré  → ID {cid}")
            ok_pdf, pdf_msg = contract_controller.export_pdf(cid)
            if ok_pdf:
                ok(f"PDF exporté  → {pdf_msg}")
            else:
                info(f"PDF : {pdf_msg}")
        else:
            info(f"Contrat : {msg}")

    sep("RÉSUMÉ FINAL")
    stats = company_controller.get_company_stats(company_id)
    info(f"Société      : [SOCIÉTÉ TEST] CleanPro Services")
    info(f"Utilisateurs : {stats['users_count']} actifs")
    info(f"Ressources   : {stats['resources_count']} enregistrées  ({stats['available_resources']} disponibles)")
    info(f"Affectations : {len(assignment_ids)} actives")
    sep()
    print("\n  Données de connexion test :")
    print("  ┌─────────────────────────────────────────────────────┐")
    print("  │  Super-admin  superadmin@gestres.test / SuperAdmin1! │")
    print("  │  Admin        responsable@cleanpro.test / Responsable1! │")
    print("  │  Employé 1    employe1@cleanpro.test  / Employe001!  │")
    print("  │  Employé 2    employe2@cleanpro.test  / Employe002!  │")
    print("  └─────────────────────────────────────────────────────┘\n")


if __name__ == "__main__":
    run()
