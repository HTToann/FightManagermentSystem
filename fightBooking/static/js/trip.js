document.addEventListener("DOMContentLoaded", function () {
    const oneWay = document.getElementById("one-way");
    const roundTrip = document.getElementById("round-trip");
    const checkOutContainer = document.getElementById("check-out-container");

    function toggleCheckOut() {
        if (oneWay.checked) {
            checkOutContainer.classList.add("hidden");
        } else {
            checkOutContainer.classList.remove("hidden");
        }
    }

    oneWay.addEventListener("change", toggleCheckOut);
    roundTrip.addEventListener("change", toggleCheckOut);

    // Kiểm tra khi tải trang
    toggleCheckOut();
});