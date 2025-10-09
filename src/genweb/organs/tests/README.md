# Tests para genweb.organs

Este directorio contiene los tests funcionales para el paquete `genweb.organs` migrado a Plone 6.

## Estructura de Tests

### Archivos de Configuración
- `__init__.py` - Inicialización del paquete de tests
- `test_config.py` - Tests de configuración del paquete
- `test_runner.py` - Configuración del runner de tests

### Tests Base
- `test_base.py` - Clase base para todos los tests funcionales

### Tests Funcionales
- `test_sessions.py` - Tests de creación y gestión de sesiones
- `test_file_permissions.py` - Tests de permisos de archivos
- `test_acta_permissions.py` - Tests de permisos de actas
- `test_organs_functionality.py` - Tests de funcionalidad de órganos
- `test_session_functionality.py` - Tests de funcionalidad de sesiones
- `test_content_functionality.py` - Tests de funcionalidad de contenido

## Ejecutar Tests

### Con buildout
```bash
# Ejecutar todos los tests
./bin/test -s genweb.organs

# Ejecutar tests específicos
./bin/test -s genweb.organs -t test_sessions

# Ejecutar con verbose
./bin/test -s genweb.organs -v
```

### Con pytest
```bash
# Ejecutar todos los tests
pytest src/genweb/organs/tests/

# Ejecutar tests específicos
pytest src/genweb/organs/tests/test_sessions.py

# Ejecutar con verbose
pytest -v src/genweb/organs/tests/
```

## Tipos de Tests

### Tests de Permisos
Los tests de permisos verifican que los diferentes roles de usuario:
- **OG1-Secretari**: Puede crear sesiones y gestionar contenido
- **OG2-Editor**: Puede crear sesiones y gestionar contenido
- **OG3-Membre**: Puede ver contenido pero no crear sesiones
- **OG4-Afectat**: Puede ver contenido pero no crear sesiones
- **OG5-Convidat**: Puede ver contenido pero no crear sesiones

### Tests de Funcionalidad
Los tests de funcionalidad verifican:
- Creación de órganos y carpetas de órganos
- Creación de sesiones y contenido asociado
- Workflows de publicación
- Navegación y búsqueda
- Soporte multilingüe

### Tests de Configuración
Los tests de configuración verifican:
- Instalación correcta del paquete
- Registro de tipos de contenido
- Configuración de workflows
- Configuración de permisos
- Configuración de catálogo

## Organización de Tests

Cada archivo de test está organizado por funcionalidad:

1. **TestSessionCreation** - Tests de creación de sesiones
2. **TestFilePermissions*** - Tests de permisos de archivos por tipo de órgano
3. **TestActaPermissions*** - Tests de permisos de actas por tipo de órgano
4. **TestOrgansFunctionality** - Tests de funcionalidad básica de órganos
5. **TestSessionFunctionality** - Tests de funcionalidad de sesiones
6. **TestContentFunctionality** - Tests de funcionalidad de contenido

## Fixtures de Test

Los tests utilizan la clase base `FunctionalTestCase` que proporciona:
- Configuración automática del entorno de test
- Creación de órganos de prueba
- Métodos de login para diferentes roles
- Métodos de aserción para permisos
- Limpieza automática después de cada test

## Dependencias

Los tests requieren:
- `plone.app.testing`
- `plone.testing`
- `pytest`
- `pytest-plone`
- `zope.testing`

## Notas de Migración

Estos tests han sido migrados desde Plone 4 a Plone 6:
- Actualizados imports y APIs
- Adaptados a Python 3.11
- Utilizan las nuevas APIs de Plone 6
- Compatibles con el sistema de testing moderno
