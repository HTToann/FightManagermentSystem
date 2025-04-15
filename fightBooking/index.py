import sys
import admin
from configs import (
    app,
    login,
    VNPAY_TMN_CODE,
    VNPAY_HASH_SECRET_KEY,
    VNPAY_PAYMENT_URL,
    VNPAY_RETURN_URL,
)
from flask import render_template, request, redirect, flash, url_for, session
from flask_login import login_user, current_user, logout_user
import cloudinary.uploader
import dao
import run
from datetime import datetime, timedelta
import requests
from vnpay import vnpay
import urllib.parse
import json
import base64


@app.route("/")
def index():
    airports = dao.get_departure_airport()
    return render_template("index.html", airports=airports)


# @app.route("/admin/create_flight", methods=["GET", "POST"])
# def create_flight():
#     if request.method == "POST":
#         try:
#             start_airport = request.form.get("start_airport")
#             end_airport = request.form.get("end_airport")
#             start_time = request.form.get("start_time")
#             end_time = request.form.get("end_time")
#             plane_id = request.form.get("plane_id")
#             rule = dao.get_rule()
#             # Kiểm tra dữ liệu rỗng
#             if (
#                 not start_airport
#                 or not end_airport
#                 or not start_time
#                 or not end_time
#                 or not plane_id
#             ):
#                 flash("❌ Vui lòng nhập đầy đủ thông tin!", "danger")
#                 raise Exception("Missing fields")

#             if start_airport == end_airport:
#                 flash("❌ Sân bay đi và đến không thể giống nhau!", "danger")
#                 raise Exception("Start and end airport must be different")

#             start_dt = datetime.strptime(start_time, "%Y-%m-%dT%H:%M")
#             end_dt = datetime.strptime(end_time, "%Y-%m-%dT%H:%M")

#             if start_dt >= end_dt:
#                 flash("❌ Thời gian khởi hành phải trước thời gian hạ cánh!", "danger")
#                 raise Exception("Invalid flight time")

#             if end_dt - start_dt < timedelta(minutes=rule.min_flight_duration):
#                 flash(
#                     f"❌ Thời gian bay tối thiểu phải là {rule.min_flight_duration}phút!",
#                     "danger",
#                 )
#                 raise Exception("Flight duration too short")

#             # Tạo route và flight
#             route = dao.add_route(start_airport=start_airport, end_airport=end_airport)
#             if not route:
#                 raise Exception("Không thể tạo tuyến bay!")

#             flight = dao.add_flight(
#                 start_time=start_time,
#                 end_time=end_time,
#                 route_id=route.id,
#                 plane_id=plane_id,
#             )
#             if not flight:
#                 raise Exception("Không thể tạo chuyến bay!")
#                 # ✅ Tạo các bản ghi FlightSeat cho chuyến bay này
#             dao.create_flight_seats(flight.id, plane_id)
#             # Xử lý sân bay trung gian nếu có
#             layover_airports = set()
#             layover_count = 0

#             if "layovers[1][airport_id]" in request.form:
#                 layover_count = len(request.form.getlist("layovers[1][airport_id]"))

#                 if layover_count > rule.max_layover_airports:
#                     flash(
#                         f"❌ Tối đa chỉ được {rule.max_layover_airports} sân bay trung gian!",
#                         "danger",
#                     )
#                     raise Exception("Too many layovers")

#                 for i in range(layover_count):
#                     airport_id = request.form.getlist(f"layovers[{i+1}][airport_id]")[0]
#                     arrival_time = request.form.getlist(f"layovers[{i+1}][arrival]")[0]
#                     departure_time = request.form.getlist(
#                         f"layovers[{i+1}][departure]"
#                     )[0]

#                     if airport_id in [start_airport, end_airport]:
#                         flash(
#                             "❌ Sân bay trung gian không được trùng sân bay đi/đến!",
#                             "danger",
#                         )
#                         raise Exception("Layover airport conflict")

#                     if airport_id in layover_airports:
#                         flash(
#                             "❌ Không được chọn 2 sân bay trung gian giống nhau!",
#                             "danger",
#                         )
#                         raise Exception("Duplicate layover airport")

#                     layover_airports.add(airport_id)

#                     arr_dt = datetime.strptime(arrival_time, "%Y-%m-%dT%H:%M")
#                     dep_dt = datetime.strptime(departure_time, "%Y-%m-%dT%H:%M")

