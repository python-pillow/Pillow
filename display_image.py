import time
import matplotlib
matplotlib.use('TkAgg')
from PIL import Image
import matplotlib.pyplot as plt

# Open an image file
img = Image.open('boy meets evil.png')

# Display the image
plt.imshow(img)
plt.show()

# Keep the script running for a while
time.sleep(10)  # keeps the script running for 10 seconds