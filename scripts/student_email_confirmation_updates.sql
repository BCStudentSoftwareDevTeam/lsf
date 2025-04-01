BEGIN;

-- Update Denied statuses

-- INSERT INTO status VALUES ('Denied by Admin');
-- INSERT INTO status VALUES ('Denied by Student');

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

-- Update email template for Secondary Labor Position for Students

UPDATE emailtemplate 
SET 
    subject = 'Labor Status Form Received',
    body = '<p>Dear <strong>@@Student@@</strong>,</p>\n
             <p><strong>ACTION IS REQUIRED - This offer will EXPIRE on @@StudentConfirmationExpiration@@.</strong></p>\n\n

            <p>This email is very important. Please take a moment to read carefully and review the information. 
            A Labor Status Form for a Secondary Position has been submitted by @@Creator@@ for you, for a position supervised by <strong>@@Supervisor@@.</strong></p>

            <p><strong>Labor Status Form Information:</strong></p>
            <p>Student&#39;s Name and B-number: <strong>@@Student@@</strong>, <strong>@@StudB@@</strong></p>
            <p>Position Code/Title: <strong>@@Position@@</strong></p>
            <p>WLS Level: <strong>@@WLS@@</strong></p>
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
WHERE purpose = 'Secondary Position Labor Status Form Submitted';

-- Update email template for Secondary Labor Position for Supervisors

UPDATE emailtemplate 
SET 
    subject = 'Labor Status Form Received',
    body = '<p>Dear <strong>@@Supervisor@@</strong>&nbsp;and <strong>@@PrimarySupervisor@@</strong>,</p>

            <p>This email is confirmation that the Labor Program Office has received a Labor Status Form for a secondary position submitted by <strong>@@Creator@@, </strong>for <strong>@@Student@@ </strong>under the supervision of <strong>@@Supervisor@@</strong>.
            Please take a moment to read carefully and review the information. Below is the position information for the student you have requested to hire.</p><p><strong>Primary Supervisors reserve the right to reject secondary positions.</strong></p>
            
            <p>The student has until <strong>@@StudentConfirmationExpiration@@</strong> to accept or deny this position. After that time the contract will be denied and a new labor status form will need to be submitted if you still wish to work with the student.</p>

            <p>NOTICE: This does not mean the position is active to begin work, only a status form has been submitted to await approval. Once this position has been approved, the student’s job will be active to allow for time entry in 24 hours. If at that time, the student cannot clock in, please contact the Labor Program Office immediately.</p>
            <p>If you have any further questions or concerns, contact the Labor Program Office at ext. 3611.</p>

            <p><strong>Labor Status Form Information:</strong></p>
            <p>Student&#39;s Name and B-number: <strong>@@Student@@</strong>, <strong>@@StudB@@</strong></p>
            <p>Position Code/Title: <strong>@@Position@@</strong></p>
            <p>WLS Level: <strong>@@WLS@@</strong></p>
            <p>Department Name: <strong>@@Department@@</strong></p>
            <p>Hours per Week (Total Contracted Hours for Break Periods): <strong>@@Hours@@</strong></p>
            <p>Begin Date: <strong>@@Date@@</strong></p>
            
            <p>If you have any further questions or concerns, contact our Labor Program Office at labor_program@berea.edu or call us at&nbsp;ext. 3611.</p>
            
            <p>Sincerely,</p>
            <p>Labor Program Office</p>
            <p>labor_program@berea.edu</p>
            <p>859-985-3611</p>'
WHERE purpose = 'Secondary Position Labor Status Form Submitted';

-- Update Supervisor email template

UPDATE emailtemplate
SET
    body = '
<p>Dear @@Supervisor@@,</p>

<p>ATTN:</p>

<p>This email is confirmation that the Labor Program Office has received a Labor Status Form by <strong>@@Creator@@</strong> for <strong>@@Student@@</strong>. Please take a moment to read carefully and review the information below.</p>

<p>The student has until <strong>@@StudentConfirmationExpiration@@</strong> to accept or deny this position. After that time the contract will be denied and a new labor status form will need to be submitted if you still wish to work with the student.</p>

<p>NOTICE: This does not mean the position is active to begin work, only a status form has been submitted to await approval. Once this position has been approved, the student’s job will be active to allow for time entry in 24 hours. If at that time, the student cannot clock in, please contact the Labor Program Office immediately.</p>
<p>If you have any further questions or concerns, contact the Labor Program Office at ext. 3611.</p>

