import json
from extensions import db
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, Enum
from sqlalchemy.orm import relationship
from enum import Enum as RoleEnum
from flask_login import UserMixin
from datetime import datetime


class UserEnum(RoleEnum):
    CUSTOMER = 1
    STAFF = 2
    STAFF_FLIGHT_SCHEDULE = 3
    ADMIN = 4


class StatusEnum(RoleEnum):
    FAILED = 0
    SUCCESS = 1
    PENDING = 2


class StatusSeat(RoleEnum):
    AVAILABLE = 0
    BOOKED = 1


class MethodEnum(RoleEnum):
    CASH = 1
    CARD = 2


class StatusFlightEnum(RoleEnum):
    CANCELLED = 0
    ONTIME = 1
    DELAYED = 2


class Base(db.Model):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)
    # created_at = Column(DateTime, server_default=db.func.now())
    # updated_at = Column(
    #     DateTime, server_default=db.func.now(), server_onupdate=db.func.now()
    # )


class Guest(Base):
    last_name = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    date_of_birth = Column(DateTime, nullable=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(255), nullable=True)
    cccd = Column(String(255), nullable=True)
    country = Column(String(255), nullable=True)
    tickets = relationship("Ticket", backref="guest", lazy=True)


class User(Base, UserMixin):
    last_name = Column(String(255), nullable=False)
    first_name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    phone = Column(String(255), nullable=False)
    cccd = Column(String(255), nullable=False)
    country = Column(String(255), nullable=False)
    role = Column(Enum(UserEnum), default=UserEnum.CUSTOMER)

    # tickets = relationship(
    #     "Ticket", foreign_keys="[Ticket.user_id]", backref="customer", lazy=True
    # )
    # managed_tickets = relationship(
    #     "Ticket", foreign_keys="[Ticket.staff_id]", backref="staff", lazy=True
    # )
    managed_tickets = relationship("Ticket", backref="user", lazy=True)

    def __str__(self):
        return self.first_name + " " + self.last_name


class Ticket(Base):
    seat_id = Column(Integer, ForeignKey("seat.id"), nullable=False, unique=True)
    # user_id = Column(Integer, ForeignKey("user.id"), nullable=True)
    guest_id = Column(Integer, ForeignKey("guest.id"), nullable=True)
    staff_id = Column(Integer, ForeignKey("user.id"), nullable=True)
    payment_id = Column(Integer, ForeignKey("payment.id"), nullable=False)
    flight_id = Column(Integer, ForeignKey("flight.id"), nullable=False)


class Payment(Base):
    price = Column(Float, nullable=False)
    payment_date = Column(DateTime, default=datetime.now, nullable=False)
    payment_status = Column(Enum(StatusEnum), default=StatusEnum.PENDING)
    payment_method = Column(Enum(MethodEnum), default=MethodEnum.CARD)
    tickets = relationship("Ticket", backref="payment", lazy=True)


class Seat(Base):
    name_seat = Column(String(255), nullable=False)
    plane_id = Column(
        Integer, ForeignKey("plane.id", ondelete="CASCADE"), nullable=False
    )
    ticket_class_id = Column(Integer, ForeignKey("ticket_class.id"), nullable=False)
    # Thêm relationship
    tickets = relationship("Ticket", backref="seat", uselist=False, lazy=True)
    flight_seats = relationship("FlightSeat", backref="seat", lazy=True)

    def __str__(self):
        return self.name_seat


class TicketClass(Base):
    name = Column(String(255), nullable=False)
    price = Column(Float, nullable=False)
    seats = relationship("Seat", backref="ticket_class", lazy=True)

    def __str__(self):
        return self.name + " " + str(self.price)


class Plane(Base):
    name = Column(String(255), nullable=False, unique=True)
    airline_id = Column(
        Integer, ForeignKey("airline.id", ondelete="CASCADE"), nullable=False
    )
    seats = relationship("Seat", backref="plane", cascade="all,delete", lazy=True)
    flights = relationship("Flight", backref="plane", cascade="all,delete", lazy=True)

    def __str__(self):
        return self.name


