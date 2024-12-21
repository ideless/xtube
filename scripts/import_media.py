from argparse import ArgumentParser
from pathlib import Path
import random
import json
from datetime import datetime, timezone
import getpass
import re
import shutil
import zipfile
import os
import xml.etree.ElementTree as ET
import tempfile
from string import Template
import hashlib
import asyncio
from enum import Enum
import html


def random_string(length: int, charset: str = 'nlu'):
    chars = {
        'n': '0123456789',
        'l': 'abcdefghijklmnopqrstuvwxyz',
        'u': 'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
        'h': '0123456789abcdef',
    }
    candidates = ''.join(chars[c] for c in charset)
    return ''.join(random.choices(candidates, k=length))


def timestamp_to_iso_local(timestamp):
    dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
    local_dt = dt.astimezone()
    return local_dt.isoformat()


def du_dir(dir: Path):
    total = 0
    for path in dir.rglob('*'):
        total += path.stat().st_size
    return total


def is_valid_key(key: str):
    # For now, only 128 bit key in hex format is supported
    return re.match("[0-9a-fA-F]{32}$", key)


def get_encrypt_key(key: str = None):
    if key:
        return key

    key_hex = getpass.getpass("Input 128 bit key in hex: ")
    assert is_valid_key(key_hex), "Invalid key"

    return key_hex


