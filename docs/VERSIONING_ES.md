# Gestión Automática de Versiones - Guía Rápida 🚀

## ¿Cómo funciona?

Cada vez que haces `push` a `main` en GitHub:

1. **Pipeline analiza tus commits**
2. **Detecta el tipo de cambio** (feature, fix, breaking)
3. **Incrementa automáticamente la versión**
4. **Construye ejecutables** con la nueva versión
5. **Crea release** en GitHub con la nueva versión

## Formato de Commits

Simplemente usa estas palabras clave en tus mensajes de commit:

```bash
# Para incrementar versión MINOR (X.Y.Z → X.(Y+1).0)
git commit -m "feat: agregar soporte para PS5 Pro"
git commit -m "feat(ui): agregar tema oscuro"

# Para incrementar versión PATCH (X.Y.Z → X.Y.(Z+1))
git commit -m "fix: resolver timeout en socat"
git commit -m "fix(lang): corregir traducción"

# Para incrementar versión MAJOR (X.Y.Z → (X+1).0.0)
git commit -m "breaking: cambiar formato de config"

# SIN incrementar versión (documentación, chores, etc.)
git commit -m "docs: actualizar README"
git commit -m "chore: actualizar dependencias"
git commit -m "test: agregar pruebas"
```

## Ejemplo: Hacer un Release

### 1. Desarrolla y haz commits con formato convencional

```bash
# Branch de desarrollo
git checkout -b feature/nueva-funcion

# Hacer cambios y commits
git commit -m "feat: agregar nueva funcionalidad"
git commit -m "fix: resolver bug encontrado"

# Merge a main
git push origin feature/nueva-funcion
# (después hacer merge en GitHub o local)
```

### 2. Push a main

```bash
git push origin main
```

### 3. ¡El pipeline automáticamente:

- ✅ Ejecuta pruebas
- ✅ Detecta cambios (`feat:` = minor bump)
- ✅ **Actualiza versión: X.Y.Z → X.(Y+1).0**
- ✅ Compila ejecutables con la nueva versión
- ✅ Crea GitHub Release con el tag correspondiente
- ✅ Descarga executables desde el release

## Probar Localmente (Antes de Push)

```bash
# Ver qué haría sin cambiar nada
python build_local/bump_version.py --dry-run

# Ejemplo de salida:
# Current version: 1.0.0
# Detected change type: minor
# New version: X.(Y+1).0
# [DRY RUN] No files modified.
```

Si quieres hacerlo de verdad:

```bash
# ACTUALIZA los archivos y crea tag
python build_local/bump_version.py
```

## Archivos Que Se Actualizan Automáticamente

| Archivo | Qué se actualiza |
|---------|-----------------|
| `src/models/version.py` | `__version__ = "<nueva_version>"` |
| `docs/CHANGELOG.md` | Nueva entrada con fecha y commits |
| Git tags | Crea tag `v<nueva_version>` |

## Ejemplo Real: Flujo Completo

```bash
# 1. Branch de feature
git checkout -b fix/socat-timeout

# 2. Hacer cambios
# ... edita code ...

# 3. Commit con mensaje convencional
git add .
git commit -m "fix: aumentar timeout socat a 30s para PS5"

# 4. Push a main (después de PR/merge)
git push origin main

# 5. Verifica en GitHub Actions:
# → Pipeline corre automáticamente
# → Detecta "fix:" commit
# → Bumps versión: 1.0.0 → 1.0.1
# → Crea executables: PS_MultiInjector-1.1.1-*
# → Release en GitHub con tag v1.1.1
```

## Más Información

Versioning completo: Ver `VERSIONING.md`

## Preguntas Frecuentes

**P: ¿Y si accidentalmente uso formato incorrecto?**
A: El pipeline detectará 0 commits relevantes y NO cambiará versión. Simplemente haz otro commit con formato correcto.

**P: ¿Puedo hacer version manual?**
A: Sí, edita `src/models/version.py` manualmente y git tag.

**P: ¿Se puede deshabilitar?**
A: Sí, comenta el job `version-bump` en `.github/workflows/release.yml`.

**P: ¿Qué versiones de Python soporta?**
A: El script funciona con Python 3.6+, pero el pipeline usa Python 3.11.
