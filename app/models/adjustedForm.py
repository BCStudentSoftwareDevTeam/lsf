from app.models import *
from app.models.laborStatusForm import LaborStatusForm

# For each adjustment made to an existing approved LSF, a new entry appears in this table
# Adjustments to pending LSFs do not go on this table! The changes go directly to the LaborStatusForm table
class AdjustedForm(baseModel):
    adjustedFormID          = PrimaryKeyField()
    lsfId                   = ForeignKeyField(LaborStatusForm, backref='adjusted_forms', column_name='lsfId')
    fieldAdjusted           = CharField()
    oldValue                = CharField()
    newValue                = CharField()
    effectiveDate           = DateField()
