from groups.models import Group, Code, AssignationMessengerUser, BotAssignation, ProgramAssignation
from django.contrib import admin

admin.site.register(Group)
admin.site.register(Code)
admin.site.register(AssignationMessengerUser)
admin.site.register(ProgramAssignation)
admin.site.register(BotAssignation)
