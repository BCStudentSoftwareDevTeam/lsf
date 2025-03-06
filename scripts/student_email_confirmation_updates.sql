BEGIN;
-- Update Denied statuses

INSERT INTO status ('Denied by Admin');
INSERT INTO status ('Denied by Student');

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
            <p><strong>ACTION IS REQUIRED - This offer will EXPIRE in 14 days.</strong></p>
            <p>This email is very important. Please take a moment to read carefully and review the information. 
            A Labor Status Form has been submitted by @@Creator@@ for you, for a position supervised by <strong>@@Supervisor@@.</strong></p>
            
            <p>The submission of this form is an offer that you must respond to before it is reviewed by the Labor Program Office. 
            By hitting "Accept", you agree to the labor status form details below. Please be aware that once an offer is accepted, 
            the offer is locked in. You and your supervisor must mutually agree to a release once the offer has been accepted. 
            Any mutual releases or adjustments must happen before the labor position change deadline listed on the academic calendar.</p>
            
            <p>If you do not accept the terms of this form, please deny the position. If you believe that some of the information 
            in this contract is correct, but some of it is incorrect, do not accept the contract. The form will have to be denied, 
            and your supervisor will have to submit a new contract.</p>
            
            <p><strong>NOTICE:</strong> This does not mean your position is active to begin work, only a status form has been submitted to await approval.</p>
            
            <p><strong>Labor Status Form Information:</strong></p>
            <p>Student Name: <strong>@@Student@@ @@StudB@@</strong></p>
            <p>Supervisor: <strong>@@Supervisor@@</strong></p>
            <p>Position Code/Title: <strong>@@Position@@</strong></p>
            <p>Department Name: <strong>@@Department@@</strong></p>
            <p>Hours per Week (Total Contracted Hours for Break Periods): <strong>@@Hours@@</strong></p>
            <p>Begin Date: <strong>@@Date@@</strong></p>
            
            <p><strong>Please review the labor contract and respond using the following link:</strong></p>
            <p><a href="@@StudentConfirmationLink@@">Click here to approve or deny the labor contract</a></p>
            
            <p>If you have any further questions or concerns, contact our Labor Program Office at labor_program@berea.edu or call us at ext. 3611.</p>
            
            <p>Sincerely,</p>
            <p>Labor Program Office</p>
            <p>labor_program@berea.edu</p>
            <p>859-985-3611</p>'
WHERE purpose = 'Labor Status Form Submitted For Student';

-- TODO Supervisor email template

COMMIT;
