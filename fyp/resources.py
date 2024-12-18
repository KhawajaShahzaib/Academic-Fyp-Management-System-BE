from import_export import resources
from .models import TimetableEntry

class TimetableEntryResource(resources.ModelResource):
    class meta:
        model = TimetableEntry
        