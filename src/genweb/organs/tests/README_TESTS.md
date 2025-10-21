# 🧪 Tests de genweb.organs - Guía de Ejecución

Esta guía documenta cómo ejecutar los tests de permisos implementados para `genweb.organs`.

## 📋 Índice de Tests Implementados

### ✅ Tests de Permisos Completos

1. **test_create_sessions.py**
   - Verifica quién puede crear sesiones
   - Cubre los 3 tipos de órganos

2. **test_file_permission_in_organs_oberts.py**
   - Permisos de archivos (visiblefile/hiddenfile) en órganos abiertos
   - Todos los roles + anónimos

3. **test_file_permission_in_organs_restricted_to_membres.py**
   - Permisos de archivos en órganos restringidos a miembros
   - Regla especial: OG3-Membre/OG5-Convidat solo ven hiddenfile

4. **test_file_permission_in_organs_restricted_to_afectats.py**
   - Permisos de archivos en órganos restringidos a afectados
   - Reglas especiales para OG3-Membre y OG4-Afectat

5. **test_actes_view_permission_in_organs_oberts.py**
   - Vista de actas/audios en órganos abiertos
   - Todos los roles, todos los estados

6. **test_actes_view_permission_in_organs_restricted_to_membres.py** ⭐ NUEVO
   - Vista de actas/audios en órganos restringidos a miembros
   - OG4-Afectat sin acceso

7. **test_actes_view_permission_in_organs_restricted_to_afectats.py** ⭐ NUEVO
   - Vista de actas/audios en órganos restringidos a afectados
   - OG4-Afectat sin acceso a actas

8. **test_content_type_permissions.py** ⭐ NUEVO
   - Permisos CRWDE sobre tipos de contenido
   - Por estado de sesión (PLANIFICADA, CONVOCADA, TANCADA)

9. **test_organ_permissions.py** ⭐ NUEVO
   - Permisos RWD sobre el órgano
   - Todos los roles + anónimos

10. **test_organ_tabs.py** ⭐ NUEVO
    - Visibilidad de pestañas del órgano (Sessions, Actes, FAQ)
    - Todos los roles + anónimos
    - 8 tests implementados

11. **test_session_actions_by_state.py** ⭐ NUEVO
    - Acciones sobre sesiones por estado de workflow
    - Convoca, Realitza, Excusa, Missatge, Presentació, Historial
    - 22 tests implementados

12. **test_organ_actions.py** ⭐ NUEVO
    - Acciones sobre el órgano (Crear sessió, Numera, Exportar acords)
    - Verificación de métodos viewOrdena, viewExportAcords
    - 12 tests implementados

13. **test_acta_actions.py** ⭐ NUEVO
    - Acciones sobre actas (Vista prèvia, Imprimeix)
    - Todos los roles según estado y tipo de órgano
    - 9 tests implementados

14. **test_votaciones.py** ⭐ NUEVO
    - Sistema de votaciones completo
    - Obrir/Tancar votació, Botons per votar, Resultados
    - 12 tests implementados

15. **test_quorum.py** ⭐ NUEVO
    - Sistema de quorum completo
    - Gestionar/Añadir/Eliminar quorum
    - Permisos para Manager, OG1-Secretari, OG2-Editor, OG3-Membre
    - 12 tests implementados

## 🚀 Comandos de Ejecución

### Ejecutar TODOS los tests

```bash
cd /Users/pilarmarinas/Development/Plone/organs6.buildout
./bin/test -s genweb.organs
```

### Ejecutar tests específicos

#### Tests de creación de sesiones
```bash
./bin/test -s genweb.organs -t test_create_sessions
```

#### Tests de permisos de archivos
```bash
# Órganos abiertos
./bin/test -s genweb.organs -t test_file_permission_in_organs_oberts

# Órganos restringidos a miembros
./bin/test -s genweb.organs -t test_file_permission_in_organs_restricted_to_membres

# Órganos restringidos a afectados
./bin/test -s genweb.organs -t test_file_permission_in_organs_restricted_to_afectats
```

#### Tests de vista de actas
```bash
# Órganos abiertos
./bin/test -s genweb.organs -t test_actes_view_permission_in_organs_oberts

# Órganos restringidos a miembros ⭐ NUEVO
./bin/test -s genweb.organs -t test_actes_view_permission_in_organs_restricted_to_membres

# Órganos restringidos a afectados ⭐ NUEVO
./bin/test -s genweb.organs -t test_actes_view_permission_in_organs_restricted_to_afectats
```

#### Tests de permisos CRWDE ⭐ NUEVO
```bash
./bin/test -s genweb.organs -t test_content_type_permissions
```

#### Tests de permisos sobre órganos ⭐ NUEVO
```bash
./bin/test -s genweb.organs -t test_organ_permissions
```

