document.addEventListener("DOMContentLoaded", function () {
    validateLoginForm();
    validateBookingForm();
});

// ✅ **Hàm kiểm tra đăng nhập (Email & Password)**
function validateLoginForm() {
    const emailInput = document.getElementById("email");
    const passwordInput = document.getElementById("password");
    const form = document.querySelector("form");

    if (!emailInput || !passwordInput || !form) return;

    function validateEmail(email) {
        const emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
        return emailPattern.test(email);
    }

    function validatePassword(password) {
        return password.length >= 6;
    }

    emailInput.addEventListener("input", function () {
        if (!validateEmail(emailInput.value)) {
            emailInput.classList.add("input-error");
        } else {
            emailInput.classList.remove("input-error");
        }
    });

    passwordInput.addEventListener("input", function () {
        if (!validatePassword(passwordInput.value)) {
            passwordInput.classList.add("input-error");
        } else {
            passwordInput.classList.remove("input-error");
        }
    });

    form.addEventListener("submit", function (event) {
        let isValid = true;
        let errorMessage = "";

        if (!validateEmail(emailInput.value)) {
            isValid = false;
            emailInput.classList.add("input-error");
            emailInput.value = "";
            emailInput.placeholder = "📧 Email không hợp lệ!";
            errorMessage += "📧 Email không hợp lệ!<br>";
        }

        if (!validatePassword(passwordInput.value)) {
            isValid = false;
            passwordInput.classList.add("input-error");
            passwordInput.value = "";
            passwordInput.placeholder = "🔑 Mật khẩu ít nhất 6 ký tự!";
            errorMessage += "🔑 Mật khẩu phải có ít nhất 6 ký tự!<br>";
        }

        if (!isValid) {
            event.preventDefault();
            Swal.fire({
                icon: "error",
                title: "Bạn ơi!",
                html: errorMessage,
                confirmButtonText: "OK",
                timer: 4000
            });
        }
    });
}

// ✅ **Hàm kiểm tra form đặt vé**
function validateBookingForm() {
    const form = document.querySelector(".flight-search-form"); // Đúng class

    if (!form) return; // Tránh lỗi nếu không tìm thấy form

    form.addEventListener("submit", function (event) {
        const destination = document.getElementById("destination")?.value;
        const arrival = document.getElementById("arrival")?.value;
        const checkIn = document.getElementById("check-in")?.value;
        const checkOut = document.getElementById("check-out")?.value;
        const guests = document.getElementById("guests")?.value;

        let errorMessage = "";

        if (!destination) errorMessage += "⚠️ Vui lòng chọn nơi đi.<br>";
        if (!arrival) errorMessage += "⚠️ Vui lòng chọn nơi đến.<br>";
        if (!checkIn) errorMessage += "⚠️ Vui lòng chọn ngày Check In.<br>";
        // if (!checkOut) errorMessage += "⚠️ Vui lòng chọn ngày Check Out.<br>";
        if (!guests || guests <= 0) errorMessage += "⚠️ Vui lòng nhập số lượng hành khách hợp lệ.<br>";

        if (errorMessage) {
            event.preventDefault(); // Ngăn không cho form gửi đi
            Swal.fire({
                icon: "warning",
                title: "Bạn ơi!",
                html: errorMessage,
                confirmButtonText: "OK"
            });
        }
    });
}