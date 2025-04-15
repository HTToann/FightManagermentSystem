function goBack() {
    window.history.back(); // Quay lại trang trước đó
}
function goToPassengerPage() {
    const selectedFlightId = sessionStorage.getItem("selectedFlightId");
    const selectedRank = sessionStorage.getItem("selectedRank");
    const selectedPrice = sessionStorage.getItem("selectedPrice");

    if (!selectedFlightId || !selectedRank || !selectedPrice) {
        alert("Vui lòng chọn một hạng vé trước khi tiếp tục!");
        return;
    }

    window.location.href = "/passenger";
}