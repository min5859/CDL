from PIL import Image

# 로고 이미지 불러오기
logo = Image.open("./CDL_logo_2.png").convert("RGBA")

# 배경색 (흰색)으로 간주하고 투명하게 만들기
datas = logo.getdata()
new_data = []

for item in datas:
    # 흰색 배경인 경우 (255, 255, 255)
    if item[0] == 255 and item[1] == 255 and item[2] == 255:
        # 완전히 투명하게 (R, G, B, A)
        new_data.append((255, 255, 255, 0))
    else:
        new_data.append(item)

# 새로운 투명 배경 이미지 생성
logo.putdata(new_data)
logo.save("./transparent_logo.png", "PNG")
