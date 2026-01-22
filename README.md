# Docker AceServe

Docker container for AceStream Engine with support for multiple architectures (ARM32, ARM64, x86_64).

## Description

This project provides Docker images for the AceStream engine that work similarly to the original AceStream service, allowing P2P stream playback using the Ace protocol.

**Images are available on Docker Hub both as [`jopsis/aceserve`](https://hub.docker.com/r/jopsis/aceserve) and [`jopsis/acestream`](https://hub.docker.com/r/jopsis/acestream), with identical tags for all architectures.**
## Supported Architectures

- `linux/arm/v7` (ARM32)
- `linux/arm64` (ARM64/ARMv8)
- `linux/amd64` (x86_64)

## Usage

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

Create a `docker-compose.yml` file:

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

Run the container:

```bash
docker-compose up -d
```

## Ports

- **6878**: AceStream HTTP API port (default)
- **8621**: P2P node port, used to communicate with other peers
- **62062**: TCP port for old engine API (deprecated, included for compatibility)

## Access

Once the container is running, you can access the web interface at:

```
http://localhost:6878
```

## Usage Example

To play an AceStream stream:

```
http://localhost:6878/ace/getstream?id=CONTENTHASH
```

Where `CONTENTHASH` is the ID of the AceStream content you want to play.

## Available Tags

For both [`jopsis/aceserve`](https://hub.docker.com/r/jopsis/aceserve) and [`jopsis/acestream`](https://hub.docker.com/r/jopsis/acestream):

- `latest`: Latest stable version
- `vX.X.X`: Specific versions (e.g., `v3.1.2`)

## Build

The project includes Dockerfiles for each architecture in their respective folders:

- `aceserve-arm32/`: For ARM32 devices
- `aceserve-arm64/`: For ARM64 devices
- `aceserve-x86_64/`: For x86_64 systems

## License

This project is provided as-is, without warranties.
