import hashlib
import hmac
import json
import urllib.parse
import random
import requests
from datetime import datetime
from flask import Flask, request, render_template, redirect, jsonify
from configs import (
    app,
    login,
    VNPAY_TMN_CODE,
    VNPAY_HASH_SECRET_KEY,
    VNPAY_PAYMENT_URL,
    VNPAY_RETURN_URL,
)
import fightBooking.vnpay as vnpay

app = Flask(__name__)


@app.route("/payment_return")
def payment_return():
    inputData = request.args
    vnp = vnpay()
    vnp.responseData = inputData.to_dict()
    if vnp.validate_response(VNPAY_HASH_SECRET_KEY):
        if inputData.get("vnp_ResponseCode") == "00":
            result = "Thành công"
        else:
            result = "Lỗi"
    else:
        result = "Sai checksum"

    return render_template(
        "payment_return.html", title="Kết quả thanh toán", result=result, data=inputData
    )


if __name__ == "__main__":
    app.run(debug=True)
