from django.db import models
from django.urls import reverse
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import Group, Permission
import datetime

POS = '0'
ELECTRONICA = '1'
COMBINADA = '2'
TIPO_FACTURA = (
    (POS, 'Pos'),
    (ELECTRONICA, 'Electrónica'),
    (COMBINADA, 'Combinada')
)

COMUN = '1'
SIMPLIFICADO = '0'
REGIMEN_EMPRESA = (
    (COMUN, 'Común'),
    (SIMPLIFICADO, 'Simplificado'),
)

INACTIVO = '0'
ACTIVO = '1'
ESTADO = (
    (INACTIVO, 'Inactivo'),
    (ACTIVO, 'Activo'),
    )

class Empresa(models.Model):
    nombre_empresa = models.CharField(max_length=100, unique=True,)
    nick_empresa = models.CharField(max_length=100, unique=True,)
    nit = models.CharField(max_length=10, unique=True)
    dv = models.CharField(max_length=1)
    representante_legal = models.CharField(max_length=200)
    email = models.EmailField(max_length=254)
    telefono_fijo = models.CharField(max_length=14)
    telefono_celular = models.CharField(max_length=14)
    direccion_principal = models.CharField(max_length=200)
    ciudad = models.CharField(max_length=30)
    regimen = models.CharField(max_length=1, choices=REGIMEN_EMPRESA, default=COMUN, )
    estado_empresa = models.CharField(max_length=1, choices=ESTADO, default=ACTIVO, )
    vigencia = models.DateField(default=datetime.date.today)

    def __str__(self):
        return '{}'.format(self.nombre_empresa)

    def get_absolute_url(self):
        return reverse('empresa-detail', kwargs={'pk': self.pk})

    class Meta:
        default_permissions = ()
        permissions = [('add_empresa', 'Puede crear empresa'),
                       ('change_empresa', 'Puede modificar empresa'),
                       ('view_empresa', 'Puede ver las empresas')]

class GrupoEmpresa(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    grupo = models.ForeignKey(Group, on_delete=models.CASCADE)

    class Meta:
        unique_together = ['empresa', 'grupo']

class PermisoEmpresa(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    permiso = models.ForeignKey(Permission, on_delete=models.CASCADE)

    class Meta:
        unique_together = ['empresa', 'permiso']


class Usuario(AbstractUser):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, blank=True, null=True)
    tel_inicial = models.CharField(max_length=10, blank=True, null=True)

    def get_absolute_url(self):
        return reverse('atpos:usuario_update', kwargs={'pk': self.pk})
    
    def __str__(self):
        return '{}'.format(self.username)
    
    class Meta:
        default_permissions = ()
        permissions = [('add_usuario', 'Usuario crear'),
                        ('change_usuario', 'Usuario modificar'),
                        ('delete_usuario', 'Usuario eliminar'),
                        ('view_usuario', 'Usuario ver'),
                        ('password_usuario', 'Puede cambiar la clave usuario')]

# // Si no trae lista de precios del cliente o tercero, establece la lista de precio del almacen
# // Si no hay lista de precios del almacen toma la BASE con id = 1
# // select id_lista_precio from lista_precio_almacen where id_almacen = 1 and estado = 'activo'
class ListaPrecios(models.Model): 
    nombre = models.CharField(max_length=20, unique=False)
    descripcion = models.CharField(max_length=250, unique=False)
    moneda = models.CharField(max_length=3, unique=False)
    estado = models.CharField(max_length=1, choices=ESTADO, default=ACTIVO )
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)

    class Meta:
        ordering = ['nombre']
        default_permissions = ()
        permissions = [('add_listaprecios', 'Lista precios crear'),
                       ('change_listaprecios', 'Lista precios modificar'),
                       ('delete_listaprecios', 'Lista precios eliminar'),
                       ('view_listaprecios', 'Lista precios ver')]
        unique_together = ('nombre', 'empresa')


    def serialize(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "moneda": self.moneda,
            "estado_listaprecios": self.estado
        }

    def __str__(self):
        return '{}'.format(self.nombre)
    
    def get_absolute_url(self):
        return reverse('listaprecios-list')

