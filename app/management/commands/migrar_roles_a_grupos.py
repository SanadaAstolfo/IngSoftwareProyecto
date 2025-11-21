"""
Comando de gestión Django para migrar los roles del modelo Perfil a grupos de Django.
Este comando crea los grupos necesarios y asigna los usuarios basándose en su perfil.rol actual.

Uso: python manage.py migrar_roles_a_grupos
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, User
from app.models import Perfil


class Command(BaseCommand):
    help = 'Migra los roles del modelo Perfil a grupos de Django'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Iniciando migración de roles a grupos...'))

        # Mapeo de roles antiguos a nombres de grupos
        MAPEO_ROLES = {
            'ADMIN': 'Administrador',
            'VET': 'Veterinario',
            'ESP': 'Veterinario Especialista',
            'SECRETARIA': 'Secretaria',
            'TUTOR': 'Tutor',
        }

        # Crear grupos si no existen
        grupos_creados = 0
        for nombre_grupo in MAPEO_ROLES.values():
            grupo, created = Group.objects.get_or_create(name=nombre_grupo)
            if created:
                grupos_creados += 1
                self.stdout.write(self.style.SUCCESS(f'  ✓ Grupo "{nombre_grupo}" creado'))
            else:
                self.stdout.write(f'  • Grupo "{nombre_grupo}" ya existe')

        self.stdout.write(self.style.SUCCESS(f'\nGrupos creados: {grupos_creados}\n'))

        # Migrar usuarios
        usuarios_migrados = 0
        usuarios_sin_perfil = 0
        errores = 0

        for usuario in User.objects.all():
            try:
                if hasattr(usuario, 'perfil') and usuario.perfil:
                    perfil = usuario.perfil
                    rol_antiguo = perfil.rol
                    
                    if rol_antiguo in MAPEO_ROLES:
                        nombre_grupo = MAPEO_ROLES[rol_antiguo]
                        grupo = Group.objects.get(name=nombre_grupo)
                        
                        # Agregar al grupo si no está ya
                        if not usuario.groups.filter(name=nombre_grupo).exists():
                            usuario.groups.add(grupo)
                            usuarios_migrados += 1
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f'  ✓ Usuario "{usuario.username}" ({usuario.email}) → Grupo "{nombre_grupo}"'
                                )
                            )
                        else:
                            self.stdout.write(
                                f'  • Usuario "{usuario.username}" ya pertenece al grupo "{nombre_grupo}"'
                            )
                    else:
                        self.stdout.write(
                            self.style.WARNING(
                                f'  ⚠ Usuario "{usuario.username}": rol desconocido "{rol_antiguo}"'
                            )
                        )
                        errores += 1
                else:
                    usuarios_sin_perfil += 1
                    self.stdout.write(
                        self.style.WARNING(
                            f'  ⚠ Usuario "{usuario.username}" no tiene perfil asociado'
                        )
                    )
            except Exception as e:
                errores += 1
                self.stdout.write(
                    self.style.ERROR(
                        f'  ✗ Error al procesar usuario "{usuario.username}": {str(e)}'
                    )
                )

        # Resumen final
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('\nRESUMEN DE MIGRACIÓN:'))
        self.stdout.write(f'  • Usuarios migrados: {usuarios_migrados}')
        self.stdout.write(f'  • Usuarios sin perfil: {usuarios_sin_perfil}')
        self.stdout.write(f'  • Errores: {errores}')
        self.stdout.write('\n' + '='*60)
        
        if errores == 0 and usuarios_migrados > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    '\n✓ Migración completada exitosamente. '
                    'Los usuarios ahora están asignados a grupos de Django.'
                )
            )
        elif usuarios_migrados == 0:
            self.stdout.write(
                self.style.WARNING(
                    '\n⚠ No se migraron usuarios. '
                    'Todos los usuarios ya estaban en sus grupos correspondientes.'
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    f'\n⚠ Migración completada con {errores} error(es). '
                    'Revisa los mensajes anteriores.'
                )
            )
