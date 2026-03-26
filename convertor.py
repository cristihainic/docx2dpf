import os
import shutil
import uuid
from subprocess import Popen

import aiofiles
from sanic import Sanic
from sanic.response import file, text

app = Sanic('docx2pdf')

BASE_PATH = '/tmp/docx2pdf/'


async def write_file(path, body):
    async with aiofiles.open(path, 'wb') as f:
        await f.write(body)


@app.route('/convert', methods=['POST'])
async def convert(request):
    # whitelist IPs
    whitelisted_ips = os.getenv('WHITELISTED_IPS')
    if whitelisted_ips:
        whitelisted_ips = whitelisted_ips.split(',')
        if not any(ip in whitelisted_ips for ip in [request.ip, request.client_ip, request.remote_addr]):
            return text('Not whitelisted', status=403)

    # check file size
    request_file = request.files['file'][0]
    if len(request_file.body) > 10485760:
        return text('File exceeds 10MB', status=400)

    # create a per-request temp directory to avoid race conditions
    request_dir = os.path.join(BASE_PATH, uuid.uuid4().hex)
    os.makedirs(request_dir, exist_ok=True)

    try:
        # write file to temp
        path = os.path.join(request_dir, request_file.name)
        await write_file(path, request_file.body)

        # convert the file
        p = Popen(['libreoffice', '--headless', '--convert-to', 'pdf', path, '--outdir', request_dir])
        p.wait(timeout=60)

        if p.returncode != 0:
            return text('Conversion failed', status=500)

        # return the pdf
        pdf_file = path.replace('.docx', '.pdf')
        if not os.path.exists(pdf_file):
            return text('Conversion produced no output', status=500)

        return await file(pdf_file)
    finally:
        shutil.rmtree(request_dir, ignore_errors=True)


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=1488,
    )