class Almacen(models.Model):
    nombre_almacen = models.CharField(max_length=20)
    prefijo = models.CharField(max_length=5)
    telefono_fijo = models.CharField(max_length=30)
    telefono_celular = models.CharField(max_length=30)
    direccion_almacen = models.CharField(max_length=200)
    ciudad = models.CharField(max_length=30)
    listaprecios = models.ForeignKey(ListaPrecios, null=True, blank=True, on_delete=models.CASCADE)
    estado = models.CharField(
        max_length=1,
        choices=ESTADO,
        default=ACTIVO,
    )
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, blank=True, null=True)

    def get_absolute_url(self):
        return reverse('almacen-list')

    def __str__(self):
        return '{}'.format(self.nombre_almacen)

    class Meta:
        default_permissions = ()
        permissions = [('add_almacen', 'Almacén crear'),
                       ('change_almacen', 'Almacén modificar'),
                       ('delete_almacen', 'Almacén borrar'),
                       ('view_almacen', 'Almacén ver')]
        unique_together = ('empresa', 'nombre_almacen', 'prefijo')


class Caja(models.Model):
    prefijo = models.CharField(max_length=5)
    #nombre_caja = models.CharField(max_length=5)
    tipo_factura = models.CharField(
        max_length=1,
        choices=TIPO_FACTURA,
        default=POS,
    )
    estado = models.CharField(max_length=1, choices=ESTADO, default=ACTIVO )
    almacen = models.ForeignKey(Almacen, on_delete=models.CASCADE, blank=False)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return '{}'.format(self.prefijo)

    def get_absolute_url(self):
        return reverse('caja-list')

    class Meta:
        default_permissions = ()
        permissions = [('add_caja', 'Caja crear'),
                       ('change_caja', 'Caja modificar'),
                       ('delete_caja', 'Caja eliminar'),
                       ('view_caja', 'Caja ver')]
        unique_together = ('prefijo', 'empresa',)

class CajaSerie(models.Model):
    numero_caja = models.IntegerField()
    estado = models.CharField(
        max_length=1,
        choices=ESTADO,
        default=ACTIVO,
    )
    almacen = models.ForeignKey(Almacen, on_delete=models.CASCADE, blank=False)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return '{}'.format(self.numero_caja)

    def get_absolute_url(self):
        return reverse('cajaserie-list')

    class Meta:
        default_permissions = ()
        permissions = [('add_cajaserie', 'CajaSerie crear'),
                       ('change_cajaserie', 'CajaSerie modificar'),
                       ('delete_cajaserie', 'CajaSerie eliminar'),
                       ('view_cajaserie', 'CajaSerie ver')]
        unique_together = ('numero_caja', 'almacen', 'empresa',)

class Categoria(models.Model):
    nombre_categoria = models.CharField(max_length=30)
    categoria_padre = models.ForeignKey('self', blank=True, null=True, related_name='child', on_delete=models.CASCADE)
    estado_categoria = models.CharField(max_length=1, choices=ESTADO, default=ACTIVO, )
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)

    def __str__(self):
        p_list = self._recurse_for_parents(self)
        p_list.append(self.nombre_categoria)
        return self.get_separator().join(p_list)

    def _recurse_for_parents(self, cat_obj):
        p_list = []
        if cat_obj.categoria_padre_id:
            p = cat_obj.categoria_padre
            p_list.append(p.nombre_categoria)
            more = self._recurse_for_parents(p)
            p_list.extend(more)
        if cat_obj == self and p_list:
            p_list.reverse()
        return p_list

    def get_separator(self):
        return ' :: '
    
    def get_absolute_url(self):
        return reverse('categoria-list') #, kwargs={'pk': self.pk})

    def _parents_repr(self):
        p_list = self._recurse_for_parents(self)
        return self.get_separator().join(p_list)
    _parents_repr.short_description = "Etiqueta padre"


