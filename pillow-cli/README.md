# Pillow CLI - Comprehensive Image Processing Tool

A feature-rich command-line interface for image processing using the Python Pillow library. This tool provides a wide range of image manipulation capabilities with an easy-to-use CLI interface.

## Features

### Core Image Operations

-   **Resize**: Resize images with aspect ratio preservation
-   **Crop**: Crop images to specific dimensions
-   **Rotate**: Rotate images by any angle
-   **Flip**: Flip images horizontally or vertically
-   **Convert**: Convert between different image formats

### Filters & Effects

-   **Filters**: Apply various filters (blur, sharpen, emboss, edge enhancement, etc.)
-   **Artistic Effects**: Apply artistic effects (sepia, grayscale, invert, posterize, solarize)
-   **Image Adjustments**: Adjust brightness, contrast, saturation, and sharpness

### Advanced Features

-   **Watermarking**: Add text watermarks with customizable position and opacity
-   **Thumbnails**: Generate thumbnails with custom sizes
-   **Collages**: Create collages from multiple images
-   **Batch Processing**: Process multiple images in a directory
-   **Metadata Extraction**: Extract EXIF and image metadata
-   **Simple GUI**: Launch a basic graphical interface

## Installation

### Option 1: Run from Source

1. Install Python 3.7 or higher
2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

### Option 2: Use Pre-built Executable

1. Download the latest `pillow-cli.exe` from the releases
2. Run directly without Python installation required

### Option 3: Build Your Own Executable

1. Install Python 3.7 or higher
2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3. Build the executable:

    ```bash
    # Windows batch script
    build_exe.bat

    # Or PowerShell script
    build_exe.ps1

    # Or manually with PyInstaller
    pyinstaller pillow-cli.spec
    ```

4. Find the executable in the `dist/` folder

## Usage

### Using the Python Script

#### Resize Image

```bash
python pillow_cli.py resize input.jpg output.jpg --width 800 --height 600
python pillow_cli.py resize input.jpg output.jpg --width 800  # Maintains aspect ratio
```

#### Apply Filters

```bash
python pillow_cli.py filter input.jpg output.jpg blur
python pillow_cli.py filter input.jpg output.jpg sharpen
python pillow_cli.py filter input.jpg output.jpg gaussian_blur
```

Available filters: `blur`, `contour`, `detail`, `edge_enhance`, `edge_enhance_more`, `emboss`, `find_edges`, `sharpen`, `smooth`, `smooth_more`, `gaussian_blur`, `unsharp_mask`

#### Adjust Image Properties

```bash
python pillow_cli.py adjust input.jpg output.jpg --brightness 1.2 --contrast 1.1 --saturation 0.9
```

#### Crop Image

```bash
python pillow_cli.py crop input.jpg output.jpg 100 100 400 300
```

#### Rotate Image

```bash
python pillow_cli.py rotate input.jpg output.jpg 45
python pillow_cli.py rotate input.jpg output.jpg 90 --no-expand
```

#### Flip Image

```bash
python pillow_cli.py flip input.jpg output.jpg horizontal
python pillow_cli.py flip input.jpg output.jpg vertical
```

#### Convert Format

```bash
python pillow_cli.py convert input.jpg output.png
python pillow_cli.py convert input.png output.jpg --format JPEG
```

#### Create Thumbnail

```bash
python pillow_cli.py thumbnail input.jpg thumb.jpg --size 150 150
```

#### Add Watermark

```bash
python pillow_cli.py watermark input.jpg output.jpg "© 2025 MyBrand" --position bottom-right --opacity 128
```

Available positions: `top-left`, `top-right`, `bottom-left`, `bottom-right`, `center`

#### Extract Metadata

```bash
python pillow_cli.py metadata input.jpg
```

#### Apply Artistic Effects

```bash
python pillow_cli.py effect input.jpg output.jpg sepia
python pillow_cli.py effect input.jpg output.jpg grayscale
```

Available effects: `sepia`, `grayscale`, `invert`, `posterize`, `solarize`

#### Create Collage

```bash
python pillow_cli.py collage output.jpg image1.jpg image2.jpg image3.jpg image4.jpg --cols 2 --padding 10
```

#### Batch Processing

```bash
# Resize all images in a directory
python pillow_cli.py batch input_dir output_dir resize --width 800 --height 600

# Apply sepia effect to all images
python pillow_cli.py batch input_dir output_dir effect --effect-type sepia

# Create thumbnails for all images
python pillow_cli.py batch input_dir output_dir thumbnail --size 200 200
```

#### Launch GUI

```bash
python pillow_cli.py gui
```

### Using the Executable

#### Resize Image

```bash
pillow-cli.exe resize input.jpg output.jpg --width 800 --height 600
pillow-cli.exe resize input.jpg output.jpg --width 800  # Maintains aspect ratio
```

#### Apply Filters

```bash
# Using Python script
python pillow_cli.py filter input.jpg output.jpg blur

# Using executable
pillow-cli.exe filter input.jpg output.jpg blur
```

## Supported Image Formats

-   JPEG (.jpg, .jpeg)
-   PNG (.png)
-   BMP (.bmp)
-   GIF (.gif)
-   TIFF (.tiff)
-   WebP (.webp)

## Examples

### Example 1: Create a Social Media Post

1. Resize image to square format:

    ```bash
    python pillow-cli.py resize photo.jpg square.jpg --width 1080 --height 1080
    ```

2. Add watermark:
    ```bash
    python pillow-cli.py watermark square.jpg final.jpg "@myhandle" --position bottom-right
    ```

### Example 2: Process Product Photos

1. Batch resize all product photos:

    ```bash
    python pillow-cli.py batch raw_photos processed_photos resize --width 1200 --height 800
    ```

2. Create thumbnails:
    ```bash
    python pillow-cli.py batch processed_photos thumbnails thumbnail --size 300 300
    ```

### Example 3: Create a Photo Collage

```bash
python pillow-cli.py collage family_collage.jpg photo1.jpg photo2.jpg photo3.jpg photo4.jpg --cols 2 --padding 15
```

## Advanced Usage

### Chaining Operations

You can chain multiple operations by using the output of one command as input to another:

```bash
# First, resize the image
python pillow-cli.py resize original.jpg resized.jpg --width 800

# Then apply a filter
python pillow-cli.py filter resized.jpg filtered.jpg sharpen

# Finally, add a watermark
python pillow-cli.py watermark filtered.jpg final.jpg "© 2025" --position bottom-right
```

### Batch Processing Different Operations

Process different types of operations on batches:

```bash
# Apply different effects
python pillow-cli.py batch photos vintage_photos effect --effect-type sepia
python pillow-cli.py batch photos bw_photos effect --effect-type grayscale

# Apply different filters
python pillow-cli.py batch photos sharp_photos filter --filter-type sharpen
python pillow-cli.py batch photos soft_photos filter --filter-type blur
```

## Error Handling

The tool includes comprehensive error handling for:

-   Invalid file paths
-   Unsupported image formats
-   Invalid crop dimensions
-   Missing required parameters
-   Corrupted image files

## Contributing

Feel free to extend this tool with additional features such as:

-   More artistic filters
-   Advanced color manipulations
-   Image composition features
-   Custom font support for watermarks
-   Integration with cloud storage services

## License

This project is open source and available under the MIT License.

## Requirements

-   Python 3.7+
-   Pillow >= 10.0.0
-   NumPy >= 1.24.0
-   tkinter (for GUI, usually included with Python)

## Author

Created with GitHub Copilot - June 2025
