function handleSelectTicket(button) {
    const destination=button.getAttribute("destination")
    const arrival = button.getAttribute("arrival")
    const flightId = button.getAttribute("data-flight-id");
    const planeName = button.getAttribute("data-plane-name");
    const startTime = button.getAttribute("data-start-time");
    const endTime = button.getAttribute("data-end-time");
    const rank = button.getAttribute("data-rank");
    const price = button.getAttribute("data-price");
    const guestCount = document.getElementById("guestCount").value;    // const tax = button.getAttribute("data-tax");
    // const service = button.getAttribute("data-service");
    // Lưu dữ liệu vào sessionStorage
    sessionStorage.setItem("selectedFlightId", flightId);
    sessionStorage.setItem("selectedPlane", planeName);
    sessionStorage.setItem("selectedStartTime", startTime);
    sessionStorage.setItem("selectedEndTime", endTime);
    sessionStorage.setItem("selectedRank", rank);
    sessionStorage.setItem("selectedPrice", price);
    sessionStorage.setItem("selectedDestination", destination);
    sessionStorage.setItem("selectedArrival", arrival);
    sessionStorage.setItem("selectedGuestCount", guestCount); // ✅ lưu thêm
    // sessionStorage.setItem("selectedTax", tax);
    // sessionStorage.setItem("selectedService", service);
    // Làm nổi bật nút đã chọn
    document.querySelectorAll(".price-button").forEach(btn => btn.classList.remove("selected"));
    button.classList.add("selected");
}

// Lấy thông tin đã lưu và hiển thị trên trang passenger.html
function loadPassengerInfo() {
    console.log("Loading passenger info...");
    const destination = sessionStorage.getItem("selectedDestination")
    const arrival = sessionStorage.getItem("selectedArrival")
    const plane = sessionStorage.getItem("selectedPlane");
    const startTime = sessionStorage.getItem("selectedStartTime");
    const endTime = sessionStorage.getItem("selectedEndTime");
    const rank = sessionStorage.getItem("selectedRank");
    const price = sessionStorage.getItem("selectedPrice");
    // const tax = sessionStorage.getItem("selectedTax");
    // const service = sessionStorage.getItem("selectedService");
    const flightId = sessionStorage.getItem("selectedFlightId");
    const guestCount=sessionStorage.getItem("selectedGuestCount")
    console.log("Loaded data from sessionStorage:", { plane, startTime, endTime, rank, price,destination,arrival });

    if (!plane || !startTime || !endTime || !rank || !price || !destination || !arrival) {
        console.warn("⚠ Lỗi: Không có dữ liệu trong sessionStorage!");
        return;
    }
    const totalPrice = parseInt(price)*parseInt(guestCount);
    //  + parseInt(tax) + parseInt(service);
    if (plane && startTime && endTime && rank && price && destination && arrival) {
        document.getElementById("selected-plane").innerText = plane;
        document.getElementById("selected-destination").innerText = destination;
        document.getElementById("selected-arrival").innerText = arrival;
        document.getElementById("selected-start-time").innerText = startTime;
        document.getElementById("selected-end-time").innerText = endTime;
        document.getElementById("selected-rank").innerText = rank;
        document.getElementById("selected-price").innerText = parseInt(price).toLocaleString('vi-VN')+ " VND";
        // document.getElementById("selected-tax").innerText = parseInt(tax).toLocaleString('vi-VN') + " VND";
        // document.getElementById("selected-service").innerText = parseInt(service).toLocaleString('vi-VN') + " VND";
        document.getElementById("selected-total-price").innerText = totalPrice.toLocaleString('vi-VN') + " VND";
        document.getElementById("plane_name").value = plane;
        document.getElementById("rank").value = rank;
        document.getElementById("destination").value = destination;
        document.getElementById("arrival").value = arrival;
        document.getElementById("start_time").value = startTime;
        document.getElementById("end_time").value = endTime;
        document.getElementById("price").value = price;
        document.getElementById("flight_id").value = flightId;


    }
}