from django.contrib import admin
from .models import Static

# Register your models here.
class StaticAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug','language', 'updated_by', 'created_at', 'updated_at']
    list_per_page = 20

    def updated_by(self, obj):
        return "{} {}".format(obj.user.first_name, obj.user.last_name)


admin.site.register(Static, StaticAdmin)
