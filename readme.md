### Rationale
I haven't found any up-to-date converter running as a http service. New fonts and special characters are not converted correctly by anything else I've tried. This service tries to fix this by always installing the latest libreoffice package and writer exporter.
## Installation

Run this with Docker, by building it yourself or by using a pre-built image. The converter is served at container port 1488.

```bash
docker pull cristihainic/docx2pdf 
docker run --init -p 1488:1488 cristihainic/docx2pdf 
```

`--init` is required, not optional: every conversion runs LibreOffice with a fresh throwaway profile, and the profile bootstrap leaves behind an orphan `soffice.bin` process that only a real init process (PID 1) can reap. Without `--init` these zombies accumulate until the container can no longer fork and every conversion fails with `Cannot fork`.

The full recommended command for production:

```bash
docker run -d --name docx2pdf \
  --init \
  --restart unless-stopped \
  --pids-limit 512 \
  --log-opt max-size=10m --log-opt max-file=3 \
  -p 1488:1488 \
  -e WHITELISTED_IPS=1.2.3.4 \
  cristihainic/docx2pdf
```

- `--pids-limit 512` caps the damage of any future process leak so it can't starve other services on the host (a single conversion tree uses a few dozen PIDs, so there's plenty of headroom).
- The `--log-opt` flags keep container logs from growing unbounded.
- `WHITELISTED_IPS` is optional — see [Security](#security) below.

## Usage
Make a `POST` request to `/convert` with your docx file. The response will contain a pdf file:
```python
curl --form file=@my_file.docx http://localhost:1488/convert > my_file.pdf
```

## Security
#### IP whitelisting
There's a basic IP check implemented in the app. If you want to serve requests from whitelisted IPs only, pass the IPs as comma-separated values to the `WHITELISTED_IPS` environment variable, e.g:
```shell
docker run -p 1488:1488 -e WHITELISTED_IPS=127.0.0.1,1.2.3.4,188.234.12.5 cristihainic/docx2pdf 
```

#### Max file size
The converter only works for files <= 10 MB in size. If you want that as an env variable, open an issue in this repo or feel free to create a merge request with the change.