def zip_directory(dir: Path, file: Path):
    with zipfile.ZipFile(file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for f in dir.rglob('*'):
            zipf.write(f, arcname=f.relative_to(dir))


class Tmp:
    def __init__(self):
        self.files = []
        self.dirs = []

    def file(self, suffix: str = None):
        file = tempfile.NamedTemporaryFile(suffix=suffix)
        self.files.append(file)
        return Path(file.name)

    def dir(self):
        dir = tempfile.TemporaryDirectory()
        self.dirs.append(dir)
        return Path(dir.name)

    def cleanup(self):
        for file in self.files:
            file.close()
        for dir in self.dirs:
            dir.cleanup()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.cleanup()
        return exc_type is None

    async def __aenter__(self):
        return self.__enter__()

    async def __aexit__(self, exc_type, exc_value, traceback):
        return self.__exit__(exc_type, exc_value, traceback)


class EPUB3:
    # https://idpf.org/epub/30/spec/epub30-overview.html

    def __init__(
        self,
        title: str,
        description: str,
        author: str,
        chapters: list,
        language: str,
        identifier: str,
        toc_title: str,
        tmp: Tmp,
    ):
        self.title = html.escape(title)
        self.description = html.escape(description)
        self.author = html.escape(author)
        self.chapters = chapters
        self.language = html.escape(language)
        self.identifier = html.escape(identifier)
        self.toc_title = html.escape(toc_title)
        self.tmp = tmp

        index_len = len(str(len(self.chapters) + 1))
        self.chap_ids = [
            f'ch{i+1:0{index_len}d}' for i in range(len(self.chapters))]

    def create_mime_type(self, dir: Path):
        with open(dir / 'mimetype', 'w') as f:
            f.write('application/epub+zip')

    def create_meta_inf(self, dir: Path):
        meta_inf_dir = dir / 'META-INF'
        meta_inf_dir.mkdir(parents=True, exist_ok=True)

        container_xml = meta_inf_dir / 'container.xml'
        container_xml.write_text('''<?xml version='1.0' encoding='utf-8'?>
<container xmlns="urn:oasis:names:tc:opendocument:xmlns:container" version="1.0">
    <rootfiles>
        <rootfile media-type="application/oebps-package+xml" full-path="EPUB/package.opf"/>
    </rootfiles>
</container>''')

    def create_package_doc(self, dir: Path):
        template = Template('''<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="id">
    <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
        <dc:identifier id="pub-id">$identifier</dc:identifier>
        <dc:title id="t1">$title</dc:title>
        <meta refines="#t1" property="title-type">main</meta>
        <dc:language>$language</dc:language>
        <dc:creator id="creator">$author</dc:creator>
        <meta refines="#creator" property="role" scheme="marc:relators" id="role">aut</meta>
        <dc:date>$date</dc:date>
        <dc:description>$description</dc:description>
    </metadata>
    <manifest>
        <item href="cover.xhtml" id="cover" media-type="application/xhtml+xml"/>
        <item href="nav.xhtml" id="nav" media-type="application/xhtml+xml" properties="nav"/>
        $chapters
    </manifest>
    <spine>
        <itemref idref="cover"/>
        <itemref idref="nav"/>
        $chapter_refs
    </spine>
</package>''')

        indent = '\n'+' '*8
        chapters = indent.join([
            '<item href="{}.xhtml" id="{}" media-type="application/xhtml+xml"/>'.format(
                name, name) for name in self.chap_ids])
        chapter_refs = indent.join([
            f'<itemref idref="{name}"/>' for name in self.chap_ids])

        content = template.safe_substitute(
            identifier=self.identifier,
            title=self.title,
            language=self.language,
            author=self.author,
            date=datetime.today().isoformat(),
            description=self.description,
            chapters=chapters,
            chapter_refs=chapter_refs,
        )
        file = dir / 'package.opf'
        file.write_text(content)

    def create_cover(self, dir: Path):
        template = Template('''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="$language" xml:lang="$language">
    <head>
        <title>$title</title>
    </head>
    <body>
        <h1>$title</h1>
    </body>
</html>''')
        content = template.safe_substitute(
            title=self.title,
            language=self.language,
        )
        file = dir / 'cover.xhtml'
        file.write_text(content)

    def create_nav(self, dir: Path):
        template = Template('''<?xml version="1.0" encoding="utf-8"?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
    <head>
        <meta charset="utf-8" />
        <title>$title</title>
    </head>
    <body>
        <nav epub:type="toc">
            <h1>$toc_title</h1>
            <ol>
                <li><a href="cover.xhtml">$title</a></li>
                <li><a href="nav.xhtml">$toc_title</a></li>
                $chapters
            </ol>
        </nav>
    </body>
</html>''')

        indent = '\n'+' '*16
        chapters = indent.join([
            '<li><a href="{}.xhtml">{}</a></li>'.format(id, chap[0])
            for id, chap in zip(self.chap_ids, self.chapters)
        ])

        content = template.safe_substitute(
            title=self.title,
            toc_title=self.toc_title,
            chapters=chapters,
        )
        file = dir / 'nav.xhtml'
        file.write_text(content)

    def create_chapters(self, dir: Path):
        for id, chap in zip(self.chap_ids, self.chapters):
            template = Template('''<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
    <head>
        <meta charset="utf-8" />
        <title>$title</title>
    </head>
    <body>
        <h1>$title</h1>
        $lines
    </body>
</html>''')

            indent = '\n'+' '*8
            lines = indent.join([
                '<p>{}</p>'.format(html.escape(line)) for line in chap[1:]])

            content = template.safe_substitute(
                title=html.escape(chap[0]),
                lines=lines,
            )
            file = dir / f'{id}.xhtml'
            file.write_text(content)

    def create_content(self, dir: Path):
        content_dir = dir / 'EPUB'
        content_dir.mkdir(parents=True, exist_ok=True)

        self.create_package_doc(content_dir)
        self.create_cover(content_dir)
        self.create_nav(content_dir)
        self.create_chapters(content_dir)

    def build(self, file: Path):
        temp_dir = self.tmp.dir()
        self.create_mime_type(temp_dir)
        self.create_meta_inf(temp_dir)
        self.create_content(temp_dir)
        zip_directory(temp_dir, file)

    def extract_epub_cover(file: Path):
        """Extracts the cover image from an EPUB file."""
        with zipfile.ZipFile(file) as z:
            # Read the container.xml to find the path of the content.opf file
            container_xml = z.read("META-INF/container.xml")
            container_tree = ET.fromstring(container_xml)

            # Find the rootfile path
            rootfile_path = container_tree.find(
                './/{urn:oasis:names:tc:opendocument:xmlns:container}rootfile'
            ).attrib['full-path']

            # Read the content.opf file
            opf_content = z.read(rootfile_path)
            opf_tree = ET.fromstring(opf_content)

            # Try to find cover image for EPUB 3
            for item in opf_tree.findall(
                    ".//{http://www.idpf.org/2007/opf}item"):
                if 'cover-image' in item.attrib.get('properties', ''):
                    cover_href = item.attrib['href']
                    cover_path = os.path.join(
                        os.path.dirname(rootfile_path), cover_href)
                    return z.open(cover_path).read(), cover_path

            # Fallback for EPUB 2
            cover_id = opf_tree.find(
                ".//{http://www.idpf.org/2007/opf}meta[@name='cover']")
            if cover_id is not None:
                cover_id = cover_id.attrib['content']
                cover_item = opf_tree.find(
                    ".//{http://www.idpf.org/2007/opf}item[@id='%s']"
                    % cover_id)
                if cover_item is not None:
                    cover_href = cover_item.attrib['href']
                    cover_path = os.path.join(
                        os.path.dirname(rootfile_path), cover_href)
                    return z.open(cover_path).read(), cover_path

        return None, None

    def parse_chapters(content: str, max_ctl: int):
        lines = content.splitlines()
        lines = [line.strip() for line in lines]

        chapters = []
        chapter = []
        empty_line_count = 0

        for line in lines:
            if line:
                if chapter and empty_line_count >= 2 and len(line) <= max_ctl:
                    chapters.append(chapter)
                    chapter = []
                chapter.append(line)
                empty_line_count = 0
            else:
                empty_line_count += 1

        if chapter:
            chapters.append(chapter)

        return chapters


class Cmd:
    @staticmethod
    async def run(cmd: list, capture=False, **kwargs):
        if capture:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                **kwargs,
            )
            stdout, stderr = await process.communicate()
            if process.returncode != 0:
                raise Exception(f"Command failed: {stderr.decode()}")
            return stdout.decode()
        else:
            process = await asyncio.create_subprocess_exec(*cmd, **kwargs)
            await process.wait()

    @staticmethod
    async def image_to_thumbnail(
        image: Path,
        output: Path,
        size: str = '300x200',
    ):
        await Cmd.run(['magick', image, '-thumbnail', size, output])

    @staticmethod
    async def text_to_thumbnail(
        text: str,
        output: Path,
        size: str = '300x200',
        background: str = 'white',
        fill: str = 'black',
        pointsize: int = 28,
        font: Path = None,
    ):
        # https://usage.imagemagick.org/text/
        cmd = ['magick', '-size', size, '-background', background,
               '-fill', fill, '-pointsize', str(pointsize),
               '-gravity', 'Center']
        if font:
            cmd.extend(['-font', font])
        cmd.extend(['caption:' + text, output])
        await Cmd.run(cmd)

    @staticmethod
    async def convert_image(
        file: Path,
        output: Path,
        resize: str = None,
        quality: int = None,
    ):
        cmd = ['magick', file]

        if resize:
            cmd.extend(['-resize', resize])
        if quality:
            cmd.extend(['-quality', str(quality)])

        await Cmd.run(cmd + [output])

    @staticmethod
    async def encrypt_file(file: Path, output: Path, key: str, iv: str):
        await Cmd.run(['openssl', 'enc', '-aes-128-cbc', '-salt',
                       '-in', file, '-out', output, '-K', key, '-iv', iv])

    @staticmethod
    async def decrypt_file(file: Path, output: Path, key: str, iv: str):
        await Cmd.run(['openssl', 'enc', '-d', '-aes-128-cbc',
                       '-in', file, '-out', output, '-K', key, '-iv', iv])

    @staticmethod
    async def get_md5(fileOrDir: Path):
        if fileOrDir.is_file():
            result = await Cmd.run(['md5sum', fileOrDir], capture=True)
            return result.split()[0]
        elif fileOrDir.is_dir():
            result = await Cmd.run(
                ['find', '.', '-type', 'f', '-exec', 'md5sum', '{}', ';'],
                capture=True, cwd=fileOrDir,
            )
            return result

    @staticmethod
    async def get_mime_type(file: Path):
        result = await Cmd.run(
            ['file', '--mime-type', '--brief', file], capture=True)
        return result

    @staticmethod
    async def get_video_format(file: Path):
        result = await Cmd.run(['ffprobe', '-v', 'quiet', '-show_format',
                                '-print_format', 'json', file], capture=True)
        return json.loads(result)

    @staticmethod
    async def get_video_screenshot(file: Path, output: Path):
        await Cmd.run([
            'ffmpeg', '-y',
            '-i', file,
            '-vf', 'thumbnail',
            '-frames:v', '1',
            output,
        ])

    @staticmethod
    async def video_to_m3u8(
        file: Path,
        output: Path,
        bitrate: str,
        hls_time: int,
        key_info_file: Path = None,
    ):
        seg_dir = output.parent / 'seg'
        seg_dir.mkdir(parents=True)
        cmd = [
            'ffmpeg',
            '-i', file,
            '-c:v', 'libx264',
            '-b:v', bitrate,
            '-c:a', 'aac',
            '-b:a', '128k',
            '-f', 'hls',
            '-hls_time', str(hls_time),
            '-hls_playlist_type', 'vod',
            '-hls_list_size', '0',
            '-hls_flags', 'independent_segments',
            '-hls_base_url', 'seg/',
            '-hls_segment_filename', seg_dir / '%03d.ts',
        ]
        if key_info_file:
            cmd.extend(['-hls_key_info_file', key_info_file])
        await Cmd.run(cmd + [output])

    @staticmethod
    async def get_image_creation_time(file: Path):
        result = await Cmd.run(
            ['identify', '-format', '%[date:create]|%[exif:datetime]', file],
            capture=True,
        )
        time = result.strip().split('|')

        if time[1]:
            dt = datetime.strptime(time[1], "%Y:%m:%d %H:%M:%S")
            return dt.astimezone().isoformat()
        elif time[0]:
            return time[0]
        else:
            # Fallback to file creation time if no date is found in metadata
            return timestamp_to_iso_local(file.stat().st_ctime)


