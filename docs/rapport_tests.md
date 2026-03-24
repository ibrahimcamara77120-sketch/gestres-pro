# Rapport de tests — GestRes Pro
**Projet** : Application de gestion de ressources (BTS SIO SLAM)
**Auteur** : CAMARA Ibrahim — N° candidat : 2545812845
**Date** : Mars 2026
**Résultat global** : **155 tests — 155 réussis — 0 échec**

---

## Résumé par fichier

| Fichier | Tests | Réussis | Échecs |
|---|---|---|---|
| tests/test_security.py | 40 | 40 | 0 |
| tests/test_models.py | 52 | 52 | 0 |
| tests/test_controllers.py | 63 | 63 | 0 |
| **Total** | **155** | **155** | **0** |

---

## tests/test_security.py — Sécurité (40 tests)

### TestPasswordHashing — Hachage bcrypt

| Test | Description |
|---|---|
| test_hash_different_from_plaintext | Le hash est différent du mot de passe en clair |
| test_hash_bcrypt_prefix | Le hash commence par `$2b$` (bcrypt) |
| test_verify_correct_password | Vérification réussie avec le bon mot de passe |
| test_verify_wrong_password | Vérification échoue avec mauvais mot de passe |
| test_same_password_different_hashes | Deux hachages du même mot de passe sont différents (salt aléatoire) |
| test_empty_string_hash | Hachage d'une chaîne vide fonctionne correctement |
| test_unicode_password | Mots de passe avec caractères accentués (Pässwörd) |
| test_long_password | Mot de passe long (45 caractères) — dans la limite bcrypt |

### TestTokenGeneration — Tokens de session

| Test | Description |
|---|---|
| test_token_length | Token de 64 caractères (32 octets hex) |
| test_tokens_are_unique | 100 tokens générés sont tous uniques |
| test_token_is_hexadecimal | Le token est bien en hexadécimal valide |
| test_hash_token_deterministic | SHA-256 d'un token est toujours identique |
| test_hash_token_length | Longueur du hash SHA-256 : 64 caractères |
| test_different_tokens_different_hashes | Deux tokens différents ont des hashes différents |
| test_session_expiry_in_future | L'expiration de session est bien dans le futur |

### TestPasswordStrength — Force du mot de passe

| Test | Description |
|---|---|
| test_valid_password | Mot de passe complet validé sans erreur |
| test_too_short | Rejet si moins de 8 caractères |
| test_no_uppercase | Rejet si pas de majuscule |
| test_no_lowercase | Rejet si pas de minuscule |
| test_no_digit | Rejet si pas de chiffre |
| test_no_special_char | Rejet si pas de caractère spécial |
| test_multiple_errors_at_once | Mot de passe "abc" — au moins 3 erreurs |
| test_exactly_8_chars | Exactement 8 caractères valides acceptés |
| test_special_chars_accepted | Les caractères `!@#$%^&*()` sont acceptés |

### TestEmailValidation — Validation d'email

| Test | Description |
|---|---|
| test_valid_emails | 5 emails valides acceptés (formats variés) |
| test_invalid_emails | 7 formats invalides rejetés |
| test_case_insensitive_domain | Domaine en majuscules accepté |

### TestSiretValidation — Numéro SIRET

| Test | Description |
|---|---|
| test_valid_siret | SIRET valide (73282932000074) accepté |
| test_empty_siret_optional | SIRET vide ou None autorisé (champ optionnel) |
| test_invalid_length_short | SIRET trop court rejeté |
| test_invalid_length_long | SIRET trop long rejeté |
| test_invalid_characters | SIRET avec lettres rejeté |
| test_siret_with_spaces_stripped | Espaces retirés avant validation |
| test_invalid_checksum | 14 chiffres mais checksum Luhn invalide rejeté |

### TestSanitizeInput — Nettoyage des entrées

| Test | Description |
|---|---|
| test_strips_whitespace | Espaces en début/fin supprimés |
| test_strips_tabs_and_newlines_around | Tabulations et sauts de ligne en bordure supprimés |
| test_none_returns_none | `None` retourne `None` |
| test_empty_returns_none | Chaîne vide retourne `None` |
| test_spaces_only_returns_none | Chaîne avec espaces seulement retourne `None` |
| test_preserves_internal_newlines | Sauts de ligne internes conservés |
| test_removes_control_characters | Caractères de contrôle (`\x00`, `\x01`) supprimés |
| test_normal_text_unchanged | Texte normal non modifié |
| test_numbers_unchanged | Chiffres non modifiés |

---

## tests/test_models.py — Modèles SQLAlchemy (52 tests)

### TestCompany — Modèle entreprise

| Test | Description |
|---|---|
| test_create_company | Création avec nom, SIRET et adresse |
| test_company_default_active | `is_active` est `True` par défaut |
| test_company_without_siret | Entreprise sans SIRET (champ optionnel) |
| test_company_repr | Représentation textuelle contient le nom |
| test_company_deactivation | Passage `is_active` à `False` |
| test_multiple_companies | Création de 5 entreprises distinctes |

