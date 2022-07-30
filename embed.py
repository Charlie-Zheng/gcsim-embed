import json
import sys
from PIL import Image, ImageFilter, ImageDraw, ImageFont


OVERLAP = 0.16

def get_data() -> dict:
    return json.load(sys.stdin)

data = get_data()
chars = data["char_details"]
# print(chars[0])
names = [(chars[x]["name"] if "traveler" not in chars[x]
          ["name"] else "lumine") for x in range(len(chars))]
weapons = [chars[x]["weapon"] for x in range(len(chars))]
artifacts = [chars[x]["sets"] for x in range(len(chars))]

char_image_shapes = []
imgs = []
new_image_width = 900
new_image_height = 0
for name in names:
    # imgs.append(Image.open(f"images/avatar/trimmed/{name}_trimmed.png"))
    imgs.append(Image.open(f"images/avatar/{name}.png"))
    char_image_shapes.append(imgs[-1].size)
    if new_image_height == 0:
        new_image_height = char_image_shapes[-1][1]

base_img = Image.new("RGBA", (new_image_width, int(new_image_height*1.65)))

location = [[0, 0] for _ in range(len(imgs))]
for i in range(len(imgs)-1):
    location[i+1][0] = location[i][0] + \
        int(char_image_shapes[i][0] * (1-OVERLAP))
# print(location)

# for i in range(len(imgs)):
#     shadow = Image.new("RGBA", char_image_shapes[i], (255, 255, 255, 255))
#     alpha = imgs[i].split()[-1]
#     shadow.putalpha(alpha)
#     shadow = shadow.filter(ImageFilter.MaxFilter(5))
#     shadow.alpha_composite(imgs[i])
#     imgs[i] = shadow

# characters
for i in range(len(imgs)-1, -1, -1):
    img = imgs[i]
    base_img.alpha_composite(img, tuple(location[i]))

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
        artifact_image_shapes[i][0]-10, new_image_height - artifact_image_shapes[i][1] + 40))
    # base_img.alpha_composite(img,  (location[i][0] + 50, new_image_height - artifact_image_shapes[i][1] + 20))
    # base_img.alpha_composite(img,  (location[i][0] + 20, 0))

blue = (102, 170, 206, 255)
purple = (154, 112, 197, 255)
gold = (217, 170, 91, 255)
white = (255, 255, 255, 255)
genshin_font = ImageFont.truetype("genshin_font.ttf", 30)
text_img = Image.new("RGBA", base_img.size, (0, 0, 0, 0))
text = ImageDraw.Draw(text_img)

for i in range(len(chars)):
    char = chars[i]
    cons = char["cons"]
    ref = char["weapon"]["refine"]

    # text.text((location[i][0] + 30, new_image_height - 30), f"C{cons}", font = genshin_font, fill = blue)
    # xDescPxl = text.textsize(f"C{cons}", font= genshin_font)[0]
    # text.text((location[i][0] + 30 + xDescPxl, new_image_height - 30), f"R{ref}", font = genshin_font, fill = gold)   
    text.text((location[i][0] + 50, 5), f"C{cons}", font = genshin_font, fill = gold)
    xDescPxl = text.textsize(f"C{cons}", font= genshin_font)[0]
    text.text((location[i][0] + 50 + xDescPxl, 5), f"R{ref}", font = genshin_font, fill = purple)

# duration
# genshin_font_28px = ImageFont.truetype("genshin_font.ttf", 28)
dps = data["dps"]
info = f"""
Total DPS: {dps['mean']:5.0f} to {data['num_targets']} target{'s' if data['num_targets'] > 1 else ''} (Avg. Per Target {dps['mean']/data['num_targets']:5.0f})
DPS min / max / stddev: {dps['min']:.0f} / {dps['max']:.0f} / {dps['sd']:.0f}
{data['sim_duration']['mean']:.2f}s combat time. {data['iter']} iteration in {(data['runtime']/1e9):.3f}s
"""
text.text((6, new_image_height), info, font = genshin_font, fill = white, spacing = 10)

# shadow = Image.new("RGBA", text_img.size, (255, 255, 255, 255))
# alpha = text_img.split()[-1]
# shadow.putalpha(alpha)
# shadow = shadow.filter(ImageFilter.MaxFilter(3))
# shadow.alpha_composite(text_img)
# text_img = shadow

shadow = Image.new("RGBA", text_img.size, (0, 0, 0, 255))
alpha = text_img.split()[-1]
shadow.putalpha(alpha)
shadow = shadow.filter(ImageFilter.MaxFilter(7))
shadow = shadow.filter(ImageFilter.GaussianBlur(1))
shadow.alpha_composite(text_img)
text_img = shadow

base_img.alpha_composite(text_img)

base_img = base_img.resize(map(lambda x: int(x*0.6), base_img.size))

output_filename = "output.png"
if len(sys.argv) > 1:
    output_filename = sys.argv[1]
    if not output_filename.endswith(".png"):
        output_filename+=(".png")
base_img.save(output_filename)
# base_img.show()


