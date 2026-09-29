# 🏥 Clínica Veterinaria — Sistema de Gestión

Sistema web desarrollado en Django para el registro y gestión de mascotas en una clínica veterinaria. Permite a los veterinarios registrar mascotas, actualizar el estado de vacunación y filtrar por especie, con permisos diferenciados entre administradores y veterinarios.

---

## 🚀 Características

- ✅ **CRUD completo** de mascotas (Crear, Leer, Editar, Eliminar)
- ✅ **Autenticación** con login y logout
- ✅ **Permisos por usuario**: cada veterinario ve solo sus mascotas; los administradores ven todas
- ✅ **Validación de datos** en formularios (nombre, edad, especie, fechas)
- ✅ **Protección CSRF** en todos los formularios
- ✅ **Admin de Django personalizado** con columnas, filtros y campos editables
- ✅ **Filtro por especie** y **búsqueda por nombre**
- ✅ **Alerta automática** de mascotas que necesitan vacuna este mes
- ✅ **Base de datos PostgreSQL online** (Supabase)
- ✅ **Variables de entorno** con `.env` (protegidas en `.gitignore`)

---

## 🛠️ Tecnologías utilizadas

| Tecnología | Versión |
|------------|---------|
| Python | 3.12 |
| Django | 6.1 |
| PostgreSQL (Supabase) | 15+ |
| psycopg2-binary | 2.9 |
| dj-database-url | 3.1 |
| python-dotenv | 1.2 |

---

## 📦 Instalación local

### 1. Clonar el repositorio

```bash
git clone https://github.com/br-out99/vet.git
cd vet