### TestRole — Modèle rôle

| Test | Description |
|---|---|
| test_get_permissions | Récupération de la liste des permissions JSON |
| test_has_permission | Vérification de permission existante/inexistante |
| test_has_permission_all | Rôle avec permission "all" accepte tout |
| test_role_empty_permissions | Rôle sans permissions — tableau vide |
| test_role_multiple_permissions | Rôle avec 3 permissions distinctes |
| test_role_repr | Représentation textuelle contient le nom du rôle |

### TestUser — Modèle utilisateur

| Test | Description |
|---|---|
| test_create_user | Création avec email, hash, prénom, nom, rôle |
| test_full_name_with_both_names | `full_name` = "Prénom Nom" |
| test_full_name_first_name_only | `full_name` = "Prénom" si pas de nom |
| test_full_name_fallback_to_email | `full_name` = email si pas de prénom |
| test_user_default_active | `is_active` est `True` par défaut |
| test_user_last_login_initially_none | `last_login` est `None` à la création |
| test_user_repr | Représentation textuelle contient l'email |
| test_user_soft_delete | Désactivation sans suppression de l'enregistrement |
| test_user_has_permission_via_role | Permission héritée du rôle |

### TestResourceType — Type de ressource

| Test | Description |
|---|---|
| test_custom_fields | Définition et lecture de 2 champs personnalisés JSON |
| test_empty_custom_fields | Pas de champs → liste vide |
| test_set_then_override_custom_fields | Remplacement complet des champs personnalisés |
| test_resource_type_repr | Représentation textuelle contient le nom |

### TestResource — Ressource

| Test | Description |
|---|---|
| test_create_resource | Création avec statut "available" par défaut |
| test_resource_custom_data | Données personnalisées (RAM, stockage) |
| test_resource_empty_custom_data | Pas de données personnalisées → dict vide |
| test_resource_status_change | Changement de statut "available" → "assigned" |
| test_resource_repr | Représentation textuelle contient le nom |

### TestAssignment — Affectation

| Test | Description |
|---|---|
| test_create_assignment | Création avec statut "active" par défaut |
| test_assignment_is_active_property | Propriété `is_active` selon le statut |
| test_assignment_with_end_date | Calcul de durée en jours avec date de fin |
| test_assignment_repr | Représentation textuelle de l'affectation |

### TestContract — Contrat

| Test | Description |
|---|---|
| test_compute_hash_deterministic | SHA-256 identique pour le même contenu |
| test_compute_hash_length | Hash de 64 caractères |
| test_different_content_different_hash | Contenu différent → hash différent |
| test_verify_integrity_ok | Intégrité validée pour un contrat non modifié |
| test_verify_integrity_tampered | Intégrité échoue si contenu modifié |
| test_sign_contract | Signature avec hash et date |
| test_contract_repr | Représentation textuelle du contrat |

### TestAuditLog — Journal d'audit

| Test | Description |
|---|---|
| test_create_log | Création d'un log avec nouvelles valeurs |
| test_log_old_values | Valeurs anciennes et nouvelles enregistrées |
| test_log_no_values_returns_empty_dict | `get_old_values()` / `get_new_values()` retournent `{}` si null |
| test_log_with_ip | Adresse IP enregistrée dans le log |
| test_log_repr | Représentation textuelle contient l'action |
| test_log_created_at | Timestamp de création dans l'intervalle attendu |

### TestSession — Session utilisateur

| Test | Description |
|---|---|
| test_session_expired | Session passée : `is_expired=True`, `is_valid=False` |
| test_session_valid | Session future : `is_expired=False`, `is_valid=True` |
| test_session_repr | Représentation textuelle de la session |
| test_session_just_expired | Session expirée depuis 1 seconde |

---

## tests/test_controllers.py — Contrôleurs (63 tests)

### TestAuthController — Authentification

