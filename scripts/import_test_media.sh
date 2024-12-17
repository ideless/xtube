set -e

PYSCRIPT=scripts/import_media.py
KEY="c0dbe78be559307c1cf9ad19215d22cd"
DATA_DIR="test/data"
MEDIA_DIR="test/media"

python $PYSCRIPT \
  video \
  -d $DATA_DIR \
  -k $KEY \
  -f $MEDIA_DIR/desktop_video_1min.mp4 \
  -T 'Desktop video 1min' \
  -D 'This is a 1920x1080 video for the purpose of testing'

python $PYSCRIPT \
  image \
  -d $DATA_DIR \
  -k $KEY \
  -f $MEDIA_DIR/desktop_image.png \
  -T 'Desktop image' \
  -D 'This is an 1920x1080 image for the purpose of testing'

python $PYSCRIPT \
  book \
  -d $DATA_DIR \
  -k $KEY \
  -f $MEDIA_DIR/childrens-literature.epub \
  -T "Children's literature" \
  -D 'This is an EPUB3 book for the purpose of testing'

python $PYSCRIPT \
  book \
  -d $DATA_DIR \
  -k $KEY \
  -f $MEDIA_DIR/plain_text.txt \
  -T "迷雾山谷" \
  -D 'This is an EPUB3 book for the purpose of testing' \
  -F 'test_media/HanyiSentyPagoda Regular.ttf'

python $PYSCRIPT \
  note \
  -d $DATA_DIR \
  -k $KEY \
  -f $MEDIA_DIR/markdown_text.md \
  -T 'The markdown syntax' \
  -D 'This is a markdown note for the purpose of testing'
