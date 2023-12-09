import math   
import Image, ImageDraw,ImageFilter

class Gradation(ImageFilter):

    name ="Gradation"

    def __init__(self,start_color,end_color,grad_dir='row'):
        self.grad1=start_color
        self.grad2=end_color
        self.shape=grad_dir

    def apply_gradation_filter(self,image):
        # 그라데이션 필터 적용
        width, height = image.size

        if self.shape == 'row' or self.shape == 'col':
            grad_image = self.visual_gradation(width, height)
        elif self.shape == 'circular':
            grad_image = self.circular_gradation(width, height, self.grad1, self.grad2)
        else:
            raise ValueError("Invalid shape. Use 'row', 'col', or 'circular'.")

        # 원본 이미지와 그라데이션 이미지를 합침
        blended_image = Image.blend(image.convert('RGB'), grad_image, 0.5)
        blended_image = blended_image.convert('RGB')

        return blended_image

    def visual_gradation(self,width, height):
        image = Image.new("RGB", (width, height))
        # 이미지 Draw 객체 생성

        draw = ImageDraw.Draw(image)

        if self.shape == 'col':
            for x in range(width):
                # 색상 그라데이션 계산
                red = int(self.grad1[0] * (1.0 - x / width) + self.grad2[0] * (x / width))
                green = int(self.grad1[1] * (1.0 - x / width) + self.grad2[1] * (x / width))
                blue = int(self.grad1[2] * (1.0 - x / width) + self.grad2[2] * (x / width))

                # 현재 열에 대한 선 그리기
                draw.line([(x, 0), (x, height)], fill=(red, green, blue))
        elif self.shape == 'row':
            for y in range(height):
                # 색상 그라데이션 계산
                red = int(self.grad1[0] * (1.0 - y / height) + self.grad2[0] * (y / height))
                green = int(self.grad1[1] * (1.0 - y / height) + self.grad2[1] * (y / height))
                blue = int(self.grad1[2] * (1.0 - y / height) + self.grad2[2] * (y / height))

                # 현재 열에 대한 선 그리기
                draw.line([(0, y), (width, y)], fill=(red, green, blue))
        else:
            raise ValueError("Invalid shape. Use 'row' or 'col'.")
        
        return image

    def circular_gradation(self,width, height):

        # 새로운 이미지 생성
        image = Image.new("RGB", (width, height))

        # 이미지 Draw 객체 생성
        draw = ImageDraw.Draw(image)

        # 중심 좌표 및 반지름 계산
        center_x, center_y = width // 2, height // 2
        radius = min(center_x, center_y)

        # 원형 그라데이션 값 적용
        for y in range(height):
            for x in range(width):
                # 현재 좌표에서 중심 좌표까지의 거리 계산
                distance = math.sqrt((x - center_x)**2 + (y - center_y)**2)

                # 반지름보다 크면 거리를 반지름으로 설정
                distance = min(distance, radius)

                # 거리에 따른 색상 계산
                ratio = distance / radius
                r = int(self.grad1[0] * (1.0 - ratio) + self.grad2[0] * ratio)
                g = int(self.grad1[1] * (1.0 - ratio) + self.grad2[1] * ratio)
                b = int(self.grad1[2] * (1.0 - ratio) + self.grad2[2] * ratio)

                # 현재 좌표에 색상 설정
                draw.point((x, y), fill=(r, g, b))

        return image