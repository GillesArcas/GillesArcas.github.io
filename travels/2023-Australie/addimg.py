import os
from PIL import Image

import clipboard


PHOTODIR = r"D:\Gilles\github.io\travels\2023-Australie\photos"
BLOGDIR = r"D:\Gilles\github.io\travels\2023-Australie\part1"
INDEXMD = r"D:\Gilles\github.io\travels\2023-Australie\part1\index.md"


def get_image_list():
    """
    Get list of file basenames from clipboard
    """
    clip = clipboard.paste()
    imglist = list()
    for imgin in clip.splitlines():
        imgin = imgin.replace('"', '')
        imglist.append(os.path.basename(imgin))
    imglist = sorted(imglist)
    print(imglist)
    return imglist


def resample_photo(imgin, imgout):
    img = Image.open(imgin)
    new_img = img.resize((1280,960), Image.ANTIALIAS)
    quality = 90
    new_img.save(imgout, "JPEG", quality=quality)


def resample_movie(movin, movout):
    os.system(f'ffmpeg -i {movin} -vf scale=720:-2 -c:a copy {movout}')


def resample(fnin, fnout):
    if os.path.splitext(fnin)[1] == '.jpg':
        resample_photo(fnin, fnout)
    else:
        resample_movie(fnin, fnout)


def media_declaration(media):
    if os.path.splitext(media)[1] == '.jpg':
        return f'![]({media})\n'
    else:
        return f'[]({media})\n'


def add_to_diary(imglist):
    with open(INDEXMD) as f:
        lines = f.readlines()

    # find last media in diary
    for index, line in enumerate(lines):
        if line.startswith('![](') or line.startswith('[]('):
            last = index

    lines = lines[:last] + [media_declaration(x) for x in imglist] + lines[last + 1:]
    with open(INDEXMD, 'wt') as f:
        f.writelines(lines)


def main():
    imglist = get_image_list()
    if not imglist:
        print("Pas d'images. Faire copier avec le chemin...")
        return

    for img in imglist:
        imgin = os.path.join(PHOTODIR, img)
        imgout = os.path.join(BLOGDIR, img)
        resample(imgin, imgout)

    add_to_diary(imglist)

    # add to repo, thumbnails remain to be added
    os.system('git add ' + ' '.join([os.path.join(BLOGDIR, x) for x in imglist]))


if __name__ == '__main__':
    main()
