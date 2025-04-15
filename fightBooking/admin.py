import hashlib
from flask import flash, redirect, request, session, url_for
from flask_admin.form import SecureForm
from flask_wtf import FlaskForm
from flask_admin import Admin, BaseView, expose, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from wtforms import IntegerField, StringField, SelectField
from wtforms_sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, NumberRange
import dao
import string
from models import (
    Airline,
    UserEnum,
    User,
    Ticket,
    TicketClass,
    Plane,
    FlightSeat,
    Seat,
    Flight,
    PartFlight,
    Route,
    Airport,
    UserEnum,
)

from configs import app, db
from flask_login import logout_user, current_user
from datetime import datetime, timedelta


class AdminAuthenticatedView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == UserEnum.ADMIN


class StaffScheduleAuthenticatedView(ModelView):
    def is_accessible(self):
        return (
            current_user.is_authenticated
            and current_user.role == UserEnum.STAFF_FLIGHT_SCHEDULE
        )


class StaffAuthenticatedView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == UserEnum.STAFF


class MyAirlineView(AdminAuthenticatedView):
    column_list = ["id", "name", "start_route", "end_route"]
    column_filters = ["name"]
    column_searchable_list = ["name"]


class MyUserView(AdminAuthenticatedView):
    column_list = ["id", "first_name", "last_name", "email", "role"]
    column_filters = ["first_name", "last_name", "email", "role"]

    def on_model_change(self, form, model, is_created):
        """
        Tự động hash mật khẩu bằng MD5 nếu là mật khẩu plain.
        """
        plain_password = form.password.data
        if plain_password and len(plain_password) < 32:
            model.password = hashlib.md5(plain_password.encode("utf-8")).hexdigest()


class MyTicketView(AdminAuthenticatedView):
    column_list = [
        "id",
        "seat_id",
        "guest_id",
        "staff_id",
        "payment_id",
        "flight_id",
    ]
    column_filters = ["seat_id", "guest_id"]
    column_searchable_list = ["seat_id", "guest_id"]


class MyTicketClassView(AdminAuthenticatedView):
    column_list = ["id", "name", "price", "seats"]
    column_filters = ["name", "price"]
    column_searchable_list = ["name", "price"]


class MyPlaneView(AdminAuthenticatedView):
    column_list = ["id", "name", "airline_id", "seats", "flights"]
    column_filters = ["name"]


class SeatForm(FlaskForm):
    """
    ✅ Form tùy chỉnh để tự động tạo ghế ngay khi nhập số lượng.
    """

    plane_id = QuerySelectField(
        "Máy bay",
        query_factory=lambda: Plane.query.all(),  # Truy vấn danh sách máy bay
        get_label="name",  # Hiển thị tên máy bay
        allow_blank=False,
        validators=[DataRequired()],
    )

    ticket_class_id = QuerySelectField(
        "Hạng vé",
        query_factory=lambda: TicketClass.query.all(),  # Truy vấn danh sách hạng vé
        get_label="name",  # Hiển thị tên hạng vé
        allow_blank=False,
        validators=[DataRequired()],
    )
    num_seats = IntegerField(
        "Số lượng ghế",
        validators=[DataRequired(), NumberRange(min=1, message="Số ghế phải >= 1")],
        default=1,
    )
    start_row = SelectField(
        "Hàng bắt đầu",
        choices=[(ch, ch) for ch in string.ascii_uppercase[:10]],  # A-J
        default="A",
    )
    status = SelectField(
        "Trạng thái",
        choices=[("available", "Còn trống"), ("booked", "Đã đặt")],
        default="available",
    )
    name_seat = StringField("Tên ghế (Tự động tạo)", render_kw={"readonly": True})


