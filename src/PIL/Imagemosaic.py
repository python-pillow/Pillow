from PIL import Image
import os

def apply_mosaic_filter(image, block_size=20):
    """
    주어진 이미지에 모자이크 기능을 적용
    
    매개변수 : 
    - image(PIL.Image.Image) : 입력된 이미지값
    - block_size (int): 모자이크 블록의 크기
    
    반환 :
    - 모자이크 된 이미지
    """
    
    width, height = image.size

    # 입력 이미지와 동일한 모드와 동일한 크기의 새 이미지 생성
    mosaic_image = Image.new(image.mode, image.size)

    for x in range(0, width, block_size):
        for y in range(0, height, block_size):
            
            # 원본 이미지에서 블록 잘라내기
            box = (x, y, x + block_size, y + block_size)
            block = image.crop(box)
            
            # 블록의 평균 색상을 계산
            average_color = (
                sum(p[0] for p in block.getdata()) // block_size**2,
                sum(p[1] for p in block.getdata()) // block_size**2,
                sum(p[2] for p in block.getdata()) // block_size**2
            )

            # 평균 색상으로 새 이미지를 생성하여 필터링된 이미지에 붙여넣기
            mosaic_block = Image.new(image.mode, block.size, average_color)
            mosaic_image.paste(mosaic_block, box)

    # 모자이크 처리된 이미지를 반환
    return mosaic_image
