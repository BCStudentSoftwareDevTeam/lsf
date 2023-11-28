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

-- Make id 181 the official id for all `CELTS - Off Campus Work`
UPDATE laborstatusform SET department_id=181 WHERE department_id=109;
UPDATE department SET departmentCompliance=1 WHERE departmentID=181;
DELETE FROM department WHERE departmentID=109;

-- Make id 174 the official id for all `Office Disability & Accessability`
UPDATE laborstatusform SET department_id=174 WHERE department_id=49 or department_id=167;
UPDATE department SET departmentCompliance=1 WHERE departmentID=174;
DELETE FROM department WHERE departmentID=49 or departmentID=167;

-- Make id 140 the official id for all `Risk Management`
UPDATE laborstatusform SET department_id=140 WHERE department_id=42;
UPDATE department SET departmentCompliance=1 WHERE departmentID=140;
DELETE FROM department WHERE departmentID=42;

-- Make id 144 the official id for all `Finance Office`
UPDATE laborstatusform SET department_id=144 WHERE department_id=31;
UPDATE department SET departmentCompliance=1 WHERE departmentID=144;
DELETE FROM department WHERE departmentID=31;

-- Make id 137 the official id for all `Student Life Administrative Office`
UPDATE laborstatusform SET department_id=137 WHERE department_id=61;
UPDATE department SET departmentCompliance=1 WHERE departmentID=137;
DELETE FROM department WHERE departmentID=61;

-- Make id 160 the official id for all `ACP General Administration`
UPDATE laborstatusform SET department_id=160 WHERE department_id=27;
UPDATE department SET departmentCompliance=1 WHERE departmentID=160;
DELETE FROM department WHERE departmentID=27;


/*
-- Make id  the official id for all ``
UPDATE laborstatusform SET department_id= WHERE department_id=;
UPDATE department SET departmentCompliance=1 WHERE departmentID=;
DELETE FROM department WHERE departmentID=;
*/

COMMIT;