class YAML:
    @staticmethod
    def parse_value(value: str):
        '''Parses a YAML value into int, float, bool, None, or str'''
        if not value or value == "null":
            return None
        elif value == "true":
            return True
        elif value == "false":
            return False
        elif re.match("('.*'|\".*\")$", value):
            return json.loads(value)
        elif re.match(r"[+-]?\d+$", value):
            return int(value)
        elif re.match(r"[+-]?\d+\.\d+$", value):
            return float(value)
        else:
            return value

    @staticmethod
    def dump_value(value):
        '''Dumps a YAML value into str'''
        if value is None:
            return "null"
        elif isinstance(value, bool):
            return "true" if value else "false"
        elif isinstance(value, str):
            return json.dumps(value, ensure_ascii=False)
        else:
            return str(value)

    @staticmethod
    def loads(yaml: str):
        '''Simple parser for parsing a dict or a list of dict'''
        yaml = yaml.strip()
        lines = [line for line in yaml.splitlines()]

        if yaml.startswith('-'):
            records = []
            current_record = {}

            for line in lines:
                if not line.strip():
                    continue
                if line.startswith('-'):
                    if current_record:
                        records.append(current_record)
                    current_record = {}
                key, value = line[2:].split(':', 1)
                key, value = key.strip(), value.strip()
                current_record[key] = YAML.parse_value(value)

            if current_record:
                records.append(current_record)

            return records
        elif not yaml:
            return []  # Default to list
        else:
            record = {}

            for line in lines:
                if not line.strip():
                    continue
                key, value = line.split(':', 1)
                key, value = key.strip(), value.strip()
                record[key] = YAML.parse_value(value)

            return record

    @staticmethod
    def dumps(records: dict | list[dict]):
        '''Simple dumper for dumping a dict or a list of dict'''
        if isinstance(records, dict):
            lines = []

            for key, value in records.items():
                value = YAML.dump_value(value)
                lines.append(f'{key}: {value}')
        elif isinstance(records, list):
            lines = []

            for record in records:
                first = True
                for key, value in record.items():
                    sign = '-' if first else ' '
                    value = YAML.dump_value(value)
                    lines.append(f'{sign} {key}: {value}')
                    first = False
        else:
            raise ValueError('Invalid records')

        return '\n'.join(lines)