<h3>Labor Status Form Information:</h3>
<p>Student Name and B-number: <strong>@@Student@@, @@StudB@@</strong></p>
<p>Supervisor: <strong>@@Supervisor@@</strong></p>
<p>Position Code/Title: <strong>@@Position@@</strong></p>
<p>WLS Level: <strong>@@WLS@@</strong></p>
<p>Department Name: <strong>@@Department@@</strong></p>
<p>Hours per Week (Total Contracted Hours for Break Periods): <strong>@@Hours@@</strong></p>
<p>Begin Date: <strong>@@Date@@</strong></p>
<br>
<p>Sincerely,</p>
<p>Labor Program Office</p>
<p>labor_program@berea.edu</p>
<p>859-985-3611</p>'
WHERE purpose = 'Primary Position Labor Status Form Submitted';

UPDATE emailtemplate 
SET 
    subject = 'ACTION REQUIRED - Labor Status Form Received',
    body = '<p>Dear <strong>@@Student@@</strong>,</p>
            <p><strong>ACTION IS REQUIRED - This offer will EXPIRE on @@StudentConfirmationExpiration@@.</strong></p>

            <p>This email is very important. Please take a moment to read carefully and review the information. 
            A Labor Status Form has been submitted by @@Creator@@ for you, for a position supervised by <strong>@@Supervisor@@.</strong></p>

            <p>NOTICE: Please be aware that you are only allowed to work maximum of 40 hours per week if you are not taking any classes.</p>
            
            <p><strong>Labor Status Form Information:</strong></p>
            <p>Student Name: <strong>@@Student@@ @@StudB@@</strong></p>
            <p>Supervisor: <strong>@@Supervisor@@</strong></p>
            <p>Position Code/Title: <strong>@@Position@@ (WLS @@WLS@@)</strong></p>
            <p>Department Name: <strong>@@Department@@</strong></p>
            <p>Total Contracted Hours for Break Periods: <strong>@@Hours@@</strong></p>
            <p>Begin Date: <strong>@@Date@@</strong></p>
            
            <p><strong>Please review the labor contract and respond using the following link:</strong></p>
            <p><a href="@@StudentConfirmationLink@@">Click here to approve or deny the labor contract</a></p>

            <p>Your approval or denial is required to process this contract. After @@StudentConfirmationExpiration@@ the contract will be considered denied and your supervisor will need to submit a new contract, if the position is still available.
            
            <p>If you have any further questions or concerns, contact our Labor Program Office at labor_program@berea.edu or call us at ext. 3611.</p>
            
            <p>Sincerely,</p>
            <p>Labor Program Office</p>
            <p>labor_program@berea.edu</p>
            <p>859-985-3611</p>'
WHERE purpose = 'Break Labor Status Form Submitted For Student';

-- Supervisor email template

UPDATE emailtemplate
SET
    body = '
<p>Dear @@Supervisor@@,</p>

<p>ATTN:</p>

<p>This email is confirmation that the Labor Program Office has received a Break Labor Status Form by <strong>@@Creator@@</strong> for <strong>@@Student@@</strong>. Please take a moment to read carefully and review the information below.</p>

<p>The student has until <strong>@@StudentConfirmationExpiration@@</strong> to accept or deny this position. After that time the contract will be denied and a new labor status form will need to be submitted if you still wish to work with the student.</p>

<p>NOTICE: This does not mean the position is active to begin work, only a status form has been submitted to await approval. Once this position has been approved, the student’s job will be active to allow for time entry in 24 hours. If at that time, the student cannot clock in, please contact the Labor Program Office immediately.</p>
<p>If you have any further questions or concerns, contact the Labor Program Office at ext. 3611.</p>

<h3>Labor Status Form Information:</h3>
<p>Student Name and B-number: <strong>@@Student@@, @@StudB@@</strong></p>
<p>Supervisor: <strong>@@Supervisor@@</strong></p>
<p>Position Code/Title: <strong>@@Position@@</strong></p>
<p>WLS Level: <strong>@@WLS@@</strong></p>
<p>Department Name: <strong>@@Department@@</strong></p>
<p>Total Contracted Hours for Break Periods: <strong>@@Hours@@</strong></p>
<p>Begin Date: <strong>@@Date@@</strong></p>
<br>
<p>Sincerely,</p>
<p>Labor Program Office</p>
<p>labor_program@berea.edu</p>
<p>859-985-3611</p>'
WHERE purpose = 'Break Labor Status Form Submitted For Supervisor';

COMMIT;
