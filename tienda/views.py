from django.contrib import messages

from django.shortcuts import redirect, render, get_object_or_404

from tienda.decorators import role_required
from django.contrib.auth.decorators import login_required

from .models import Categoria, Ocasion, Producto

from .forms import CategoriaForm, OcasionForm, ProductoForm, RegistroForm, EditarPerfilForm

from django.db.models import Q

from django.contrib.auth import login
from django.contrib.auth import get_user_model


def inicio(request):
    return render(request, 'inicio.html')

#Catalogo de productos
def catalogo_productos(request):
    #Carga los productos y filtra los productos no disponibles.
    productos = Producto.objects.filter(disponible=True).select_related('categoria','ocasion')

    #Cargamos las Categorias y Ocasiones.
    categorias = Categoria.objects.all()
    ocasiones = Ocasion.objects.all()

    #Conseguimos las id de Categoria y Ocasion.
    categoria_id = request.GET.get('categoria')
    ocasion_id = request.GET.get('ocasion')

    #Filtra productos por categoria y ocasion.
    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)
    if ocasion_id:
        productos = productos.filter(ocasion_id=ocasion_id)

    #Diccionario para la pantilla (catalogo/catalogo_productos.html).
    context = {
        'productos' : productos,
        'categorias' : categorias,
        'ocasiones' : ocasiones,
        'categoria_actual' : categoria_id or '',
        'ocasion_actual' : ocasion_id or '',
    }
    
    return render(request, 'catalogo/catalogo_producto.html', context)

#PRUEBA NAVBAR Y FOOTER
def prueba_global_componentes(request):
    return render(request, 'global_componentes/base.html')
#PRUEBA DETALLE PRODUCTO
def detalle_producto(request):
    return render(request, 'catalogo/detalle_producto.html')
    #producto = get_object_or_404(Producto, id=id)
    #return render(request, 'productos/detalle_producto.html', {'producto': producto})

def lista_productos(request):
    #falta agregar no mostrar productos que no esten disponibles, quizas se pueda hacer en el html con un if,
    #pero mejor hacerlo en la vista.

    productos = Producto.objects.filter(disponible=True).select_related('categoria', 'ocasion')

    categoria_id = request.GET.get('categoria')
    ocasion_id = request.GET.get('ocasion')

    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)
    if ocasion_id:
        productos = productos.filter(ocasion_id=ocasion_id)

    categorias= Categoria.objects.all() 
    ocasiones= Ocasion.objects.all()

    context = {
        'productos': productos,
        'categorias': categorias,
        'ocasiones': ocasiones,
        'categoria_actual': categoria_id or '',
        'ocasion_actual': ocasion_id or '',
    }

    return render(request, 'productos/lista_productos.html', context)

#Inicio seccion admin
@role_required('admin') 
def admin_lista_productos(request):
    # Obtenemos todos los productos optimizando las relaciones
    productos = Producto.objects.all().select_related('categoria', 'ocasion')
    
    # Capturamos los parámetros de búsqueda y filtro
    query = request.GET.get('q', '').strip()
    categoria_id = request.GET.get('categoria')

    # Aplicamos filtro de texto si existe
    if query:
        productos = productos.filter(
            Q(nombre__icontains=query) | Q(descripcion__icontains=query))\
        .order_by("-creado_el")  # Limite de 10 resultados

    # Aplicamos filtro de categoría si existe
    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)
        
    categorias = Categoria.objects.all()

    context = {
        'productos': productos,
        'categorias': categorias,
        'categoria_actual': categoria_id or '',
        'query': query,
    }

    # SI LA PETICIÓN VIENE DE HTMX: Devolvemos solo el partial del tbody
    if request.headers.get('HX-Request'):
        return render(request, 'admin/partials/productos_tbody.html', context)

    # CARGA NORMAL: Devolvemos la página completa
    return render(request, 'admin/lista_productos.html', context)

#NO IMPLEMENTADO
#def buscar(request):

    q = request.GET.get('q', '').strip()
    if q:
        results=Producto.objects.filter(Q(nombre__icontains=q) | Q(categoria__nombre__icontains=q)) \
        .order_by("-creado_el")[0:10] #limite de 10 resultados
    else:
        results=[]

    return render(request, 'partials/results.html', {"results": results})
@role_required('admin')
def crear_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('admin_lista_productos')
    else:
        form = ProductoForm()
    return render(request, 'admin/crear.html', {'form': form})

@role_required('admin')
def editar_producto(request, id):
    producto = get_object_or_404(Producto, id=id)
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            return redirect('admin_lista_productos')
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'admin/editar.html', {'form': form, 'producto': producto})

@role_required('admin')
def eliminar_producto(request, id):
    producto = get_object_or_404(Producto, id=id)
    if request.method == 'POST':
        producto.disponible = False
        producto.save()
        return redirect('admin_lista_productos')
    return render(request, 'admin/eliminar.html', {'producto': producto})

@role_required('admin')
def crear_categoria(request):
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_lista_productos') 
    else:
        form = CategoriaForm()
    return render(request, 'admin/crear_categoria.html', {'form': form})
@role_required('admin')
def crear_ocasion(request):
    if request.method == 'POST':
        form = OcasionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_lista_productos') 
    else:
        form = OcasionForm()
    return render(request, 'admin/crear_ocasion.html', {'form': form})

@role_required('admin')
def admin_dashboard(request):
    # contenido del dashboard, por ejemplo estadísticas, gráficos, etc.
    context = {}
    return render(request, 'admin/dashboard.html', context)
#Fin seccion admin

#Registro de usuarios
User = get_user_model()

def registro_view(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('inicio') 
    else:
        form = RegistroForm()
    
    return render(request, 'usuarios/registro.html', {'form': form})



@login_required
def editar_perfil_view(request):
    if request.method == 'POST':
        form = EditarPerfilForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Datos actualizados correctamente.')
            return redirect('editar_perfil')
    else:
        form = EditarPerfilForm(instance=request.user)
    
    return render(request, 'usuarios/editar_perfil.html', {'form': form})