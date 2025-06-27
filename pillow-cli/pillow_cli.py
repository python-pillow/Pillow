#!/usr/bin/env python3
import argparse
import os
import sys
from pathlib import Path
import json
from PIL import Image, ImageFilter, ImageEnhance, ImageDraw, ImageFont, ImageOps
from PIL.ExifTags import TAGS
import numpy as np
try:
    from PIL import ImageTk
    import tkinter as tk
    from tkinter import ttk
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False

class PillowCLI:
    """Main CLI class for image processing operations"""
    
    def __init__(self):
        self.supported_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp'}
    
    def validate_image_path(self, path):
        """Validate if the path is a valid image file"""
        if not os.path.exists(path):
            raise FileNotFoundError(f"Image file not found: {path}")
        
        if not Path(path).suffix.lower() in self.supported_formats:
            raise ValueError(f"Unsupported image format. Supported: {', '.join(self.supported_formats)}")
        
        return True
    
    def load_image(self, path):
        """Load an image from file path"""
        self.validate_image_path(path)
        return Image.open(path)
    
    def save_image(self, image, output_path, quality=95):
        """Save image to file with specified quality"""
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
        
        # Convert RGBA to RGB if saving as JPEG
        if Path(output_path).suffix.lower() in ['.jpg', '.jpeg'] and image.mode == 'RGBA':
            background = Image.new('RGB', image.size, (255, 255, 255))
            background.paste(image, mask=image.split()[-1])
            image = background
        
        image.save(output_path, quality=quality, optimize=True)
        print(f"Image saved to: {output_path}")
    
    def resize_image(self, input_path, output_path, width=None, height=None, maintain_aspect=True):
        """Resize image with optional aspect ratio preservation"""
        image = self.load_image(input_path)
        original_width, original_height = image.size
        
        if width and height:
            if maintain_aspect:
                # Calculate the aspect ratio
                aspect_ratio = original_width / original_height
                if width / height > aspect_ratio:
                    width = int(height * aspect_ratio)
                else:
                    height = int(width / aspect_ratio)
            new_size = (width, height)
        elif width:
            aspect_ratio = original_height / original_width
            new_size = (width, int(width * aspect_ratio))
        elif height:
            aspect_ratio = original_width / original_height
            new_size = (int(height * aspect_ratio), height)
        else:
            raise ValueError("Must specify at least width or height")
        
        resized_image = image.resize(new_size, Image.Resampling.LANCZOS)
        self.save_image(resized_image, output_path)
        print(f"Resized from {original_width}x{original_height} to {new_size[0]}x{new_size[1]}")
    
    def apply_filters(self, input_path, output_path, filter_type):
        """Apply various filters to the image"""
        image = self.load_image(input_path)
        
        filters = {
            'blur': ImageFilter.BLUR,
            'contour': ImageFilter.CONTOUR,
            'detail': ImageFilter.DETAIL,
            'edge_enhance': ImageFilter.EDGE_ENHANCE,
            'edge_enhance_more': ImageFilter.EDGE_ENHANCE_MORE,
            'emboss': ImageFilter.EMBOSS,
            'find_edges': ImageFilter.FIND_EDGES,
            'sharpen': ImageFilter.SHARPEN,
            'smooth': ImageFilter.SMOOTH,
            'smooth_more': ImageFilter.SMOOTH_MORE,
            'gaussian_blur': ImageFilter.GaussianBlur(radius=2),
            'unsharp_mask': ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3)
        }
        
        if filter_type not in filters:
            raise ValueError(f"Unknown filter: {filter_type}. Available: {', '.join(filters.keys())}")
        
        filtered_image = image.filter(filters[filter_type])
        self.save_image(filtered_image, output_path)
        print(f"Applied {filter_type} filter")
    
    def adjust_image(self, input_path, output_path, brightness=1.0, contrast=1.0, saturation=1.0, sharpness=1.0):
        """Adjust image brightness, contrast, saturation, and sharpness"""
        image = self.load_image(input_path)
        
        # Apply enhancements
        if brightness != 1.0:
            enhancer = ImageEnhance.Brightness(image)
            image = enhancer.enhance(brightness)
        
        if contrast != 1.0:
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(contrast)
        
        if saturation != 1.0:
            enhancer = ImageEnhance.Color(image)
            image = enhancer.enhance(saturation)
        
        if sharpness != 1.0:
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(sharpness)
        
        self.save_image(image, output_path)
        print(f"Adjusted image - Brightness: {brightness}, Contrast: {contrast}, Saturation: {saturation}, Sharpness: {sharpness}")
    
    def crop_image(self, input_path, output_path, x, y, width, height):
        """Crop image to specified dimensions"""
        image = self.load_image(input_path)
        
        # Make sure we're not trying to crop outside the image bounds
        img_width, img_height = image.size
        if x + width > img_width or y + height > img_height:
            raise ValueError(f"Crop dimensions exceed image size ({img_width}x{img_height})")
        
        cropped_image = image.crop((x, y, x + width, y + height))
        self.save_image(cropped_image, output_path)
        print(f"Cropped to {width}x{height} from position ({x}, {y})")
    
    def rotate_image(self, input_path, output_path, angle, expand=True):
        """Rotate image by specified angle"""
        image = self.load_image(input_path)
        rotated_image = image.rotate(angle, expand=expand, fillcolor='white')
        self.save_image(rotated_image, output_path)
        print(f"Rotated image by {angle} degrees")
    
    def flip_image(self, input_path, output_path, direction='horizontal'):
        """Flip image horizontally or vertically"""
        image = self.load_image(input_path)
        
        if direction == 'horizontal':
            flipped_image = image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        elif direction == 'vertical':
            flipped_image = image.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        else:
            raise ValueError("Direction must be 'horizontal' or 'vertical'")
        
        self.save_image(flipped_image, output_path)
        print(f"Flipped image {direction}ly")
    
    def convert_format(self, input_path, output_path, format_type='PNG'):
        """Convert image to different format"""
        image = self.load_image(input_path)
        
        # Handle transparency for JPEG conversion
        if format_type.upper() == 'JPEG' and image.mode in ('RGBA', 'LA'):
            background = Image.new('RGB', image.size, (255, 255, 255))
            background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
            image = background
        
        self.save_image(image, output_path)
        print(f"Converted to {format_type.upper()} format")
    
    def create_thumbnail(self, input_path, output_path, size=(128, 128)):
        """Create thumbnail of the image"""
        image = self.load_image(input_path)
        image.thumbnail(size, Image.Resampling.LANCZOS)
        self.save_image(image, output_path)
        print(f"Created thumbnail with size {size}")
    
    def add_watermark(self, input_path, output_path, watermark_text, position='bottom-right', opacity=128):
        """Add text watermark to image"""
        image = self.load_image(input_path)
        
        # Create a transparent overlay
        overlay = Image.new('RGBA', image.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(overlay)
        
        # Try to use a default font, fallback to default if not available
        try:
            font = ImageFont.truetype("arial.ttf", 36)
        except OSError:
            font = ImageFont.load_default()
        
        # Get text size
        bbox = draw.textbbox((0, 0), watermark_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Calculate position
        img_width, img_height = image.size
        positions = {
            'top-left': (10, 10),
            'top-right': (img_width - text_width - 10, 10),
            'bottom-left': (10, img_height - text_height - 10),
            'bottom-right': (img_width - text_width - 10, img_height - text_height - 10),
            'center': ((img_width - text_width) // 2, (img_height - text_height) // 2)
        }
        
        if position not in positions:
            raise ValueError(f"Invalid position. Available: {', '.join(positions.keys())}")
        
        x, y = positions[position]
        
        # Draw text with semi-transparent background
        draw.rectangle([x-5, y-5, x+text_width+5, y+text_height+5], fill=(0, 0, 0, opacity//2))
        draw.text((x, y), watermark_text, font=font, fill=(255, 255, 255, opacity))
        
        # Composite the overlay with the original image
        watermarked_image = Image.alpha_composite(image.convert('RGBA'), overlay)
        self.save_image(watermarked_image, output_path)
        print(f"Added watermark '{watermark_text}' at {position}")
    
    def extract_metadata(self, input_path):
        """Extract and display image metadata"""
        image = self.load_image(input_path)
        
        metadata = {
            'filename': os.path.basename(input_path),
            'format': image.format,
            'mode': image.mode,
            'size': image.size,
            'width': image.width,
            'height': image.height,
        }
        
        # Extract EXIF data if available
        exif_data = {}
        if hasattr(image, '_getexif') and image._getexif():
            exif = image._getexif()
            for tag_id, value in exif.items():
                tag = TAGS.get(tag_id, tag_id)
                exif_data[tag] = value
        
        if exif_data:
            metadata['exif'] = exif_data
        
        print(json.dumps(metadata, indent=2, default=str))
        return metadata
    
    def create_collage(self, input_paths, output_path, cols=2, padding=10):
        """Create a collage from multiple images"""
        if not input_paths:
            raise ValueError("No input images provided")
        
        # Load all images
        images = [self.load_image(path) for path in input_paths]
        
        # Calculate grid dimensions
        rows = (len(images) + cols - 1) // cols
        
        # Find the maximum dimensions
        max_width = max(img.width for img in images)
        max_height = max(img.height for img in images)
        
        # Resize all images to the same size
        resized_images = []
        for img in images:
            resized_img = img.resize((max_width, max_height), Image.Resampling.LANCZOS)
            resized_images.append(resized_img)
        
        # Calculate collage dimensions
        collage_width = cols * max_width + (cols + 1) * padding
        collage_height = rows * max_height + (rows + 1) * padding
        
        # Create collage
        collage = Image.new('RGB', (collage_width, collage_height), 'white')
        
        for i, img in enumerate(resized_images):
            row = i // cols
            col = i % cols
            x = col * (max_width + padding) + padding
            y = row * (max_height + padding) + padding
            collage.paste(img, (x, y))
        
        self.save_image(collage, output_path)
        print(f"Created collage with {len(images)} images ({rows}x{cols} grid)")
    
    def apply_artistic_effects(self, input_path, output_path, effect='sepia'):
        """Apply artistic effects to the image"""
        image = self.load_image(input_path).convert('RGB')
        
        if effect == 'sepia':
            # Convert to sepia
            pixels = image.load()
            for y in range(image.height):
                for x in range(image.width):
                    r, g, b = pixels[x, y]
                    tr = int(0.393 * r + 0.769 * g + 0.189 * b)
                    tg = int(0.349 * r + 0.686 * g + 0.168 * b)
                    tb = int(0.272 * r + 0.534 * g + 0.131 * b)
                    pixels[x, y] = (min(255, tr), min(255, tg), min(255, tb))
        
        elif effect == 'grayscale':
            image = ImageOps.grayscale(image)
        
        elif effect == 'invert':
            image = ImageOps.invert(image)
        
        elif effect == 'posterize':
            image = ImageOps.posterize(image, 4)
        
        elif effect == 'solarize':
            image = ImageOps.solarize(image, threshold=128)
        
        else:
            raise ValueError(f"Unknown effect: {effect}. Available: sepia, grayscale, invert, posterize, solarize")
        
        self.save_image(image, output_path)
        print(f"Applied {effect} effect")
    
    def batch_process(self, input_dir, output_dir, operation, **kwargs):
        """Process multiple images in a directory"""
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        
        if not input_path.exists():
            raise FileNotFoundError(f"Input directory not found: {input_dir}")
        
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Find all image files
        image_files = []
        for ext in self.supported_formats:
            image_files.extend(input_path.glob(f"*{ext}"))
            image_files.extend(input_path.glob(f"*{ext.upper()}"))
        
        if not image_files:
            print("No image files found in the input directory")
            return
        
        print(f"Processing {len(image_files)} images...")
        
        for i, image_file in enumerate(image_files, 1):
            try:
                output_file = output_path / image_file.name
                print(f"[{i}/{len(image_files)}] Processing: {image_file.name}")
                
                if operation == 'resize':
                    self.resize_image(str(image_file), str(output_file), **kwargs)
                elif operation == 'filter':
                    self.apply_filters(str(image_file), str(output_file), **kwargs)
                elif operation == 'adjust':
                    self.adjust_image(str(image_file), str(output_file), **kwargs)
                elif operation == 'effect':
                    self.apply_artistic_effects(str(image_file), str(output_file), **kwargs)
                elif operation == 'thumbnail':
                    self.create_thumbnail(str(image_file), str(output_file), **kwargs)
                else:
                    print(f"Unknown batch operation: {operation}")
                    return
                
            except Exception as e:
                print(f"Error processing {image_file.name}: {e}")
        
        print(f"Batch processing complete! Output saved to: {output_dir}")
    
    def simple_gui(self):
        """Launch a simple GUI for image processing"""
        if not GUI_AVAILABLE:
            print("GUI not available. Install tkinter to use this feature.")
            return
        
        def process_image():
            input_file = input_var.get()
            output_file = output_var.get()
            operation = operation_var.get()
            
            if not input_file or not output_file:
                status_var.set("Please select input and output files")
                return
            
            try:
                if operation == "Resize":
                    self.resize_image(input_file, output_file, width=300, height=300)
                elif operation == "Blur":
                    self.apply_filters(input_file, output_file, 'blur')
                elif operation == "Sepia":
                    self.apply_artistic_effects(input_file, output_file, 'sepia')
                elif operation == "Grayscale":
                    self.apply_artistic_effects(input_file, output_file, 'grayscale')
                
                status_var.set(f"Success! Processed image saved to {output_file}")
            except Exception as e:
                status_var.set(f"Error: {str(e)}")
        
        root = tk.Tk()
        root.title("Pillow CLI - Simple GUI")
        root.geometry("600x400")
        
        # Variables
        input_var = tk.StringVar()
        output_var = tk.StringVar()
        operation_var = tk.StringVar(value="Resize")
        status_var = tk.StringVar(value="Ready")
        
        # GUI elements
        ttk.Label(root, text="Input Image:").pack(pady=5)
        ttk.Entry(root, textvariable=input_var, width=60).pack(pady=5)
        
        ttk.Label(root, text="Output Image:").pack(pady=5)
        ttk.Entry(root, textvariable=output_var, width=60).pack(pady=5)
        
        ttk.Label(root, text="Operation:").pack(pady=5)
        ttk.Combobox(root, textvariable=operation_var, 
                    values=["Resize", "Blur", "Sepia", "Grayscale"]).pack(pady=5)
        
        ttk.Button(root, text="Process Image", command=process_image).pack(pady=20)
        
        ttk.Label(root, text="Status:").pack(pady=5)
        ttk.Label(root, textvariable=status_var, foreground="blue").pack(pady=5)
        
        root.mainloop()
    
    def analyze_histogram(self, input_path, output_path=None):
        """Analyze and optionally save image histogram"""
        image = self.load_image(input_path).convert('RGB')
        
        # Calculate histogram for each channel
        hist_r = image.histogram()[0:256]
        hist_g = image.histogram()[256:512]
        hist_b = image.histogram()[512:768]
        
        histogram_data = {
            'red_channel': hist_r,
            'green_channel': hist_g,
            'blue_channel': hist_b,
            'total_pixels': image.width * image.height
        }
        
        print(f"Image: {os.path.basename(input_path)}")
        print(f"Dimensions: {image.width}x{image.height}")
        print(f"Total pixels: {histogram_data['total_pixels']}")
        
        # Basic statistics
        avg_r = sum(i * hist_r[i] for i in range(256)) / sum(hist_r)
        avg_g = sum(i * hist_g[i] for i in range(256)) / sum(hist_g)
        avg_b = sum(i * hist_b[i] for i in range(256)) / sum(hist_b)
        
        print(f"Average RGB values: R={avg_r:.1f}, G={avg_g:.1f}, B={avg_b:.1f}")
        
        if output_path:
            with open(output_path, 'w') as f:
                json.dump(histogram_data, f, indent=2)
            print(f"Histogram data saved to: {output_path}")
        
        return histogram_data
    
    def extract_color_palette(self, input_path, num_colors=5):
        """Extract dominant colors from image"""
        image = self.load_image(input_path).convert('RGB')
        
        # Resize image for faster processing
        image = image.resize((150, 150))
        
        # Convert to numpy array and reshape
        img_array = np.array(image)
        pixels = img_array.reshape(-1, 3)
        
        # Use k-means clustering to find dominant colors
        try:
            from sklearn.cluster import KMeans
            kmeans = KMeans(n_clusters=num_colors, random_state=42, n_init=10)
            kmeans.fit(pixels)
            colors = kmeans.cluster_centers_.astype(int)
            
            print(f"Dominant colors in {os.path.basename(input_path)}:")
            for i, color in enumerate(colors, 1):
                hex_color = '#{:02x}{:02x}{:02x}'.format(color[0], color[1], color[2])
                print(f"  {i}. RGB({color[0]}, {color[1]}, {color[2]}) - {hex_color}")
            
            return colors.tolist()
        except ImportError:
            print("scikit-learn not installed. Using simple color extraction...")
            # Fallback to simple method
            unique_colors = {}
            for pixel in pixels:
                color = tuple(pixel)
                unique_colors[color] = unique_colors.get(color, 0) + 1
            
            # Get most common colors
            sorted_colors = sorted(unique_colors.items(), key=lambda x: x[1], reverse=True)
            top_colors = [list(color[0]) for color in sorted_colors[:num_colors]]
            
            print(f"Most common colors in {os.path.basename(input_path)}:")
            for i, color in enumerate(top_colors, 1):
                hex_color = '#{:02x}{:02x}{:02x}'.format(color[0], color[1], color[2])
                print(f"  {i}. RGB({color[0]}, {color[1]}, {color[2]}) - {hex_color}")
            
            return top_colors
    
    def create_border(self, input_path, output_path, border_width=10, border_color='black'):
        """Add border around image"""
        image = self.load_image(input_path)
        
        # Parse border color
        if isinstance(border_color, str):
            if border_color.startswith('#'):
                # Hex color
                border_color = tuple(int(border_color[i:i+2], 16) for i in (1, 3, 5))
            elif border_color in ['black', 'white', 'red', 'green', 'blue']:
                # Named colors
                color_map = {
                    'black': (0, 0, 0),
                    'white': (255, 255, 255),
                    'red': (255, 0, 0),
                    'green': (0, 255, 0),
                    'blue': (0, 0, 255)
                }
                border_color = color_map[border_color]
        
        bordered_image = ImageOps.expand(image, border=border_width, fill=border_color)
        self.save_image(bordered_image, output_path)
        print(f"Added {border_width}px border with color {border_color}")
    
    def create_composite(self, background_path, overlay_path, output_path, position=(0, 0), opacity=1.0):
        """Composite two images together"""
        background = self.load_image(background_path).convert('RGBA')
        overlay = self.load_image(overlay_path).convert('RGBA')
        
        # Adjust overlay opacity
        if opacity < 1.0:
            overlay = overlay.copy()
            overlay.putalpha(int(255 * opacity))
        
        # Create composite
        composite = Image.new('RGBA', background.size, (0, 0, 0, 0))
        composite.paste(background, (0, 0))
        composite.paste(overlay, position, overlay)
        
        self.save_image(composite, output_path)
        print(f"Created composite image at position {position} with opacity {opacity}")
    
    def apply_vignette(self, input_path, output_path, strength=0.5):
        """Apply vignette effect to image"""
        image = self.load_image(input_path).convert('RGBA')
        width, height = image.size
        
        # Create vignette mask
        mask = Image.new('L', (width, height), 0)
        mask_draw = ImageDraw.Draw(mask)
        
        # Calculate center and radii
        center_x, center_y = width // 2, height // 2
        max_radius = min(center_x, center_y)
        
        # Draw gradient circles
        steps = 100
        for i in range(steps):
            radius = max_radius * (i / steps)
            alpha = int(255 * (1 - strength * (i / steps)))
            mask_draw.ellipse([center_x - radius, center_y - radius,
                              center_x + radius, center_y + radius], fill=alpha)
        
        # Apply vignette
        vignette_overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        vignette_overlay.putalpha(mask)
        
        result = Image.alpha_composite(image, vignette_overlay)
        self.save_image(result, output_path)
        print(f"Applied vignette effect with strength {strength}")
    
    def create_contact_sheet(self, input_paths, output_path, sheet_width=1200, margin=10):
        """Create a contact sheet from multiple images"""
        if not input_paths:
            raise ValueError("No input images provided")
        
        images = [self.load_image(path) for path in input_paths]
        
        # Calculate thumbnail size based on sheet width and number of images
        cols = min(4, len(images))  # Max 4 columns
        rows = (len(images) + cols - 1) // cols
        
        thumb_width = (sheet_width - margin * (cols + 1)) // cols
        thumb_height = thumb_width  # Square thumbnails
        
        # Create contact sheet
        sheet_height = rows * thumb_height + margin * (rows + 1)
        contact_sheet = Image.new('RGB', (sheet_width, sheet_height), 'white')
        
        for i, img in enumerate(images):
            # Create thumbnail
            img.thumbnail((thumb_width, thumb_height), Image.Resampling.LANCZOS)
            
            # Calculate position
            row = i // cols
            col = i % cols
            x = col * (thumb_width + margin) + margin
            y = row * (thumb_height + margin) + margin
            
            # Center the thumbnail if it's smaller than the allocated space
            if img.width < thumb_width:
                x += (thumb_width - img.width) // 2
            if img.height < thumb_height:
                y += (thumb_height - img.height) // 2
            
            contact_sheet.paste(img, (x, y))
        
        self.save_image(contact_sheet, output_path)
        print(f"Created contact sheet with {len(images)} images ({rows}x{cols} grid)")
    
    def split_channels(self, input_path, output_dir):
        """Split image into separate color channels"""
        image = self.load_image(input_path).convert('RGB')
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        base_name = Path(input_path).stem
        
        # Split channels
        r, g, b = image.split()
        
        # Save each channel
        r_path = output_path / f"{base_name}_red.png"
        g_path = output_path / f"{base_name}_green.png"
        b_path = output_path / f"{base_name}_blue.png"
        
        # Convert to RGB for saving (grayscale channels)
        r_img = Image.merge('RGB', [r, Image.new('L', image.size, 0), Image.new('L', image.size, 0)])
        g_img = Image.merge('RGB', [Image.new('L', image.size, 0), g, Image.new('L', image.size, 0)])
        b_img = Image.merge('RGB', [Image.new('L', image.size, 0), Image.new('L', image.size, 0), b])
        
        self.save_image(r_img, str(r_path))
        self.save_image(g_img, str(g_path))
        self.save_image(b_img, str(b_path))
        
        print(f"Split channels saved to {output_dir}")
        return [str(r_path), str(g_path), str(b_path)]

def main():
    """Main function to handle command line arguments"""
    parser = argparse.ArgumentParser(description="Pillow CLI - Comprehensive Image Processing Tool")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Resize command
    resize_parser = subparsers.add_parser('resize', help='Resize image')
    resize_parser.add_argument('input', help='Input image path')
    resize_parser.add_argument('output', help='Output image path')
    resize_parser.add_argument('--width', type=int, help='Target width')
    resize_parser.add_argument('--height', type=int, help='Target height')
    resize_parser.add_argument('--no-aspect', action='store_true', help='Don\'t maintain aspect ratio')
    
    # Filter command
    filter_parser = subparsers.add_parser('filter', help='Apply filter to image')
    filter_parser.add_argument('input', help='Input image path')
    filter_parser.add_argument('output', help='Output image path')
    filter_parser.add_argument('type', choices=['blur', 'contour', 'detail', 'edge_enhance', 
                                               'edge_enhance_more', 'emboss', 'find_edges', 
                                               'sharpen', 'smooth', 'smooth_more', 'gaussian_blur', 
                                               'unsharp_mask'], help='Filter type')
    
    # Adjust command
    adjust_parser = subparsers.add_parser('adjust', help='Adjust image properties')
    adjust_parser.add_argument('input', help='Input image path')
    adjust_parser.add_argument('output', help='Output image path')
    adjust_parser.add_argument('--brightness', type=float, default=1.0, help='Brightness factor (default: 1.0)')
    adjust_parser.add_argument('--contrast', type=float, default=1.0, help='Contrast factor (default: 1.0)')
    adjust_parser.add_argument('--saturation', type=float, default=1.0, help='Saturation factor (default: 1.0)')
    adjust_parser.add_argument('--sharpness', type=float, default=1.0, help='Sharpness factor (default: 1.0)')
    
    # Crop command
    crop_parser = subparsers.add_parser('crop', help='Crop image')
    crop_parser.add_argument('input', help='Input image path')
    crop_parser.add_argument('output', help='Output image path')
    crop_parser.add_argument('x', type=int, help='X coordinate')
    crop_parser.add_argument('y', type=int, help='Y coordinate')
    crop_parser.add_argument('width', type=int, help='Crop width')
    crop_parser.add_argument('height', type=int, help='Crop height')
    
    # Rotate command
    rotate_parser = subparsers.add_parser('rotate', help='Rotate image')
    rotate_parser.add_argument('input', help='Input image path')
    rotate_parser.add_argument('output', help='Output image path')
    rotate_parser.add_argument('angle', type=float, help='Rotation angle in degrees')
    rotate_parser.add_argument('--no-expand', action='store_true', help='Don\'t expand canvas')
    
    # Flip command
    flip_parser = subparsers.add_parser('flip', help='Flip image')
    flip_parser.add_argument('input', help='Input image path')
    flip_parser.add_argument('output', help='Output image path')
    flip_parser.add_argument('direction', choices=['horizontal', 'vertical'], help='Flip direction')
    
    # Convert command
    convert_parser = subparsers.add_parser('convert', help='Convert image format')
    convert_parser.add_argument('input', help='Input image path')
    convert_parser.add_argument('output', help='Output image path')
    convert_parser.add_argument('--format', default='PNG', help='Target format (default: PNG)')
    
    # Thumbnail command
    thumbnail_parser = subparsers.add_parser('thumbnail', help='Create thumbnail')
    thumbnail_parser.add_argument('input', help='Input image path')
    thumbnail_parser.add_argument('output', help='Output image path')
    thumbnail_parser.add_argument('--size', type=int, nargs=2, default=[128, 128], help='Thumbnail size (width height)')
    
    # Watermark command
    watermark_parser = subparsers.add_parser('watermark', help='Add watermark')
    watermark_parser.add_argument('input', help='Input image path')
    watermark_parser.add_argument('output', help='Output image path')
    watermark_parser.add_argument('text', help='Watermark text')
    watermark_parser.add_argument('--position', choices=['top-left', 'top-right', 'bottom-left', 
                                                        'bottom-right', 'center'], 
                                 default='bottom-right', help='Watermark position')
    watermark_parser.add_argument('--opacity', type=int, default=128, help='Watermark opacity (0-255)')
    
    # Metadata command
    metadata_parser = subparsers.add_parser('metadata', help='Extract image metadata')
    metadata_parser.add_argument('input', help='Input image path')
    
    # Collage command
    collage_parser = subparsers.add_parser('collage', help='Create collage from multiple images')
    collage_parser.add_argument('output', help='Output image path')
    collage_parser.add_argument('inputs', nargs='+', help='Input image paths')
    collage_parser.add_argument('--cols', type=int, default=2, help='Number of columns')
    collage_parser.add_argument('--padding', type=int, default=10, help='Padding between images')
    
    # Effect command
    effect_parser = subparsers.add_parser('effect', help='Apply artistic effects')
    effect_parser.add_argument('input', help='Input image path')
    effect_parser.add_argument('output', help='Output image path')
    effect_parser.add_argument('type', choices=['sepia', 'grayscale', 'invert', 'posterize', 'solarize'], 
                              help='Effect type')
    
    # Batch command
    batch_parser = subparsers.add_parser('batch', help='Batch process images')
    batch_parser.add_argument('input_dir', help='Input directory')
    batch_parser.add_argument('output_dir', help='Output directory')
    batch_parser.add_argument('operation', choices=['resize', 'filter', 'adjust', 'effect', 'thumbnail'], 
                             help='Batch operation')
    batch_parser.add_argument('--width', type=int, help='Width for resize operation')
    batch_parser.add_argument('--height', type=int, help='Height for resize operation')
    batch_parser.add_argument('--filter-type', help='Filter type for filter operation')
    batch_parser.add_argument('--effect-type', help='Effect type for effect operation')
    batch_parser.add_argument('--size', type=int, nargs=2, default=[128, 128], help='Size for thumbnail operation')
    
    # GUI command
    gui_parser = subparsers.add_parser('gui', help='Launch simple GUI')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    cli = PillowCLI()
    
    try:
        if args.command == 'resize':
            cli.resize_image(args.input, args.output, args.width, args.height, 
                           maintain_aspect=not args.no_aspect)
        
        elif args.command == 'filter':
            cli.apply_filters(args.input, args.output, args.type)
        
        elif args.command == 'adjust':
            cli.adjust_image(args.input, args.output, args.brightness, args.contrast, 
                           args.saturation, args.sharpness)
        
        elif args.command == 'crop':
            cli.crop_image(args.input, args.output, args.x, args.y, args.width, args.height)
        
        elif args.command == 'rotate':
            cli.rotate_image(args.input, args.output, args.angle, expand=not args.no_expand)
        
        elif args.command == 'flip':
            cli.flip_image(args.input, args.output, args.direction)
        
        elif args.command == 'convert':
            cli.convert_format(args.input, args.output, args.format)
        
        elif args.command == 'thumbnail':
            cli.create_thumbnail(args.input, args.output, tuple(args.size))
        
        elif args.command == 'watermark':
            cli.add_watermark(args.input, args.output, args.text, args.position, args.opacity)
        
        elif args.command == 'metadata':
            cli.extract_metadata(args.input)
        
        elif args.command == 'collage':
            cli.create_collage(args.inputs, args.output, args.cols, args.padding)
        
        elif args.command == 'effect':
            cli.apply_artistic_effects(args.input, args.output, args.type)
        
        elif args.command == 'batch':
            kwargs = {}
            if args.operation == 'resize':
                kwargs = {'width': args.width, 'height': args.height}
            elif args.operation == 'filter':
                kwargs = {'filter_type': args.filter_type}
            elif args.operation == 'effect':
                kwargs = {'effect': args.effect_type}
            elif args.operation == 'thumbnail':
                kwargs = {'size': tuple(args.size)}
            
            cli.batch_process(args.input_dir, args.output_dir, args.operation, **kwargs)
        
        elif args.command == 'gui':
            cli.simple_gui()
    
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()