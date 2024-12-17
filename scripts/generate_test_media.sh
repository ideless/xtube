#!/usr/bin/env nix-shell
#!nix-shell -i bash -p ffmpeg

function generate_video {
  TEXT="$1"
  OUTPUT_FILE="$2"
  WIDTH=$3
  HEIGHT=$4
  FONTSIZE=$5
  DURATION=$6

  # Create a text overlay image
  IMG_FILE="text.png"
  ffmpeg -y -f lavfi -i color=white:size=${WIDTH}x${HEIGHT} -vf "drawtext=text='$TEXT':fontcolor=black:fontsize=$FONTSIZE:x=(w-text_w)/2:y=(h-text_h)/2" -frames:v 1 "$IMG_FILE"

  # Create the video from the image
  ffmpeg -y -loop 1 -i "$IMG_FILE" -c:v libx264 -t $DURATION -pix_fmt yuv420p -vf "scale=${WIDTH}:${HEIGHT}" -crf 18 "$OUTPUT_FILE"

  # Clean up the temporary image file
  rm "$IMG_FILE"
}

function generate_image {
  TEXT="$1"
  OUTPUT_FILE="$2"
  WIDTH=$3
  HEIGHT=$4
  FONTSIZE=$5

  ffmpeg -y -f lavfi -i color=white:size=${WIDTH}x${HEIGHT} -vf "drawtext=text='$TEXT':fontcolor=black:fontsize=$FONTSIZE:x=(w-text_w)/2:y=(h-text_h)/2" -frames:v 1 "$OUTPUT_FILE"
}

function generate_markdown_text {
  cat <<'EOF' >markdown_text.md
# Markdown 测试文档

这是一个测试Markdown格式的文档，包括各种常用元素。

## 1. 段落

这是一个普通段落。你可以在这里自由地写任何文本。

## 2. 标题

### 2.1 二级标题

#### 2.1.1 三级标题

##### 2.1.1.1 四级标题

## 3. 列表

- 这是一个无序列表项
- 这是另一个列表项
  - 嵌套的列表项

1. 这是一个有序列表项
2. 第二个有序列表项
   1. 嵌套的有序列表项

## 4. 链接

[点击这里访问 OpenAI](https://www.openai.com)

## 5. 图片

![示例图片](https://via.placeholder.com/150 "示例图片")

## 6. 引用

> 这是一个引用示例。

## 7. 代码

```python
def hello_world():
    print("Hello, World!")
```

## 8. 粗体与斜体

这是一个**粗体**文本和*斜体*文本的示例。

## 9. 分隔线

---

## 10. 表格

| 星期 | 活动       |
|------|------------|
| 一   | 开会       |
| 二   | 编码       |
| 三   | 测试       |

## 11. 任务列表

- [x] 任务 1
- [ ] 任务 2
EOF
}

function generate_plain_text {
  cat <<'EOF' >plain_text.txt
标题：《迷雾山谷》


第一章：神秘的邀请

在一个阳光明媚的早晨，李明收到了来自一个陌生人的信件。信中提到了一处神秘的地方——迷雾山谷，邀请他参与一场古老的探险。虽然他心中充满疑惑，但对未知世界的好奇促使他决定前往。


第二章：迷雾中的秘密

李明按照信中的指引，来到迷雾山谷。山谷被厚厚的雾气笼罩，视线模糊不清。就在他感觉迷失的时候，突然听到一阵低语声。循着声音走去，李明发现了一组古老的石碑，上面铭刻着关于失落文明的传说。


第三章：意外的伙伴

正当李明沉浸在石碑的秘密中时，一个女孩从雾中走出，自我介绍叫做小雨。她也是为了探寻这片土地的历史而来。两人在相识后决定联手揭开山谷中的秘密，他们的冒险旅程正式开始。


第四章：深入险境

随着调查的深入，李明和小雨遭遇了各种挑战。迷雾越来越浓，甚至出现了怪异的现象，仿佛有人在暗中监视他们。他们在山谷中迷了路，心中产生了恐惧，但彼此的鼓励让他们咬牙坚持。


第五章：发现宝藏

在一处古老的洞穴中，李明和小雨终于发现了传说中的宝藏——一枚闪耀着奇异光芒的宝石。宝石不仅是无价之宝，更承载着古文明的智慧。两人意识到，这次发现将改变他们的人生。


第六章：回归现实

经过一番波折，李明和小雨成功带回了宝石。然而，当他们在现实世界中分享这段经历时，众人却充满质疑。秘宝的神秘与他们的冒险，最终化为心灵深处的永恒记忆，成为了他们人生中最珍贵的财富。


第七章：新的开始

随着时间的推移，李明和小雨的友谊愈加深厚。迷雾山谷的经历激发了他们对探险的热情，他们决定一起探寻更多的未知世界，为未来的冒险开启新的篇章。
EOF
}

function generate_epub {
  curl -LO https://github.com/IDPF/epub3-samples/releases/download/20230704/childrens-literature.epub
}

DIR=test_media

mkdir -p $DIR

pushd $DIR

# generate_image 'Mobile image' 'mobile_image.png' 1080 1920 88
generate_image 'Desktop image' 'desktop_image.png' 1920 1080 128

# generate_video 'Mobile video 1min' 'mobile_video_1min.mp4' 1080 1920 88 60
generate_video 'Desktop video 1min' 'desktop_video_1min.mp4' 1920 1080 128 60

generate_markdown_text
generate_plain_text
generate_epub

popd
