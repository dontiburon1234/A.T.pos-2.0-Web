"""inicio URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.contrib.auth.decorators import login_required
from atpos.views import activate_account

from atpos.views import (
    Tablero, 
    CreateAccount, 
    EmpresaCreate, 
    EmpresaDetail, 
    EmpresaUpdate, 
    UsuarioCreate, 
    UsuarioList,
    UsuarioDetail,
    UsuarioUpdate,
    UsuarioUpdatePassword,
    UsuarioDelete,
    cambiar_estado,
    create_group,
    lista_grupos,
    create_permiso,
    lista_permisos,
    crear_grupo,
    AsignarPermisosGrupo,
    RecibirPermisosGrupo,
    UsuarioGruposPermisos,
    AlmacenCreate, AlmacenList, AlmacenDetail, AlmacenUpdate, AlmacenDelete,
    CajaCreate, CajaList, CajaDetail, CajaUpdate, CajaDelete, 
    CajaSerieCreate, CajaSerieList, CajaSerieDetail, CajaSerieUpdate, CajaSerieDelete,
    CategoriaCreate, CategoriaList, CategoriaListArticulos, CategoriaUpdate, CategoriaDelete,
    UnidadMedidaCreate, UnidadMedidaList, UnidadMedidaUpdate, UnidadMedidaDelete,
    BaseIVACreate, BaseIVAList, BaseIVAUpdate,BaseIVADelete,
    ArticuloCreate, ArticuloDelete, ArticuloList, CodigoAlternoCreate, ArticuloUpdate, Alterno, AlternoFetch,
    ListaPreciosCreate, ListaPreciosList, ListaPreciosDelete, ListaPreciosUpdate
    )

urlpatterns = [
    path('admin/', admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    
    path('', login_required(Tablero.as_view()), name='tablero'),
    path('createaccount/', CreateAccount.as_view(), name='create_account'),
    path('activate/<uidb64>/<token>/', activate_account, name='activate_account'),
    path('crearempresa/', EmpresaCreate.as_view(), name='crear_empresa'),
    path('detail/<int:pk>/', login_required(EmpresaDetail.as_view()), name='empresa-detail'),
    path('update/<int:pk>/', login_required(EmpresaUpdate.as_view()), name='empresa-update'),
    # path('list/', login_required(EmpresaList.as_view()), name='empresa-list'),

    path('user/add/', login_required(UsuarioCreate.as_view()), name='usuario_crear'),
    path('user/list/', login_required(UsuarioList.as_view()), name='user_list'),
    path('user/detail/<int:pk>/', login_required(UsuarioDetail.as_view()), name='usuario_detail'),
    path('user/<slug:pk>/', login_required(UsuarioUpdate.as_view()), name='usuario_update'),

    path('user1/<int:idUser>/', login_required(UsuarioGruposPermisos.as_view()), name='usuario_grupos_permisos'),

    path('user/<int:pk>/password/', login_required(UsuarioUpdatePassword.as_view()), name='usuario_update_password'),
    path('user/<int:pk>/delete/', login_required(UsuarioDelete.as_view()), name='usuario-delete'),

    path('cambiar_estado/', login_required(cambiar_estado), name='cambiar_estado'),

    path('crear_grupo/', login_required(crear_grupo.as_view()), name='crear_grupo'),
    path('asignar_permisos_grupo/<int:grupo>/', login_required(AsignarPermisosGrupo.as_view()), name='asignar_permisos_grupo'),
    path('recibir_permisos_grupo/', login_required(RecibirPermisosGrupo), name='recibir_permisos_grupo'),

    path('almacen/add/', login_required(AlmacenCreate.as_view()), name='almacen-crear'),
    path('almacen/list/', login_required(AlmacenList.as_view()), name='almacen-list'),
    path('almacen/detail/<int:pk>/', login_required(AlmacenDetail.as_view()), name="almacen-detail"),
    path('almacen/update/<int:pk>/', login_required(AlmacenUpdate.as_view()), name='almacen-update'),
    path('almacen/<int:pk>/delete/', login_required(AlmacenDelete.as_view()), name='almacen-delete'),

    path('caja/add/', login_required(CajaCreate.as_view()), name='caja-crear'),
    path('caja/list/', login_required(CajaList.as_view()), name='caja-list'),
    path('caja/detail/<int:pk>/', login_required(CajaDetail.as_view()), name="caja-detail"),
    path('caja/update/<int:pk>/', login_required(CajaUpdate.as_view()), name='caja-update'),
    path('caja/<int:pk>/delete/', login_required(CajaDelete.as_view()), name='caja-delete'),

    path('cajaserie/add/', login_required(CajaSerieCreate.as_view()), name='cajaserie-crear'),
    path('cajaserie/list/', login_required(CajaSerieList.as_view()), name='cajaserie-list'),
    path('cajaserie/detail/<int:pk>/', login_required(CajaSerieDetail.as_view()), name="cajaserie-detail"),
    path('cajaserie/update/<int:pk>/', login_required(CajaSerieUpdate.as_view()), name='cajaserie-update'),
    path('cajaserie/<int:pk>/delete/', login_required(CajaSerieDelete.as_view()), name='cajaserie-delete'),

    path('categoria/add/', login_required(CategoriaCreate.as_view()), name='categoria-add'),
    path('categoria/list/', login_required(CategoriaList.as_view()), name='categoria-list'),
    path('categoria/update/<int:pk>/', login_required(CategoriaUpdate.as_view()), name='categoria-update'),
    path('categoria/list/articulos/<int:pk>/', login_required(CategoriaListArticulos.as_view()), name='categoria-list-articulos'),
    path('categoria/<int:pk>/delete/', login_required(CategoriaDelete.as_view()), name='categoria-delete'),

    path('unidadmedida/add/', login_required(UnidadMedidaCreate.as_view()), name='unidadmedida-add'),
    path('unidadmedida/list/', login_required(UnidadMedidaList.as_view()), name='unidadmedida-list'),
    path('unidadmedida/update/<int:pk>/', login_required(UnidadMedidaUpdate.as_view()), name='unidadmedida-update'),
    path('unidadmedida/<int:pk>/delete/', login_required(UnidadMedidaDelete.as_view()), name='unidadmedida-delete'),

    path('baseiva/add/', login_required(BaseIVACreate.as_view()), name='baseiva-add'),
    path('baseiva/list/', login_required(BaseIVAList.as_view()), name='baseiva-list'),
    path('baseiva/update/<int:pk>/', login_required(BaseIVAUpdate.as_view()), name='baseiva-update'),
    path('baseiva/<int:pk>/delete/', login_required(BaseIVADelete.as_view()), name='baseiva-delete'),

    path('articulo/add/', login_required(ArticuloCreate.as_view()), name='articulo-add'),
    path('articulo/<int:pk>/delete/', login_required(ArticuloDelete.as_view()), name='articulo-delete'),
    path('articulo/list/', login_required(ArticuloList.as_view()), name='articulo-list'),
    path('articulo/update/<int:pk>/', login_required(ArticuloUpdate.as_view()), name='articulo-update'),

    path('articulo/alterno/<int:pk>/', login_required(CodigoAlternoCreate.as_view()), name='articulo-codigo-alterno'),
    path('articulo/<int:pk>/alterno/', login_required(Alterno.as_view()), name='alterno'),
    path('alterno/<int:pk>/', AlternoFetch.as_view(), name='alternofetch'),

    path('listaprecios/add/', login_required(ListaPreciosCreate.as_view()), name='listaprecios-add'),
    path('listaprecios/list/', login_required(ListaPreciosList.as_view()), name='listaprecios-list'),
    path('listaprecios/<int:pk>/delete/', login_required(ListaPreciosDelete.as_view()), name='listaprecios-delete'),
    path('listaprecios/update/<int:pk>/', login_required(ListaPreciosUpdate.as_view()), name='listaprecios-update'),

    path('crear_grupo1/', login_required(create_group), name='crear_grupo1'),
    path('lista_grupos/', login_required(lista_grupos), name='lista_grupos'),
    
    path('create_permiso/', login_required(create_permiso), name='create_permiso'),
    # path('lista_permisos/', login_required(lista_permisos), name='lista_permisos'),

]