#### Tests de pestañas del órgano ⭐ NUEVO
```bash
./bin/test -s genweb.organs -t test_organ_tabs
```

#### Tests de acciones sobre sesiones por estado ⭐ NUEVO
```bash
./bin/test -s genweb.organs -t test_session_actions_by_state
```

#### Tests de acciones sobre el órgano ⭐ NUEVO
```bash
./bin/test -s genweb.organs -t test_organ_actions
```

#### Tests de acciones sobre actas ⭐ NUEVO
```bash
./bin/test -s genweb.organs -t test_acta_actions
```

#### Tests de votaciones ⭐ NUEVO
```bash
./bin/test -s genweb.organs -t test_votaciones
```

#### Tests de quorum ⭐ NUEVO
```bash
./bin/test -s genweb.organs -t test_quorum
```

#### Ejecutar todos los tests de acciones y UI (75 tests) ⭐ NUEVO
```bash
./bin/test -s genweb.organs -t test_organ_tabs -t test_session_actions_by_state -t test_organ_actions -t test_acta_actions -t test_votaciones -t test_quorum
```

### Ejecutar con verbosidad

```bash
# Ver detalles de ejecución
./bin/test -s genweb.organs -vvv

# Ver solo nombres de tests
./bin/test -s genweb.organs -v
```

### Ejecutar con coverage

```bash
# Coverage con reporte
./bin/test -s genweb.organs --coverage=coverage_report

# Ver el reporte generado
# El reporte se guarda en la carpeta coverage_report/
```

### Ejecutar solo un test específico

```bash
# Ejecutar un solo método de test
./bin/test -s genweb.organs -t test_secretari_permissions_in_planificada
```

## 📊 Interpretación de los Prints

Los tests incluyen prints informativos con emojis para facilitar el seguimiento:

### Emojis utilizados

- ✅ **Verde**: Test de permisos permitidos (debería tener acceso)
- ❌ **Rojo**: Test de restricciones (NO debería tener acceso)
- ✓ **Checkmark**: Verificación individual exitosa
- ⚠️ **Warning**: Advertencia o nota informativa
- 📊 **Gráfico**: Resumen de permisos

### Ejemplo de output

```
✅ Verificando permisos del rol OG1-Secretari en órgano membres
  ✓ Verificando acceso en sesión PLANIFICADA
  ✓ Acceso correcto a actas en sesión PLANIFICADA
  ✓ Verificando acceso en sesión CONVOCADA
  ✓ Acceso correcto a actas en sesión CONVOCADA
  ✓ Verificación completa como OG1-Secretari

❌ Verificando restricciones del rol OG3-Membre en órgano membres
  ✓ Verificando restricciones en sesión PLANIFICADA
  ✓ Acceso denegado correctamente en sesión PLANIFICADA
  ✓ Verificando acceso permitido en sesión CONVOCADA
  ✓ Acceso permitido en sesión CONVOCADA
  ✓ Verificación completa como OG3-Membre
```

## 🔍 Debugging

### Ejecutar con ipdb

Si un test falla y quieres debuggear:

```bash
# Ejecutar con debugger automático en errores
./bin/test -s genweb.organs --ipdb
```

### Ver logs detallados

```bash
# Ejecutar con verbosidad máxima
./bin/test -s genweb.organs -vvv
```

### Ejecutar un solo test con debug

```bash
# Añadir ipdb.set_trace() en el código del test
import ipdb; ipdb.set_trace()

# Ejecutar el test
./bin/test -s genweb.organs -t nombre_del_test
```

## 📝 Notas Importantes

### Request del Layer

Los tests usan `self.request = self.layer['request']` en lugar de crear un `TestRequest()`.
Esto es crítico para tests funcionales en Plone 6.

### Warnings Suprimidos

Los tests suprimen warnings molestos:
- `ResourceWarning`: Archivos blob no cerrados explícitamente
- `DeprecationWarning`: Avisos de deprecación de Plone

### Logout entre Tests

Todos los tests hacen `logout()` al inicio y al final para aislar estados.

### Estados de Workflow

Los tests cubren 5 estados de sesión:
1. `planificada` (estado inicial)
2. `convocada` (transición: convocar)
3. `realitzada` (transiciones: convocar, realitzar)
4. `tancada` (transiciones: convocar, realitzar, tancar)
5. `correccio` (transiciones: convocar, realitzar, correccio)

## 🎯 Permisos Verificados

### Por Rol