#                     if arr_dt >= dep_dt:
#                         flash(
#                             "❌ Giờ đến phải trước giờ đi ở sân bay trung gian!",
#                             "danger",
#                         )
#                         raise Exception("Invalid layover time")

#                     stop_duration = dep_dt - arr_dt
#                     if stop_duration < timedelta(
#                         minutes=rule.min_layover_duration
#                     ) or stop_duration > timedelta(minutes=rule.max_layover_duration):
#                         flash(
#                             f"❌ Thời gian dừng phải từ {rule.min_layover_duration}-{rule.max_layover_duration} phút!",
#                             "danger",
#                         )
#                         raise Exception("Invalid layover duration")

#                     if arr_dt < start_dt or dep_dt > end_dt:
#                         flash(
#                             "❌ Sân bay trung gian phải nằm trong khoảng thời gian chuyến bay!",
#                             "danger",
#                         )
#                         raise Exception("Layover outside flight time")

#                     dao.add_part_flight(
#                         start_time=arrival_time,
#                         end_time=departure_time,
#                         route_id=route.id,
#                         flight_id=flight.id,
#                     )

#             flash("✅ Tạo chuyến bay thành công!", "success")
#             return redirect("/admin/create_flight")

#         except Exception as e:
#             flash("❌Lỗi khi tạo chuyến bay!", "danger")
#             print("❌ Lỗi khi tạo chuyến bay:", str(e))

#     airports = dao.get_departure_airport()
#     planes = dao.get_all_plane()
#     ticket_classes = dao.get_all_ticket_classes()

#     return render_template(
#         "admin/create_flight.html",
#         airports=airports,
#         planes=planes,
#         ticket_classes=ticket_classes,
#     )


@app.route("/passenger")
def passenger():
    return render_template("passengers/passenger.html")


@app.route("/search", methods=["GET", "POST"])
def search_booking():
    if request.method == "POST":
        try:
            destination = request.form.get("destination")
            arrival = request.form.get("arrival")
            check_in = request.form.get("check-in")
            guests = request.form.get("guests")

            flights = dao.get_flight(destination, arrival, check_in)
            flight_ticket_classes = {
                flight.id: dao.get_ticket_classes_by_plane(flight.plane_id)
                for flight in flights
            }

            flights_data = [
                {
                    "id": flight.id,
                    "plane_id": flight.plane.id,
                    "plane_name": flight.plane.name,
                    "destination": destination,
                    "arrival": arrival,
                    "start_time": flight.start_time.strftime("%H:%M"),
                    "end_time": flight.end_time.strftime("%H:%M"),
                }
                for flight in flights
            ]
            return render_template(
                "search/search.html",
                flights=flights_data,
                flight_ticket_classes=flight_ticket_classes,
                destination=destination,
                arrival=arrival,
                guests=guests,
            )
        except Exception as e:
            return f"Lỗi: {e}"


@app.route("/seatSelection", methods=["GET", "POST"])
def seat_selection():
    if request.method.__eq__("POST"):
        guests = {}
        first_names = request.form.getlist("first_name[]")
        last_names = request.form.getlist("last_name[]")
        birth_dates = request.form.getlist("date[]")
        countries = request.form.getlist("country[]")
        phones = request.form.getlist("phone[]")
        emails = request.form.getlist("email[]")
        cccds = request.form.getlist("cccd[]")
        for i in range(len(first_names)):
            key = f"guest_{i+1}"
            guests[key] = {
                "first_name": first_names[i],
                "last_name": last_names[i],
                "date_of_birth": birth_dates[i],
                "country": countries[i],
                "phone": phones[i],
                "email": emails[i],
                "cccd": cccds[i],
            }
        session["passenger_info"] = guests
        data = {
            "flight_id": request.form.get("flight_id"),
            "plane_name": request.form.get("plane_name"),
            "destination": request.form.get("destination"),
            "arrival": request.form.get("arrival"),
            "start_time": request.form.get("start_time"),
            "end_time": request.form.get("end_time"),
            "rank": request.form.get("rank"),
            "price": request.form.get("price"),
        }
        session["data"] = data
        flight_id = request.form.get("flight_id")
        ticket_class_name = request.form.get("rank")
        seats = dao.get_all_seats_by_flight(
            flight_id=flight_id, ticket_class_name=ticket_class_name
        )
        number_of_guests = len(guests)
        return render_template(
            "passengers/seatSelection.html",
            seats=seats,
            number_of_guests=number_of_guests,
        )


def get_client_ip():
    return request.remote_addr or "127.0.0.1"


