import hashlib
import urllib.parse
import json
from extensions import db
from configs import app
from models import (
    User,
    Route,
    Airport,
    Flight,
    PartFlight,
    Seat,
    TicketClass,
    Plane,
    Ticket,
    Payment,
    Guest,
    SystemRule,
    FlightSeat,
    StatusEnum,
    StatusSeat,
)
from sqlalchemy import distinct, cast, Date
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
import string
from math import ceil
from sqlalchemy import extract, func
from sqlalchemy.orm import aliased


def send_ticket_email(guest, seat, ticket_class, flight_name):
    from_email = "nodpou7@gmail.com"
    password = "crht wsrb brrx tqbu"

    subject = "✈️ Vé máy bay điện tử"

    body = f"""\
            VÉ CHUYẾN BAY

            Chuyến bay: {flight_name}
            Hành khách: {guest.first_name}
            CMND/CCCD: {guest.cccd}
            Điện thoại: {guest.phone}
            Hạng vé: {ticket_class[0]['name'] if ticket_class else 'Không rõ'}
            Số ghế: {seat[0]['name'] if seat else 'Không rõ'}
            Giá tiền: {ticket_class[0]['price'] if ticket_class else 'Không rõ'} VND
        """

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = guest.email

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(from_email, password)
            server.send_message(msg)
            print(f"📩 Đã gửi vé máy bay đến {guest.email}")
    except Exception as e:
        print(f"❌ Gửi email đến {guest.email} thất bại:", str(e))


def send_ticket_email_plain(
    guest_infos, ticket_infos, seat_infos, ticket_class_infos, flight_name
):
    from_email = "nodpou7@gmail.com"
    password = "crht wsrb brrx tqbu"

    subject = "✈️ Vé máy bay điện tử"

    for guest, ticket in zip(guest_infos, ticket_infos):
        # Tìm seat tương ứng với ticket
        seat = next((s for s in seat_infos if s["id"] == ticket["seat_id"]), None)
        # Tìm hạng vé tương ứng
        ticket_class = (
            next(
                (
                    tc
                    for tc in ticket_class_infos
                    if tc["id"] == seat["ticket_class_id"]
                ),
                None,
            )
            if seat
            else None
        )

        body = f"""\
            VÉ CHUYẾN BAY

            Chuyến bay: {flight_name}
            Hành khách: {guest['first_name']}
            CMND/CCCD: {guest['cccd']}
            Điện thoại: {guest['phone']}
            Hạng vé: {ticket_class['name'] if ticket_class else 'Không rõ'}
            Số ghế: {seat['name'] if seat else 'Không rõ'}
            Giá tiền: {ticket_class['price'] if ticket_class else 'Không rõ'} VND
"""

        msg = MIMEText(body, "plain", "utf-8")
        msg["Subject"] = subject
        msg["From"] = from_email
        msg["To"] = guest["email"]

        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(from_email, password)
                server.send_message(msg)
                print(f"📩 Đã gửi vé máy bay đến {guest['email']}")
        except Exception as e:
            print(f"❌ Gửi email đến {guest['email']} thất bại:", str(e))


def get_route_by_flight_id(flight_id):
    flight = Flight.query.get(flight_id)
    print("Thông tin", flight)
    if flight:
        route = flight.route
        print("Route", route.id)
        if route:
            start_airport = route.start_airport
            end_airport = route.end_airport
            start_airport_name = Airport.query.get(start_airport)
            end_airport_name = Airport.query.get(end_airport)

            return {
                "start_airport": start_airport_name.name,
                "end_airport": end_airport_name.name,
            }
    return None


def get_guest_info_by_ids(ids):
    if isinstance(ids, str):
        ids = json.loads(ids)  # Chuyển chuỗi JSON thành list
    elif isinstance(ids, int):
        ids = [ids]  # Chuyển số thành list

    guests = Guest.query.filter(Guest.id.in_(ids)).all()
    result = []

    for guest in guests:
        result.append(
            {
                "id": guest.id,
                "first_name": guest.first_name,
                "phone": guest.phone,
                "email": guest.email,
                "cccd": guest.cccd,
            }
        )

    return result


def get_flight_by_id(flight_id):
    return Flight.query.get(flight_id)


def get_all_ticket_classes():
    return TicketClass.query.all()


def create_flight_seats(flight_id, plane_id):
    seats = Seat.query.filter_by(plane_id=plane_id).all()

    for seat in seats:
        flight_seat = FlightSeat(
            flight_id=flight_id, seat_id=seat.id, status=StatusSeat.AVAILABLE
        )
        db.session.add(flight_seat)

    db.session.commit()