class MySeatView(AdminAuthenticatedView):
    """
    ✅ Flask-Admin View với form tùy chỉnh để tự động tạo ghế trước khi insert vào DB.
    """

    form_base_class = SecureForm
    form = SeatForm  # Gán form tùy chỉnh vào Flask-Admin

    column_list = [
        "id",
        "name_seat",
        "plane_id",
        "ticket_class_id",
        "tickets",
        "status",
    ]
    form_excluded_columns = ["tickets"]  # Không hiển thị danh sách vé
    column_formatters = {
        "plane_id": lambda v, c, m, p: m.plane.name if m.plane else "Không có",
        "ticket_class_id": lambda v, c, m, p: (
            m.ticket_class.name if m.ticket_class else "Không có"
        ),
    }

    def create_model(self, form):
        """
        ✅ Tạo ghế ngay từ form, bảo đảm `name_seat` không NULL.
        """
        session = self.session
        num_seats = form.num_seats.data
        start_row = form.start_row.data

        created_seats = []
        for i in range(num_seats):
            row_letter = chr(ord(start_row) + (i // 10))  # A -> B -> C...
            seat_number = (i % 10) + 1
            seat_name = f"{row_letter}-{seat_number}"

            new_seat = self.model(
                name_seat=seat_name,
                plane_id=form.plane_id.data.id,
                ticket_class_id=form.ticket_class_id.data.id,
            )
            session.add(new_seat)
            created_seats.append(seat_name)

        session.commit()
        flash(f"🎫 Đã tạo {num_seats} ghế mới: {', '.join(created_seats)}", "success")

        return None  # Không cho Flask-Admin insert thêm bản ghi trống


class MyFlightView(AdminAuthenticatedView):
    column_list = [
        "id",
        "start_time",
        "end_time",
        "status",
        "plane_name",
        "route_id",
        "tickets",
        "parts",
    ]
    column_filters = [
        "start_time",
        "end_time",
    ]
    column_searchable_list = [
        "start_time",
        "end_time",
    ]
    column_formatters = {
        "plane_name": lambda v, c, m, p: (m.plane.name if m.plane else "N/A"),
    }

    def create_model(self, form):
        # print(form.__dict__)
        route_id = form.route.data.id if form.route.data else None
        plane_id = form.plane.data.id if form.plane.data else None
        start_time = form.start_time.data
        end_time = form.end_time.data

        if not all([route_id, plane_id, start_time, end_time]):
            flash("❌ Vui lòng nhập đầy đủ thông tin chuyến bay!", "danger")
            return None

        # Kiểm tra trùng
        existing = (
            self.session.query(Flight)
            .filter_by(
                route_id=route_id,
                plane_id=plane_id,
                start_time=start_time,
                end_time=end_time,
            )
            .first()
        )

        if existing:
            flash(
                "❌ Chuyến bay đã tồn tại với tuyến, thời gian và máy bay này!",
                "danger",
            )
            return None

        return super().create_model(form)

    def update_model(self, form, model):
        route_id = form.route.data.id if form.route.data else None
        plane_id = form.plane.data.id if form.plane.data else None
        start_time = form.start_time.data
        end_time = form.end_time.data

        if not all([route_id, plane_id, start_time, end_time]):
            flash("❌ Vui lòng nhập đầy đủ thông tin chuyến bay!", "danger")
            return False

        # Kiểm tra trùng thông tin với các chuyến bay khác (trừ chính nó)
        existing = (
            self.session.query(Flight)
            .filter(
                Flight.route_id == route_id,
                Flight.plane_id == plane_id,
                Flight.start_time == start_time,
                Flight.end_time == end_time,
                Flight.id != model.id,  # Không so sánh với chính nó
            )
            .first()
        )

        if existing:
            flash("❌ Thông tin chỉnh sửa bị trùng với một chuyến bay khác!", "danger")
            return False

        return super().update_model(form, model)

    def delete_model(self, model):
        # Nếu chuyến bay đang hoạt động thì không cho xóa
        if model.status.name not in ["CANCELLED"]:
            flash("❌ Không thể xóa chuyến bay đang hoạt động!", "danger")
            return False

        return super().delete_model(model)


class MyRouteView(AdminAuthenticatedView):
    column_list = [
        "id",
        "start_airport_name",
        "end_airport_name",
        "flights",
        "part_flights",
    ]
    column_filters = ["start_airport_ref", "end_airport_ref"]
    column_searchable_list = ["start_airport", "end_airport"]
    column_formatters = {
        "start_airport_name": lambda v, c, m, p: (
            m.start_airport_ref.name if m.start_airport_ref else "N/A"
        ),
        "end_airport_name": lambda v, c, m, p: (
            m.end_airport_ref.name if m.end_airport_ref else "N/A"
        ),
    }

    def create_model(self, form):
        # Lấy ID sân bay đi và đến từ form
        start_airport = form.start_airport_ref.data
        end_airport = form.end_airport_ref.data

        # Check nếu đã có tuyến tồn tại
        existing_route = (
            self.session.query(Route)
            .filter_by(start_airport=start_airport.id, end_airport=end_airport.id)
            .first()
        )

        if existing_route:
            flash("❌ Tuyến bay đã tồn tại!", "danger")
            return None  # Không tạo mới

        return super().create_model(form)  # Tiếp tục tạo nếu chưa tồn tại

    def update_model(self, form, model):
        start_airport = form.start_airport_ref.data
        end_airport = form.end_airport_ref.data

        # Check nếu chỉnh sửa trùng tuyến khác
        existing_route = (
            self.session.query(Route)
            .filter_by(start_airport=start_airport.id, end_airport=end_airport.id)
            .filter(Route.id != model.id)  # Tránh trùng chính nó
            .first()
        )

        if existing_route:
            flash("❌ Tuyến bay sau khi chỉnh sửa đã trùng với tuyến khác!", "danger")
            return False  # Không cho cập nhật

        return super().update_model(form, model)

    def delete_model(self, model):
        if model.flights and len(model.flights) > 0:
            flash(
                "❌ Không thể xóa! Tuyến bay đang được sử dụng trong các chuyến bay.",
                "danger",
            )
            return False  # Ngăn việc xóa

        return super().delete_model(model)


class MyFlightSeatView(AdminAuthenticatedView):
    column_list = ["id", "flight_id", "seat_id", "status"]


class MyAirportView(AdminAuthenticatedView):
    column_list = ["id", "name", "location", "country"]
    column_filters = ["name", "location"]
    column_searchable_list = ["name", "location"]


class CreateScheduleFlightView(BaseView):
    @expose("/", methods=["GET", "POST"])
    def index(self):
        if request.method == "POST":
            try:
                start_airport = request.form.get("start_airport")
                end_airport = request.form.get("end_airport")
                start_time = request.form.get("start_time")
                end_time = request.form.get("end_time")
                plane_id = request.form.get("plane_id")
                rule = dao.get_rule()

                if (
                    not start_airport
                    or not end_airport
                    or not start_time
                    or not end_time
                    or not plane_id
                ):
                    flash("❌ Vui lòng nhập đầy đủ thông tin!", "danger")
                    raise Exception("Missing fields")

                if start_airport == end_airport:
                    flash("❌ Sân bay đi và đến không thể giống nhau!", "danger")
                    raise Exception("Start and end airport must be different")

                start_dt = datetime.strptime(start_time, "%Y-%m-%dT%H:%M")
                end_dt = datetime.strptime(end_time, "%Y-%m-%dT%H:%M")

                if start_dt >= end_dt:
                    flash(
                        "❌ Thời gian khởi hành phải trước thời gian hạ cánh!", "danger"
                    )
                    raise Exception("Invalid flight time")

                if end_dt - start_dt < timedelta(minutes=rule.min_flight_duration):
                    flash(
                        f"❌ Thời gian bay tối thiểu phải là {rule.min_flight_duration}phút!",
                        "danger",
                    )
                    raise Exception("Flight duration too short")

                route = dao.add_route(
                    start_airport=start_airport, end_airport=end_airport
                )
                if not route:
                    raise Exception("Không thể tạo tuyến bay!")

                flight = dao.add_flight(
                    start_time=start_time,
                    end_time=end_time,
                    route_id=route.id,
                    plane_id=plane_id,
                )
                if not flight:
                    raise Exception("Không thể tạo chuyến bay!")

                dao.create_flight_seats(flight.id, plane_id)

                layover_airports = set()
                layover_count = 0

                if "layovers[1][airport_id]" in request.form:
                    layover_count = len(request.form.getlist("layovers[1][airport_id]"))

                    if layover_count > rule.max_layover_airports:
                        flash(
                            f"❌ Tối đa chỉ được {rule.max_layover_airports} sân bay trung gian!",
                            "danger",
                        )
                        raise Exception("Too many layovers")

                    for i in range(layover_count):
                        airport_id = request.form.getlist(
                            f"layovers[{i+1}][airport_id]"
                        )[0]
                        arrival_time = request.form.getlist(
                            f"layovers[{i+1}][arrival]"
                        )[0]
                        departure_time = request.form.getlist(
                            f"layovers[{i+1}][departure]"
                        )[0]

                        if airport_id in [start_airport, end_airport]:
                            flash(
                                "❌ Sân bay trung gian không được trùng sân bay đi/đến!",
                                "danger",
                            )
                            raise Exception("Layover airport conflict")

                        if airport_id in layover_airports:
                            flash(
                                "❌ Không được chọn 2 sân bay trung gian giống nhau!",
                                "danger",
                            )
                            raise Exception("Duplicate layover airport")

                        layover_airports.add(airport_id)

                        arr_dt = datetime.strptime(arrival_time, "%Y-%m-%dT%H:%M")
                        dep_dt = datetime.strptime(departure_time, "%Y-%m-%dT%H:%M")

                        if arr_dt >= dep_dt:
                            flash(
                                "❌ Giờ đến phải trước giờ đi ở sân bay trung gian!",
                                "danger",
                            )
                            raise Exception("Invalid layover time")

                        stop_duration = dep_dt - arr_dt
                        if stop_duration < timedelta(
                            minutes=rule.min_layover_duration
                        ) or stop_duration > timedelta(
                            minutes=rule.max_layover_duration
                        ):
                            flash(
                                f"❌ Thời gian dừng phải từ {rule.min_layover_duration}-{rule.max_layover_duration} phút!",
                                "danger",
                            )
                            raise Exception("Invalid layover duration")

                        if arr_dt < start_dt or dep_dt > end_dt:
                            flash(
                                "❌ Sân bay trung gian phải nằm trong khoảng thời gian chuyến bay!",
                                "danger",
                            )
                            raise Exception("Layover outside flight time")

                        dao.add_part_flight(
                            start_time=arrival_time,
                            end_time=departure_time,
                            route_id=route.id,
                            flight_id=flight.id,
                        )

                flash("✅ Tạo chuyến bay thành công!", "success")
                return redirect("/admin/create_flight")

            except Exception as e:
                flash("❌Lỗi khi tạo chuyến bay!", "danger")
                print("❌ Lỗi khi tạo chuyến bay:", str(e))

        airports = dao.get_departure_airport()
        planes = dao.get_all_plane()
        ticket_classes = dao.get_all_ticket_classes()

        return self.render(
            "admin/create_flight.html",
            airports=airports,
            planes=planes,
            ticket_classes=ticket_classes,
            admin_base_template=self.admin.base_template,
        )

    def is_accessible(self):
        return current_user.is_authenticated and current_user.role in [
            UserEnum.ADMIN,
            UserEnum.STAFF_FLIGHT_SCHEDULE,
        ]


class ReportView(BaseView):
    @expose("/", methods=["GET", "POST"])
    def index(self):

        selected_month = request.form.get("month") or datetime.now().strftime("%Y-%m")
        data, total_revenue, selected_month = dao.get_monthly_revenue_report(
            selected_month
        )

        return self.render(
            "admin/report.html",
            data=data,
            month=selected_month,
            total_revenue=total_revenue,
        )

    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == UserEnum.ADMIN


class SellTicketView(BaseView):
    @expose("/", methods=["GET", "POST"])
    def index(self):
        if request.method == "POST":
            last_name = request.form.get("last_name")
            departure = request.form.get("departure")
            arrival = request.form.get("arrival")
            first_name = request.form.get("first_name")
            email = request.form.get("email")
            phone = request.form.get("phone")
            cccd = request.form.get("cccd")
            country = request.form.get("country")
            seat_id = request.form.get("seat_id")
            flight_id = request.form.get("flight_id")
            ticket_class_id = request.form.get("ticket_class_id")
            payment_method = request.form.get("payment_method")
            staff_id = None

            # check thoi gian ban
            rule = dao.get_rule()
            flight = dao.get_flight_by_id(flight_id)
            now = datetime.now()
            if flight.start_time - now < timedelta(hours=rule.latest_booking_hour):
                flash(
                    f"❌ Không thể bán vé vì còn dưới {rule.latest_booking_hour} giờ trước khi khởi hành!",
                    "danger",
                )
                return redirect("/admin/sellticketview/")
            if payment_method == "CASH":
                guest = dao.add_guest_by_some_info(
                    first_name=first_name,
                    last_name=last_name,
                    cccd=cccd,
                    email=email,
                    phone=phone,
                    country=country,
                )
                price = dao.get_price_by_ticket_class(ticket_class_id=ticket_class_id)
                payment = dao.add_payment(price)
                dao.update_status_seat(seat_ids=seat_id)
                if current_user.role in [
                    UserEnum.STAFF,
                    UserEnum.STAFF_FLIGHT_SCHEDULE,
                ]:
                    staff_id = current_user.id
                    dao.add_ticket(
                        seat_ids=seat_id,
                        payment_id=payment.id,
                        guest_ids=guest.id,
                        flight_id=flight_id,
                        staff_id=staff_id,
                    )
                else:
                    dao.add_ticket(
                        seat_ids=seat_id,
                        payment_id=payment.id,
                        guest_ids=guest.id,
                        flight_id=flight_id,
                    )
                dao.update_payment_status(payment.id)
                # email
                flight_name = f"{departure} - {arrival}"
                ticket_class = dao.get_ticket_class_info_by_ids(
                    ticket_class_ids=ticket_class_id
                )
                seat_info = dao.get_seat_info_by_ids(seat_ids=seat_id)
                dao.send_ticket_email(
                    guest=guest,
                    seat=seat_info,
                    ticket_class=ticket_class,
                    flight_name=flight_name,
                )
                flash("🧾Đã bán vé thành công hành khách!", "success")
                return redirect("/admin/sellticketview/")
            if payment_method == "CARD":
                # 1. Tạo khách hàng (nhưng chưa lưu ticket)
                guest = dao.add_guest_by_some_info(
                    first_name=first_name,
                    last_name=last_name,
                    cccd=cccd,
                    email=email,
                    phone=phone,
                    country=country,
                )

                # 2. Tạo payment (giá tiền)
                price = dao.get_price_by_ticket_class(ticket_class_id=ticket_class_id)
                payment = dao.add_payment(price)
                # Xóa session cũ nếu có
                session.pop("data", None)
                session.pop("passenger_info", None)
                # 3. Lưu session tạm (dữ liệu thanh toán)
                session["data"] = {
                    "flight_id": flight_id,
                    "ticket_class_id": ticket_class_id,
                    "price": price,
                }
                session["passenger_info"] = [
                    {
                        "first_name": first_name,
                        "last_name": last_name,
                        "cccd": cccd,
                        "email": email,
                        "phone": phone,
                        "country": country,
                    }
                ]
                if current_user.role in [
                    UserEnum.STAFF,
                    UserEnum.STAFF_FLIGHT_SCHEDULE,
                ]:
                    staff_id = current_user.id

                # 4. Chuyển hướng qua trang thanh toán (truyền thêm seat_id)
                return redirect(
                    url_for(
                        "payment",
                        payment_id=payment.id,
                        seat_ids=seat_id,
                        staff_id=staff_id,
                    )
                )
            return redirect("/admin/sellticketview/")
        airports = dao.get_all_airports()
        return self.render(
            "admin/sell_ticket.html",
            airports=airports,
        )

    def is_accessible(self):
        return current_user.is_authenticated and current_user.role in [
            UserEnum.STAFF,
            UserEnum.STAFF_FLIGHT_SCHEDULE,
        ]


class LogoutAdmin(BaseView):
    @expose("/")
    def index(self):
        logout_user()
        return redirect("/admin")

    def is_accessible(self):
        return current_user.is_authenticated  # ✅ Chỉ hiển thị nếu đã đăng nhập


class MyAdminIndexView(AdminIndexView):
    @expose("/")
    def index(self):
        return self.render("admin/index.html")


admin = Admin(
    app=app,
    name="AirNava System",
    template_mode="bootstrap4",
    index_view=MyAdminIndexView(),
)

admin.add_view(MyUserView(User, db.session))
admin.add_view(MyAirlineView(Airline, db.session))
admin.add_view(MyTicketView(Ticket, db.session))
admin.add_view(MyTicketClassView(TicketClass, db.session))
admin.add_view(MyPlaneView(Plane, db.session))
admin.add_view(MySeatView(Seat, db.session))
admin.add_view(MyFlightView(Flight, db.session))
admin.add_view(MyRouteView(Route, db.session))
admin.add_view(MyAirportView(Airport, db.session))
admin.add_view(MyFlightSeatView(FlightSeat, db.session))
admin.add_view(
    CreateScheduleFlightView(name="Tạo chuyến bay", endpoint="create_flight")
)
admin.add_view(SellTicketView(name="Bán vé", endpoint="sellticketview"))
admin.add_view(ReportView(name="Thống kê"))
admin.add_view(LogoutAdmin(name="Đăng xuất"))
