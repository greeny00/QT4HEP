"""QR code for the GitHub repository (reportlab encoder), verified by decoding with OpenCV."""
from reportlab.graphics.barcode import qrencoder
from PIL import Image
import numpy as np, cv2
URL = "https://github.com/greeny00/QT4HEP"
qr = qrencoder.QRCode(3, qrencoder.QRErrorCorrectLevel.M)
qr.addData(URL); qr.make()
n = qr.getModuleCount()
quiet, box = 4, 24
img = np.full(((n + 2 * quiet) * box,) * 2, 255, dtype=np.uint8)
for r in range(n):
    for c in range(n):
        if qr.isDark(r, c):
            img[(r + quiet) * box:(r + quiet + 1) * box, (c + quiet) * box:(c + quiet + 1) * box] = 0
Image.fromarray(img).save("qr_github.png")
data, _, _ = cv2.QRCodeDetector().detectAndDecode(cv2.imread("qr_github.png"))
print("modules", n, "decoded:", repr(data), "OK" if data == URL else "MISMATCH")
small = cv2.resize(cv2.imread("qr_github.png"), (150, 150), interpolation=cv2.INTER_AREA)
print("decoded at 150 px:", repr(cv2.QRCodeDetector().detectAndDecode(small)[0]))
