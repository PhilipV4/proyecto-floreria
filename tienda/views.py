from django.shortcuts import redirect, render, get_object_or_404

from .models import Categoria, Ocasion, Producto

from .forms import CategoriaForm, OcasionForm, ProductoForm

# Create your views here.
def inicio(request):
    return render(request, 'inicio.html')

def test(request):
    return render(request, 'test.html')

def lista_productos(request):

    productos = Producto.objects.all().select_related('categoria', 'ocasion')

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

def crear_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('lista_productos')
    else:
        form = ProductoForm()
    return render(request, 'productos/crear.html', {'form': form})


def editar_producto(request, id):
    producto = get_object_or_404(Producto, id=id)
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            return redirect('lista_productos')
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'productos/editar.html', {'form': form, 'producto': producto})


def eliminar_producto(request, id):
    producto = get_object_or_404(Producto, id=id)
    if request.method == 'POST':
        producto.delete()
        return redirect('lista_productos')
    return render(request, 'productos/eliminar.html', {'producto': producto})

def crear_categoria(request):
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('crear_producto') # Vuelve a la creación de producto
    else:
        form = CategoriaForm()
    return render(request, 'productos/crear_categoria.html', {'form': form})

def crear_ocasion(request):
    if request.method == 'POST':
        form = OcasionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('crear_producto') # Vuelve a la creación de producto
    else:
        form = OcasionForm()
    return render(request, 'productos/crear_ocasion.html', {'form': form})