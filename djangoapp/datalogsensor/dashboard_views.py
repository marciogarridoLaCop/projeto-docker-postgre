from datetime import datetime, timedelta

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, Http404
from django.shortcuts import render
from django.utils import timezone

from device.models import Sensor
from .models import Registro

# Períodos disponíveis no seletor do dashboard (rótulo -> janela de tempo).
PERIODOS = {
    '24h': timedelta(hours=24),
    '7d': timedelta(days=7),
    '30d': timedelta(days=30),
}

# Máximo de pontos enviados ao gráfico para manter o payload leve.
MAX_PONTOS = 1000


def sensores_do_usuario(user):
    """Sensores que o usuário pode ver. Superuser vê todos, demais veem os atribuídos."""
    qs = Sensor.objects.all()
    if not user.is_superuser:
        qs = qs.filter(clientes=user).distinct()
    return qs.order_by('local', 'sensor')


@login_required
def dashboard(request):
    """Página do dashboard com o seletor de sensores do usuário logado."""
    return render(request, 'datalogsensor/dashboard.html', {
        'sensores': sensores_do_usuario(request.user),
        'periodos': list(PERIODOS.keys()),
    })


def _parse_dt(valor):
    """Converte 'YYYY-MM-DDTHH:MM' (input datetime-local) em datetime com timezone."""
    if not valor:
        return None
    try:
        dt = datetime.fromisoformat(valor)
    except ValueError:
        return None
    if timezone.is_naive(dt):
        dt = timezone.make_aware(dt, timezone.get_current_timezone())
    return dt


@login_required
def sensor_series(request, pk):
    """Séries temporais (JSON) de um sensor, isoladas por usuário."""
    # Garante que o sensor pertence ao usuário (ou que ele é superuser).
    if not sensores_do_usuario(request.user).filter(pk=pk).exists():
        raise Http404('Sensor não encontrado.')

    registros = (
        Registro.objects
        .filter(Sensor_id=pk, Sensor__clientes=request.user)
        if not request.user.is_superuser
        else Registro.objects.filter(Sensor_id=pk)
    )

    # Intervalo personalizado (inicio/fim) tem prioridade sobre os presets.
    inicio = _parse_dt(request.GET.get('inicio'))
    fim = _parse_dt(request.GET.get('fim'))
    if inicio and fim:
        registros = registros.filter(data_registro__gte=inicio, data_registro__lte=fim)
    else:
        periodo = request.GET.get('periodo', '24h')
        janela = PERIODOS.get(periodo, PERIODOS['24h'])
        registros = registros.filter(data_registro__gte=timezone.now() - janela)

    registros = registros.order_by('data_registro')

    # Amostra uniformemente ao longo do período para que todos os intervalos
    # (24h, 7d, 30d) mostrem dados distribuídos no tempo, não apenas os mais recentes.
    total = registros.count()
    if total > MAX_PONTOS:
        step = max(1, total // MAX_PONTOS)
        registros = list(registros[::step])[:MAX_PONTOS]
    else:
        registros = list(registros)

    labels, temperatura, pressao, umidade, altitude = [], [], [], [], []
    for r in registros:
        labels.append(timezone.localtime(r.data_registro).strftime('%d/%m %H:%M'))
        temperatura.append(r.temperatura)
        pressao.append(r.pressao)
        umidade.append(r.umidade)
        altitude.append(r.altitude)

    return JsonResponse({
        'labels': labels,
        'series': {
            'temperatura': temperatura,
            'pressao': pressao,
            'umidade': umidade,
            'altitude': altitude,
        },
        'total': len(registros),
    })
