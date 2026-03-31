# tugboat-vm-images

Pre-built VM images as OCI artifacts for the [Tugboat](https://github.com/SiLeader/tugboat) VM orchestration system.

Images are published to the GitHub Container Registry (`ghcr.io/sileader/tugboat-vm-images`) and can be referenced directly in Tugboat `Ship` manifests.

## Available Images

| Image | Tag(s) | OS | Format |
|:------|:-------|:---|:-------|
| `ghcr.io/sileader/tugboat-vm-images/ubuntu` | `24.04`, `lts` | Ubuntu 24.04 LTS (Noble Numbat) | qcow2 |
| `ghcr.io/sileader/tugboat-vm-images/debian` | `trixie` | Debian 13 (Trixie) | qcow2 |
| `ghcr.io/sileader/tugboat-vm-images/freebsd` | `15.0` | FreeBSD 15.0-RELEASE | qcow2 |

All images target the `x64` architecture.

## Usage

Reference an image in a Tugboat `Ship` manifest:

```yaml
apiVersion: v1
kind: Ship
metadata:
  namespace: default
  name: my-vm
spec:
  image: ghcr.io/sileader/tugboat-vm-images/ubuntu:24.04
  shipClass: lightweight
```

See the [Tugboat documentation](https://github.com/SiLeader/tugboat) for full `Ship` manifest details.

## How It Works

1. **`config.json`** — Declares each image: source URL, checksum, compression, and disk format.
2. **`build.py`** — Downloads each source image, verifies its checksum, generates an `Imagefile`, and calls `tugboat-cli build` to package it as an OCI artifact.
3. **`tugboat-cli`** — The CLI tool from the Tugboat project used to build and push VM image artifacts.
4. **GitHub Actions** — On every push to `master` that modifies `build.py`, `config.json`, or `tugboat-cli`, all images are rebuilt and pushed to `ghcr.io`.

### Imagefile Format

Each image is built with an `Imagefile` equivalent to:

```
FROM image.qcow2
ARCH x64
FORMAT qcow2
```

## Building Locally

### Prerequisites

- Python 3.10+
- `wget`
- `xz` (for XZ-compressed sources)
- `tugboat-cli` binary (already included in this repository)
- A container registry to push to (and write credentials configured)

### Steps

1. Update `config.json` with your registry base if needed.
2. Log in to your registry:
   ```sh
   docker login ghcr.io
   ```
3. Run the build script:
   ```sh
   python3 build.py
   ```

## Adding a New Image

Edit `config.json` and add an entry under `images`:

```json
{
  "base": "ghcr.io/sileader/tugboat-vm-images",
  "images": {
    "<os-name>": {
      "<tag>": {
        "type": "qcow2",
        "url": "https://example.com/path/to/image.qcow2",
        "sha256": "<sha256-checksum>"
      }
    }
  }
}
```

For XZ-compressed images, add `"compress": "xz"` and provide the URL to the `.qcow2.xz` file.
Either `sha256` or `sha512` must be provided; omitting both will cause the build to fail.

## CI/CD

Images are automatically built and published via GitHub Actions on pushes to `master`.
The workflow uses `GITHUB_TOKEN` to authenticate with `ghcr.io` (no additional secrets required).

## License

Apache License 2.0 — see [LICENSE](./LICENSE) for details.
