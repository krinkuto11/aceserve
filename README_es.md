# Docker AceServe

Contenedor Docker para AceStream Engine compatible con múltiples arquitecturas (ARM32, ARM64, x86_64).

## Descripción

Este proyecto proporciona imágenes Docker del motor AceStream que funcionan de manera similar al servicio AceStream original, permitiendo la reproducción de streams P2P mediante el protocolo Ace.

## Arquitecturas soportadas

- `linux/arm/v7` (ARM32)
- `linux/arm64` (ARM64/ARMv8)
- `linux/amd64` (x86_64)

## Uso

### Docker Run

```bash
docker run -d \
  --name aceserve \
  -p 6878:6878 \
  -p 8621:8621 \
  -p 62062:62062 \
  jopsis/aceserve:latest
```

### Docker Compose

Crea un archivo `docker-compose.yml`:

```yaml
services:
  aceserve:
    image: jopsis/aceserve:latest
    container_name: aceserve
    ports:
      - "6878:6878"
      - "8621:8621"
      - "62062:62062"
    restart: unless-stopped
```

Ejecuta el contenedor:

```bash
docker-compose up -d
```

## Puertos

- **6878**: Puerto HTTP API de AceStream (por defecto)
- **8621**: Puerto del nodo P2P, usado para comunicarse con otros peers
- **62062**: Puerto TCP para la API antigua del motor (deprecated, incluido por compatibilidad) 

## Acceso

Una vez iniciado el contenedor, puedes acceder a la interfaz web en:

```
http://localhost:6878
```

## Ejemplo de uso

Para reproducir un stream de AceStream:

```
http://localhost:6878/ace/getstream?id=CONTENTHASH
```

Donde `CONTENTHASH` es el ID del contenido AceStream que deseas reproducir.

## Tags disponibles

- `latest`: Última versión estable
- `vX.X.X`: Versiones específicas (ej: `v3.1.2`)

## Construcción

El proyecto incluye Dockerfiles para cada arquitectura en sus respectivas carpetas:

- `aceserve-arm32/`: Para dispositivos ARM32
- `aceserve-arm64/`: Para dispositivos ARM64
- `aceserve-x86_64/`: Para sistemas x86_64

## Licencia

Este proyecto se proporciona tal cual, sin garantías.
