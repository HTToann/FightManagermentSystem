from flask import Flask
import cloudinary
from extensions import db, login

app = Flask(__name__)

app.secret_key = "%$@%^@%#^ZXCASD"
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "mysql+pymysql://root:tien84119@localhost/flightbooking?charset=utf8mb4"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
db.init_app(app)
login.init_app(app)
# Đăng ký API Blueprint

# VNP_TMNCODE = "F67XZR6Q"
# VNP_HASH_SECRET = "L4UZO7JJVKHE2CUUFU7PBJHJJDELOFYM"
# VNP_URL = "https://sandbox.vnpayment.vn/paymentv2/vpcpay.html"
# VNP_RETURN_URL = "http://localhost:5000/vnpay-return"

VNPAY_RETURN_URL = "http://localhost:5000/payment_return"  # get from config
VNPAY_PAYMENT_URL = "https://sandbox.vnpayment.vn/paymentv2/vpcpay.html"
VNPAY_API_URL = "https://sandbox.vnpayment.vn/merchant_webapi/api/transaction"
VNPAY_TMN_CODE = "F67XZR6Q"  # Website ID in VNPAY System, get from config
VNPAY_HASH_SECRET_KEY = (
    "L4UZO7JJVKHE2CUUFU7PBJHJJDELOFYM"  # Secret key for create checksum,get from config
)