def get_ticket_classes_by_plane(plane_id):
    seats = Seat.query.filter(Seat.plane_id == plane_id).all()
    ticket_classes = {seat.ticket_class for seat in seats}  # loại trùng

    filtered = []
    for tc in ticket_classes:
        if "RANK 1" in tc.name or "RANK 2" in tc.name:
            filtered.append(tc)

    return sorted(filtered, key=lambda x: x.id)


def get_rule():
    rule = SystemRule.query.first()
    return rule


def get_all_seats_by_flight(flight_id, ticket_class_name=None):
    # Truy vấn join từ FlightSeat → Seat → Plane → TicketClass
    query = (
        db.session.query(FlightSeat, Seat, TicketClass)
        .join(Seat, FlightSeat.seat_id == Seat.id)
        .join(TicketClass, Seat.ticket_class_id == TicketClass.id)
        .filter(FlightSeat.flight_id == flight_id)
    )

    if ticket_class_name:
        query = query.filter(TicketClass.name == ticket_class_name)

    results = query.all()

    seat_data = []
    for flight_seat, seat, ticket_class in results:
        seat_data.append(
            {
                "id": seat.id,
                "name": seat.name_seat,
                "class": ticket_class.name,
                "price": ticket_class.price,
                "status": flight_seat.status.name,  # status lấy từ bảng flight_seat
            }
        )
    return seat_data


def get_price_by_ticket_class(ticket_class_id=None, ticket_class_name=None):
    ticket_class = None
    if ticket_class_name:
        ticket_class = TicketClass.query.filter_by(name=ticket_class_name).first()
    if ticket_class_id:
        ticket_class = TicketClass.query.filter_by(id=ticket_class_id).first()
    if ticket_class:
        return ticket_class.price
    return None


def get_flight(destination, arrival, check_in_date):
    now = datetime.now()
    rule = get_rule()
    print(rule.latest_booking_hour)
    min_start_time = now + timedelta(hours=rule.latest_booking_hour)

    if destination and arrival and check_in_date:
        flights = Flight.query.filter(
            Flight.route.has(
                (Route.start_airport_ref.has(name=destination))
                & (Route.end_airport_ref.has(name=arrival))
            ),
            cast(Flight.start_time, Date) == check_in_date,
            Flight.start_time >= min_start_time,  # ✅ Bỏ chuyến sắp bay
        ).all()
        return flights

    return []  # Nếu thiếu thông tin, trả về danh sách rỗng


def get_payment_by_id(payment_id):
    payment = Payment.query.get(payment_id)
    return payment


def get_departure_airport():
    airports = (
        Airport.query.with_entities(Airport.id, Airport.name, Airport.location)
        .distinct()
        .all()
    )
    return airports


def get_all_plane():
    planes = Plane.query.with_entities(Plane.id, Plane.name).distinct().all()
    return planes


def add_part_flight(start_time, end_time, flight_id, route_id):
    part_flight = PartFlight(
        start_time=start_time,
        end_time=end_time,
        flight_id=flight_id,
        route_id=route_id,
    )
    db.session.add(part_flight)
    db.session.commit()
    return part_flight


def add_flight(start_time, end_time, plane_id, route_id):
    flight = Flight(
        start_time=start_time,
        end_time=end_time,
        plane_id=plane_id,
        route_id=route_id,
    )
    db.session.add(flight)
    db.session.commit()
    return flight


def add_route(start_airport, end_airport):
    # Kiểm tra nếu đã tồn tại route tương tự
    route = Route.query.filter_by(
        start_airport=start_airport, end_airport=end_airport
    ).first()

    if route:
        return route  # Nếu đã tồn tại thì trả về luôn

    # Nếu chưa có, thì tạo mới
    route = Route(start_airport=start_airport, end_airport=end_airport)
    db.session.add(route)
    db.session.commit()
    return route


def add_payment(price):
    payment = Payment(price=price, payment_status=StatusEnum.PENDING)
    db.session.add(payment)
    db.session.commit()
    return payment


def get_ticket_by_guest_ids(guest_ids):
    if isinstance(guest_ids, str):
        guest_ids = json.loads(guest_ids)  # Chuyển chuỗi JSON thành list
    elif isinstance(guest_ids, int):
        guest_ids = [guest_ids]  # Chuyển số thành list
    tickets = Ticket.query.filter(Ticket.guest_id.in_(guest_ids)).all()
    ticket_data = []
    for ticket in tickets:
        ticket_data.append(
            {
                "id": ticket.id,
                "seat_id": ticket.seat_id,
            }
        )
    return ticket_data


