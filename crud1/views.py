# views.py
from django.shortcuts import render, redirect 
from .forms import UsuarioForm
from .models import Usuario
from django.http import JsonResponse
from .models import Pelicula
from django.http import JsonResponse, HttpResponseNotFound
from django.contrib import messages
from .models import Pelicula
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Horario
import json
from django.http import HttpResponse
from django.template.loader import get_template
from django.conf import settings
from xhtml2pdf import pisa
from django.shortcuts import render, redirect 
from .forms import UsuarioForm
from .models import Usuario, Pelicula
from django.http import JsonResponse, HttpResponseNotFound
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.shortcuts import render, redirect

def login(request):
    if request.method == 'POST':
        username = request.POST.get('user')
        password = request.POST.get('password')

        user = Usuario.objects.filter(nombre_usuario=username).first()

        if user and user.contraseña == password:
            if user.tipo_usuario == 'taquillero':
                request.session['user_id'] = user.id
                return redirect('interfaz_ta')
            else:
                request.session['user_id'] = user.id
                return redirect('menu')  # Redirige a menu.html
        else:
            error_message = "Nombre de usuario o contraseña incorrectos."
            return render(request, 'login.html', {'error_message': error_message})
    else:
        return render(request, 'login.html')



def logout(request):
    request.session.flush()
    return redirect('login')




def interfaz_sa(request):
    if 'user_id' not in request.session:
        return redirect('login')
    usuarios = Usuario.objects.all()
    return render(request, 'interfaz_sa.html', {'usuarios': usuarios})


def interfaz_ta(request):
    peliculas = Pelicula.objects.all()
    return render(request, 'interfaz_ta.html', {'peliculas': peliculas})

def guardar_usuario(request):
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('interfaz_sa')  
    else:
        form = UsuarioForm()
    return render(request, 'guardar_usuario.html', {'form': form})


def eliminar_usuario(request, usuario_id):
    usuario = Usuario.objects.get(id=usuario_id)
    # Lógica para eliminar el usuario
    usuario.delete()
    return redirect('interfaz_sa')


def editar_usuario(request, usuario_id):
    usuario = Usuario.objects.get(id=usuario_id)
    if request.method == 'POST':
        # Obtener los nuevos datos del formulario
        nombre_usuario = request.POST.get('nombre_usuario')
        tipo_usuario = request.POST.get('tipo_usuario')
        estado = request.POST.get('estado')

        # Actualizar el usuario con los nuevos valores
        usuario.nombre_usuario = nombre_usuario
        usuario.tipo_usuario = tipo_usuario
        usuario.estado = estado
        usuario.save()  # Guardar los cambios en la base de datos

        # Retornar un JSON con el mensaje de éxito
        return JsonResponse({'success': True, 'message': 'Usuario editado exitosamente'})

    return render(request, 'editar_usuario.html', {'usuario': usuario})


def peliculas(request):
    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        
        # Verificar si ya existe una película con el mismo título
        if Pelicula.objects.filter(titulo=titulo).exists():
            return JsonResponse({'error': 'Ya existe una película con este título.'}, status=400)
        
        # Resto del código para guardar la película
        sinopsis = request.POST.get('sinopsis')
        duracion = request.POST.get('duracion')
        genero = request.POST.get('genero')  # Agregar la lógica para el campo de género
        estado = request.POST.get('estado')
        imagen = request.FILES.get('imagen')
        precio = request.POST.get('precio')
        
        pelicula = Pelicula(titulo=titulo, sinopsis=sinopsis, duracion=duracion, genero=genero, estado=estado, imagen=imagen, precio=precio)
        pelicula.save()
        
        return JsonResponse({'message': 'Película agregada exitosamente.'})
    elif request.method == 'GET':
        peliculas_list = Pelicula.objects.all()
        
        # Lista de géneros comunes de películas
        generos_comunes = ['Acción', 'Comedia', 'Drama', 'Ciencia Ficción', 'Fantasía', 'Terror', 'Romance', 'Animación', 'Aventura', 'Documental']

        # Paginación
        paginator = Paginator(peliculas_list, 3)  # Muestra 3 películas por página

        page = request.GET.get('page')
        try:
            peliculas = paginator.page(page)
        except PageNotAnInteger:
            # Si la página no es un número entero, muestra la primera página
            peliculas = paginator.page(1)
        except EmptyPage:
            # Si la página está fuera del rango, muestra la última página de resultados
            peliculas = paginator.page(paginator.num_pages)
        return render(request, 'peliculas.html', {'peliculas': peliculas, 'generos_comunes': generos_comunes})
    else:
        return HttpResponseNotFound()




    #Elimar una pelicula
