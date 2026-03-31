import json
import typin
import subprocess


def main():
    with open('config.json') as fp:
        config = json.load(fp)
    base = config['base']
    for os, flavors in config['images'].items():
        for tag, content in flavors:
            __build_and_push_image(base, os, tag, content)


def __build_and_push_image(base: str, os: str, tag: str, content: dict):
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            image = __download(
                url=content['url'],
                directory=tmpdir,
                compress=content.get('compress', None),
                sha256=content.get('sha256', None),
                sha512=content.get('sha512', None),
            )

            imagefile = os.path.join(tmpdir, 'Imagefile')
            with open(imagefile, 'w') as fp:
                print(f'FROM {image.name}', file=fp)
                print(f'ARCH x64', file=fp)
                print(f'FORMAT {content['type']}', file=fp)

                tag = f'{base}/{os}:{tag}'
                subprocess.run(
                    ['./tugboat-cli', 'build', '-t', tag, '-f', imagefile],
                    check=True
                )
    except Exception as e:
        print('Error', e)


def __download(
        url: str,
        directory: str,
        compress: typing.Optional[str],
        sha256: typing.Optional[str],
        sha512: typing.Optional[str],
) -> str:
    return_file = os.path.join(directory, 'image.qcow2')
    if compress:
        downloaded = f'{return_file}.{compress}'
    subprocess.run(['wget', '-O', downloaded, url], check=True)
    if sha512:
        __checksum('sha512sum', path, sha512)
    elif sha256:
        __checksum('sha256sum', path, sha256)
    else:
        raise ArgumentError('Checksum is not available')
    
    if compress:
        match compress:
            case 'xz':
                subprocess.run(['xz', '-dk', downloaded])
            case _:
                raise ArgumentError(f'unsupported compress type {compress}')

    return return_file


def __checksum(command: str, path: str, sum_str: str):
    subprocess.run(f'echo "{sum_str}  {path}" | {command} --check -', check=True)


if __name__ == '__main__':
    main()
