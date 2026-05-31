"""
Migração: substitui o ForeignKey `cliente` por ManyToMany com modelo intermediário
SensorUsuario, preservando os dados existentes.

Ordem das operações:
  1. Ajustes de meta e campos (não-destrutivos)
  2. Cria tabela SensorUsuario
  3. Migração de dados: copia cliente → SensorUsuario(nivel='proprietario')
  4. Remove o campo cliente (agora seguro)
  5. Adiciona o campo clientes (M2M through)
"""
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def migrar_cliente_para_sensor_usuario(apps, schema_editor):
    Sensor = apps.get_model('device', 'Sensor')
    SensorUsuario = apps.get_model('device', 'SensorUsuario')
    criados = 0
    for sensor in Sensor.objects.filter(cliente__isnull=False).select_related('cliente'):
        _, novo = SensorUsuario.objects.get_or_create(
            sensor=sensor,
            usuario=sensor.cliente,
            defaults={'nivel': 'proprietario'},
        )
        if novo:
            criados += 1
    print(f'\n  → {criados} acesso(s) de proprietário migrado(s).')


def reverter_sensor_usuario(apps, schema_editor):
    """Desfaz apenas a migração de dados (não recria o campo cliente)."""
    SensorUsuario = apps.get_model('device', 'SensorUsuario')
    SensorUsuario.objects.filter(nivel='proprietario').delete()


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('device', '0003_sensor_cliente'),
    ]

    operations = [
        # ── 1. Ajustes de meta e campos (não-destrutivos) ─────────────────────
        migrations.AlterModelOptions(
            name='sensor',
            options={
                'ordering': ['data_cadastro'],
                'verbose_name': 'Sensor',
                'verbose_name_plural': 'Sensores',
            },
        ),
        migrations.AlterModelOptions(
            name='tipo',
            options={
                'ordering': ['nome'],
                'verbose_name': 'Tipo de Sensor',
                'verbose_name_plural': 'Tipos de Sensor',
            },
        ),
        migrations.AlterField(
            model_name='sensor',
            name='data_cadastro',
            field=models.DateField(verbose_name='Data de Cadastro'),
        ),
        migrations.AlterField(
            model_name='sensor',
            name='latitude',
            field=models.CharField(blank=True, max_length=11, null=True, verbose_name='Latitude'),
        ),
        migrations.AlterField(
            model_name='sensor',
            name='longitude',
            field=models.CharField(blank=True, max_length=11, null=True, verbose_name='Longitude'),
        ),
        migrations.AlterField(
            model_name='sensor',
            name='macaddress',
            field=models.CharField(max_length=17, unique=True, verbose_name='Endereço MAC'),
        ),
        migrations.AlterField(
            model_name='sensor',
            name='observacao',
            field=models.TextField(blank=True, max_length=200, null=True, verbose_name='Observação'),
        ),
        migrations.AlterField(
            model_name='sensor',
            name='tipo',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to='device.tipo',
                verbose_name='Tipo',
            ),
        ),

        # ── 2. Cria a tabela SensorUsuario ────────────────────────────────────
        migrations.CreateModel(
            name='SensorUsuario',
            fields=[
                ('id', models.BigAutoField(
                    auto_created=True, primary_key=True, serialize=False, verbose_name='ID',
                )),
                ('nivel', models.CharField(
                    choices=[('proprietario', 'Proprietário'), ('colaborador', 'Colaborador')],
                    default='colaborador',
                    max_length=20,
                    verbose_name='Nível de Acesso',
                )),
                ('desde', models.DateField(auto_now_add=True, verbose_name='Desde')),
                ('sensor', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='acessos',
                    to='device.sensor',
                    verbose_name='Sensor',
                )),
                ('usuario', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='sensor_acessos',
                    to=settings.AUTH_USER_MODEL,
                    verbose_name='Usuário',
                )),
            ],
            options={
                'verbose_name': 'Acesso ao Sensor',
                'verbose_name_plural': 'Acessos ao Sensor',
                'ordering': ['nivel', 'usuario__username'],
                'unique_together': {('sensor', 'usuario')},
            },
        ),

        # ── 3. Migração de dados: cliente FK → SensorUsuario ─────────────────
        migrations.RunPython(
            migrar_cliente_para_sensor_usuario,
            reverse_code=reverter_sensor_usuario,
        ),

        # ── 4. Remove o campo cliente (agora seguro) ──────────────────────────
        migrations.RemoveField(
            model_name='sensor',
            name='cliente',
        ),

        # ── 5. Adiciona o campo clientes (M2M through SensorUsuario) ──────────
        migrations.AddField(
            model_name='sensor',
            name='clientes',
            field=models.ManyToManyField(
                blank=True,
                related_name='sensores',
                through='device.SensorUsuario',
                to=settings.AUTH_USER_MODEL,
                verbose_name='Usuários com Acesso',
            ),
        ),
    ]
