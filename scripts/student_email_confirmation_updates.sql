BEGIN;

-- XXX TEMPORARY set an open term
INSERT INTO `term` (`termCode`, `termName`, `termState`, `isBreak`, `isSummer`, `isAcademicYear`, `isFinalEvaluationOpen`, `isMidyearEvaluationOpen`) VALUES (202500, 'AY 2025-2026', 0, 0, 0, 1, 0, 0);
UPDATE `term` SET `termName` = 'AY 2025-2026', `termStart` = '2025-08-01', `termEnd` = '2026-05-01', `primaryCutOff` = '2025-09-04', `adjustmentCutOff` = '2025-09-12', `termState` = 1, `isBreak` = 0, `isSummer` = 0, `isAcademicYear` = 1, `isFinalEvaluationOpen` = 0, `isMidyearEvaluationOpen` = 0 WHERE (`term`.`termCode` = 202500);

-- Update Denied statuses

-- XXX INSERT INTO status VALUES ('Denied by Admin');
-- XXX INSERT INTO status VALUES ('Denied by Student');

update overloadform set financialAidApproved_id='Denied by Admin' where financialAidApproved_id='Denied';
update overloadform set SAASApproved_id='Denied by Admin' where SAASApproved_id='Denied';
update overloadform set laborApproved_id='Denied by Admin' where laborApproved_id='Denied';
update formhistory set status_id='Denied by Admin' where status_id='Denied';

DELETE from status where statusName='Denied';


-- Update emailtemplate for Labor Status Form Submitted for Student
UPDATE emailtemplate 
SET 
    subject = 'ACTION REQUIRED - Labor Status Form Received',
    body = '<p>Dear <strong>@@Student@@</strong>,</p>
            <p><strong>ACTION IS REQUIRED - This offer will EXPIRE on @@StudentConfirmationExpiration@@.</strong></p>

            <p>This email is very important. Please take a moment to read carefully and review the information. 
            A Labor Status Form has been submitted by @@Creator@@ for you, for a position supervised by <strong>@@Supervisor@@.</strong></p>
            
            <p><strong>Labor Status Form Information:</strong></p>
            <p>Student Name: <strong>@@Student@@ @@StudB@@</strong></p>
            <p>Supervisor: <strong>@@Supervisor@@</strong></p>
            <p>Position Code/Title: <strong>@@Position@@ (WLS @@WLS@@)</strong></p>
            <p>Department Name: <strong>@@Department@@</strong></p>
            <p>Hours per Week (Total Contracted Hours for Break Periods): <strong>@@Hours@@</strong></p>
            <p>Begin Date: <strong>@@Date@@</strong></p>
            
            <p><strong>Please review the labor contract and respond using the following link:</strong></p>
            <p><a href="@@StudentConfirmationLink@@">Click here to approve or deny the labor contract</a></p>

            <p>Your approval or denial is required to process this contract. After @@StudentConfirmationExpiration@@ the contract will be considered denied and your supervisor will need to submit a new contract, if the position is still available.
            
            <p>If you have any further questions or concerns, contact our Labor Program Office at labor_program@berea.edu or call us at ext. 3611.</p>
            
            <p>Sincerely,</p>
            <p>Labor Program Office</p>
            <p>labor_program@berea.edu</p>
            <p>859-985-3611</p>'
WHERE purpose = 'Labor Status Form Submitted For Student';

-- TODO Supervisor email template

COMMIT;
