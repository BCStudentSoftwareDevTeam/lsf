from app.models.status import Status
from app.models.historyType import HistoryType
from app.models.emailTemplate import EmailTemplate
from app.models.user import User
from app.models.user import Supervisor

print("Inserting base data for all environments")

#############################
# Status
#############################
stats = [
            {"statusName":"Pending" },
            {"statusName":"Approved" },
            {"statusName":"Denied by Admin" },
            {"statusName":"Denied by Student" },
            {"statusName":"Pre-Student Approval" }
        ]
Status.insert_many(stats).on_conflict_replace().execute()
print(" * status added")

#############################
# History Type
#############################
types = [
            {"historyTypeName":"Labor Status Form"
            },
            {"historyTypeName":"Labor Overload Form"
            },
            {"historyTypeName":"Labor Release Form"
            },
            {"historyTypeName":"Labor Adjustment Form"
            }
        ]
HistoryType.insert_many(types).on_conflict_replace().execute()
print(" * history types added")

#############################
#emailtemplates
#############################
emailtemps= [
                {
                "purpose":"Labor Status Form Submitted For Student",
                "formType":"Labor Status Form",
                "action":"Submitted",
                "subject":"Labor Status Form Received",
                "body":'''<p>Dear <strong>@@Student@@</strong>,</p>
                            <p>&nbsp;</p>
                            <p>This email is very important. Please take a moment to read carefully and review the information. A Labor Status Form has been submitted for you by <strong>@@Creator@@</strong>. Below is the position information for which you have been hired. If you do not accept the terms of this form, you will have 24 hours to contact the supervisor or Berea's Work College Program Office. If we do not hear from you within 24 hours of this notification, it will be determined that it is accepted and the forms will be processed as submitted.</p>
                            <p>&nbsp;</p>
                            <p><strong>NOTICE:</strong> This does not mean your position is active to begin work, only a status form has been submitted to await approval. Once this position has been approved, your job will be active to allow for time entry in 24 hours. If at that time, you cannot clock in, please contact Berea's Work College Program Office immediately.</p>
                            <p>&nbsp;</p>
                            <p>If you have any further questions or concerns, contact Berea's Work College Program Office at ext. 3611.</p>
                            <p>&nbsp;</p>
                            <p>&nbsp;</p>
                            <p><strong>Labor Status Form Information:</strong></p>
                            <p>Position Code/Title: <strong>@@Position@@</strong></p>
                            <p>Department Name: <strong>@@Department@@</strong></p>
                            <p>Hours per Week (Total Contracted Hours for Break Periods): <strong>@@Hours@@</strong></p>
                            <p>Begin Date: <strong>@@Date@@</strong></p>
                            <p>&nbsp;</p>
                            <p>&nbsp;</p>
                            <p>Sincerely,</p>
                            <p>Berea's Work College Program Office</p>
                            <p>labor_program@berea.edu</p>
                            <p>859-985-3611</p>''',

                "audience":"Student"
                 },
                {
                "purpose":"Secondary Position Labor Status Form Submitted",
                "formType":"Secondary Labor Status Form",
                "action":"Submitted",
                "subject":"Labor Status Form Received",
                "body":'''<p>Dear <strong>@@Supervisor@@</strong> and <strong>@@PrimarySupervisor@@</strong>,</p>
                            <p>&nbsp;</p>
                            <p>This email is confirmation that Berea's Work College Program Office has received a Labor Status Form for a secondary position by
                            <strong>@@Supervisor@@</strong> for <strong>@@Student@@</strong>.Please take a moment to read carefully and review the information. Below is the position information for the student you have requested to hire.</p>
                            <p>&nbsp;</p>
                            <p><strong>NOTICE:</strong> This does not mean your position is active to begin work, only a status form has been submitted to await approval. Once this position has been approved, the student’s job will be active to allow for time entry in 24 hours. If at that time, the student cannot clock in, please contact Berea's Work College Program Office immediately.</p>
                            <p>&nbsp;</p>
                            <p>If you have any further questions or concerns, contact Berea's Work College Program Office at ext. 3611.</p>
                            <p>&nbsp;</p>
                            <p>&nbsp;</p>
                            <p><strong>Labor Status Form Information:</strong></p>
                            <p>Student's Name and B-number: <strong>@@Student@@</strong>, <strong>@@StudB@@</strong></p>
                            <p>Position Code/Title: <strong>@@Position@@</strong></p>
                            <p>WLS Level: <strong>@@WLS@@</strong></p>
                            <p>Department Name: <strong>@@Department@@</strong></p>
                            <p>Hours per Week (Total Contracted Hours for Break Periods): <strong>@@Hours@@</strong></p>
                            <p>Begin Date: <strong>@@Date@@</strong></p>
                            <p>&nbsp;</p>
                            <p>&nbsp;</p>
                            <p>Sincerely,</p>
                            <p>Berea's Work College Program Office</p>
                            <p>labor_program@berea.edu</p>
                            <p>859-985-3611</p>
                            ''',
                "audience":"Supervisor"
                },
                {
                "purpose":"Primary Position Labor Status Form Submitted",
                "formType":"Labor Status Form",
                "action":"Submitted",
                "subject":"Labor Status Form Received",
                "body":'''<p>Dear <strong>@@Supervisor@@</strong>,</p>
                            <p>&nbsp;</p>
                            <p>This email is confirmation that Berea's Work College Program Office has received a Labor Status Form by
                            <strong>@@Creator@@</strong> for <strong>@@Student@@</strong>. Please take a moment to read carefully and review the information Below is the position information for the student you have requested to hire.</p>
                            <p>&nbsp;</p>
                            <p><strong>NOTICE:</strong> This does not mean your position is active to begin work, only a status form has been submitted to await approval. Once this position has been approved, the student’s job will be active to allow for time entry in 24 hours. If at that time, the student cannot clock in, please contact Berea's Work College Program Office immediately.</p>
                            <p>&nbsp;</p>
                            <p>If you have any further questions or concerns, contact Berea's Work College Program Office at ext. 3611.</p>
                            <p>&nbsp;</p>
                            <p>&nbsp;</p>
                            <p><strong>Labor Status Form Information:</strong></p>
                            <p>Student's Name and B-number: <strong>@@Student@@</strong>, <strong>@@StudB@@</strong></p>
                            <p>Position Code/Title: <strong>@@Position@@</strong></p>
                            <p>WLS Level: <strong>@@WLS@@</strong></p>
                            <p>Department Name: <strong>@@Department@@</strong></p>
                            <p>Hours per Week (Total Contracted Hours for Break Periods): <strong>@@Hours@@</strong></p>
                            <p>Begin Date: <strong>@@Date@@</strong></p>
                            <p>&nbsp;</p>
                            <p>&nbsp;</p>
                            <p>Sincerely,</p>
                            <p>Berea's Work College Program Office</p>
                            <p>labor_program@berea.edu</p>
                            <p>859-985-3611</p>
                            ''',
                "audience":"Supervisor"
                },
                #LSF approved
                {
                "purpose":"Labor Status Form Approved For Student",
                "formType":"Labor Status Form",
                "action":"Approved",
                "subject":"Labor Status Form Approved",
                "body":'''<p>Dear <strong>@@Student@@</strong>,</p>
                            <p>&nbsp;</p>
                            <p>A Labor This email is very important. Please take a moment to read carefully and review the information. A Labor Release Form previously submitted for you by <strong>@@Student@@</strong> has been <strong>Approved</strong>. You will no longer be able to record time in this position effective of the release date below. If you have concerns, please contact the supervisor or Berea's Work College Program Office immediately.</p>
                            <p>&nbsp;</p>
                            <p><strong>NOTICE:</strong> Please allow 24 hours for the position to become active in Tracy (Ultratime). Students should not work until time can be recorded for the position. If at any time, the student cannot clock in, please contact Berea's Work College Program Office immediately.</p>
                            <p>&nbsp;</p>
                            <p>If you have any further questions or concerns, contact Berea's Work College Program Office at ext. 3611.</p>
                            <p>&nbsp;</p>
                            <p>&nbsp;</p>
                            <p><strong>Labor Status Form Information:</strong></p>
                            <p>Student's Name and B-number: <strong>@@Student@@</strong>, <strong>@@StudB@@</strong></p>
                            <p>Position Code/Title: <strong>@@Position@@</strong></p>
                            <p>WLS Level: <strong>@@WLS@@</strong></p>
                            <p>Department Name: <strong>@@Department@@</strong></p>
                            <p>Hours per Week (Total Contracted Hours for Break Periods): <strong>@@Hours@@</strong></p>
                            <p>Begin Date: <strong>@@Date@@</strong></p>
                            <p>&nbsp;</p>
                            <p>&nbsp;</p>
                            <p>Sincerely,</p>
                            <p>Berea's Work College Program Office</p>
                            <p>labor_program@berea.edu</p>
                            <p>859-985-3611</p>
                            ''',
                "audience":"Student"
                },
                {
                "purpose":"Primary Position Labor Status Form Approved",
                "formType":"Labor Status Form",
                "action":"Approved",
                "subject":"Labor Status Form Approved",
                "body":'''<p>Dear <strong>@@Supervisor@@</strong>,</p>
                            <p>&nbsp;</p>
                            <p>A Labor Status Form previously submitted by you for
                            <strong>@@Student@@</strong> has been <strong>Approved</strong>. Below is the position information for the student that you have hired.</p>
                            <p>&nbsp;</p>
                            <p><strong>NOTICE:</strong> Please allow 24 hours for the position to become active in Tracy (Ultratime). Students should not work until time can be recorded for the position. If at any time, the student cannot clock in, please contact Berea's Work College Program Office immediately.</p>
                            <p>&nbsp;</p>
                            <p>If you have any further questions or concerns, contact Berea's Work College Program Office at ext. 3611.</p>
                            <p>&nbsp;</p>
                            <p>&nbsp;</p>
                            <p><strong>Labor Status Form Information:</strong></p>
                            <p>Student's Name and B-number: <strong>@@Student@@</strong>, <strong>@@StudB@@</strong></p>
                            <p>Position Code/Title: <strong>@@Position@@</strong></p>
                            <p>WLS Level: <strong>@@WLS@@</strong></p>
                            <p>Department Name: <strong>@@Department@@</strong></p>
                            <p>Hours per Week (Total Contracted Hours for Break Periods): <strong>@@Hours@@</strong></p>
                            <p>Begin Date: <strong>@@Date@@</strong></p>
                            <p>&nbsp;</p>
                            <p>&nbsp;</p>
                            <p>Sincerely,</p>
                            <p>Berea's Work College Program Office</p>
                            <p>labor_program@berea.edu</p>
                            <p>859-985-3611</p>
                            ''',
                "audience":"Supervisor"
                },

                {
                "purpose":"Secondary Position Labor Status Form Approved",
                "formType":"Secondary Labor Status Form",
                "action":"Approved",
                "subject":"Labor Status Form Approved",
                "body":'''

                            ''',
                "audience":"Supervisor"
                },
                #LSF Rejected
                {
                "purpose":"Labor Status Form Rejected For Student",
                "formType":"Labor Status Form",
                "action":"Rejected",
                "subject":"Labor Status Form Rejected",
                "body":'''
                            ''',
                "audience":"Student"
                },
                {
                "purpose":"Secondary Position Labor Status Form Rejected",
                "formType":"Secondary Labor Status Form",
                "action":"Rejected",
                "subject":"Labor Status Form Rejected",
                "body":'''<p>Dear <strong>@@Supervisor@@</strong> and <strong>@@PrimarySupervisor@@</strong>,</p>
                            <p>&nbsp;</p>
                            <p>A Labor Status Form previously submitted by you for
                            <strong>@@Student@@</strong>, <strong>@@StudB@@</strong> hiring him/her to work in a secondary position has been Denied. This is an informational email to you as the supervisor for the primary labor position.</p>
                            <p>&nbsp;</p>

                            <p>&nbsp;</p>
                            <p><strong>Labor Status Form Information:</strong></p>
                            <p>Student's Name and B-number: <strong>@@Student@@</strong>, <strong>@@StudB@@</strong></p>
                            <p>Position Code/Title: <strong>@@Position@@</strong></p>
                            <p>WLS Level: <strong>@@WLS@@</strong></p>
                            <p>Department Name: <strong>@@Department@@</strong></p>
                            <p>Hours per Week (Total Contracted Hours for Break Periods): <strong>@@Hours@@</strong></p>
                            <p>Begin Date: <strong>@@Date@@</strong></p>
                            <p>&nbsp;</p>
                            <p>&nbsp;</p>
                            <p>Sincerely,</p>
                            <p>Berea's Work College Program Office</p>
                            <p>labor_program@berea.edu</p>
                            <p>859-985-3611</p>
                            ''',
                "audience":"Supervisor"
                },
                {
                "purpose":"Primary Position Labor Status Form Rejected",
                "formType":"Labor Status Form",
                "action":"Rejected",
                "subject":"Labor Status Form Rejected",
                "body":'''
                            ''',
                "audience":"Supervisor"
                },
                #LSF modified
                {
                "purpose":"Labor Status Form Adjusted For Student",
                "formType":"Labor Status Form",
                "action":"Adjusted",
                "subject":"Labor Status Form Adjusted",
                "body":'''
                            ''',
                "audience":"Student"
                },
                {
                "purpose":"Labor Status Form Adjusted For Supervisor",
                "formType":"Labor Status Form",
                "action":"Adjusted",
                "subject":"Labor Status Form Adjusted",
                "body":'''
                            ''',
                "audience":"Supervisor"
                },
                #LRF Submitted
                {
                "purpose":"Labor Release Form Submitted For Student",
                "formType":"Labor Release Form",
                "action":"Submitted",
                "subject":"Labor Release Form Submitted",
                "body":'''
                            ''',
                "audience":"Student"
                },
                {
                "purpose":"Labor Release Form Submitted For Supervisor",
                "formType":"Labor Release Form",
                "action":"Submitted",
                "subject":"Labor Release Form Submitted",
                "body":'''
                            ''',
                "audience":"Supervisor"
                },
                #LRF approved

                {
                "purpose":"Labor Release Form Approved For Student",
                "formType":"Labor Release Form",
                "action":"Approved",
                "subject":"Labor Release Form Approved",
                "body":'''<p>Dear <strong>@@Student@@</strong>,</p>
                            <p>&nbsp;</p>
                            <p>This email is very important. Please take a moment to read carefully and review the information. A Labor Release Form previously submitted for you by <strong>@@Supervisor@@</strong> has been <strong>Approved</strong>. You will no longer be able to record time in this position effective of the release date below. If you have concerns, please contact the supervisor or Berea's Work College Program Office immediately.</p>
                            <p>&nbsp;</p>
                            <p>If you have any further questions or concerns, contact Berea's Work College Program Office at ext. 3611.</p>
                            <p>&nbsp;</p>
                            <p>&nbsp;</p>
                            <p><strong>Labor Status Form Information:</strong></p>
                            <p>Student's Name and B-number: <strong>@@Student@@</strong>, <strong>@@StudB@@</strong></p>
                            <p>Position Code/Title: <strong>@@Position@@</strong></p>
                            <p>WLS Level: <strong>@@WLS@@</strong></p>
                            <p>Department Name: <strong>@@Department@@</strong></p>
                            <p>Release Date: <strong>@@ReleaseDate@@</strong></p>
                            <p>Reason for Release:: <strong>@@ReleaseReason@@</strong></p>
                            <p>&nbsp;</p>
                            <p>&nbsp;</p>
                            <p>Sincerely,</p>
                            <p>Berea's Work College Program Office</p>
                            <p>labor_program@berea.edu</p>
                            <p>859-985-3611</p>
                            ''',
                "audience":"Student"
                },
                {
                "purpose":"Labor Release Form Approved For Supervisor",
                "formType":"Labor Release Form",
                "action":"Approved",
                "subject":"Labor Release Form Approved",
                "body":'''
                            ''',
                "audience":"Supervisor"
                },
                #LRF Rejected
                {
                "purpose":"Labor Release Form Rejected For Student",
                "formType":"Labor Release Form",
                "action":"Rejected",
                "subject":"Labor Release Form Rejected",
                "body":'''
                            ''',
                "audience":"Student"
                },
                {
                "purpose":"Labor Release Form Rejected For Supervisor",
                "formType":"Labor Release Form",
                "action":"Rejected",
                "subject":"Labor Release Form Rejected",
                "body":'''
                            ''',
                "audience":"Supervisor"
                },
                #LOF
                {
                "purpose":"Labor Overload Form Submitted For Student",
                "formType":"Labor Overload Form",
                "action":"Submitted",
                "subject":"Labor Overload Form Submitted",
                "body":'''
                    <p>Dear <strong>@@Student@@</strong>,</p>
                    <p>&nbsp;</p>
                    <p>Please follow the attached link to verify information needed for the approval of an overload form: <a href="@@link@@">@@link@@</a></p>
                    ''',
                "audience":"Student"
                },
                {
                "purpose":"Labor Overload Form Submitted For Supervisor",
                "formType":"Labor Overload Form",
                "action":"Submitted",
                "subject":"Labor Overload Form Submitted",
                "body":'''
                            ''',
                "audience":"Supervisor"
                },
                {
                "purpose":"Labor Overload Form Approved For Student",
                "formType":"Labor Overload Form",
                "action":"Approved",
                "subject":"Labor Overload Form Approved",
                "body":'''
                            ''',
                "audience":"Student"
                },
                {
                "purpose":"Labor Overload Form Approved For Supervisor",
                "formType":"Labor Overload Form",
                "action":"Approved",
                "subject":"Labor Overload Form Approved",
                "body":'''
                            ''',
                "audience":"Supervisor"
                },
                {
                "purpose":"Labor Overload Form Rejected For Student",
                "formType":"Labor Overload Form",
                "action":"Rejected",
                "subject":"Labor Overload Form Rejected",
                "body":'''
                            ''',
                "audience":"Student"
                },
                {
                "purpose":"Labor Overload Form Rejected For Supervisor",
                "formType":"Labor Overload Form",
                "action":"Rejected",
                "subject":"Labor Overload Form Rejected",
                "body":'''
                            ''',
                "audience":"Supervisor"
                },
                #SAAS
                {
                "purpose":"SAAS and Financial Aid Office",
                "formType":"Labor Overload Form",
                "action":"Submitted",
                "subject":"Overload Verification",
                "body":'''
                    <p>Please follow the attached link to verify information needed for the approval of an overload form: <a href="@@link@@">@@link@@</a></p>
                            ''',
                "audience":"SAAS and Financial Aid Office"
                },
                # Break Labor Status Forms
                {
                "purpose":"Break Labor Status Form Submitted For Student",
                "formType":"Break Labor Status Form",
                "action":"Submitted",
                "subject":"Labor Status Form Received",
                "body":'''<p>Dear <strong>@@Student@@</strong>,</p>
                            <p>&nbsp;</p>
                            <p>This email is very important. Please take a moment to read carefully and review the information. A Labor Status Form has been submitted for you by <strong>@@Creator@@</strong>. Below is the position information for which you have been hired. If you do not accept the terms of this form, you will have 24 hours to contact the supervisor or Berea's Work College Program Office. If we do not hear from you within 24 hours of this notification, it will be determined that it is accepted and the forms will be processed as submitted.</p>
                            <p>&nbsp;</p>
                            <p><strong>NOTICE:</strong> This does not mean your position is active to begin work, only a status form has been submitted to await approval. Once this position has been approved, your job will be active to allow for time entry in 24 hours. If at that time, you cannot clock in, please contact Berea's Work College Program Office immediately.</p>
                            <p>&nbsp;</p>
                            <p><strong>NOTICE:</strong> There is already another labor position submitted for you. (put position and x hrs/week???)
                             Please be aware that you are only allowed to work maximum of 40 hours per week if you are not taking any classes.</p>
                            <p>&nbsp;</p>
                            <p>If you have any further questions or concerns, contact Berea's Work College Program Office at ext. 3611.</p>
                            <p>&nbsp;</p>
                            <p>&nbsp;</p>
                            <p><strong>Labor Status Form Information:</strong></p>
                            <p>Position Code/Title: <strong>@@Position@@</strong></p>
                            <p>Department Name: <strong>@@Department@@</strong></p>
                            <p>Hours per Week (Total Contracted Hours for Break Periods): <strong>@@Hours@@</strong></p>
                            <p>Begin Date: <strong>@@Date@@</strong></p>
                            <p>&nbsp;</p>
                            <p>&nbsp;</p>
                            <p>Sincerely,</p>
                            <p>Berea's Work College Program Office</p>
                            <p>labor_program@berea.edu</p>
                            <p>859-985-3611</p>''',
                "audience":"Student"
                },
                {
                "purpose":"Break Labor Status Form Submitted For Supervisor", #Original name: Break Labor Status Form Submitted For Supervisor
                "formType":"Break Labor Status Form",
                "action":"Submitted",
                "subject":"Labor Status Form Received",
                "body":'''<p>Dear <strong>@@Supervisor@@</strong>,</p>
                            <p>&nbsp;</p>
                            <p>This email is confirmation that Berea's Work College Program Office has received a Labor Status Form for Break by
                            <strong>@@Creator@@</strong> for <strong>@@Student@@</strong>. Please take a moment to read carefully and review the information Below is the position information for the student you have requested to hire.</p>
                            <p>&nbsp;</p>
                            <p><strong>NOTICE:</strong> This does not mean your position is active to begin work, only a status form has been submitted to await approval. Once this position has been approved, the student’s job will be active to allow for time entry in 24 hours. If at that time, the student cannot clock in, please contact Berea's Work College Program Office immediately.</p>
                            <p>&nbsp;</p>
                            Please note that students are only allowed to work for a maximum of 40 hours per week.</p>
                            <p>&nbsp;</p>
                            <p>If you have any further questions or concerns, contact Berea's Work College Program Office at ext. 3611.</p>
                            <p>&nbsp;</p>
                            <p>&nbsp;</p>
                            <p><strong>Labor Status Form Information:</strong></p>
                            <p>Student's Name and B-number: <strong>@@Student@@</strong>, <strong>@@StudB@@</strong></p>
                            <p>Position Code/Title: <strong>@@Position@@</strong></p>
                            <p>WLS Level: <strong>@@WLS@@</strong></p>
                            <p>Department Name: <strong>@@Department@@</strong></p>
                            <p>Hours per Week (Total Contracted Hours for Break Periods): <strong>@@Hours@@</strong></p>
                            <p>Begin Date: <strong>@@Date@@</strong></p>
                            <p>&nbsp;</p>
                            <p>&nbsp;</p>
                            <p>Sincerely,</p>
                            <p>Berea's Work College Program Office</p>
                            <p>labor_program@berea.edu</p>
                            <p>859-985-3611</p>
                            ''',
                "audience":"Supervisor"
                },
                {
                "purpose":"Break Labor Status Form Approved for Student",
                "formType":"Break Labor Status Form",
                "action":"Approved",
                "subject":"Labor Status Form Approved",
                "body":'''
                            ''',
                "audience":"Student"
                },
                {"purpose":"Break Labor Status Form Approved For Supervisor",
                "formType":"Break Labor Status Form",
                "action":"Approved",
                "subject":"Labor Status Form Approved",
                "body":'''
                            ''',
                "audience":"Supervisor"
                },
                {
                "purpose":"Break Labor Status Form Rejected for Student",
                "formType":"Break Labor Status Form",
                "action":"Rejected",
                "subject":"Labor Status Form Rejected",
                "body":'''
                            ''',
                "audience":"Student"
                },
                {"purpose":"Break Labor Status Form Rejected For Supervisor",
                "formType":"Break Labor Status Form",
                "action":"Rejected",
                "subject":"Labor Status Form Rejected",
                "body":'''
                            ''',
                "audience":"Supervisor"
                },
                {
                "purpose":"Break Labor Status Form Submitted For Supervisor on Additional LSF", #Original name: Break Labor Status Form Submitted For Supervisor on Second LSF
                "formType":"Additional Break Labor Status Form",
                "action":"Submitted",
                "subject":"Labor Status Form Received",
                "body":'''<p>Dear <strong>@@Supervisor@@</strong>,</p>
                            <p>&nbsp;</p>
                            <p>This email is confirmation that Berea's Work College Program Office has received a Labor Status Form for Break position by
                            <strong>@@Creator@@</strong> for <strong>@@Student@@</strong>. Please take a moment to read carefully and review the information Below is the position information for the student you have requested to hire.</p>
                            <p>&nbsp;</p>
                            <p><strong>NOTICE:</strong> This does not mean your position is active to begin work, only a status form has been submitted to await approval. Once this position has been approved, the student’s job will be active to allow for time entry in 24 hours. If at that time, the student cannot clock in, please contact Berea's Work College Program Office immediately.</p>
                            <p>&nbsp;</p>
                            <p><strong>NOTICE:</strong> <strong>@@Student@@</strong> is already working with <strong>@@PreviousSupervisor(s)@@</strong>.
                            Please note that students are only allowed to work for a maximum of 40 hours per week.</p>
                            <p>&nbsp;</p>
                            <p>If you have any further questions or concerns, contact Berea's Work College Program Office at ext. 3611.</p>
                            <p>&nbsp;</p>
                            <p>&nbsp;</p>
                            <p><strong>Labor Status Form Information:</strong></p>
                            <p>Student's Name and B-number: <strong>@@Student@@</strong>, <strong>@@StudB@@</strong></p>
                            <p>Position Code/Title: <strong>@@Position@@</strong></p>
                            <p>WLS Level: <strong>@@WLS@@</strong></p>
                            <p>Department Name: <strong>@@Department@@</strong></p>
                            <p>Hours per Week (Total Contracted Hours for Break Periods): <strong>@@Hours@@</strong></p>
                            <p>Begin Date: <strong>@@Date@@</strong></p>
                            <p>&nbsp;</p>
                            <p>&nbsp;</p>
                            <p>Sincerely,</p>
                            <p>Berea's Work College Program Office</p>
                            <p>labor_program@berea.edu</p>
                            <p>859-985-3611</p>
                            ''',
                "audience":"Supervisor"
                },
                {"purpose":"Break Labor Status Form Submitted For Additional Supervisor", # Original name: Break Labor Status Form Submitted For Second Supervisor
                "formType":"Additional Break Labor Status Form",
                "action":"Submitted",
                "subject":"Labor Status Form Received",
                "body":'''<p>Dear <strong>@@PreviousSupervisor(s)@@</strong>,</p>
                            <p>&nbsp;</p>
                            <p>This email is notify you that @@Supervisor@@ (@@SupervisorEmail@@) has submitted another labor status form for @@Student@@</p>
                            <p>&nbsp;</p>
                            Please note that students are only allowed to work for a maximum of 40 hours per week.</p>
                            <p>&nbsp;</p>
                            <p>If you have any further questions or concerns, contact Berea's Work College Program Office at ext. 3611.</p>
                            <p>&nbsp;</p>
                            <p><strong>Labor Status Form Information:</strong></p>
                            <p>Student's Name and B-number: <strong>@@Student@@</strong>, <strong>@@StudB@@</strong></p>
                            <p>Position Code/Title: <strong>@@Position@@</strong></p>
                            <p>WLS Level: <strong>@@WLS@@</strong></p>
                            <p>Department Name: <strong>@@Department@@</strong></p>
                            <p>Hours per Week (Total Contracted Hours for Break Periods): <strong>@@Hours@@</strong></p>
                            <p>Begin Date: <strong>@@Date@@</strong></p>
                            <p>&nbsp;</p>
                            <p>&nbsp;</p>
                            <p>Sincerely,</p>
                            <p>Berea's Work College Program Office</p>
                            <p>labor_program@berea.edu</p>
                            <p>859-985-3611</p>
                            ''',
                "audience":"Break Supervisor"
                },
                {"purpose":"Labor Overload Form Submitted Notification For Student",
                "formType":"Labor Overload Form",
                "action":"Notification",
                "subject":"Labor Overload Form Student Reason",
                "body":'',
                "audience":"Student"
                },
                {"purpose":"Labor Overload Form Submitted Notification For Labor Office",
                "formType":"Labor Overload Form",
                "action":"Notification",
                "subject":"Labor Overload Form Student Reason",
                "body":'',
                "audience":"Labor Office"
                }
            ]
EmailTemplate.insert_many(emailtemps).on_conflict_replace().execute()
print(" * emailtemplates added")