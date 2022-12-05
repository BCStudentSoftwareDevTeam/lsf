-- Note: Single quotes are ok, double quotes are not. Queries must be one-liners

-- Randomize evaluation scores
UPDATE studentlaborevaluation SET attendance_score=FLOOR(RAND() * (20-1) + 1), accountability_score=FLOOR(RAND() * (10-1) + 1), teamwork_score=FLOOR(RAND() * (10-1) + 1), initiative_score=FLOOR(RAND() * (10-1) + 1), respect_score=FLOOR(RAND() * (10-1) + 1), learning_score=FLOOR(RAND() * (20-1) + 1), jobSpecific_score=FLOOR(RAND() * (20-1) + 1)

-- Remove comments and notes
UPDATE formhistory set rejectReason=CASE WHEN LENGTH(rejectReason)>0 THEN '<redacted>' ELSE '' END
UPDATE overloadform set studentOverloadReason=CASE WHEN LENGTH(studentOverloadReason)>0 THEN '<redacted>' ELSE '' END
UPDATE laborreleaseform set reasonForRelease=CASE WHEN LENGTH(reasonForRelease)>0 THEN '<redacted>' ELSE '' END
UPDATE laborstatusform set supervisorNotes=CASE WHEN LENGTH(supervisorNotes)>0 THEN '<redacted>' ELSE '' END
UPDATE laborstatusform set laborDepartmentNotes=CASE WHEN LENGTH(laborDepartmentNotes)>0 THEN '<redacted>' ELSE '' END
UPDATE notes set notesContents='Notes are not visible except in the production environment'

UPDATE studentlaborevaluation SET attendance_comment=CASE WHEN LENGTH(attendance_comment)>0 THEN '<redacted>' ELSE '' END, accountability_comment=CASE WHEN LENGTH(accountability_comment)>0 THEN '<redacted>' ELSE '' END, teamwork_comment=CASE WHEN LENGTH(teamwork_comment)>0 THEN '<redacted>' ELSE '' END, initiative_comment=CASE WHEN LENGTH(initiative_comment)>0 THEN '<redacted>' ELSE '' END, respect_comment=CASE WHEN LENGTH(respect_comment)>0 THEN '<redacted>' ELSE '' END, learning_comment=CASE WHEN LENGTH(learning_comment)>0 THEN '<redacted>' ELSE '' END, jobSpecific_comment=CASE WHEN LENGTH(jobSpecific_comment)>0 THEN '<redacted>' ELSE '' END, transcript_comment=CASE WHEN LENGTH(transcript_comment)>0 THEN '<redacted>' ELSE '' END
