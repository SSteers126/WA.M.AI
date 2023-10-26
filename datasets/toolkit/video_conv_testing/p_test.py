from PIL import Image
from os import listdir
from pathlib import Path


folder = Path(r"C:\Users\Zestyy\OneDrive - MMU\Programming\Python\Tensorflow\WA.M.AI\datasets\image_labeller\out\t")
out = Path(r"C:\Users\Zestyy\OneDrive - MMU\Programming\Python\Tensorflow\WA.M.AI\datasets\image_labeller\out\t_pillow")

for img in listdir(folder):
    if (img_path := folder / img).is_file():
        pil_img = Image.open(img_path)
        pil_img.save(out / img, optimize=True)