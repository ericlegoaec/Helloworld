import cv2
import codecs
from wand.image import Image
from PIL import Image as PI
import pyocr
import pyocr.builders
import io

tool = pyocr.get_available_tools()[0]
lang = tool.get_available_languages()[2]
builder = pyocr.builders.LineBoxBuilder()
# req_image = []

# image_pdf = Image(filename="./Notification Letter and Information Request-Haitong.pdf", resolution=300)
# image_jpeg = image_pdf.convert('jpeg')

# for img in image_jpeg.sequence:
#     img_page = Image(image=img)
#     req_image.append(img_page.make_blob('jpeg'))

final_text = []
if True:
# for img in req_image: 
    txt = tool.image_to_string(
        # PI.open(io.BytesIO(img)),
        PI.open("sample2_large.png"),
        lang=lang,
        builder=builder
    )
    final_text.append(txt)

with codecs.open("toto.html", 'w', encoding='utf-8') as file_descriptor:
    builder.write_file(file_descriptor, final_text[0])
