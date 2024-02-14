from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.auth.models import User, Group, Permission
from django.contrib.auth.tokens import default_token_generator
from django.views import View
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect, HttpResponse, Http404, JsonResponse
from django.urls import reverse_lazy, reverse
from django.conf import settings
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.db import IntegrityError
from django.db.models import ProtectedError
import datetime
import json
from django.views.generic import (
    TemplateView, 
    CreateView, 
    DetailView,
    ListView,
    UpdateView,
    DeleteView
    )
from .models import (
    Empresa,
    GrupoEmpresa,
    PermisoEmpresa,
    Almacen,
    Caja,
    CajaSerie,
    Categoria,
    UnidadMedida, 
    BaseIVA,
    Articulo,
    CodigoAlterno,
    ListaPrecios
    )
from atpos.forms import (
    CreateUserForm, 
    UpdateUserForm,
    GroupForm,
    PermisoForm,
    DuallistGroupForm,
    CreateCategoriaForm,
    ArticuloForm,
    CodigoAlternoForm
    )

Usuario = get_user_model() # settings.AUTH_USER_MODEL

class CreateAccount(View):

    def get(self, request, *args, **kwargs):
        contexto = {}
        return render(request, 'creation/datos_activation.html', contexto)

    def post(self, request, *args, **kwargs):
        tunombre = request.POST.get('tunombre')
        tucorreo = request.POST.get('tucorreo')
        phone_number = request.POST.get('phone_number')
        empresa = Empresa.objects.get(id=1)
        # TODO validar y enviar el correo de registro de la empresa.
        ue = get_user_model().objects.filter(email=tucorreo)
        if ue:
            print('raise ValueError()')
            messages.error(request, 'El correo ya existe en nuestro sistema')
            return redirect('create_account')
        else:
            u = get_user_model().objects.create(username=tunombre, password='', email=tucorreo, first_name=tunombre, last_name='', empresa=empresa, tel_inicial=phone_number)
            u.save()
            register_client(request, tucorreo)
        contexto = {}
        return render(request, 'creation/activation_email_done.html', contexto)

def register_client(request, cliente_email):
    # Generar el token de activación
    # print(cliente_email)
    user = get_user_model().objects.get(email=cliente_email)  # Suponiendo que cliente_email es el correo del nuevo cliente
    # print(user)
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))

    # Crear el enlace de activación
    protocol = 'http' # if request.is_secure() else 'https'
    domain = request.get_host()
    activate_url = f"{protocol}://{domain}/activate/{uid}/{token}/"
    # print(activate_url)
    # Renderizar la plantilla del correo con el enlace de activación
    subject = 'Procesus - Completa tu registro en nuestro sitio'
    message = render_to_string('creation/activation_email.html', {
        'activate_url': activate_url,
    })

    # Enviar el correo electrónico
    print('message->', message)
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [cliente_email], fail_silently=False,)