class FlightSeat(Base):
    flight_id = Column(Integer, ForeignKey("flight.id"), nullable=False)
    seat_id = Column(Integer, ForeignKey("seat.id"), nullable=False)
    status = Column(Enum(StatusSeat), default=StatusSeat.AVAILABLE, nullable=False)


class Airline(Base):
    name = Column(String(255), nullable=False)
    planes = relationship("Plane", backref="airline", cascade="all,delete", lazy=True)

    def __str__(self):
        return self.name


class Flight(Base):
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    status = Column(
        Enum(StatusFlightEnum), default=StatusFlightEnum.ONTIME, nullable=False
    )  # Thay đổi ở đây
    plane_id = Column(
        Integer, ForeignKey("plane.id", ondelete="CASCADE"), nullable=False
    )
    route_id = Column(Integer, ForeignKey("route.id"), nullable=False)
    flight_seats = relationship("FlightSeat", backref="flight", lazy=True)
    tickets = relationship("Ticket", backref="flight", lazy=True)
    parts = relationship(
        "PartFlight", backref="flight", cascade="all,delete", lazy=True
    )


class PartFlight(Base):
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    status = Column(
        Enum(StatusFlightEnum), default=StatusFlightEnum.ONTIME, nullable=False
    )
    route_id = Column(Integer, ForeignKey("route.id"), nullable=False)
    flight_id = Column(
        Integer, ForeignKey("flight.id", ondelete="CASCADE"), nullable=False
    )

    def __str__(self):
        return self.name


class Route(Base):
    start_airport = Column(
        Integer, ForeignKey("airport.id", ondelete="CASCADE"), nullable=False
    )
    end_airport = Column(
        Integer, ForeignKey("airport.id", ondelete="CASCADE"), nullable=False
    )
    flights = relationship("Flight", backref="route", lazy=True)
    part_flights = relationship("PartFlight", backref="route", lazy=True)

    def __str__(self):
        return f"{self.start_airport_ref.name} - {self.end_airport_ref.name}"


class Airport(Base):
    name = Column(String(255), nullable=False)
    location = Column(String(255), nullable=False)
    country = Column(String(255), nullable=False, default="Việt Nam")
    start_route = relationship(
        "Route",
        foreign_keys=[Route.start_airport],
        backref="start_airport_ref",
        cascade="all,delete",
        lazy=True,
    )
    end_route = relationship(
        "Route",
        foreign_keys=[Route.end_airport],
        backref="end_airport_ref",
        cascade="all,delete",
        lazy=True,
    )

    def __str__(self):
        return self.name

    # departures = relationship(
    #     "Route", foreign_keys="[Route.start_airport]", backref="departures_airport"
    # )
    # arrivals = relationship(
    #     "Route", foreign_keys="[Route.end_airport]", backref="arrivals_airport"
    # )


class SystemRule(Base):

    # Số lượng sân bay trung gian tối đa
    max_layover_airports = Column(Integer, default=2)

    # Thời gian bay tối thiểu (phút)
    min_flight_duration = Column(Integer, default=30)

    # Thời gian dừng tại sân bay trung gian (phút)
    min_layover_duration = Column(Integer, default=20)
    max_layover_duration = Column(Integer, default=30)

    # Số lượng hạng vé tối đa
    max_ticket_classes = Column(Integer, default=3)

    # Thời gian giới hạn bán vé (giờ trước khi bay)
    latest_booking_hour = Column(Integer, default=4)


# if __name__ == "__main__":
#     with app.app_context():
#         db.create_all()
#         # db.drop_all()
#         # db.create_all()
#         # db.session.add(User(firstname="Tien", lastname="Nguyen", email="
#         db.session.commit()
