from PIL import Image, ImageDraw


class GradationFilter:
    def __init__(self, image_path):
        self.original_image = Image.open(image_path)

    def apply_gradation_filter(self, start_color, end_color, input_alpha=0.5):
        alpha_mask = self.original_image.convert("L").point(
            lambda x: 0 if x == 0 else 255
        )
        self.original_image.putalpha(alpha_mask)

        width, height = self.original_image.size
        grad_image = self.visual_gradation(width, height, start_color, end_color)

        result_image = Image.alpha_composite(
            Image.new("RGBA", self.original_image.size, (0, 0, 0, 0)), grad_image
        )
        result_image.paste(self.original_image, (0, 0), self.original_image)

        return result_image

    def visual_gradation(self, width, height, start, end):
        image = Image.new("RGBA", (width, height), (0, 0, 0, 0))

        draw = ImageDraw.Draw(image)
        for x in range(width):
            for y in range(height):
                alpha = int((1.0 - x / width) * 255)
                color = start + (alpha,)
                image.putpixel((x, y), color)

        return image

    @staticmethod
    def hex_to_rgb(hex_color):
        return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))


try:
    image_path = "Gradation/60D2151A-A12A-4F89-9D79-D7FD5DBEA4C4.png"

    gradation_filter = GradationFilter(image_path)

    start_color_input = input("Enter start color (hex): ")
    start_color = GradationFilter.hex_to_rgb(start_color_input)

    end_color_input = input("Enter end color (hex): ")
    end_color = GradationFilter.hex_to_rgb(end_color_input)

    filtered_image = gradation_filter.apply_gradation_filter(start_color, end_color)
    filtered_image.show()

except OSError:
    print("Error: Not a PNG file.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