class DB:
    def __init__(self, key: str, tmp: Tmp, root_dir: Path = None):
        self.key = key
        self.tmp = tmp
        self.root_dir = root_dir or Path('.')

        self.db_file = self.root_dir / 'db.yaml.enc'
        self.media_dir = self.root_dir / 'media'

        key_info_file = self.root_dir / 'key_info.yaml'
        key_hash = hashlib.sha256(bytes.fromhex(self.key)).hexdigest()[:6]

        if key_info_file.is_file():
            yaml = key_info_file.read_text()
            info = YAML.loads(yaml)
            if info["key_hash"] != key_hash:
                raise ValueError("Invalid key")
        else:
            info = {
                "key_hash": key_hash,
                "iv": random_string(32, 'h'),
            }
            yaml = YAML.dumps(info)
            key_info_file.write_text(yaml)

        self.iv = info["iv"]

    async def __aenter__(self):
        self.pt_path = self.tmp.file()

        if self.db_file.is_file():
            await Cmd.decrypt_file(
                self.db_file, self.pt_path, self.key, self.iv)
            yaml = self.pt_path.read_text()
            self.db = YAML.loads(yaml)
        else:
            self.db = []

        return self.db

    async def __aexit__(self, exc_type, exc_value, traceback):
        yaml = YAML.dumps(self.db)
        self.pt_path.write_text(yaml)
        await Cmd.encrypt_file(self.pt_path, self.db_file, self.key, self.iv)
        return exc_type is None

    def print_record(self, record: dict):
        keylen = max(len(str(key)) for key in record)
        vallen = max(len(str(value)) for value in record.values())

        gap = '  '
        print('Key'.ljust(keylen) + gap + 'Value'.ljust(vallen))
        print('-'*keylen + gap + '-'*vallen)

        for key, value in record.items():
            print(str(key).ljust(keylen) + gap + str(value).ljust(vallen))

    async def print(self):
        async with self as db:
            for index, record in enumerate(db):
                print(f"#{index+1}")
                self.print_record(record)
                if index < len(db) - 1:
                    print()

    def clear(self):
        if self.db_file.is_file():
            self.db_file.unlink()
        if self.media_dir.is_dir():
            shutil.rmtree(self.media_dir)

    async def remove(self, uid_list: list[str]):
        async with self as db:
            uid_set = set(uid_list)
            all_uid_set = {record['uid'] for record in db}

            to_remove = uid_set.intersection(all_uid_set)
            not_found = uid_set - all_uid_set

            db[:] = [r for r in db if r['uid'] not in to_remove]

            for uid in to_remove:
                resource_dir = self.media_dir / uid
                if resource_dir.is_dir():
                    shutil.rmtree(resource_dir)

            if to_remove:
                print(f"Removed: {' '.join(to_remove)}")
            if not_found:
                print(f"Not found: {' '.join(not_found)}")

    async def append(self, record: dict):
        async with self as db:
            db.append(record)

    async def load(self, file: Path):
        await Cmd.encrypt_file(file, self.db_file, self.key, self.iv)

    async def save(self, file: str):
        await Cmd.decrypt_file(self.db_file, file, self.key, self.iv)