@app.route("/payment", methods=["GET", "POST"])
def payment():
    payment_id = request.args.get("payment_id")
    if not payment_id:
        return "Thiếu payment_id", 400
    staff_id = request.args.get("staff_id")  # ✅ Lấy staff_id nếu có
    if request.method == "POST":
        seat_ids = request.form.get("selected_seat_id")
        return redirect(
            url_for(
                "payment",
                payment_id=payment_id,
                seat_ids=seat_ids,
            )
        )
    # GET request

    data = session.get("data")
    passenger_info = session.get("passenger_info")

    seat_ids_raw = request.args.get("seat_ids", "")

    seat_ids = [sid for sid in seat_ids_raw.split(",") if sid]
    # tính tiền
    try:
        total = float(data.get("price", 0)) * len(seat_ids)
    except (TypeError, ValueError):
        total = 0

    return render_template(
        "payment/payment.html",
        title="Thanh toán",
        current_time=datetime.now(),
        datetime=datetime,
        payment_id=payment_id,
        total=total,
        data=data,
        passenger_info=passenger_info,
        seat_id=seat_ids,
        staff_id=staff_id,
    )


@app.route("/create_payment", methods=["POST"])
def create_payment():
    if request.method == "POST":
        raw_data = request.form.get("data")
        raw_passenger_info = request.form.get("passenger_info")
        seat_ids = request.form.get("seat_id")
        order_type = request.form.get("order_type")
        order_id = request.form.get("order_id")
        amount_raw = request.form.get("amount")
        order_desc = request.form.get("order_desc")
        bank_code = request.form.get("bank_code")
        language = request.form.get("language")
        staff_id = request.form.get("staff_id")
        try:
            amount = int(amount_raw)
        except (ValueError, TypeError):
            return "Invalid amount value", 400
        # lấy id flight từ dữ liệu JSON
        json_data = json.loads(raw_data)  # ✅ Chuyển từ JSON string thành dict
        flight_id = json_data["flight_id"]
        seat_ids = seat_ids.replace("[", "").replace("]", "").replace("'", "")
        guests = dao.add_guest(info=raw_passenger_info)
        guest_ids = [guest.id for guest in guests]
        vnp = vnpay()
        vnp.requestData = {
            "vnp_Version": "2.1.0",
            "vnp_Command": "pay",
            "vnp_TmnCode": VNPAY_TMN_CODE,
            "vnp_Amount": str(amount * 100),
            "vnp_CurrCode": "VND",
            "vnp_TxnRef": order_id,
            "vnp_OrderInfo": order_desc,
            "vnp_OrderType": order_type,
            "vnp_Locale": language if language else "vn",
            "vnp_CreateDate": datetime.now().strftime("%Y%m%d%H%M%S"),
            "vnp_IpAddr": get_client_ip(),
            "vnp_ReturnUrl": VNPAY_RETURN_URL
            + f"?payment_id={order_id}&amount={amount}&seat_ids={seat_ids}&guest_ids={guest_ids}&flight_id={flight_id}&staff_id={staff_id}",
        }

        if bank_code:
            vnp.requestData["vnp_BankCode"] = bank_code

        payment_url = vnp.get_payment_url(VNPAY_PAYMENT_URL, VNPAY_HASH_SECRET_KEY)
        print("🔗 Payment URL:", payment_url)
        return redirect(payment_url)


