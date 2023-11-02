import glob
import os
from subprocess import Popen

import aiofiles
from sanic import Sanic
from sanic.response import file, text

app = Sanic('docx2pdf')

FILE_PATH = '/tmp/docx2pdf/'


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

    if not os.path.exists(FILE_PATH):
        os.makedirs(FILE_PATH)

    # clear tmp files
    files = glob.glob(f'{FILE_PATH}*')
    for f in files:
        os.remove(f)

    # write file to temp
    path = FILE_PATH + request_file.name
    await write_file(path, request_file.body)

    # convert the file
    p = Popen(['libreoffice', '--headless', '--convert-to', 'pdf', f'{path}', '--outdir', f'{FILE_PATH}'])
    p.wait(timeout=60)

    # return the pdf
    pdf_file = path.replace('.docx', '.pdf')
    return await file(pdf_file)


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=1488,
    )
