import gc
import json
import gzip
import zlib
import sys
import time
from PIL import Image, ImageFilter, ImageDraw2


OVERLAP = 0.15
start = time.time()

def get_data(filename) -> dict:
    try:
        with open(filename, 'rb') as file:
            data = file.read()
            try:
                data = gzip.decompress(data)
            except:
                data = zlib.decompress(data)
            data = json.loads(data)
            # perform some data validation to make sure the file is a gcsim config
            debug = json.loads(data["debug"])
            return data
    except Exception:
        err(f"Did not find file \033[1;32m{filename}\033[0m or it is not a valid gcsim output file")


def err(msg):
    print(msg, file=sys.stderr)
    input("Press Enter to continue...")
    sys.exit(1)


data = get_data("nat.gz")
chars = data["char_details"]
# print(chars[0])
names = [(chars[x]["name"] if "traveler" not in chars[x]
          ["name"] else "lumine") for x in range(len(chars))]
weapons = [chars[x]["weapon"] for x in range(len(chars))]
artifacts = [chars[x]["sets"] for x in range(len(chars))]

char_image_shapes = []
imgs = []
new_image_width = 0
new_image_height = 0
for name in names:
    # imgs.append(Image.open(f"images/avatar/trimmed/{name}_trimmed.png"))
    imgs.append(Image.open(f"images/avatar/{name}.png"))
    char_image_shapes.append(imgs[-1].size)
    if new_image_width == 0:
        new_image_width = char_image_shapes[-1][0]
        new_image_height = char_image_shapes[-1][1]
    else:
        new_image_width += int(char_image_shapes[-1][1] * (1-OVERLAP))
base_img = Image.new("RGBA", (new_image_width, int(new_image_height*1.2)))

location = [[0, 0] for _ in range(len(imgs))]
for i in range(len(imgs)-1):
    location[i+1][0] = location[i][0] + \
        int(char_image_shapes[i][0] * (1-OVERLAP))
# print(location)

# for i in range(len(imgs)):
#     shadow = Image.new("RGBA", char_image_shapes[i], (255, 255, 255, 255))
#     alpha = imgs[i].split()[-1]
#     shadow.putalpha(alpha)
#     shadow = shadow.filter(ImageFilter.MaxFilter(1))
#     shadow.alpha_composite(imgs[i])
#     imgs[i] = shadow

# characters
for i in range(len(imgs)-1, -1, -1):
    img = imgs[i]
    base_img.alpha_composite(img, tuple(location[i]))


del imgs
gc.collect()
# weapons
# print(weapons)
imgs: list[Image.Image] = []
weapon_image_shapes = []
for weapon in weapons:
    imgs.append(Image.open(f"images/weapons/{weapon['name']}.png"))
    width, height = imgs[-1].size
    imgs[-1] = imgs[-1].resize((int(width*0.7), int(height*0.7)))
    weapon_image_shapes.append(imgs[-1].size)

weapon_img = Image.new("RGBA", base_img.size, (0,0,0,0))
for i in range(len(imgs)):
    img = imgs[i]
    weapon_img.alpha_composite(img,  (location[i][0] + char_image_shapes[i][0] - int(
        weapon_image_shapes[i][0] * 0.95)-10, new_image_height - weapon_image_shapes[i][1] + 20))

shadow = Image.new("RGBA", weapon_img.size, (255, 255, 255, 255))
alpha = weapon_img.split()[-1]
shadow.putalpha(alpha)
shadow = shadow.filter(ImageFilter.MaxFilter(5))
shadow.alpha_composite(weapon_img)
weapon_img = shadow

shadow = Image.new("RGBA", weapon_img.size, (0, 0, 0, 255))
alpha = weapon_img.split()[-1]
shadow.putalpha(alpha)
shadow = shadow.filter(ImageFilter.MaxFilter(7))
shadow = shadow.filter(ImageFilter.GaussianBlur(2))
shadow.alpha_composite(weapon_img)
weapon_img = shadow

base_img.alpha_composite(weapon_img,  (0,0))

del imgs
gc.collect()
imgs: list[Image.Image] = []
artifact_image_shapes = []
ARITFACT_SIZE = 0.4
for arti in artifacts:
    arti = {key: val for key, val in arti.items() if val >= 2}

    sets = list(arti.keys())
    total_sets = len(sets)
    # print(sets)
    if total_sets == 1:
        imgs.append(Image.open(f"images/artifacts/{sets[0]}_flower.png"))
        width, height = imgs[-1].size
        imgs[-1] = imgs[-1].resize((int(width*ARITFACT_SIZE), int(height*ARITFACT_SIZE)))
        artifact_image_shapes.append(imgs[-1].size)
    elif total_sets == 2:
        img0 = Image.open(f"images/artifacts/{sets[0]}_flower.png")
        width, height = img0.size
        img0 = img0.resize((int(width*ARITFACT_SIZE), int(height*ARITFACT_SIZE)))
        img0 = img0.crop((0, 0, int(width*ARITFACT_SIZE)//2, int(height*ARITFACT_SIZE)))

        img1 = Image.open(f"images/artifacts/{sets[1]}_flower.png")
        width, height = img1.size
        img1 = img1.resize((int(width*ARITFACT_SIZE), int(height*ARITFACT_SIZE)))
        img1 = img1.crop((int(width*ARITFACT_SIZE)//2, 0, int(width*ARITFACT_SIZE), int(height*ARITFACT_SIZE)))

        dst = Image.new("RGBA",(img0.width + img1.width, max(img0.height, img1.height)), (0,0,0,0))
        dst.paste(img0, (0, 0))
        dst.paste(img1, (img0.width, 0))
        imgs.append(dst)
        artifact_image_shapes.append(imgs[-1].size)

for i in range(len(imgs)):
    shadow = Image.new("RGBA", artifact_image_shapes[i], (255, 255, 255, 255))
    alpha = imgs[i].split()[-1]
    shadow.putalpha(alpha)
    shadow = shadow.filter(ImageFilter.MaxFilter(5))
    shadow.alpha_composite(imgs[i])
    imgs[i] = shadow

for i in range(len(imgs)):
    shadow = Image.new("RGBA", artifact_image_shapes[i], (0, 0, 0, 255))
    alpha = imgs[i].split()[-1]
    shadow.putalpha(alpha)
    shadow = shadow.filter(ImageFilter.MaxFilter(7))
    shadow = shadow.filter(ImageFilter.GaussianBlur(2))
    shadow.alpha_composite(imgs[i])
    imgs[i] = shadow

for i in range(len(imgs)):
    img = imgs[i]
    base_img.alpha_composite(img,  (location[i][0] + char_image_shapes[i][0] - 
        artifact_image_shapes[i][0]-10, new_image_height - artifact_image_shapes[i][1] + 20))
    # base_img.alpha_composite(img,  (location[i][0] + 50, new_image_height - artifact_image_shapes[i][1] + 20))
    # base_img.alpha_composite(img,  (location[i][0] + 20, 0))
base_img.save("test.png")

print(f"Total time taken {time.time()-start}")