def get_seat_info_by_ids(seat_ids):
    # Nếu là string (ví dụ: "304"), ép thành list [304]
    if isinstance(seat_ids, str):
        seat_ids = [int(seat_ids)]
    elif isinstance(seat_ids, int):
        seat_ids = [seat_ids]

    seats = Seat.query.filter(Seat.id.in_(seat_ids)).all()

    seat_info = []
    for seat in seats:
        seat_info.append(
            {
                "id": seat.id,
                "name": seat.name_seat,
                "ticket_class_id": seat.ticket_class_id,
            }
        )
    return seat_info


def get_ticket_class_info_by_ids(ticket_class_ids):
    # Nếu là string (chẳng hạn '1'), chuyển thành list [1]
    if isinstance(ticket_class_ids, str):
        ticket_class_ids = [int(ticket_class_ids)]
    elif isinstance(ticket_class_ids, int):
        ticket_class_ids = [ticket_class_ids]

    ticket_classes = TicketClass.query.filter(
        TicketClass.id.in_(ticket_class_ids)
    ).all()

    result = []
    for t in ticket_classes:
        result.append({"id": t.id, "name": t.name, "price": t.price})
    return result


def add_guest(info):
    if isinstance(info, str):
        info = json.loads(info)

    guests = []

    # ✅ Nếu là dict dạng {"1": {...}, "2": {...}}
    if isinstance(info, dict):
        for guest_key, guest_data in info.items():
            guest = Guest(
                last_name=guest_data.get("last_name"),
                first_name=guest_data.get("first_name"),
                date_of_birth=guest_data.get("date_of_birth"),
                email=guest_data.get("email"),
                phone=guest_data.get("phone"),
                cccd=guest_data.get("cccd"),
                country=guest_data.get("country"),
            )
            db.session.add(guest)
            guests.append(guest)

    # ✅ Nếu là list gồm các dict
    elif isinstance(info, list):
        for guest_data in info:
            guest = Guest(
                last_name=guest_data.get("last_name"),
                first_name=guest_data.get("first_name"),
                date_of_birth=guest_data.get("date_of_birth"),
                email=guest_data.get("email"),
                phone=guest_data.get("phone"),
                cccd=guest_data.get("cccd"),
                country=guest_data.get("country"),
            )
            db.session.add(guest)
            guests.append(guest)

    else:
        raise ValueError("❌ Dữ liệu hành khách không hợp lệ!")

    db.session.commit()
    return guests


def add_guest_by_some_info(first_name, last_name, cccd, email, phone, country):
    guest = Guest(
        last_name=last_name,
        first_name=first_name,
        cccd=cccd,
        phone=phone,
        email=email,
        country=country,
    )
    db.session.add(guest)
    db.session.commit()

    return guest


def update_payment_status(payment_id):
    payment = Payment.query.get(payment_id)
    if not payment:
        raise ValueError(f" Payment ID {payment_id} không tồn tại.")
    payment.payment_status = StatusEnum.SUCCESS
    db.session.commit()


def update_status_seat(seat_ids):
    if isinstance(seat_ids, (str, int)):
        seat_ids = [seat_ids]

    for sid in seat_ids:
        seat = FlightSeat.query.filter_by(seat_id=sid).first()
        if not seat:
            raise ValueError(f"Seat ID {sid} không tồn tại.")
        seat.status = StatusSeat.BOOKED

    db.session.commit()


def add_ticket(seat_ids, payment_id, flight_id, guest_ids=None, staff_id=None):
    # ✅ Xử lý seat_ids (int, str -> list)
    if isinstance(seat_ids, str):
        seat_ids = [int(sid) for sid in seat_ids.split(",") if sid.strip()]
    elif isinstance(seat_ids, int):
        seat_ids = [seat_ids]

    # ✅ Xử lý guest_ids (int, str, JSON string, list)
    if guest_ids is not None:
        if isinstance(guest_ids, str):
            try:
                guest_ids = json.loads(guest_ids)  # "[14, 15]"
                if isinstance(guest_ids, int):
                    guest_ids = [guest_ids]
            except json.JSONDecodeError:
                guest_ids = [int(g.strip()) for g in guest_ids.split(",") if g.strip()]
        elif isinstance(guest_ids, int):
            guest_ids = [guest_ids]
        elif not isinstance(guest_ids, list):
            guest_ids = []

    tickets_created = []

    for idx, seat_id in enumerate(seat_ids):
        # Tránh trùng vé
        existing = (
            db.session.query(Ticket)
            .filter_by(payment_id=payment_id, seat_id=seat_id)
            .first()
        )
        if existing:
            print(f"⚠️ Ticket cho seat {seat_id} đã tồn tại.")
            tickets_created.append(existing.id)
            continue

        ticket = Ticket(seat_id=seat_id, payment_id=payment_id, flight_id=flight_id)

        if guest_ids and idx < len(guest_ids):
            ticket.guest_id = guest_ids[idx]

        if staff_id is not None:
            ticket.staff_id = staff_id

        db.session.add(ticket)
        db.session.flush()
        tickets_created.append(ticket.id)

    db.session.commit()
    return tickets_created