class MediaImporter:
    def __init__(
        self,
        file: Path,
        key: str,
        tmp: Tmp,
        title: str = None,
        description: str = None,
        thumbnail: Path = None,
        thumbnail_font: Path = None,
        root_dir: Path = None,
        no_encryption: bool = False,
        **kwargs,  # Allow additional arguments
    ):
        self.file = file
        self.key = key
        self.tmp = tmp
        self.title = title or file.stem
        self.description = description or ''
        self.thumbnail = thumbnail
        self.thumbnail_font = thumbnail_font
        self.root_dir = root_dir or Path('.')
        self.no_encryption = no_encryption

        self.uid = random_string(9)
        self.resource_dir = self.root_dir / f'media/{self.uid}'
        self.resource_dir.mkdir(parents=True)
        self.record = {
            'uid': self.uid,
            'original_name': self.file.name,
            'original_size': self.file.stat().st_size,
            'original_hash': '',
            'title': self.title,
            'description': self.description,
            'encrypted': not no_encryption,
        }
        self.db = DB(self.key, tmp, self.root_dir)

        if not self.no_encryption:
            self.iv = random_string(32, 'h')
            self.record['iv'] = self.iv

    async def get_info(self):
        self.record['creation_time'] = timestamp_to_iso_local(
            self.file.stat().st_ctime)

    async def get_mime_type(self, kind: str = None, mime_type: str = None):
        self.record.update({
            "kind": kind or "file",
            "mime_type": mime_type or await Cmd.get_mime_type(self.file),
        })

    async def get_alternative_thumbnail(self) -> Path:
        return None

    async def create_thumbnail(self):
        pt_path = self.tmp.file(suffix=".webp")
        size = '300x200'

        if self.thumbnail:
            await Cmd.image_to_thumbnail(self.thumbnail, pt_path, size=size)
        elif alt := await self.get_alternative_thumbnail():
            await Cmd.image_to_thumbnail(alt, pt_path, size=size)
        else:
            await Cmd.text_to_thumbnail(self.title, pt_path,
                                        font=self.thumbnail_font, size=size)

        if self.no_encryption:
            ct_path = self.resource_dir / 'thumbnail.webp'
            shutil.copy(pt_path, ct_path)
        else:
            ct_path = self.resource_dir / 'thumbnail.webp.enc'
            await Cmd.encrypt_file(pt_path, ct_path, self.key, self.iv)

        self.record['thumbnail'] = ct_path.relative_to(self.root_dir)

    async def process_file(self, file: Path = None, name: str = 'file'):
        if self.no_encryption:
            ct_path = self.resource_dir / name
            shutil.copy(file or self.file, ct_path)
        else:
            ct_path = self.resource_dir / f'{name}.enc'
            await Cmd.encrypt_file(
                file or self.file, ct_path, self.key, self.iv)

        self.record['file'] = ct_path.relative_to(self.root_dir)

    async def calc_md5(self):
        md5 = await Cmd.get_md5(self.file)
        self.record['original_hash'] = md5

        md5 = await Cmd.get_md5(self.resource_dir)
        md5_file = self.resource_dir / 'md5sum.txt'
        md5_file.write_text(md5)
        self.record['hash'] = md5_file

    def calc_size(self):
        self.record['size'] = du_dir(self.resource_dir)

    async def consume(self):
        try:
            await self.get_info()
            await self.get_mime_type()
            await self.create_thumbnail()
            await self.process_file()
            await self.calc_md5()
            self.calc_size()
            self.db.print_record(self.record)
            # Put it at last, in case of failure
            await self.db.append(self.record)
        except Exception as e:
            shutil.rmtree(self.resource_dir)
            raise e


