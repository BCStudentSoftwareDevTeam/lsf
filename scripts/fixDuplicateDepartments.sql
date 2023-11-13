BEGIN;

-- Make id 170 the official id for all `Craft Creative ACP Student Labor - St. P/R - Broomcraft`
UPDATE laborstatusform SET department_id=170 WHERE department_id=65 or department_id=165;
UPDATE department SET departmentCompliance=1 WHERE departmentID=170;
DELETE FROM department WHERE departmentID=65 or departmentID=165;

-- Make id 171 the official id for all `Craft Creative ACP Student Labor - St. P/R - Ceramics`
UPDATE laborstatusform SET department_id=171 WHERE department_id=32;
UPDATE department SET departmentCompliance=1 WHERE departmentID=171;
DELETE FROM department WHERE departmentID=32;

-- Make id 172 the official id for all `Craft Creative ACP Student Labor - St. P/R - Weaving`
UPDATE laborstatusform SET department_id=172 WHERE department_id=28 or department_id=168;
UPDATE department SET departmentCompliance=1 WHERE departmentID=172;
DELETE FROM department WHERE departmentID=28 or departmentID=168;


/*
-- Make id  the official id for all ``
UPDATE laborstatusform SET department_id= WHERE department_id=;
UPDATE department SET departmentCompliance=1 WHERE departmentID=;
DELETE FROM department WHERE departmentID=;
*/

COMMIT;