class UnidadMedida(models.Model):
    codigo_unidad_medida = models.CharField(max_length=30, unique=False)
    nombre_unidad_medida = models.CharField(max_length=30, unique=False)
    estado = models.CharField(max_length=1, choices=ESTADO, default=ACTIVO )
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre_unidad_medida
    
    def get_absolute_url(self):
        return reverse('unidadmedida-list')
    
    class Meta:
        default_permissions = ()
        permissions = [('add_unidadmedida', 'Unidad Medida crear'),
                       ('change_unidadmedida', 'Unidad Medida modificar'),
                       ('delete_unidadmedida', 'Unidad Medida eliminar'),
                       ('view_unidadmedida', 'Unidad Medida ver')]
        unique_together = ('codigo_unidad_medida', 'empresa')

class BaseIVA(models.Model):
    base_iva = models.DecimalField(max_digits=7, decimal_places=4)
    nombre_base_iva = models.CharField(max_length=30)
    estado = models.CharField(max_length=1, choices=ESTADO, default=ACTIVO )
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre_base_iva
    
    def get_absolute_url(self):
        return reverse('baseiva-list')

    class Meta:
        default_permissions = ()
        permissions = [('add_baseiva', 'Base IVA crear'),
                       ('change_baseiva', 'Base IVA modificar'),
                       ('delete_baseiva', 'Base IVA eliminar'),
                       ('view_baseiva', 'Base IVA ver')]
        unique_together = ('base_iva', 'nombre_base_iva')

class Articulo(models.Model):
    codigo_articulo = models.CharField(max_length=20, unique=False)
    nombre_articulo = models.CharField(max_length=30)
    nombre_largo_articulo = models.CharField(max_length=250, null=True, blank=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT)
    unidad_medida = models.ForeignKey(UnidadMedida, on_delete=models.PROTECT)
    base_iva = models.ForeignKey(BaseIVA, default=0, on_delete=models.PROTECT)
    estado = models.CharField(max_length=1, choices=ESTADO, default=ACTIVO )
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)

    def __str__(self):
        return '{} - {}'.format(self.codigo_articulo, self.nombre_articulo)
    
    def get_absolute_url(self):
        return reverse('articulo-list')
    
    class Meta:
        default_permissions = ()
        permissions = [('add_articulo', 'Artículo crear'),
                       ('change_articulo', 'Artículo modificar'),
                       ('view_articulo', 'Artículo ver'),
                       ('delete_articulo', 'Artículo borrar')]
        unique_together = ('codigo_articulo', 'empresa')

""" TODO -> Hay que hacer 2 cosas al momento de salvar un nuevo articulo o item, 
        crearlo en códigos alternos y cuidar la posición del alterno.

    TODO -> En el CodigoAlterno incluir CANTIDAD, PRECIO, LISTA DE PRECIOS para
    manejar 

    SELECT codigo, id_articulo, posicion, descripcion, estado, dg_fecha_accion, dg_accion
	FROM public.codigo_articulo order by id_articulo, posicion ASC """
class CodigoAlterno(models.Model):
    articulo = models.ForeignKey(Articulo, on_delete=models.PROTECT)
    nuevo_codigo_articulo = models.CharField(max_length=20, unique=False)
    posicion = models.IntegerField(default=0)
    cantidad = models.IntegerField(default=1)
    precio = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    listaPrecio = models.ForeignKey(ListaPrecios, on_delete=models.PROTECT, null=True, blank=True)
    nombre_articulo = models.CharField(max_length=30)
    estado = models.CharField(max_length=1, choices=ESTADO, default=ACTIVO )
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    
    def get_absolute_url(self):        
        return reverse('articulo-list')
    
    class Meta:
        default_permissions = ()
        permissions = [('add_codigoalterno', 'Código Alterno crear'),
                       ('change_codigoalterno', 'Código Alterno modificar'),
                       ('view_codigoalterno', 'Código Alterno ver'),
                       ('delete_codigoalterno', 'Código Alterno borrar')]
        unique_together = ('nuevo_codigo_articulo', 'empresa')


class Serial(models.Model):
    id_articulo = models.ForeignKey(Articulo, on_delete=models.CASCADE)
    serial = models.CharField(max_length=20, unique=True)
    fecha_ingreso = models.DateField(auto_now=False)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)

    def __str__(self):
        return self.serial


