FROM python:3.11-slim-trixie
ENV PYTHONUNBUFFERED=1

# LibreOffice comes from trixie-backports, which tracks the newest release
# (trixie itself is frozen on 25.2). The fonts are metric-compatible stand-ins
# for the Microsoft fonts documents usually use (Arial, Times New Roman and
# Courier New -> Liberation, Calibri -> Carlito, Cambria -> Caladea); without
# them all text falls back to the wider DejaVu and the layout reflows. DejaVu
# stays as the fallback for fonts with no clone: without it fontconfig picks
# Liberation Mono, a monospace font.
RUN echo 'deb http://deb.debian.org/debian trixie-backports main' > /etc/apt/sources.list.d/backports.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends -t trixie-backports \
        libreoffice-writer \
        default-jre-headless libreoffice-java-common \
        fonts-liberation fonts-crosextra-carlito fonts-crosextra-caladea \
        fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY reqs.txt /app/
RUN pip install --no-cache-dir -r reqs.txt
COPY . /app/

CMD ["python", "convertor.py"]

EXPOSE 1488/tcp
EXPOSE 1488/udp
