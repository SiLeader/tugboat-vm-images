import argparse
import json
import typing
import subprocess
import tempfile
import pathlib


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--verify', action='store_true', help='Verify config.json values')
    args = parser.parse_args()

    with open('config.json') as fp:
        config = json.load(fp)
    base = config['base']
    for os, flavors in config['images'].items():
        for tag, content in flavors.items():
            __build_and_push_image(base, os, tag, content, dry=args.verify)


def __build_and_push_image(base: str, os: str, tag: str, content: dict, dry: bool):
    tag = f'{base}/{os}:{tag}'
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            td = pathlib.Path(tmpdir)
            __download(
                url=content['url'],
                directory=td,
                out_file='image.qcow2',
                compress=content.get('compress', None),
                sha256=content.get('sha256', None),
                sha512=content.get('sha512', None),
            )
            if dry:
                print('OK', tag)
                return

            imagefile = td / 'Imagefile'
            with open(imagefile, 'w') as fp:
                print(f'FROM image.qcow2', file=fp)
                print(f'ARCH x64', file=fp)
                print(f'FORMAT {content['type']}', file=fp)
            print(imagefile)
            with open(imagefile) as fp:
                print(fp.read())
            subprocess.run(
                ['./tugboat-cli', 'build', '-t', tag, '-f', str(imagefile), tmpdir],
                check=True
            )
    except Exception as e:
        print('Error', e)
        if dry:
            raise


def __download(
        url: str,
        directory: pathlib.Path,
        out_file: str,
        compress: typing.Optional[str],
        sha256: typing.Optional[str],
        sha512: typing.Optional[str],
):
    return_file = directory / out_file
    if compress:
        downloaded = f'{return_file}.{compress}'
    else:
        downloaded = str(return_file)
    subprocess.run(['wget', '-O', downloaded, url], check=True)
    if sha512:
        __checksum('sha512sum', downloaded, sha512)
    elif sha256:
        __checksum('sha256sum', downloaded, sha256)
    else:
        raise ArgumentError('Checksum is not available')
    
    if compress:
        match compress:
            case 'xz':
                subprocess.run(['xz', '-dk', downloaded])
            case _:
                raise ArgumentError(f'unsupported compress type {compress}')


def __checksum(command: str, path: str, sum_str: str):
    subprocess.run(f'echo "{sum_str}  {path}" | {command} --check -', check=True, shell=True)


if __name__ == '__main__':
    main()