class NivelesInventario(models.Model):
    id_articulo = models.ForeignKey(Articulo, on_delete=models.CASCADE)
    maximo = models.DecimalField(max_digits=5, decimal_places=4)
    minimo = models.DecimalField(max_digits=5, decimal_places=4)
    reorden = models.DecimalField(max_digits=5, decimal_places=4)
    almacen = models.ForeignKey(Almacen, on_delete=models.CASCADE)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)

    def __str__(self):
        return 'ID={} Maximo={} Minimo={} Reorden={}'.format(self.id_articulo, self.maximo, self.minimo, self.reorden)


# todo bodega picking
class Bodega(models.Model):
    id_almacen = models.ForeignKey(Almacen, on_delete=models.CASCADE)
    estante = models.IntegerField(default=0)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)

    def __str__(self):
        return self.id_almacen

'''
SELECT id, nombre, descripcion, moneda, estado, fecha_exportacion, dg_fecha_accion, dg_accion
	FROM public.lista_precio;
	
SELECT id, id_lista_precio, id_articulo, cantidad, precio, id_presentacion, descripcion, estado, dg_fecha_accion, dg_accion
	FROM public.lista_precio_articulo;	

SELECT id, id_lista_precio, id_almacen, estado, fecha_exportacion, dg_fecha_accion, dg_accion
	FROM public.lista_precio_almacen;

verifico cual lista de precio se debe usar 
- select id_lista_precio from tercero where id = 3 and documento = 900123456 and estado='activo' /*con el documento del tercero me da el id_lista_precio 
si no tiene lista de precio en tercero lo busca en cliente 
- select id_lista_precio from cliente where id = 11 and documento = 108 and estado='activo' /* con el dcumento del cliente me da el id_lista_precio
si no tiene lista de precio en cliente toma la del almacen el id_almacen se encuentra en la licencia que está en C:\tmp\lic\serv
- select id_lista_precio from lista_precio_almacen where id_almacen = 1 and estado = 'activo'
si no tiene lista de precios en el almacen toma la lista BASE
- select * from lista_precio /* La lista de precios BASE siempre es la 1
Con la lista de precios establecida se va a la lista_precio_articulo
El caso de los huevos un códgo por unidad y un código por empaque de 30, maneja descuentos por cantidad
- select * from articulo where codigo = '1272.01'
- select * from codigo_articulo where id_articulo = 211
verifico que el producto tenga precio en la lista de precios seleccionada
- select COUNT(*) from lista_precio_articulo where id_articulo = 211 and id_lista_precio = 2
si la respuesta es 0 se dirige a la base o sea la 1, el producto no tiene descuento por cantidad en esa lista de precios
si es >=1, con la lista de precios y el id sel articulo se conoce si tiene descuentos por cantidad
- select * from lista_precio_articulo where id_articulo = 211 and id_lista_precio = 1 order by cantidad DESC
Tomo la cantidad que compra el cliente y la comparo con la cantidad mayor
select * from lista_precio_articulo where id_articulo = 211 and id_lista_precio = 1*/
'''



class ListaPreciosArticulo(models.Model):
    id_lista_precio = models.ForeignKey(ListaPrecios, on_delete=models.CASCADE)
    id_articulo = models.ForeignKey(Articulo, on_delete=models.CASCADE)
    cantidad = models.DecimalField(max_digits=5, decimal_places=4) 
    precio = models.DecimalField(max_digits=5, decimal_places=4)
    id_presentacion = models.ForeignKey(UnidadMedida, on_delete=models.CASCADE)
    descripcion = models.CharField(max_length=20, unique=True)
    estado = models.CharField(max_length=1, choices=ESTADO, default=ACTIVO )
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)

    def __str__(self):
        return '{} {}'.format(self.id_lista_precio, self.id_articulo)

class ListaPreciosAlmacen(models.Model):
    id_lista_precio = models.ForeignKey(ListaPrecios, on_delete=models.CASCADE)
    id_almacen = models.ForeignKey(Almacen, on_delete=models.CASCADE)
    estado = models.CharField(max_length=1, choices=ESTADO, default=ACTIVO )
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)

    def __str__(self):
        return '{} {}'.format(self.id_lista_precio, self.id_almacen)












