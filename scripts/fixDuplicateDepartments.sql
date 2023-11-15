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

-- Make id 173 the official id for all `Craft Creative ACP Student Labor - St. P/R - Woodcraft`
UPDATE laborstatusform SET department_id=173 WHERE department_id=15 or department_id=162;
UPDATE department SET departmentCompliance=1 WHERE departmentID=173;
DELETE FROM department WHERE departmentID=15 or departmentID=162;

-- Make id 175 the official id for all `Student Success and Transition`
UPDATE laborstatusform SET department_id=175 WHERE department_id=127 or department_id=163;
UPDATE department SET departmentCompliance=1 WHERE departmentID=175;
DELETE FROM department WHERE departmentID=127 or departmentID=163;


-- Make id 177 the official id for all `VC&S and Log House Student Labor`
UPDATE laborstatusform SET department_id=177 WHERE department_id=164;
UPDATE department SET departmentCompliance=1 WHERE departmentID=177;
DELETE FROM department WHERE departmentID=164;

-- Make id 146 the official id for all `MAC Office`
UPDATE laborstatusform SET department_id=146 WHERE department_id=102;
UPDATE department SET departmentCompliance=1 WHERE departmentID=146;
DELETE FROM department WHERE departmentID=102;





/*
-- Make id  the official id for all ``
UPDATE laborstatusform SET department_id= WHERE department_id=;
UPDATE department SET departmentCompliance=1 WHERE departmentID=;
DELETE FROM department WHERE departmentID=;
*/

COMMIT;