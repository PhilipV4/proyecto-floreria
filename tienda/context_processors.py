from .models import Categoria


def categorias_navbar(request):
    return {'categorias_navbar': Categoria.objects.order_by('nombre')}