def activate_account(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = get_user_model().objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, ObjectDoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        # Realiza la activación de la cuenta aquí
        user.is_active = True
        user.save()
        print(user.id)
        return redirect('crear_empresa')  # Redirige a la página de cuenta activada
    else:
        contexto = {}
        return render(request, 'registration/password_reset_confirm.html', contexto)
        # return redirect('password_reset_confirm.html') 
        # # HttpResponse('El enlace de activación es inválido o ha expirado.')


class Tablero(TemplateView):
    template_name = 'atpos/index.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class EmpresaCreate(CreateView):
    model = Empresa
    fields = ['nombre_empresa', 'nick_empresa', 'nit', 'dv', 'representante_legal', 'email', 'telefono_fijo', 'telefono_celular',
              'direccion_principal', 'ciudad', 'regimen', 'estado_empresa', 'vigencia']
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        empresa = form.save()
        userNew = get_user_model().objects.filter(email=empresa.email)
        x = userNew.update(empresa=empresa)
        print('ID del usuario que se agregó->', x)
        return super().form_valid(form)

class EmpresaDetail(DetailView):
    model = Empresa

    def get_queryset(self):
        return Empresa.objects.filter(id=self.request.user.empresa.id)

# class EmpresaList(ListView):
#     model = Empresa

#     def get_queryset(self):
#         return Empresa.objects.filter(id=self.request.user.empresa.id)

class EmpresaUpdate(UpdateView):
    model = Empresa
    fields = '__all__'

    def get_queryset(self):
        return Empresa.objects.filter(id=self.request.user.empresa.id)


class UsuarioList(ListView):
    model = Usuario
    template_name = 'atpos/user_list.html'

    def get_queryset(self):
        return get_user_model().objects.filter(empresa=self.request.user.empresa.id)

class UsuarioCreate(CreateView):
    model = Usuario
    form_class = CreateUserForm
    template_name='atpos/user_form.html'
    success_url = '/user/list/'
    
    def get_form_kwargs(self):
        """Return the keyword arguments for instantiating the form."""
        kwargs = super(UsuarioCreate, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

class UsuarioDetail(DetailView):
    model = Usuario
    template_name = 'atpos/user_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # print('\n', context)
        usuario = self.get_object()
        
        # Obtener los grupos a los que pertenece el usuario
        gu = usuario.groups.all()
        grupos_usuario = [p.name for p in gu]
        
        # Obtener los permisos individuales del usuario
        pi = usuario.user_permissions.all()
        permisos_individuales = [p.name for p in pi]
        
        context['grupos_usuario'] = grupos_usuario
        context['permisos_individuales'] = permisos_individuales
        
        return context


class UsuarioUpdatePassword(UpdateView):
    model = Usuario
    form_class = CreateUserForm
    template_name = 'atpos/user_form.html'
    success_url = '/user/list/'
    
    def get_form_kwargs(self):
        """Return the keyword arguments for instantiating the form."""
        kwargs = super(UsuarioUpdatePassword, self).get_form_kwargs()
        empresa = self.request.user.empresa
        kwargs.update({'user': self.request.user, 'empresa': empresa})
        return kwargs

    def get_queryset(self):
        return Usuario.objects.filter(empresa=self.request.user.empresa.id)

class UsuarioUpdate(UpdateView):
    model = Usuario
    form_class = UpdateUserForm
    # fields = ['username', 'first_name', 'last_name', 'email', 'is_active', 'tel_inicial']
    template_name = 'atpos/user_update_form.html'
    success_url = '/user/list/'
    
class UsuarioDelete(DeleteView):
    model = Usuario
    success_url = reverse_lazy('user_list')

    def get_queryset(self):
        return Usuario.objects.filter(empresa=self.request.user.empresa.id)

def cambiar_estado(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        id = data.get('id')
        tipo = data.get('tipo')
        
        # Aquí realiza la lógica para cambiar el estado de activo a inactivo para el ID y el tipo correspondiente
        # Por ejemplo, supongamos que cambiamos el estado a 'activo' si estaba 'inactivo', o viceversa
        if tipo == 'usuario':
            usuario = get_user_model().objects.get(pk=id)
            usuario.is_active = not usuario.is_active
            usuario.save()
            return JsonResponse({'estado': 'activo' if usuario.is_active else 'inactivo'})
        elif tipo == 'almacen':
            almacen = Almacen.objects.get(pk=id)
            if almacen.estado == '1':
                almacen.estado = '0'
            else:
                almacen.estado = '1'
            almacen.save()
            return JsonResponse({'estado': 'activo' if almacen.estado == '1' else 'inactivo'})
        elif tipo == 'caja':
            caja = Caja.objects.get(pk=id)
            if caja.estado == '1':
                caja.estado = '0'
            else:
                caja.estado ='1'
            caja.save()
            return JsonResponse({'estado': 'activo' if caja.estado == '1' else 'inactivo'})
        elif tipo == 'cajaserie':
            cajaserie = CajaSerie.objects.get(pk=id)
            if cajaserie.estado == '1':
                cajaserie.estado = '0'
            else:
                cajaserie.estado ='1'
            cajaserie.save()
            return JsonResponse({'estado': 'activo' if cajaserie.estado == '1' else 'inactivo'})
        elif tipo == 'articulo':
            articulo = Articulo.objects.get(pk=id)
            if articulo.estado == '1':
                articulo.estado = '0'
            else:
                articulo.estado ='1'
            articulo.save()
            return JsonResponse({'estado': 'activo' if articulo.estado == '1' else 'inactivo'})
        elif tipo == 'listaprecios':
            listaprecios = ListaPrecios.objects.get(pk=id)
            if listaprecios.estado == '1':
                listaprecios.estado = '0'
            else:
                listaprecios.estado ='1'
            listaprecios.save()
            return JsonResponse({'estado': 'activo' if listaprecios.estado == '1' else 'inactivo'})
        elif tipo == 'alterno':
            alterno = CodigoAlterno.objects.get(pk=id)
            if alterno.estado == '1':
                alterno.estado = '0'
            else:
                alterno.estado = '1'
            alterno.save()
            return JsonResponse({'estado': 'activo' if alterno.estado == '1' else 'inactivo'})



        # Luego, devuelve un JSON con el nuevo estado
        # return JsonResponse({'estado': 'activo' if usuario.is_active else 'inactivo'})

def create_group(request):
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            # Guardar el grupo en la base de datos
            grupo = form.save()

            # Obtener la empresa del usuario autenticado (o de donde la tengas almacenada)
            empresa = request.user.empresa

            # Crear la relación entre el grupo y la empresa en el modelo GrupoEmpresa
            GrupoEmpresa.objects.create(empresa=empresa, grupo=grupo)

            # Agregar los permisos seleccionados al grupo
            permisos_seleccionados = form.cleaned_data['permissions']
            grupo.permissions.set(permisos_seleccionados)

            # Redireccionar a la página de detalle del grupo o a donde desees
            return redirect('lista_grupos')
    else:
        form = GroupForm()

    return render(request, 'atpos/create_group.html', {'form': form})


def lista_grupos(request):
    # Obtener la empresa del usuario autenticado (o de donde la tengas almacenada)
    empresa = request.user.empresa

    # Filtrar los grupos por la empresa del usuario
    grupos_empresa = GrupoEmpresa.objects.filter(empresa=empresa)

    return render(request, 'atpos/lista_grupos.html', {'grupos_empresa': grupos_empresa})

def create_permiso(request):
    if request.method == 'POST':
        form = PermisoForm(request.POST)
        if form.is_valid():
            # Guardar el permiso en la base de datos
            permiso = form.save()

            # Obtener la empresa del usuario autenticado (o de donde la tengas almacenada)
            empresa = request.user.empresa

            # Crear la relación entre el permiso y la empresa en el modelo PermisoEmpresa
            PermisoEmpresa.objects.create(empresa=empresa, permiso=permiso)

            return redirect('atpos/lista_permisos')  # Redirige a la página de lista de permisos después de crear uno nuevo
    else:
        form = PermisoForm()

    return render(request, 'atpos/create_permiso.html', {'form': form})
    

def lista_permisos(request):
    # Obtener la empresa del usuario autenticado (o de donde la tengas almacenada)
    empresa = request.user.empresa

    # Obtener la lista de permisos asociados a la empresa
    permisos_empresa = PermisoEmpresa.objects.filter(empresa=empresa)

    # return render(request, 'atpos/lista_permisos.html', {'permisos_empresa': permisos_empresa})
    return render(request, 'atpos/lista_permisos.html', {'permisos_empresa': permisos_empresa})


class crear_grupo(CreateView):
    model = Group
    fields = ["name"]
    template_name = 'atpos/crear_grupo.html' #'atpos/group_form.html'

    def get(self, request, *args, **kwargs):
        empresa = request.user.empresa_id
        gruposEmpresa = GrupoEmpresa.objects.values_list("grupo").filter(empresa=empresa)
        listGrupo = {}
        for grupo in gruposEmpresa:
            grupos = Group.objects.get(id=grupo[0])
            listGrupo[grupos.id] = grupos.name
        contexto = {'listName': listGrupo}
        return render(request, 'atpos/crear_grupo.html', contexto)

    def post(self, request, *args, **kwargs):

        name_nuevo = request.POST.get('name')
        grupo = Group.objects.create(name=name_nuevo)

        # Obtener la empresa del usuario autenticado (o de donde la tengas almacenada)
        empresa = request.user.empresa

        # Crear la relación entre el grupo y la empresa en el modelo GrupoEmpresa
        GrupoEmpresa.objects.create(empresa=empresa, grupo=grupo)

        # Agregar los permisos seleccionados al grupo
        # permisos_seleccionados = form.cleaned_data['group']
        # grupo.permissions.set(permisos_seleccionados)

        # Redireccionar a la página de detalle del grupo o a donde desees
        return redirect(request.path)
    

class AsignarPermisosGrupo(View):

    def get(self, request, grupo, *args, **kwargs):
        idGrupo = grupo
        empresa = request.user.empresa_id
        nombreGrupo = Group.objects.get(id=idGrupo)
        permisosDisponibles = Permission.objects.filter(content_type__app_label='atpos')
        grupo = Group.objects.get(id=idGrupo)
        permisos = grupo.permissions.all()
        permisosGrupo = [p.id for p in permisos]
        contexto = {
            'idGrupo':idGrupo, 
            'nombreGrupo':nombreGrupo, 
            'permisosGrupo':permisosGrupo, 
            'permisosDisponibles':permisosDisponibles
        }
        return render(request, 'atpos/asignar_permisos_grupo.html', contexto)
    
    def post(self, request, *args, **kwargs):
        alterno_nuevo = request.POST.get('formData')
        pass

def RecibirPermisosGrupo(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        formData = data.get('formData')
        idGrupo = data.get('idGrupo')
        try:
            grupo = Group.objects.get(id=idGrupo)
            grupo.permissions.set(formData)
        except Group.DoesNotExist:
            pass
    return render(request, 'atpos/crear_grupo.html')

class UsuarioGruposPermisos(View):

    def get(self, request, idUser, *args, **kwargs):
        # Obtener el usuario
        user = get_object_or_404(Usuario, id=idUser)
        
        # Obtener la empresa del usuario
        empresa = user.empresa
        
        # Obtener grupos disponibles correspondientes a la empresa
        ge = GrupoEmpresa.objects.filter(empresa=empresa)
        gruposEmpresa = [p.grupo for p in ge]

        # Obtener grupos del usuario
        gu = user.groups.all()
        gruposUsuario = [p.id for p in gu]
        
        # Obtener permisos disponibles
        permisosDisponibles = Permission.objects.filter(content_type__app_label='atpos')
        
        # Obtener permisos del usuario
        pu = user.user_permissions.all()
        permisosUsuario = [p.id for p in pu]
        
        contexto = {
            'idUser': idUser,
            'nameUser': user.username,
            'permisosDisponibles': permisosDisponibles,
            'permisosUsuario': permisosUsuario,
            'gruposEmpresa': gruposEmpresa,
            'gruposUsuario': gruposUsuario,
        }
        
        return render(request, 'atpos/usuario_grupos_permisos.html', contexto)
    
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        # Obtener permisos seleccionados del formulario
        permisos_seleccionados = data.get('dataPermisos')
         # Obtener grupos seleccionados del formulario
        grupos_seleccionados = data.get('dataGrupos')
        idUser = data.get('idUser')
        user = get_object_or_404(Usuario, id=idUser)
        
        # Obtener permisos existentes del usuario
        permisos_usuario_existentes = user.user_permissions.all()
        
        # Limpiar permisos existentes del usuario
        user.user_permissions.clear()
        
        # Asignar nuevos permisos seleccionados al usuario
        for permiso_id in permisos_seleccionados:
            permiso = get_object_or_404(Permission, id=permiso_id)
            user.user_permissions.add(permiso)
        
        # Obtener grupos existentes del usuario
        grupos_usuario_existentes = user.groups.all()
        
        # Limpiar grupos existentes del usuario
        user.groups.clear()
        
        # Asignar nuevos grupos seleccionados al usuario
        for grupo_id in grupos_seleccionados:
            grupo = get_object_or_404(Group, id=grupo_id)
            user.groups.add(grupo)

        return JsonResponse({'message': 'Grupos y permisos actualizados con éxito'})

''' ALMACEN '''

class AlmacenCreate(CreateView):
    model = Almacen
    fields = [
        'nombre_almacen', 
        'prefijo', 
        'telefono_fijo', 
        'telefono_celular', 
        'direccion_almacen', 
        'listaprecios',
        'ciudad', 
        'estado']

    def form_valid(self, form):
        form.instance.empresa = self.request.user.empresa
        return super().form_valid(form)
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        empresa = self.request.user.empresa
        listaprecios_queryset = ListaPrecios.objects.filter(empresa=empresa)
        form.fields['listaprecios'].queryset = listaprecios_queryset
        return form
    
    def get_success_url(self):
        return reverse('almacen-list')

class AlmacenList(ListView):
    model = Almacen

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        empresa = self.request.user.empresa
        listaprecios = ListaPrecios.objects.filter(empresa=empresa)
        context['listaprecios'] = listaprecios
        return context
    
    def get_queryset(self):
        return Almacen.objects.filter(empresa=self.request.user.empresa.id)


class AlmacenDetail(DetailView):
    model = Almacen

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_queryset(self):
        return Almacen.objects.filter(empresa=self.request.user.empresa.id)



class AlmacenUpdate(UpdateView):
    model = Almacen
    fields = [
        'nombre_almacen', 
        'prefijo', 
        'telefono_fijo', 
        'telefono_celular', 
        'direccion_almacen', 
        'listaprecios',
        'ciudad', 
        'estado']
    template_name_suffix = "_update_form"

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        empresa = self.request.user.empresa
        listaprecios_queryset = ListaPrecios.objects.filter(empresa=empresa)
        form.fields['listaprecios'].queryset = listaprecios_queryset
        return form

''' TODO no se puede borrar ningún almacen mientras tenga asociado un inventario '''
class AlmacenDelete(DeleteView):
    model = Almacen
    success_url = reverse_lazy("almacen-list")

''' CAJA '''

class CajaCreate(CreateView):
    model = Caja
    fields = ['prefijo', 'tipo_factura', 'estado', 'almacen']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario = self.request.user.empresa
        
        # Obtener los almacenes que tiene la empresa
        almacen = Almacen.objects.filter(empresa=usuario)

        context['almacen'] = almacen
        return context
    
    def form_valid(self, form):
        # Realizar acciones adicionales antes de guardar el objeto
        # por ejemplo, asignar el usuario actual como el creador
        form.instance.empresa = self.request.user.empresa
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('caja-list')

class CajaList(ListView):
    model = Caja

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
    
    def get_queryset(self):
        return Caja.objects.filter(empresa=self.request.user.empresa.id)


class CajaDetail(DetailView):
    model = Caja

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_queryset(self):
        return Caja.objects.filter(empresa=self.request.user.empresa.id)


class CajaUpdate(UpdateView):
    model = Caja
    fields = ['prefijo', 'tipo_factura', 'estado', 'almacen']
    template_name_suffix = "_update_form"

    def get(self, request, *args, **kwargs):
        caja = Caja.objects.get(id=kwargs['pk'])
        empresa = request.user.empresa
        almacenes = Almacen.objects.filter(empresa=empresa)
        contexto = {'caja': caja, 'almacenes': almacenes}
        return render(request, 'atpos/caja_update_form.html', contexto)

    def post(request, *args, **kwargs):
        pass


class CajaDelete(DeleteView):
    model = Caja
    success_url = reverse_lazy("caja-list")

''' CajaSerie '''

class CajaSerieCreate(CreateView):
    model = CajaSerie
    fields = ['numero_caja', 'estado', 'almacen']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        empresa = self.request.user.empresa
        
        # Obtener los almacenes que tiene la empresa
        almacenes = Almacen.objects.filter(empresa=empresa)
        context['almacenes'] = almacenes
        # Obtener el siguiente número de caja
        cajas_queryset = CajaSerie.objects.filter(empresa=empresa)
        numeros_caja = [caja.numero_caja for caja in cajas_queryset]
        if len(numeros_caja) != 0:
            mayor_numero_caja = max(numeros_caja)
        else:
            mayor_numero_caja = 0
        context['numeroCaja'] = mayor_numero_caja+1
        return context
    
    def form_valid(self, form):
        # Realizar acciones adicionales antes de guardar el objeto
        # por ejemplo, asignar el usuario actual como el creador
        form.instance.empresa = self.request.user.empresa
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('cajaserie-list')


class CajaSerieList(ListView):
    model = CajaSerie
    fields = ['numero_caja', 'estado', 'almacen']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        empresa = self.request.user.empresa
        cajaserie = CajaSerie.objects.filter(empresa=empresa)
        context["cajaserie"] = cajaserie
        return context

class CajaSerieDetail(DetailView):
    model = CajaSerie
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
    
    def get_queryset(self):
        return CajaSerie.objects.filter(empresa=self.request.user.empresa.id)

class CajaSerieUpdate(UpdateView):
    model = CajaSerie
    fields = ['numero_caja', 'estado', 'almacen']
    template_name_suffix = "_update_form"

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        empresa = self.request.user.empresa
        almacenes = Almacen.objects.filter(empresa=empresa)
        form.fields['almacen'].queryset = almacenes
        return form

    # def get_queryset(self):
    #     empresa = self.request.user.empresa
    #     return Almacen.objects.filter(empresa=empresa)

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     empresa = self.request.user.empresa
        
    #     # Obtener los almacenes que tiene la empresa
    #     almacenes = Almacen.objects.filter(empresa=empresa)
    #     context['almacenes'] = almacenes
    #     # Obtener el siguiente número de caja
    #     # cajas_queryset = CajaSerie.objects.filter(empresa=empresa)
    #     # numeros_caja = [caja.numero_caja for caja in cajas_queryset]
    #     # if len(numeros_caja) != 0:
    #     #     mayor_numero_caja = max(numeros_caja)
    #     # else:
    #     #     mayor_numero_caja = 0
    #     # context['numeroCaja'] = mayor_numero_caja+1
    #     return context

class CajaSerieDelete(DeleteView):
    model = CajaSerie
    success_url = reverse_lazy("cajaserie-list")


''' CATEGORIA '''

class CategoriaCreate(CreateView):
    model = Categoria
    template_name = 'atpos/categoria_form.html'
    form_class = CreateCategoriaForm

    def post(self, request, *args, **kwargs):
        resultado = request.POST
        nombreCategoria = resultado['nombre_categoria'].lower()
        nombreCategoria = nombreCategoria.capitalize()
        print('nombreCategoria', nombreCategoria)
        if resultado['categoria_padre'] != '':
            categoriaPadre = Categoria.objects.get(id=resultado['categoria_padre'])
        else:
            categoriaPadre = None
        estadoCategoria= resultado['estado_categoria']
        empresaId = Empresa.objects.get(id=self.request.user.empresa_id)
        exiteCodigoCategoria = Categoria.objects.filter(nombre_categoria=nombreCategoria, empresa=empresaId).exists()
        if not exiteCodigoCategoria:
            p = Categoria(nombre_categoria=nombreCategoria, categoria_padre=categoriaPadre, estado_categoria=estadoCategoria, empresa=empresaId)
            p.save()
            return HttpResponseRedirect(reverse_lazy('categoria-list'))
        else:
            form = self.form_class(request.POST)
            form.add_error('nombre_categoria', 'Nombre repetido en Categoria')
            return render(request, 'articulo/categoria_form.html', {'form': form})
    
    def get_form_kwargs(self):
        """Return the keyword arguments for instantiating the form."""
        kwargs = super(CategoriaCreate, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        print("CategoriaCreate kwargs ", kwargs)
        return kwargs

class CategoriaList(ListView):
    model = Categoria
    template_name = 'articulo/categoria_list.html'

    def get_queryset(self):
        return Categoria.objects.filter(empresa=self.request.user.empresa_id)

class CategoriaUpdate(UpdateView):
    model = Categoria
    fields = ['nombre_categoria', 'categoria_padre', 'estado_categoria']
    # form_class = CategoriaForm
    template_name_suffix = '_update_form'

    def form_valid(self, form):
        # Realizar acciones adicionales antes de guardar el objeto
        # por ejemplo, asignar el usuario actual como el creador
        resultado = self.request.POST
        nombreCategoria = resultado['nombre_categoria']
        form.instance.nombre_categoria = nombreCategoria.lower().capitalize()
        form.instance.empresa = self.request.user.empresa
        return super().form_valid(form)

class CategoriaDelete(DeleteView):
    model = Categoria
    template_name = 'atpos/categoria_confirm_delete.html'
    success_url = reverse_lazy('categoria-list')

    # get_queryset: Este método se ejecuta primero y se utiliza para obtener el 
    # conjunto de consultas que representa el conjunto de objetos que se pueden 
    # eliminar. Normalmente, esto es simplemente una consulta que recupera el 
    # objeto que se va a eliminar.
    def get_queryset(self):
        return Categoria.objects.filter(empresa=self.request.user.empresa_id)

    # get_object: Después de obtener el conjunto de consultas, Django ejecuta get_object. 
    # Este método se utiliza para obtener el objeto específico que se va a eliminar. 
    # Por lo general, se basa en la clave primaria (PK) proporcionada en la URL.
    # Anulamos get_object para personalizar su comportamiento.
    def get_object(self, queryset=None):
        # Obtenemos la categoría por su clave principal.
        return Categoria.objects.get(pk=self.kwargs['pk'])

    # get: El método get se utiliza para procesar las solicitudes GET. 
    # Si un usuario visita la página de eliminación, este método se ejecutará. 
    # Aquí es donde puede personalizar el comportamiento de la página de eliminación. 
    # En algunos casos, este método puede redirigir al usuario si no cumple con ciertos requisitos.
    # def get(self, request, pk):
    #     categoria = Categoria.objects.get(pk=pk)
    #     if categoria:
    #         articulo = Articulo.objects.filter(categoria=categoria)
    #         if articulo:
    #             error_message = "No se puede eliminar esta categoría porque hay artículos asociados a ella."
    #             return render(request, 'atpos/categoria_delete_error.html', {'error_message': error_message})
    #     return self.render_to_response(self.get_context_data(object=categoria))

        # try:
        #     categoria = Categoria.objects.get(pk=pk)
        #     categoria.delete()
        #     # Si el borrado se realiza con éxito, redirige a la página de lista de categorías o muestra un mensaje de éxito.
        #     return HttpResponseRedirect(reverse('categoria-list'))
        # except ProtectedError as e:
        #     print(type(e))
        #     # Si se produce una excepción ProtectedError, muestra un mensaje de error personalizado.
        #     error_message = "No se puede eliminar esta categoría porque hay artículos asociados a ella."
        #     return render(request, 'atpos/categoria_delete_error.html', {'error_message': error_message})

    # delete: Cuando un usuario confirma la eliminación, se ejecuta el método delete. 
    # Este método es responsable de eliminar el objeto de la base de datos. Puedes 
    # anularlo para agregar lógica personalizada antes o después de la eliminación.
    # Definimos un método personalizado para manejar la eliminación y la confirmación.
    # def delete(self, request, *args, **kwargs):
    #     # Obtenemos la categoría.
    #     categoria = self.get_object()

    #     # Verificamos si hay objetos relacionados.
    #     if categoria.articulo_set.exists():
    #         # Si hay objetos relacionados, mostramos una página de confirmación personalizada.
    #         return self.render_to_response(self.get_context_data(object=categoria))
    #     else:
    #         # Si no hay objetos relacionados, eliminamos la categoría.
    #         categoria.delete()
    #         return HttpResponseRedirect(self.success_url)

    # get_context_data: Después de que se confirma la eliminación, se ejecuta get_context_data. 
    # Este método se utiliza para proporcionar datos adicionales al contexto de la plantilla. 
    # Puedes usarlo para personalizar la plantilla de confirmación.
    def get_context_data(self, **kwargs):
        instance = self.object
        categoria = Categoria.objects.get(pk=instance.id)
        if categoria:
            articulo = Articulo.objects.filter(categoria=categoria)
            if articulo.exists():
                if 'form' not in kwargs:
                    kwargs['form'] = self.get_form()
                    kwargs['error'] = 'error'
                    kwargs['categoria'] = categoria.nombre_categoria
                    kwargs['mensaje'] = "No se puede eliminar esta categoría porque hay artículos asociados a ella."
        return super().get_context_data(**kwargs)

class CategoriaListArticulos(ListView):
    model = Articulo
    template_name = 'atpos/articulo_list.html'
    # fields = ['codigo_articulo', 'nombre_articulo', 'nombre_largo_articulo', 'categoria', 'unidad_medida', 'base_iva', 'estado_articulo', 'empresa' ]

    def get_queryset(self, **kwargs):
       qs = super().get_queryset(**kwargs)
       xx = qs.filter(categoria=self.kwargs['pk'], empresa=self.request.user.empresa_id)
       print('qs qs qs qs ->', xx)
       return qs.filter(categoria=self.kwargs['pk'], empresa=self.request.user.empresa_id)


''' UNIDAD DE MEDIDA '''

class UnidadMedidaCreate(CreateView):
    model = UnidadMedida
    fields = ['codigo_unidad_medida', 'nombre_unidad_medida', 'estado']
    # template_name = 'articulo/unidadmedida_form.html'
    # form_class = CreateUnidadMedidaForm

    def form_valid(self, form):
        resultado = self.request.POST
        nombreUnidadMedida = resultado['nombre_unidad_medida']
        form.instance.nombre_unidad_medida = nombreUnidadMedida.lower().capitalize()
        codigoUnidadMedida = resultado['codigo_unidad_medida']
        form.instance.codigo_unidad_medida = codigoUnidadMedida.upper()
        form.instance.empresa = self.request.user.empresa
        return super().form_valid(form)

    def get_queryset(self):
        return UnidadMedidaCreate.objects.filter(id=self.request.user.empresa.id)

class UnidadMedidaList(ListView):
    model = UnidadMedida
    template_name = 'articulo/unidadmedida_list.html'

    def get_queryset(self):
        return UnidadMedida.objects.filter(empresa=self.request.user.empresa_id)

class UnidadMedidaDelete(DeleteView):
    model = UnidadMedida
    success_url = reverse_lazy('unidadmedida-list')

    def get_queryset(self):
        return UnidadMedida.objects.filter(empresa=self.request.user.empresa_id)

class UnidadMedidaUpdate(UpdateView):
    model = UnidadMedida
    fields = ['codigo_unidad_medida', 'nombre_unidad_medida', 'estado']
    template_name_suffix = '_update_form'

    def form_valid(self, form):
        resultado = self.request.POST
        nombreUnidadMedida = resultado['nombre_unidad_medida']
        form.instance.nombre_unidad_medida = nombreUnidadMedida.lower().capitalize()
        codigoUnidadMedida = resultado['codigo_unidad_medida']
        form.instance.codigo_unidad_medida = codigoUnidadMedida.upper()
        form.instance.empresa = self.request.user.empresa
        return super().form_valid(form)

''' BASE IVA '''

class BaseIVACreate(CreateView):
    model = BaseIVA
    fields = ['base_iva', 'nombre_base_iva', 'estado']
    success_url = reverse_lazy('baseiva-list')

    def form_valid(self, form):
        # resultado = self.request.POST
        # nombreUnidadMedida = resultado['nombre_unidad_medida']
        # form.instance.nombre_unidad_medida = nombreUnidadMedida.lower().capitalize()
        # codigoUnidadMedida = resultado['codigo_unidad_medida']
        # form.instance.codigo_unidad_medida = codigoUnidadMedida.upper()
        form.instance.empresa = self.request.user.empresa
        return super().form_valid(form)

class BaseIVAList(ListView):
    model = BaseIVA
    template_name = 'articulo/baseiva_list.html'

    def get_queryset(self):
        return BaseIVA.objects.filter(empresa=self.request.user.empresa_id)

class BaseIVADelete(DeleteView):
    model = BaseIVA
    success_url = reverse_lazy('baseiva-list')

class BaseIVAUpdate(UpdateView):
    model = BaseIVA
    fields = ['base_iva', 'nombre_base_iva', 'estado']
    template_name_suffix = '_update_form'

    def form_valid(self, form):
        # resultado = self.request.POST
        # nombreUnidadMedida = resultado['nombre_unidad_medida']
        # form.instance.nombre_unidad_medida = nombreUnidadMedida.lower().capitalize()
        # codigoUnidadMedida = resultado['codigo_unidad_medida']
        # form.instance.codigo_unidad_medida = codigoUnidadMedida.upper()
        form.instance.empresa = self.request.user.empresa
        return super().form_valid(form)


''' ARTICULO '''

class ArticuloCreate(CreateView):
    model = Articulo
    form_class = ArticuloForm
    # fields = ['codigo_articulo','nombre_articulo', 'nombre_largo_articulo', 'categoria', 'unidad_medida', 'base_iva', 'estado']
    template_name = 'atpos/articulo_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = 'Creación de artículos'
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user_empresa'] = self.request.user.empresa
        return kwargs

    def form_valid(self, form):
        empresa = self.request.user.empresa
        resultado = self.request.POST
        precio = resultado['precio']
        codigoArticulo = resultado['codigo_articulo']
        codigoAlterno = CodigoAlterno.objects.filter(nuevo_codigo_articulo=codigoArticulo, empresa=empresa)
        codigo_articulo = Articulo.objects.filter(codigo_articulo= codigoArticulo, empresa=empresa)
        if codigo_articulo.exists():
            form.add_error('codigo_articulo', "El código ya existe.")
            return self.form_invalid(form)
            ''' TODO cuando se crea un artículo es necesario crear 
            el código en codigos alternos y asociar su lista de precios
            se debe validar el nuevo código en el código alterno.
            '''
        elif codigoAlterno.exists():
            form.add_error('codigo_articulo', "El código ya existe como alterno.")
            return self.form_invalid(form)
        form.instance.empresa = empresa
        response = super().form_valid(form)
        ultimo_registro = self.object
        # articulo, codigo_articulo, posicion, cantidad, precio, listaPrecio, descripcion, estado, empresa
        listaPrecio = ListaPrecios.objects.filter(empresa=empresa).first()
        nuevoalterno = CodigoAlterno.objects.create(
            articulo=ultimo_registro, 
            nuevo_codigo_articulo=ultimo_registro.codigo_articulo,
            posicion=1, 
            cantidad=1, 
            precio=precio, 
            listaPrecio=listaPrecio,
            nombre_articulo=ultimo_registro.nombre_articulo, 
            estado=1, 
            empresa=empresa)
        return response

class ArticuloDelete(DeleteView):
    '''
    TODO cuando se borra el artículo hay que alvertirle al usuario que 
    también se borraran todos los códigos alternos asociados al 
    artículo que se elimina, si los hay.
    '''
    model = Articulo
    success_url = reverse_lazy("articulo-list")

    def get_context_data(self, **kwargs):
        instance = self.get_object()
        codigosAlterno = CodigoAlterno.objects.filter(articulo=instance)
        codigosAlternosEliminar=''
        cantidadAlternosEliminar = 0
        for codigoAlterno in codigosAlterno:
            cantidadAlternosEliminar += 1
            if cantidadAlternosEliminar != len(codigosAlterno):
                codigosAlternosEliminar += codigoAlterno.nuevo_codigo_articulo+', '
            else:
                codigosAlternosEliminar += codigoAlterno.nuevo_codigo_articulo+'. '

        if len(codigosAlterno) > 1:
            if 'form' not in kwargs:
                kwargs['form'] = self.get_form()
                kwargs['codigosAlternosEliminar'] = codigosAlternosEliminar
                kwargs['mensaje'] = 'Se eliminará el artículo y los códigos alternos asociados al artículo '+codigosAlterno[0].nombre_articulo+' '+codigosAlternosEliminar
        return super().get_context_data(**kwargs)
    
    def form_valid(self, form):
        success_url = self.get_success_url() # /articulo/list/
        articulo = self.object
        alternos = CodigoAlterno.objects.filter(articulo=articulo)
        for alterno in alternos:
            alterno.delete()
        self.object.delete()
        return HttpResponseRedirect(success_url)

''' CODIGO ALTERNO  '''

class CodigoAlternoCreate(CreateView):
    model = CodigoAlterno
    # fields = ['articulo', 'nuevo_codigo_articulo', 'cantidad', 'precio', 'listaPrecio', 'nombre_articulo']
    form_class = CodigoAlternoForm
    template_name = 'atpos/codigoalterno_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['datosArticulo'] = self.get_object()
        return context

    def get_object(self):
        pk = self.kwargs.get(self.pk_url_kwarg)
        try:
            obj = Articulo.objects.get(pk=pk)
        except Articulo.DoesNotExist:
            raise Http404("No matches the given query.")
        return obj
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user_empresa'] = self.request.user.empresa
        objArticulo = self.get_object()
        kwargs['objArticulo'] = objArticulo
        return kwargs

    def form_valid(self, form):
        # posicion, estado, empresa
        empresa = self.request.user.empresa
        alterno = CodigoAlterno.objects.filter(articulo=self.get_object(), empresa=empresa)
        articulo = self.get_object()
        form.instance.articulo = articulo
        form.instance.posicion = len(alterno) + 1
        form.instance.estado = 1
        form.instance.empresa = empresa
        try:
            return super().form_valid(form)
        except IntegrityError:
            form.add_error('nuevo_codigo_articulo', 'Ya existe una código alterno con ese valor.')
            return self.form_invalid(form)

class Alterno(View):
    def get(self, request, pk):
        datosArticulo = Articulo.objects.get(pk=pk, empresa=request.user.empresa_id)
        aa = CodigoAlterno.objects.filter(articulo=pk, empresa=request.user.empresa_id)
        alternosArticulos = []
        for alternoArticulo in aa:
            alternosArticulos.append(alternoArticulo)
        contexto = {'articulo': datosArticulo, 'alterno': alternosArticulos}
        return render(request, 'atpos/alterno_form.html', contexto)

    def post(self, request, pk, *args, **kwargs):
        alterno_nuevo = request.POST.get('alterno_nuevo')

        if len(alterno_nuevo) > 0:
            articulo = Articulo.objects.get(pk=pk, empresa=request.user.empresa_id)
            empresa = Empresa(pk=self.request.user.empresa_id)

            codigoalterno = CodigoAlterno.objects.filter(id_articulo=articulo, empresa= self.request.user.empresa_id).order_by('-posicion')
            print('codigoalterno vacio-> ',codigoalterno)
            if codigoalterno:
                posicion = codigoalterno[0].posicion+1
            else:
                posicion = 1

            alterno = CodigoAlterno(id_articulo=articulo, codigo_articulo=alterno_nuevo, posicion=posicion, 
            descripcion=articulo.nombre_articulo, estado_codigoalterno=1, empresa=empresa)
            alterno.save()

            # TODO hacer esto con Ajax o algo que no renderice toda la página.
            return redirect(request.path)

        else:
            return HttpResponse('El código alterno_nuevo no fue diligenciado.')

class AlternoFetch(View):
    def get(self, request, pk):
        data = {
            'mensaje': '¡Hola desde el servidor!',
            'valor': pk,
        }
        return JsonResponse(data)

class ArticuloUpdate(UpdateView):
    model = Articulo
    form_class = ArticuloForm
    # fields = ['codigo_articulo','nombre_articulo', 'nombre_largo_articulo', 'categoria', 'unidad_medida', 'base_iva', 'estado']
    template_name = 'atpos/articulo_form.html'

class ArticuloList(ListView):
    model = Articulo
    template_name = 'atpos/articulo_list.html'

    def get_queryset(self):
        empresa = self.request.user.empresa.id
        return Articulo.objects.filter(empresa=empresa)

''' LISTAPRECIOS '''

class ListaPreciosCreate(CreateView):
    model = ListaPrecios
    fields = ['nombre', 'descripcion', 'estado']
    # form_class = ListaPreciosForm
    template_name = 'atpos/listaprecios_form.html'

    def form_valid(self, form):
        form.instance.empresa = self.request.user.empresa
        form.instance.moneda = 'COL'
        
        try:
            return super().form_valid(form)
        except IntegrityError:
            form.add_error('nombre', 'Ya existe una lista de precios con este nombre.')
            return self.form_invalid(form)

class ListaPreciosList(ListView):
    model = ListaPrecios

    def get_queryset(self):
        empresa = self.request.user.empresa.id
        return ListaPrecios.objects.filter(empresa=empresa)

''' TODO Antes de borrar una lista de precios hay que tener en cuenta
    que no esté asociada a ningún almacen o cliente, y que quede
    sin lista de precios, al menos debe tener una.'''
class ListaPreciosDelete(DeleteView):
    model = ListaPrecios
    success_url = reverse_lazy("listaprecios-list")

    def get_context_data(self, **kwargs):
        instance = self.get_object()
        almacenesAsociado = Almacen.objects.filter(listaprecios=instance)
        empresa = self.request.user.empresa
        lpEmpresa = ListaPrecios.objects.filter(empresa=empresa)
        cantidadlp = len(lpEmpresa) # Cantidad de lista de precios de la empresa.
        print('almacenesAsociado->', len(almacenesAsociado))
        almacen = ''
        cantidadDeAlmacenes = 0
        if almacenesAsociado.exists():
            for almacenAsociado in almacenesAsociado:
                cantidadDeAlmacenes +=1
                if cantidadDeAlmacenes != len(almacenesAsociado):
                    almacen += str(almacenAsociado.nombre_almacen)+', '
                else:
                    almacen += str(almacenAsociado.nombre_almacen)+'.'
            if 'form' not in kwargs:
                kwargs['form'] = self.get_form()
                kwargs['almacenAsociado'] = almacen
                kwargs['mensaje'] = 'No se puede borrar esta lista de precios, primero debe retirarla del almacen: '+almacen
        elif cantidadlp == 1:
            if 'form' not in kwargs:
                kwargs['form'] = self.get_form()
                kwargs['almacenAsociado'] = 1
                kwargs['mensaje'] = 'No se puede borrar esta lista de precios, siempre debe tener al menos una lista de precios que contenga todos los artículos.'

        return super().get_context_data(**kwargs)

class ListaPreciosUpdate(UpdateView):
    model = ListaPrecios
    fields = ['nombre', 'descripcion', 'estado']
    success_url = reverse_lazy("listaprecios-list")








