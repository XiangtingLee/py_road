from django.contrib import admin
from position.models.company.size import CompanySize
from position.models.company.regStatus import CompanyRegStatus
from position.models.company.financing import CompanyFinancing
from position.models.company.industry import CompanyIndustries
from position.models.company.label import CompanyLabels
from position.models.position.type import PositionType
from position.models.position.education import PositionEducation
from position.models.position.experience import PositionExperience
from position.models.position.label import PositionLabels

# Register your models here.
admin.site.register(CompanySize)
admin.site.register(CompanyRegStatus)
admin.site.register(CompanyFinancing)
admin.site.register(CompanyIndustries)
admin.site.register(CompanyLabels)
admin.site.register(PositionType)
admin.site.register(PositionEducation)
admin.site.register(PositionExperience)
admin.site.register(PositionLabels)