def add_user(last_name, first_name, email, password, phone, cccd, country):
    password = str(hashlib.md5(password.encode("utf-8")).hexdigest())
    cccd = hashlib.md5(cccd.encode()).hexdigest()
    new_user = User(
        last_name=last_name,
        first_name=first_name,
        email=email,
        password=password,
        phone=phone,
        cccd=cccd,
        country=country,
    )
    db.session.add(new_user)
    db.session.commit()


def get_user_by_id(user_id):
    return User.query.get(user_id)


def check_exists_email(email):
    if User.query.filter_by(email=email).first():
        return True
    return False


def get_all_airports():
    return Airport.query.all()


def search_flights_by_route_and_date(departure_name, arrival_name, flight_date_str):
    try:
        flight_date = datetime.strptime(flight_date_str, "%Y-%m-%d").date()

        flights = (
            Flight.query.join(Route)
            .filter(
                Route.start_airport_ref.has(name=departure_name),
                Route.end_airport_ref.has(name=arrival_name),
                cast(Flight.start_time, Date) == flight_date,
            )
            .all()
        )
        return flights
    except Exception as e:
        print("❌ Lỗi khi tìm chuyến bay:", e)
        return []


def get_available_seats_by_flight_id(flight_id):
    flight = Flight.query.get(flight_id)
    if not flight:
        return []

    # Lấy danh sách seat_id đã được đặt cho chuyến bay này
    booked_seat_ids = db.session.query(Ticket.seat_id).filter_by(flight_id=flight.id)

    # Trả về các seat thuộc plane của flight, chưa được dùng trong flight này
    return Seat.query.filter(
        Seat.plane_id == flight.plane_id, ~Seat.id.in_(booked_seat_ids)
    ).all()


def create_flight_seats_from_plane(flight_id):
    flight = Flight.query.get(flight_id)
    if not flight:
        raise Exception("Không tìm thấy chuyến bay!")

    plane_seats = Seat.query.filter_by(plane_id=flight.plane_id).all()
    flight_seats = []

    for seat in plane_seats:
        fs = FlightSeat(
            flight_id=flight_id, seat_id=seat.id, status=StatusSeat.AVAILABLE
        )
        flight_seats.append(fs)

    db.session.add_all(flight_seats)
    db.session.commit()
    print(f"✅ Tạo {len(flight_seats)} ghế cho chuyến bay ID {flight_id}")


def get_all_flights():
    return Flight.query.all()


def get_monthly_revenue_report(selected_month=None):
    if not selected_month:
        selected_month = datetime.now().strftime("%Y-%m")

    year, month = map(int, selected_month.split("-"))

    StartAirport = aliased(Airport)
    EndAirport = aliased(Airport)

    data = (
        db.session.query(
            Route.id,
            StartAirport.name.label("start_name"),
            EndAirport.name.label("end_name"),
            func.sum(TicketClass.price).label("revenue"),
            func.count(Flight.id).label("flight_count"),
        )
        .join(Flight, Flight.route_id == Route.id)
        .join(Ticket, Ticket.flight_id == Flight.id)
        .join(Seat, Seat.id == Ticket.seat_id)
        .join(TicketClass, TicketClass.id == Seat.ticket_class_id)
        .join(StartAirport, Route.start_airport == StartAirport.id)
        .join(EndAirport, Route.end_airport == EndAirport.id)
        .filter(extract("year", Flight.start_time) == year)
        .filter(extract("month", Flight.start_time) == month)
        .group_by(Route.id, StartAirport.name, EndAirport.name)
        .all()
    )

    total_revenue = sum([d.revenue for d in data]) if data else 0
    return data, total_revenue, selected_month


def authenticate(email, password):
    password = str(hashlib.md5(password.encode("utf-8")).hexdigest())
    user = User.query.filter(
        User.email.__eq__(email), User.password.__eq__(password)
    ).first()
    return user


if __name__ == "__main__":
    with app.app_context():
        pass
        # guest = get_guest_info_by_ids([24, 25])
        # print(guest)
        # ticket = get_ticket_by_guest_ids([24, 25])
        # print(ticket)
        # seat = get_seat_info_by_ids([21, 20])
        # print(seat)

        # ticket_class = get_ticket_class_info_by_ids([1])
        # print(ticket_class)