| Test | Description |
|---|---|
| test_initial_state | Pas d'utilisateur connecté à l'initialisation |
| test_create_user_success | Création d'un utilisateur valide |
| test_create_user_invalid_email | Email invalide → rejet |
| test_create_user_weak_password | Mot de passe trop faible → rejet |
| test_create_user_duplicate_email | Email déjà utilisé → rejet |
| test_create_user_unknown_role | Rôle inexistant → rejet |
| test_login_success | Connexion réussie + état authentifié |
| test_login_wrong_password | Mauvais mot de passe → non connecté |
| test_login_nonexistent_user | Utilisateur inconnu → non connecté |
| test_login_inactive_user | Compte désactivé → message adapté |
| test_login_empty_credentials | Identifiants vides → rejet |
| test_logout | Déconnexion → état réinitialisé |
| test_logout_not_authenticated | Déconnexion sans être connecté → `False` |
| test_has_permission | Permission présente/absente sur rôle admin |
| test_has_permission_not_authenticated | Permission refusée si non connecté |
| test_has_permission_super_admin | Super admin a toutes les permissions |
| test_is_admin | Admin est admin, pas super_admin |
| test_is_admin_not_authenticated | is_admin() = False si non connecté |
| test_change_password_success | Changement de mot de passe + reconnexion |
| test_change_password_wrong_current | Mauvais mot de passe actuel → rejet |
| test_change_password_weak_new | Nouveau mot de passe trop faible → rejet |
| test_change_password_not_authenticated | Non connecté → rejet |
| test_create_initial_super_admin | Création du premier super admin |
| test_create_initial_super_admin_duplicate | Deuxième super admin → rejet |
| test_login_updates_last_login | `last_login` mis à jour après connexion |
| test_login_case_insensitive_email | Email en majuscules accepté |

### TestUserController — Gestion des utilisateurs

| Test | Description |
|---|---|
| test_get_all_users_empty | Liste vide au départ |
| test_create_user_success | Création retourne `True` et un `user_id` entier |
| test_create_user_invalid_email | Email invalide → rejet |
| test_create_user_duplicate_email | Email doublon → rejet |
| test_create_user_invalid_role | `role_id` inexistant → rejet |
| test_get_all_users_after_create | 1 utilisateur après création |
| test_get_user_by_id | Récupération par ID avec données correctes |
| test_get_user_by_id_not_found | ID inexistant → `None` |
| test_update_user_name | Mise à jour du nom de famille |
| test_update_user_not_found | ID inexistant → message d'erreur |
| test_update_user_invalid_email | Email invalide à la mise à jour → rejet |
| test_delete_user | Soft delete → `is_active=False` |
| test_delete_user_not_found | ID inexistant → rejet |
| test_reset_password_success | Réinitialisation du mot de passe réussie |
| test_reset_password_weak | Nouveau mot de passe trop faible → rejet |
| test_reset_password_user_not_found | ID inexistant → rejet |
| test_get_all_roles | 3 rôles présents (super_admin, admin, employee) |
| test_get_users_by_company | Filtre par `company_id` fonctionnel |

### TestCompanyController — Gestion des entreprises

| Test | Description |
|---|---|
| test_create_company_success | Création avec nom et adresse |
| test_create_company_with_siret | Création avec SIRET valide |
| test_create_company_invalid_siret | SIRET avec checksum Luhn invalide → rejet |
| test_create_company_short_name | Nom d'1 caractère → rejet |
| test_create_company_duplicate_siret | SIRET déjà enregistré → rejet |
| test_get_all_companies_empty | Liste vide au départ |
| test_get_all_companies | 2 entreprises créées retrouvées |
| test_get_company_by_id | Récupération par ID correcte |
| test_get_company_by_id_not_found | ID inexistant → `None` |
| test_update_company_name | Mise à jour du nom |
| test_update_company_not_found | ID inexistant → rejet |
| test_update_company_invalid_siret | SIRET invalide à la mise à jour → rejet |
| test_delete_company_success | Soft delete → `is_active=False` |
| test_delete_company_with_active_users | Suppression bloquée si utilisateurs actifs |
| test_delete_company_not_found | ID inexistant → rejet |
| test_get_company_stats | Stats : utilisateurs, ressources, dispo |
| test_get_all_companies_excludes_inactive | Filtre actif/inactif fonctionnel |

---

## Commandes d'exécution

```bash
# Activer l'environnement virtuel
source .venv/bin/activate

# Lancer tous les tests
python -m pytest tests/ -v

# Lancer un seul fichier
python -m pytest tests/test_security.py -v

# Avec rapport de couverture
python -m pytest tests/ --tb=short
```

---

## Couverture fonctionnelle

| Module | Fonctionnalités testées |
|---|---|
| `utils/security.py` | Hachage bcrypt, tokens, force mdp, validation email/SIRET, sanitize |
| `models/company.py` | CRUD, champs par défaut, soft delete |
| `models/user.py` | CRUD, full_name, permissions, soft delete |
| `models/role.py` | Permissions JSON, permission "all" |
| `models/resource_type.py` | Champs personnalisés JSON |
| `models/resource.py` | Statuts, données personnalisées |
| `models/assignment.py` | Création, statut, durée |
| `models/contract.py` | Intégrité SHA-256, signature |
| `models/audit_log.py` | Logs d'action, valeurs JSON, timestamps |
| `models/audit_log.py` (Session) | Expiration, validité |
| `controllers/auth_controller.py` | Login, logout, permissions, changement mdp |
| `controllers/user_controller.py` | CRUD utilisateurs, filtre entreprise, rôles |
| `controllers/company_controller.py` | CRUD entreprises, stats, contraintes métier |