def eliminar_pelicula(request):
    if request.method == 'POST':
        titulo = request.POST.get('titulo')  # Obtener el título de la película a eliminar
        peliculas_a_eliminar = Pelicula.objects.filter(titulo=titulo)  # Buscar todas las películas con ese título
        peliculas_a_eliminar.delete()  # Eliminar todas las películas encontradas
        return redirect('peliculas')  # Redirigir a la página de películas después de la eliminación
    else:
        # Manejar otras solicitudes HTTP
        return HttpResponseNotFound()

def editar_pelicula(request, pelicula_id):
    pelicula = Pelicula.objects.get(id=pelicula_id)
    if request.method == 'POST':
        # Obtener los nuevos datos del formulario
        titulo = request.POST.get('titulo')
        sinopsis = request.POST.get('sinopsis')
        duracion = request.POST.get('duracion')
        genero = request.POST.get('genero')
        estado = request.POST.get('estado')
        imagen = request.FILES.get('imagen')
        precio = request.POST.get('precio')

        # Actualizar la película con los nuevos valores
        pelicula.titulo = titulo
        pelicula.sinopsis = sinopsis
        pelicula.duracion = duracion
        pelicula.genero = genero
        pelicula.estado = estado
        if imagen:
            pelicula.imagen = imagen
        pelicula.precio = precio
        pelicula.save()  # Guardar los cambios en la base de datos

        # Retornar una respuesta de éxito
        return JsonResponse({'success': True, 'message': 'Película editada exitosamente'})

    return render(request, 'editar_pelicula.html', {'pelicula': pelicula})


def guardar_usuario(request):
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            nombre_usuario = form.cleaned_data['nombre_usuario']
            tipo_usuario = form.cleaned_data['tipo_usuario']
            estado = form.cleaned_data['estado']
            
            # Verificar si ya existe un usuario con el mismo nombre de usuario
            if Usuario.objects.filter(nombre_usuario=nombre_usuario).exists():
                
                messages.error(request, error_message)  # Agregar el mensaje de error a la lista de mensajes
                return redirect('interfaz_sa')  # Redirigir de vuelta a la página de interfaz_sa
            
            # Si el usuario no existe, guardar el usuario
            form.save()
            return redirect('interfaz_sa')  
    else:
        form = UsuarioForm()
    return render(request, 'guardar_usuario.html', {'form': form})



def home(request):
    peliculas = Pelicula.objects.all()
    return render(request, 'home.html', {'peliculas': peliculas})


def menu(request):
    return render(request, 'menu.html')


def generate_pdf(request):
    # Recopila los datos del POST request
     # Recopila los datos del POST request
    sala = request.POST.get('sala')
    fecha = request.POST.get('fecha')
    pelicula = request.POST.get('pelicula')
    hora = request.POST.get('hora')
    cantidad_boletos = request.POST.get('cantidadBoletos')

    # Procesa los datos y genera el contenido del PDF
    template_path = 'pdf_template.html'
    context = {
        'sala': sala,
        'fecha': fecha,
        'pelicula': pelicula,
        'hora': hora,
        'cantidad_boletos': cantidad_boletos
    }
    template = get_template(template_path)
    html = template.render(context)

    # Convierte HTML a PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename="boleto_{sala}_{fecha}_{hora}.pdf"'
    pisa_status = pisa.CreatePDF(html, dest=response)

    # Verifica si hubo errores al generar el PDF
    if pisa_status.err:
        return HttpResponse('Error al generar el PDF', status=500)

    return response