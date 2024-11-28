<?php
// Kết nối với cơ sở dữ liệu MySQL
$conn = new mysqli("localhost", "ouvuepwe_hieu", "Hieu1601", "ouvuepwe_membershiphp");

// Kiểm tra kết nối
if ($conn->connect_error) {
    die("Kết nối thất bại: " . $conn->connect_error);
}

// Lấy danh sách fullname từ bảng members
$sql = "SELECT fullname FROM members";
$result = $conn->query($sql);
?>
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chấm Công Nhận Diện Khuôn Mặt</title>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Roboto', sans-serif;
        }

        .container {
            margin: 20px auto;
            max-width: 800px;
        }

        .header {
            text-align: center;
            background: #3498db;
            color: #fff;
            padding: 10px;
            border-radius: 5px;
        }

        .content {
            margin-top: 20px;
        }

        button {
            padding: 10px 15px;
            background: #3498db;
            color: #fff;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            margin: 5px 0;
        }

        button:hover {
            background: #2980b9;
        }

        select, input {
            display: block;
            width: 100%;
            padding: 10px;
            margin: 10px 0;
            border-radius: 5px;
            border: 1px solid #ccc;
        }

        video, canvas {
            width: 100%;
            display: block;
            margin: 10px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Chấm Công Nhận Diện Khuôn Mặt</h1>
        </div>
        <div class="content">
            <!-- Nút Open API -->
            <button id="open-api">Kiểm Tra API</button>

            <!-- Form thêm nhân viên -->
            <h2>Thêm Nhân Viên Mới</h2>
            <select name="employee-name" required>
                <option value="">Chọn tên nhân viên</option>
                <?php
                if ($result->num_rows > 0) {
                    while ($row = $result->fetch_assoc()) {
                        echo "<option value='" . $row['fullname'] . "'>" . $row['fullname'] . "</option>";
                    }
                }
                ?>
            </select>
            <input type="text" id="employee-id" placeholder="Mã Nhân Viên" required>
            <button id="capture-photo">Chụp Ảnh</button>
            <p>Ảnh đã chụp: <span id="photo-count">0</span>/4</p>
            <button id="save-employee" disabled>Thêm Nhân Viên</button>

            <!-- Khu vực chấm công -->
            <h2>Chấm Công</h2>
            <video id="video" autoplay></video>
            <canvas id="canvas" style="display:none;"></canvas>
            <button id="check-in">Chấm Công Vào</button>
            <button id="check-out">Chấm Công Ra</button>
        </div>
    </div>

    <script src="script.js"></script>
</body>
</html>
