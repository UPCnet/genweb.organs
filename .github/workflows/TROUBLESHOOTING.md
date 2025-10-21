# 🔧 Troubleshooting GitHub Actions

## Error: cmarkgfm build failed

### Síntoma
```
FileNotFoundError: [Errno 2] No such file or directory:
'/tmp/pip-req-build-xxx/src/cmarkgfm/cmark.cffi.h'
```

### Causa
`zest.releaser` requiere `cmarkgfm` que necesita `cmake` y compilación C.

### Solución aplicada ✅
Creado `buildout-ci.cfg` que excluye `releaser` del build de CI.
El releaser solo se necesita para hacer releases, no para tests.

## Error: buildout falla sin logs claros

### Solución
1. Probar localmente:
```bash
cd /path/to/genweb.organs
python3.11 -m venv test-venv
source test-venv/bin/activate
pip install -r requirements.txt
buildout -c buildout-ci.cfg -N
```

2. Ver logs completos en GitHub Actions expandiendo el step

## Tests fallan localmente pero pasan en CI (o viceversa)

### Causa
Diferencias entre entornos

### Verificar
- Versión de Python: `python --version` (debe ser 3.11)
- Versiones de paquetes: `pip list`
- Buildout limpio: `rm -rf eggs parts .installed.cfg`

## Cache de buildout corrupto

### Síntoma
Errores extraños que desaparecen al re-ejecutar

### Solución
Cambiar la clave del cache en test.yml:
```yaml
key: ${{ runner.os }}-buildout-ci-v2-${{ hashFiles('buildout-ci.cfg', 'requirements.txt') }}
```

## Dependencia del sistema faltante

### Síntoma
```
error: command 'gcc' failed
fatal error: xxx.h: No such file or directory
```

### Solución
Añadir paquete en el step "Install system dependencies"

## Coverage no se genera

### Causa
Tests fallaron antes de llegar al step de coverage

### Verificar
1. Tests pasan: `bin/test`
2. Coverage funciona: `bin/coverage run --source=src/genweb/organs bin/test`