| Rol | Permisos sobre Órgano | Crear Sesiones | Actas | Archivos |
|-----|----------------------|----------------|-------|----------|
| **OG1-Secretari** | RWD | ✅ | ✅ Todos | ✅ Todos |
| **OG2-Editor** | RW | ✅ | ✅ Todos | ✅ Todos |
| **OG3-Membre** | R | ❌ | ⚠️ Desde CONVOCADA | ⚠️ Reglas especiales |
| **OG4-Afectat** | R | ❌ | ⚠️ Solo TANCADA (open) | ⚠️ Reglas especiales |
| **OG5-Convidat** | R | ❌ | ⚠️ Desde CONVOCADA | ⚠️ Reglas especiales |
| **Anónimo** | R (solo open) | ❌ | ❌ (except open) | ⚠️ Solo visiblefile |

### Por Estado de Sesión

#### PLANIFICADA
- Solo OG1-Secretari y OG2-Editor
- CRWDE (Secretari) / CRWE (Editor)

#### CONVOCADA, REALITZADA, EN_CORRECCIO
- OG1-Secretari: CRWDE
- OG2-Editor: CRWE
- Otros roles: R (solo lectura)

#### TANCADA
- OG1-Secretari: RWDE (sin Create)
- OG2-Editor: RWE (sin Create)
- Otros roles: R (solo lectura)

## 📚 Documentación Relacionada

- **Documento de Permisos**: `docs/resumen_permisos_organs.html`
- **Cobertura de Tests**: `docs/tests_coverage.md`
- **Testing Layer**: `src/genweb/organs/testing.py`

## 🐛 Troubleshooting

### Test falla con "Unauthorized"

Verifica:
1. ¿El usuario tiene el rol correcto?
2. ¿El rol está asignado al objeto correcto (órgano)?
3. ¿El estado de la sesión es el esperado?

### Test falla con "AttributeError"

Verifica:
1. ¿Los objetos se crearon correctamente en setUp?
2. ¿Las transiciones de workflow se aplicaron?
3. ¿Existe el archivo/contenido que intentas acceder?

### Tests muy lentos

- Los tests funcionales son más lentos que los de integración
- Cada test crea una estructura completa de órgano/sesiones
- Considera ejecutar solo los tests que necesitas durante desarrollo

## 📊 Coverage Report

### Generar reporte de cobertura

```bash
# Desde el directorio del paquete
cd src/genweb.organs

# Ejecutar coverage con todos los tests
../../bin/coverage run --source=src/genweb/organs ../../bin/test -s genweb.organs

# Generar reporte HTML
../../bin/coverage html -d coverage_report

# Abrir en navegador
open coverage_report/index.html
```

### Ejecutar coverage con un test específico

```bash
cd src/genweb.organs

# Solo test_votaciones
../../bin/coverage run --source=src/genweb/organs ../../bin/test -s genweb.organs -t test_votaciones

# Generar reporte
../../bin/coverage html -d coverage_report
```

### Ver reporte en texto

```bash
cd src/genweb.organs
../../bin/coverage report --show-missing
```

### Configuración Coverage (.coveragerc)

El archivo `.coveragerc` en `src/genweb.organs/` está configurado correctamente:

```ini
[run]
source = src/genweb/organs

[report]
include =
    src/genweb/organs/*

omit =
    */test*
    */tests/*
    */testing/*

[html]
directory = coverage_report
```

## ✅ Checklist antes de Commit

- [ ] Todos los tests pasan: `./bin/test -s genweb.organs`
- [ ] Coverage generado correctamente (ver comandos arriba)
- [ ] No hay prints de debug olvidados (excepto los informativos)
- [ ] No hay `import ipdb; ipdb.set_trace()` olvidados
- [ ] Los mensajes de commit siguen el formato convencional

## 📊 Resumen de Tests Implementados

**Total: 15/15 tests (100%)**

**75 tests funcionales en total**:
- ✅ 8 tests - Pestañas del órgano
- ✅ 22 tests - Acciones sobre sesiones por estado
- ✅ 12 tests - Acciones sobre el órgano
- ✅ 12 tests - Sistema de votaciones
- ✅ 12 tests - Sistema de quorum
- ✅ 9 tests - Acciones sobre actas

**Estado**: ✅ 0 failures, 0 errors

### 🎯 Tests de Quorum

El test de quorum (`test_quorum.py`) verifica 3 permisos específicos:

| Permiso | Manager | OG1-Secretari | OG2-Editor | OG3-Membre | Otros |
|---------|---------|---------------|------------|------------|-------|
| **Gestionar quorum** | ✅ | ✅ | ✅ | ❌ | ❌ |
| **Añadir quorum** | ✅ | ✅ | ❌ | ✅ | ❌ |
| **Eliminar quorum** | ✅ | ❌ | ❌ | ❌ | ❌ |

**Particularidades**:
- **OG2-Editor**: Puede gestionar pero NO añadir quorum
- **OG3-Membre**: Puede añadir pero NO gestionar quorum
- **Manager**: Único con permiso para eliminar quorum

---

**Última actualización**: Octubre 2025
**Versión de Plone**: 6.0.11
**Tests implementados**: 15/15 (100%) ✅
