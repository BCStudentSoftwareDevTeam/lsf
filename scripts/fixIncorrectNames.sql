BEGIN;
-- Update Cody Vaughn's name
UPDATE supervisor SET legal_name="Cody", LAST_NAME="Vaughn" where supervisor.ID="B00649661";
-- Update Lexi Bass name
UPDATE supervisor SET legal_name="Lexi", LAST_NAME="Bass" where supervisor.ID="B00356129";
-- Update Mariah Lunsford-Brown name
UPDATE supervisor SET legal_name="Mariah", LAST_NAME="Lunsford-Brown" where supervisor.ID="B00643838";
-- Update Maxellende Ezin's name
UPDATE supervisor SET legal_name="Maxellende", LAST_NAME="Ezin" where supervisor.ID="B00749867";
-- Update Michael Schuier's name
UPDATE supervisor SET legal_name="Michael", LAST_NAME="Schuier" where supervisor.ID="B00733583";
-- Update Sarah Nicely's name
UPDATE supervisor SET legal_name="Sarah", LAST_NAME="Nicely" where supervisor.ID="B00633436";
COMMIT;