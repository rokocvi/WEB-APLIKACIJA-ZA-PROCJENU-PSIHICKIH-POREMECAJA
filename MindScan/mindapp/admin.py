from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from .models import Lijecnik, PsiholoskiTest, Notifikacija, Pacijent

@admin.register(Lijecnik)
class LijecnikAdmin(admin.ModelAdmin):
    list_display = ['ime', 'prezime', 'email', 'telefon', 'strucnost', 'lokacija', 'dostupnost', 'odobren']
    list_filter = ['strucnost', 'odobren', 'dostupnost']
    search_fields = ['ime', 'prezime', 'email']
    fieldsets = (
        (None, {
            'fields': (
                'ime', 'prezime', 'email', 'telefon',
                'strucnost', 'lokacija', 'opis',
                'dostupnost', 'odobren', 'verifikacijski_dokument'
            )
        }),
    )

@admin.register(PsiholoskiTest)
class PsiholoskiTestAdmin(admin.ModelAdmin):
    list_display = ['user', 'datum', 'predikcija']

@admin.register(Notifikacija)
class NotifikacijaAdmin(admin.ModelAdmin):
    list_display = ['korisnik', 'poruka', 'procitano', 'datum']

class PacijentAdmin(DefaultUserAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # filtrira da vidiš samo obične korisnike (ne staff i ne superuser)
        return qs.filter(is_staff=False, is_superuser=False)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        from django.contrib.auth.models import Group
        grupa, _ = Group.objects.get_or_create(name='Pacijenti')
        obj.groups.add(grupa)
        obj.save()

admin.site.register(Pacijent, PacijentAdmin)
