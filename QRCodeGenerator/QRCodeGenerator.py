import qrcode

user_input = input("Enter the text you want to convert to QR Code: ")

if user_input:
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(user_input)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img.save("qrcode.png")
    print("QR Code saved as qrcode.png")
else:
    print("Please enter some text to convert to QR Code")
    