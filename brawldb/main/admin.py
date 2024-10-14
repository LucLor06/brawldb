from django.contrib import admin
from . import models

admin.site.register(models.Combo)
admin.site.register(models.Legend)
admin.site.register(models.Weapon)
admin.site.register(models.Modifier)
admin.site.register(models.Move)
admin.site.register(models.Attack)
admin.site.register(models.Patch)
admin.site.register(models.Change)