class VideoImporter(MediaImporter):
    def __init__(
        self,
        *args,
        bitrate: str = None,
        hls_time: int = None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self.bitrate = bitrate or '2000k'
        self.hls_time = hls_time or 10

    async def get_info(self):
        obj = await Cmd.get_video_format(self.file)

        self.record['duration'] = float(obj['format']['duration'])
        self.record['creation_time'] = obj['format']['tags'].get(
            'creation_time',
            timestamp_to_iso_local(self.file.stat().st_ctime),
        )

    async def get_mime_type(self):
        await super().get_mime_type('video', 'application/vnd.apple.mpegurl')

    async def get_alternative_thumbnail(self):
        shot_path = self.tmp.file(suffix=".webp")
        await Cmd.get_video_screenshot(self.file, shot_path)
        return shot_path

    async def process_file(self):
        m3u8_path = self.resource_dir / 'playlist.m3u8'

        if self.no_encryption:
            await Cmd.video_to_m3u8(self.file, m3u8_path, self.bitrate,
                                    self.hls_time)
        else:
            key_path = self.tmp.file()
            key_path.write_bytes(bytes.fromhex(self.key))

            key_info_path = self.tmp.file()
            key_info_path.write_text(f'key.bin\n{key_path}\n{self.iv}')

            await Cmd.video_to_m3u8(self.file, m3u8_path, self.bitrate,
                                    self.hls_time, key_info_path)

        self.record['file'] = m3u8_path.relative_to(self.root_dir)


class ImageImporter(MediaImporter):
    def __init__(
        self,
        *args,
        resize: str = None,
        quality: int = None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self.resize = resize or '1920x1080>'
        self.quality = quality or 75

    async def get_info(self):
        self.record['creation_time'] = await Cmd.get_image_creation_time(
            self.file)

    async def get_mime_type(self):
        await super().get_mime_type('image', 'image/webp')

    async def get_alternative_thumbnail(self):
        return self.file

    async def process_file(self):
        pt_path = self.tmp.file(suffix=".webp")
        await Cmd.convert_image(
            self.file,
            pt_path,
            resize=self.resize,
            quality=self.quality,
        )
        await super().process_file(pt_path, 'image.webp')


class BookImporter(MediaImporter):
    def __init__(
        self,
        *args,
        encoding: str = None,
        author: str = None,
        language: str = None,
        toc_title: str = None,
        max_ctl: int = None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self.encoding = encoding or 'utf-8'
        self.author = author or 'Anonymous'
        self.language = language or 'en-US'
        self.toc_title = toc_title or 'Table of Contents'
        self.max_ctl = max_ctl or 100

        self.record.update({
            'author': self.author,
            'language': self.language,
        })

    async def get_mime_type(self):
        await super().get_mime_type('book', 'application/epub+zip')

    async def get_alternative_thumbnail(self):
        if not self.thumbnail and self.file.suffix == '.epub':
            data, path = EPUB3.extract_epub_cover(self.file)
            suffix = Path(path).suffix
            if data:
                cover_file = self.tmp.file(suffix=suffix)
                cover_file.write_bytes(data)
                return cover_file

    async def process_file(self):
        if self.file.suffix == '.epub':
            await super().process_file(self.file, 'book.epub')
        else:
            book_path = self.tmp.file(suffix=".epub")
            content = self.file.read_text(encoding=self.encoding)
            chapters = EPUB3.parse_chapters(content, self.max_ctl)
            EPUB3(
                title=self.title,
                description=self.description,
                author=self.author,
                chapters=chapters,
                language=self.language,
                identifier=self.uid,
                toc_title=self.toc_title,
                tmp=self.tmp,
            ).build(book_path)
            await super().process_file(book_path, 'book.epub')


class NoteImporter(MediaImporter):
    async def get_mime_type(self):
        await super().get_mime_type('note', 'text/markdown')

    async def process_file(self):
        await super().process_file(name='note.md')


class FileImporter(MediaImporter):
    pass


def get_command_line_args():
    # Validators
    def v_file(path: str):
        path = Path(path)
        assert path.is_file(), f'File not found: {path}'
        return path

    def v_dir(path: str):
        path = Path(path)
        assert path.is_dir(), f'Dir not found: {path}'
        return path

    def v_key(key: str):
        assert is_valid_key(key), "Invalid key"
        return key

    # Common parser
    common_parser = ArgumentParser(add_help=False)
    ca = common_parser.add_argument
    ca('-k', '--key', help='The 128bit hex key', type=v_key)
    ca('-d', '--root-dir', help='The root dir (default: .)', type=v_dir)

    # Base parser
    base_parser = ArgumentParser(add_help=False)
    ba = base_parser.add_argument
    ba('-f', '--file', help='The file path', type=v_file)
    ba('-T', '--title', help='The title (default: file name)')
    ba('-D', '--description', help='The description')
    ba('-t', '--thumbnail', help='The thumbnail image path', type=v_file)
    ba('-F', '--thumbnail-font', help='The thumbnail font path', type=v_file)
    ba('-n', '--no-encryption', help='Disable encryption', action='store_true')

    # Main parser
    parser = ArgumentParser(description='Import file into the database')
    subparsers = parser.add_subparsers(
        dest='command', help='The command to run', required=True)

    # Video
    video_parser = subparsers.add_parser(
        'video', parents=[common_parser, base_parser], help='Import video')
    va = video_parser.add_argument
    va('--bitrate', help='The output video bitrate (default: 2000k)')
    va('--hls-time', help='The segment duration (default: 10)', type=int)

    # Image
    image_parser = subparsers.add_parser(
        'image', parents=[common_parser, base_parser], help='Import image')
    ia = image_parser.add_argument
    ia('--resize', help='The resize geometry (default: 1920x1080>)')
    ia('--quality', help='The output image quality (default: 75)', type=int)

    # Book
    book_parser = subparsers.add_parser(
        'book', parents=[common_parser, base_parser],
        help='Import book [epub or text]')
    ba = book_parser.add_argument
    ba('--encoding', help='[text] Encoding of the file (default: utf-8)')
    ba('--author', help='[text] Author of the book (default: Anonymous)')
    ba('--language', help='[text] Language of the book (default: en-US)')
    ba('--toc-title', help='[text] TOC title (default: Table of Contents)')
    ba('--max-ctl', help='[text] Max chapter title length (default: 100)')

    # Note
    subparsers.add_parser(
        'note', parents=[common_parser, base_parser], help='Import note')

    # File
    subparsers.add_parser(
        'file', parents=[common_parser, base_parser], help='Import file')

    # List
    subparsers.add_parser(
        'list', parents=[common_parser], help='Display the database')

    # Clear
    subparsers.add_parser(
        'clear', parents=[common_parser], help='Clear the database')

    # Remove
    remove_parser = subparsers.add_parser(
        'remove', parents=[common_parser], help='Remove by uid')
    ra = remove_parser.add_argument
    ra("uid", nargs='+', help="The uid to remove")

    # Export DB
    export_db_parser = subparsers.add_parser(
        'export-db', parents=[common_parser], help='Export database')
    ea = export_db_parser.add_argument
    ea('path', help='The output file path')

    # Import DB
    import_db_parser = subparsers.add_parser(
        'import-db', parents=[common_parser], help='Export database')
    ia = import_db_parser.add_argument
    ia('path', help='The input file path', type=v_file)

    return parser.parse_args()


class MediaKind(str, Enum):
    video = "video"
    image = "image"
    book = "book"
    note = "note"
    file = "file"


importer_classes = {
    'video': VideoImporter,
    'image': ImageImporter,
    'book': BookImporter,
    'note': NoteImporter,
    'file': FileImporter,
}


async def import_media(kind: MediaKind = None, **kwargs):
    await importer_classes[kind](**kwargs).consume()


async def main(tmp: Tmp):
    args = get_command_line_args()
    key = get_encrypt_key(args.key)

    if args.command in importer_classes:
        kwargs = vars(args).copy()
        kwargs.pop('command')
        kwargs['key'] = key
        kwargs['tmp'] = tmp
        await import_media(kind=args.command, **kwargs)
    elif args.command == 'list':
        await DB(key, tmp, args.root_dir).print()
    elif args.command == 'clear':
        DB(key, tmp, args.root_dir).clear()
    elif args.command == 'remove':
        await DB(key, tmp, args.root_dir).remove(args.uid)
    elif args.command == 'export-db':
        await DB(key, tmp, args.root_dir).save(args.path)
    elif args.command == 'import-db':
        await DB(key, tmp, args.root_dir).load(args.path)


if __name__ == '__main__':
    with Tmp() as tmp:
        asyncio.run(main(tmp))
