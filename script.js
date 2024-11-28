// Cấu hình URL của API
const API_URL = "https://hcrm-iuh.top/face-attendance-systembk2";

// Kiểm tra API
document.getElementById("open-api").addEventListener("click", () => {
    fetch(`${API_URL}/`)
        .then((response) => {
            if (response.ok) {
                alert("API đang hoạt động!");
            } else {
                alert("API không hoạt động!");
            }
        })
        .catch(() => {
            alert("Không thể kết nối đến API. Vui lòng kiểm tra lại.");
        });
});

let capturedPhotos = [];
let photoCount = 0;

// Khởi động camera
navigator.mediaDevices.getUserMedia({ video: true })
    .then((stream) => {
        const video = document.getElementById("video");
        video.srcObject = stream;
    })
    .catch((err) => {
        console.error("Không thể truy cập camera:", err);
    });

// Chụp ảnh và lưu ảnh
document.getElementById("capture-photo").addEventListener("click", () => {
    if (photoCount < 4) {
        const canvas = document.getElementById("canvas");
        const context = canvas.getContext("2d");
        const video = document.getElementById("video");

        context.drawImage(video, 0, 0, canvas.width, canvas.height);
        capturedPhotos.push(canvas.toDataURL("image/jpeg"));

        photoCount++;
        document.getElementById("photo-count").textContent = photoCount;

        if (photoCount === 4) {
            document.getElementById("save-employee").disabled = false;
        }
    } else {
        alert("Bạn đã chụp đủ 4 ảnh.");
    }
});

// Thêm nhân viên mới
document.getElementById("save-employee").addEventListener("click", () => {
    const employeeId = document.getElementById("employee-id").value;
    const employeeName = document.querySelector('select[name="employee-name"]').value;

    if (!employeeId || !employeeName) {
        alert("Vui lòng nhập đầy đủ thông tin.");
        return;
    }

    fetch(`${API_URL}/add-employee`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            name: employeeName,
            employeeId: employeeId,
            photos: capturedPhotos
        }),
    })
        .then((response) => response.json())
        .then((data) => {
            if (data.status === "success") {
                alert(data.message);
                resetForm();
            } else {
                alert("Lỗi: " + data.message);
            }
        })
        .catch((error) => console.error("Lỗi khi thêm nhân viên:", error));
});

// Reset form
function resetForm() {
    document.getElementById("employee-id").value = "";
    document.querySelector('select[name="employee-name"]').selectedIndex = 0;
    photoCount = 0;
    capturedPhotos = [];
    document.getElementById("photo-count").textContent = photoCount;
    document.getElementById("save-employee").disabled = true;
}

// Xử lý chấm công
document.getElementById("check-in").addEventListener("click", () => recognizeFace("in"));
document.getElementById("check-out").addEventListener("click", () => recognizeFace("out"));

async function recognizeFace(type) {
    const canvas = document.getElementById("canvas");
    const context = canvas.getContext("2d");
    const video = document.getElementById("video");

    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    const imageData = canvas.toDataURL("image/jpeg").split(",")[1];

    fetch(`${API_URL}/recognize`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ image: imageData, type: type }),
    })
        .then((response) => response.json())
        .then((data) => {
            alert(data.message);
        })
        .catch((error) => console.error("Lỗi khi chấm công:", error));
}
