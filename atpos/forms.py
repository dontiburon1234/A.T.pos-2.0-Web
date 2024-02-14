from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import RegexValidator, EmailValidator
from django.contrib.auth.models import Permission, Group
from django.contrib.auth import get_user_model

from .models import (
    Caja, 
    Almacen, 
    Categoria,
    UnidadMedida,
    BaseIVA,
    Articulo,
    CodigoAlterno,
    ListaPrecios
    )

Usuario = get_user_model()

# First, enter a username and password. Then, you’ll be able to edit more user options.
# Primero, ingrese un nombre de usuario y contraseña. Luego, podrá editar más opciones de usuario.
class CreateUserForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = ["username", "password1", "password2"]
        # widgets = {'empresa': forms.HiddenInput()}

    def clean_empresa(self, *args, **kwargs):
        return self.user.empresa
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        self.empresa = kwargs.pop('empresa')
        super(CreateUserForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Identificación del usuario'})
        self.fields['password1'].widget.attrs.update({'type': "password", 'class': "form-control", 'name': "password", 'placeholder': "Contraseña"})
        self.fields['password2'].widget.attrs.update({'type': "password", 'class': "form-control", 'name': "password", 'placeholder': "Repita la contraseña"})


class UpdateUserForm(forms.ModelForm):
    username = forms.CharField(
        validators=[RegexValidator('^[a-zA-Z0-9ñÑáéíóúÁÉÍÓÚ_]*$', 
        message="¡Solo letras y números sin caracteres especiales!")],
        label="Usuario",
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    first_name = forms.CharField(
        validators=[RegexValidator('^[a-zA-ZñÑáéíóúÁÉÍÓÚ ]*$', 
        message="¡Solo letras!")],
        label="Nombre",
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        validators=[RegexValidator('^[a-zA-ZñÑáéíóúÁÉÍÓÚ ]*$', 
        message="¡Solo letras!")],
        label="Apellido",
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        validators=[EmailValidator(message='¡Introduzca un e-mail válido!')],
        label="Correo electrónico",
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    is_active = forms.BooleanField(
        label="Activo",
        widget=forms.CheckboxInput(attrs={'class': 'form-check'})
    )
    tel_inicial = forms.IntegerField(
        label="Teléfono",
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        max_value=9999999999  # 10 dígitos en total
    )
    
    class Meta:
        model = Usuario
        fields = ['username', 'first_name', 'last_name', 'email', 'is_active', 'tel_inicial']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            widget_attrs = field.widget.attrs
            widget_attrs.update({'class': 'form-control'})

    def as_table(self):
        return self._html_output(
            normal_row='<tr%(html_class_attr)s><th scope="row">%(label)s</th><td>%(field)s%(help_text)s%(errors)s</td></tr>',
            error_row='<tr><td colspan="2">%s</td></tr>',
            row_ender='</td></tr>',
            help_text_html='<br><span class="helptext">%s</span>',
            errors_on_separate_row=True
        )
    
    def as_ul(self):
        return self._html_output(
            normal_row='<li%(html_class_attr)s>%(label)s %(field)s%(help_text)s%(errors)s</li>',
            error_row='<li>%s</li>',
            row_ender='</li>',
            help_text_html='<br><span class="helptext">%s</span>',
            errors_on_separate_row=True
        )
    
    def as_p(self):
        return self._html_output(
            normal_row='<p%(html_class_attr)s>%(label)s %(field)s%(help_text)s%(errors)s</p>',
            error_row='<p>%s</p>',
            row_ender='</p>',
            help_text_html='<br><span class="helptext">%s</span>',
            errors_on_separate_row=True
        )











class GroupForm(forms.ModelForm):
    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'duallistbox', 'multiple': 'multiple'})
    )
    class Meta:
        model = Group
        fields = ['name', 'permissions']
        


class PermisoForm(forms.ModelForm):
    class Meta:
        model = Permission
        fields = ['content_type', 'codename', 'name']


class DuallistGroupForm(forms.ModelForm):
    grupo = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'duallistbox', 'multiple': 'multiple'})
    )
    class Meta:
        model = Group
        fields = ['name', 'grupo']

class GroupForm(forms.ModelForm):
    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'duallistbox', 'multiple': 'multiple'})
    )

    class Meta:
        model = Group
        fields = ['name', 'permissions']


class CreateCategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre_categoria', 'categoria_padre', 'estado_categoria', 'empresa']
        widgets = {'empresa': forms.HiddenInput()}
        
    def clean_empresa(self, *args, **kwargs):
        print("CreateCategoriaForm clean_empresa self.user.empresa", self.user.empresa)
        return self.user.empresa
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(CreateCategoriaForm, self).__init__(*args, **kwargs)
        self.fields['nombre_categoria'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'nombre_categoria'})
        self.fields['categoria_padre'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'categoria_padre'})
        self.fields['categoria_padre'].queryset = Categoria.objects.filter(empresa_id=self.user.empresa.id)
        self.fields['estado_categoria'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'estado_categoria'})


class ArticuloForm(forms.ModelForm):
    precio = forms.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        label='Precio', 
        required=True, 
        widget=forms.NumberInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Articulo
        fields = ['codigo_articulo','nombre_articulo', 'nombre_largo_articulo', 'categoria', 'unidad_medida', 'base_iva', 'estado']
        widgets = {
            'codigo_articulo': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre_articulo': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre_largo_articulo': forms.TextInput(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'unidad_medida': forms.Select(attrs={'class': 'form-control'}),
            'base_iva': forms.Select(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, user_empresa=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user_empresa:
            self.fields['categoria'].queryset = Categoria.objects.filter(empresa=user_empresa)
            self.fields['unidad_medida'].queryset = UnidadMedida.objects.filter(empresa=user_empresa)
            self.fields['base_iva'].queryset = BaseIVA.objects.filter(empresa=user_empresa)

class CodigoAlternoForm(forms.ModelForm):
    
    class Meta:
        model = CodigoAlterno
        fields = ['nuevo_codigo_articulo', 'nombre_articulo', 'cantidad', 'precio', 'listaPrecio']
        widgets = {
            'nuevo_codigo_articulo': forms.TextInput(), 
            'nombre_articulo': forms.TextInput(),
            'cantidad': forms.TextInput(), 
            'precio': forms.TextInput(), 
            'listaPrecio': forms.Select(), 
        }
    
    def __init__(self, *args, user_empresa=None, objArticulo=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user_empresa:
            self.fields['listaPrecio'].queryset = ListaPrecios.objects.filter(empresa=user_empresa)

            
    # def get_initial(self):
    #     initial = super().get_initial()
    #     empresa = self.request.user.empresa
    #     nombreArticulo = self.get_object().nombre_articulo
    #     initial['articulo'] = nombreArticulo
    #     initial['nombre_articulo'] = nombreArticulo
    #     initial['listaPrecio'] = ListaPrecios.objects.filter(empresa=empresa).first
    #     print(initial)
    #     return initial


