
pem init

# See: https://stackoverflow.com/questions/394230/how-to-detect-the-os-from-a-bash-script/18434831
if [[ "$OSTYPE" == "linux-gnu" ]]; then
        # Linux
    sed -i 's/migrations/lsf_migrations/g' migrations.json
elif [[ "$OSTYPE" == "darwin"* ]]; then
        # Mac OSX
    sed -i '' 's/migrations/lsf_migrations/g' migrations.json
fi

#pem add app.models.[filename].[classname]
pem add app.models.user.User
pem add app.models.laborStatusForm.LaborStatusForm
pem add app.models.laborReleaseForm.LaborReleaseForm
pem add app.models.term.Term
pem add app.models.department.Department
pem add app.models.emailTemplate.EmailTemplate
pem add app.models.formHistory.FormHistory
pem add app.models.adjustedForm.AdjustedForm
pem add app.models.overloadForm.OverloadForm
pem add app.models.status.Status
pem add app.models.student.Student
pem add app.models.historyType.HistoryType
pem add app.models.visitTracker.VisitTracker
pem add app.models.emailTracker.EmailTracker
pem add app.models.notes.Notes
pem add app.models.supervisor.Supervisor
pem add app.models.studentLaborEvaluation.StudentLaborEvaluation
pem watch
pem migrate