@app.route("/payment_return")
def payment_return():
    inputData = request.args
    vnp = vnpay()
    vnp.responseData = inputData.to_dict()
    if vnp.validate_response(VNPAY_HASH_SECRET_KEY):
        if inputData.get("vnp_ResponseCode") == "00":
            result = "Thành công"
            # dao.update_payment_status(payment_id, "success")
            # Lưu thông tin thanh toán vào cơ sở dữ liệu
            # dao.save_payment_info(inputData.to_dict())

            payment_id = request.args.get("payment_id")
            amount = request.args.get("amount")
            seat_ids = request.args.get("seat_ids")
            guest_ids = request.args.get("guest_ids")
            flight_id = request.args.get("flight_id")
            staff_id = request.args.get("staff_id")
            if staff_id and staff_id != "None":
                staff_id = int(staff_id)
            else:
                staff_id = None
            payment = dao.get_payment_by_id(payment_id)
            print("Payment ID:", payment_id)
            print("Amount:", amount)
            print("Seat ID:", seat_ids)
            print("Guest ID:", guest_ids)
            print("Flight ID:", flight_id)
            print("SATFFFID", staff_id)
            if staff_id is not None:
                dao.add_ticket(
                    seat_ids=seat_ids,
                    payment_id=payment_id,
                    guest_ids=guest_ids,
                    flight_id=flight_id,
                    staff_id=staff_id,
                )
            else:
                dao.add_ticket(
                    seat_ids=seat_ids,
                    payment_id=payment_id,
                    guest_ids=guest_ids,
                    flight_id=flight_id,
                )
            dao.update_status_seat(seat_ids=seat_ids)
            dao.update_payment_status(payment_id)
            # gửi email cho khách hàng
            guest_infos = dao.get_guest_info_by_ids(ids=guest_ids)
            ticket_infos = dao.get_ticket_by_guest_ids(guest_ids=guest_ids)
            seat_info_ids = [s["seat_id"] for s in ticket_infos]
            seat_infos = dao.get_seat_info_by_ids(seat_ids=seat_info_ids)
            ticket_class_info_ids = [t["ticket_class_id"] for t in seat_infos]
            ticket_class_info = dao.get_ticket_class_info_by_ids(
                ticket_class_ids=ticket_class_info_ids
            )
            flight_info = dao.get_route_by_flight_id(flight_id=flight_id)
            start_airport = flight_info["start_airport"]
            end_airport = flight_info["end_airport"]
            flight_name = f"{start_airport} - {end_airport}"
            print("Guest Info:", guest_infos)
            print("Ticket Info:", ticket_infos)
            print("Seat Info:", seat_infos)
            print("Ticket Class Info:", ticket_class_info)
            print("start_airport:", start_airport)
            print("end_airport:", end_airport)
            dao.send_ticket_email_plain(
                flight_name=flight_name,
                guest_infos=guest_infos,
                ticket_infos=ticket_infos,
                seat_infos=seat_infos,
                ticket_class_infos=ticket_class_info,
            )
        else:
            result = "Lỗi"
    else:
        result = "Sai checksum"

    return render_template(
        "payment/payment_return.html",
        title="Kết quả thanh toán",
        amount=amount,
        payment=payment,
        result=result,
        data=inputData,
        datetime=datetime,
    )


@app.route("/sign-in", methods=["GET", "POST"])
def sign_in():
    err_msg = None
    next_page = request.args.get("next")  # từ URL ?next=/passenger
    if request.method == "POST":
        # Nếu là POST, lấy next từ form
        next_page = request.form.get("next")
    if current_user.is_authenticated:
        return redirect(next_page or "/")
    if request.method.__eq__("POST"):
        email = request.form.get("email")
        password = request.form.get("password")
        user = dao.authenticate(email, password)
        if user:
            login_user(user)
            flash("Đăng nhập thành công!", "success")
            return redirect(next_page or "/")
        else:
            flash("Tài khoản hoặc mật khẩu không hợp lệ!", "error")

    return render_template("account/sign-in.html")


@app.route("/login-admin", methods=["post"])
def login_admin_process():
    email = request.form.get("email")
    password = request.form.get("password")

    user = dao.authenticate(email=email, password=password)
    if user:
        login_user(user)
        msg = "Đăng nhập thành công!"
        flash(msg, "success")  # 👈 thêm thông báo lỗi vào flash
    else:
        msg = "Tài khoản hoặc mật khẩu không khớp!"
        flash(msg, "danger")  # 👈 thêm thông báo lỗi vào flash
    return redirect("/admin")


@login.user_loader
def get_user(user_id):
    return dao.get_user_by_id(user_id)


@app.route("/logout")
def logout_my_user():
    logout_user()
    return redirect("/")


@app.route("/sign-up", methods=["GET", "POST"])
def sign_up():
    data = request.form.to_dict()  # Lưu dữ liệu nhập vào
    if request.method.__eq__("POST"):
        last_name = request.form.get("last_name")
        first_name = request.form.get("first_name")
        email = request.form.get("email")
        password = request.form.get("password")
        phone = request.form.get("phone")
        cccd = request.form.get("cccd")
        country = request.form.get("country")

        if dao.check_exists_email(email=email):
            flash("Tài khoản email đã tồn tại!", "error")
        else:
            dao.add_user(last_name, first_name, email, password, phone, cccd, country)
            flash("Đăng ký thành công!", "success")
            return redirect(url_for("sign_in"))
    return render_template("account/sign-up.html", data={})


if __name__ == "__main__":
    app.run(debug=True)
