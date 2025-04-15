async function submitSearchForm() {
  const form = document.getElementById("flightSearchForm");
  const destination = document.getElementById("destination").value;
  const arrival = document.getElementById("arrival").value;
  const checkIn = document.getElementById("check-in").value;
  const checkOut = document.getElementById("check-out").value;
  const guests = document.getElementById("guests").value;

  let errorMessage = "";
  if (!destination) errorMessage += "⚠️ Vui lòng chọn nơi đi.<br>";
  if (!arrival) errorMessage += "⚠️ Vui lòng chọn nơi đến.<br>";
  if (!checkIn) errorMessage += "⚠️ Vui lòng chọn ngày Check In.<br>";
  if (document.getElementById("round-trip").checked && !checkOut)
    errorMessage += "⚠️ Vui lòng chọn ngày Check Out.<br>";
  if (!guests || guests <= 0)
    errorMessage += "⚠️ Vui lòng nhập số lượng hành khách hợp lệ.<br>";

  if (errorMessage) {
    Swal.fire({
      icon: "warning",
      title: "Bạn ơi!",
      html: errorMessage,
      confirmButtonText: "OK"
    });
    return;
  }

  const data = {
    destination,
    arrival,
    check_in: checkIn,
    check_out: checkOut,
  };

  try {
    const response = await fetch("/api/search", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(data)
    });

    const result = await response.json();

    if (result.success) {
      sessionStorage.setItem("searchFlights", JSON.stringify(result.flights));
      sessionStorage.setItem("guest", guests);
    } else {
      Swal.fire("Lỗi", result.error, "error");
    }
  } catch (err) {
    console.error(err);
    Swal.fire("Lỗi", "Không thể kết nối server!", "error");
  }
}
