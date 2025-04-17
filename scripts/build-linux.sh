set -e

mkdir -p build

cp scripts/server.py scripts/import_media.py build
cp -r dist build/ui

mkdir -p build/tools

pushd build/tools

if [ ! -f magick ]; then
  curl -LO https://imagemagick.org/archive/binaries/magick
  ln -sf magick identify
fi

if [ ! -f ffmpeg ]; then
  name=ffmpeg-master-latest-linux64-gpl
  curl -LO https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/$name.tar.xz
  tar xf $name.tar.xz
  cp $name/bin/ffmpeg $name/bin/ffprobe .
  rm -rf $name*
fi

if [ ! -f openssl ]; then
  cp $(which openssl) .
fi

popd

# font

pushd build

pyinstaller \
  --name xtube \
  --onedir \
  --add-data ui:ui \
  --add-data tools/*:tools \
  --noconfirm \
  server.py

popd
