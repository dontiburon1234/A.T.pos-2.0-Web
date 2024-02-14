from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Empresa, Usuario, Almacen, Caja, Categoria, UnidadMedida

class EmpresaAdmin(admin.ModelAdmin):
    pass

class UsuarioAdmin(admin.ModelAdmin):
    pass

admin.site.register(Empresa, EmpresaAdmin)
admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(Almacen)
admin.site.register(Caja)
admin.site.register(Categoria)
admin.site.register(UnidadMedida)