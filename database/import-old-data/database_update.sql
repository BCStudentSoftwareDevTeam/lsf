--
-- This is the first query to run so everything is reverted back
-- to what it was in the CSV files.
--

UPDATE laborstatusform, term
INNER JOIN term ON laborstatusform.termCode = term.termCode
SET laborstatusform.contractHours = laborstatusform.contractHours / 40
WHERE term.isSummer = 1 AND term.termName != "Summer 2020";

--
-- This is the second query to run. Here we will multiply all the contract
-- hours that are 2, 4, 6, 8, 10. These are daily hours.
--

UPDATE laborstatusform, term
INNER JOIN term ON laborstatusform.termCode = term.termCode
SET laborstatusform.contractHours = laborstatusform.contractHours * 40
WHERE term.isSummer = 1 AND laborstatusform.contractHours <= 10;

--
-- This is the third query to run. Here we will multiply all the contract
-- hours that are greater than 10 but less than 20. These are weekly hours.
--

UPDATE laborstatusform, term
INNER JOIN term ON laborstatusform.termCode = term.termCode
SET laborstatusform.contractHours = laborstatusform.contractHours * 8
WHERE term.isSummer = 1 AND 10 < laborstatusform.contractHours AND laborstatusform.contractHours <= 20;
