from flask import Blueprint, request, jsonify, session
from flask_restful import Resource, Api
from models import FlightSeat, StatusSeat, Seat, TicketClass, StatusEnum
import dao
import traceback

# Khai báo Blueprint cho API
search_bp = Blueprint("search", __name__)
payment_bp = Blueprint("payment_api", __name__)
search_detail_bp = Blueprint("search_detail", __name__)

api_search = Api(search_bp)
api_payment = Api(payment_bp)
api_search_detail = Api(search_detail_bp)


class SearchFlightAPI(Resource):
    def post(self):
        try:
            print("API Search Flight")
            data = request.get_json()  # Nhận JSON từ request
            destination = data.get("destination")
            arrival = data.get("arrival")
            check_in = data.get("check_in")
            check_out = data.get(
                "check_out", None
            )  # Có thể không cần check_out nếu là một chiều

            # Lấy danh sách chuyến bay từ DAO
            flights = dao.get_flight(destination, arrival, check_in)

            # Chuyển đổi dữ liệu flights thành JSON
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
            return jsonify({"success": True, "flights": flights_data})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500


class FlightDetailAPI(Resource):
    def get(self, flight_id):
        try:
            flight = dao.get_flight_by_id(flight_id)
            if not flight:
                return jsonify(
                    {"success": False, "error": "Không tìm thấy chuyến bay!"}
                )

            flight_data = {
                "id": flight.id,
                "plane_id": flight.plane.id,
                "plane_name": flight.plane.name,
                "start_time": flight.start_time.strftime("%Y-%m-%d %H:%M"),
                "end_time": flight.end_time.strftime("%Y-%m-%d %H:%M"),
                "route": {
                    "departure": flight.route.start_airport_ref.name,
                    "arrival": flight.route.end_airport_ref.name,
                },
                "status": flight.status.name,
            }
            # Danh sách hạng vé
            ticket_classes = dao.get_all_ticket_classes()
            ticket_class_data = [
                {"id": cls.id, "name": cls.name, "price": cls.price}
                for cls in ticket_classes
            ]
            # Lấy danh sách ghế trống từ bảng FlightSeat
            flight_seats = (
                FlightSeat.query.filter_by(
                    flight_id=flight_id, status=StatusSeat.AVAILABLE
                )
                .join(Seat)
                .join(TicketClass)
                .all()
            )
            seats_data = [
                {
                    "id": fs.seat.id,
                    "name_seat": fs.seat.name_seat,
                    "class_name": fs.seat.ticket_class.name,
                    "class_name_id": fs.seat.ticket_class.id,  # thêm id để lọc
                }
                for fs in flight_seats
            ]

            return jsonify(
                {
                    "success": True,
                    "flight": flight_data,
                    "ticket_classes": ticket_class_data,
                    "available_seats": seats_data,
                }
            )
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500


class CreatePaymentIdAPI(Resource):
    def get(self):
        try:
            data = session.get("data")
            if not data or "price" not in data:
                return jsonify({"error": "❌ Missing price in session"}), 400

            price = data["price"]
            payment = dao.add_payment(price=price)

            return jsonify({"payment_id": payment.id})
        except Exception as e:
            return jsonify({"error": str(e)}), 500


# Đăng ký API endpoint
api_search.add_resource(SearchFlightAPI, "/api/search")
# Đăng ký API endpoint
api_payment.add_resource(CreatePaymentIdAPI, "/api/create_payment_id")
api_search_detail.add_resource(FlightDetailAPI, "/api/flight_details/<int:flight_id>")
