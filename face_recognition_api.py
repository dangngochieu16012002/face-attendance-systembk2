from flask import Flask, request, jsonify
from flask_cors import CORS
import face_recognition
import cv2
import numpy as np
import base64
import os
import mysql.connector
from datetime import datetime
from flask import Flask

app = Flask(__name__)

@app.route("/")
def index():
    return {"message": "Face Recognition Attendance API đang hoạt động!"}


# Đường dẫn tới thư mục chứa ảnh mẫu của nhân viên
EMPLOYEE_DIR = os.path.join(os.getcwd(), "employees")
TEMP_DIR = os.path.join(os.getcwd(), "temp_photos")


# Tạo thư mục tạm nếu không tồn tại
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)


# Tải dữ liệu khuôn mặt của nhân viên từ thư mục
def load_employee_faces():
    employee_faces = []
    employee_names = []

    for employee_folder in os.listdir(EMPLOYEE_DIR):
        employee_path = os.path.join(EMPLOYEE_DIR, employee_folder)
        if os.path.isdir(employee_path):
            for filename in os.listdir(employee_path):
                if filename.endswith(".jpg") or filename.endswith(".jpeg"):
                    image_path = os.path.join(employee_path, filename)
                    image = face_recognition.load_image_file(image_path)
                    encoding = face_recognition.face_encodings(image)

                    if encoding:
                        employee_faces.append(encoding[0])  # Lưu encoding đầu tiên
                        employee_names.append(employee_folder)  # Lấy tên thư mục làm tên nhân viên
                        print(f"Đã thêm khuôn mặt của {employee_folder} từ ảnh {filename}")
                    else:
                        print(f"Không tìm thấy encoding cho ảnh {filename} của {employee_folder}")

    return employee_faces, employee_names

# Tải dữ liệu khuôn mặt của nhân viên
employee_faces, employee_names = load_employee_faces()
print(f"Số lượng khuôn mặt đã tải: {len(employee_faces)}")

# Kết nối đến cơ sở dữ liệu MySQL và ghi nhật ký chấm công
def log_attendance(employee_name, attendance_type):
    conn = mysql.connector.connect(
        host="localhost:3306",
        user="ouvuepwe_hieu",
        password="Hieu1601",
        database="ouvuepwe_membershiphp"
    )
    cursor = conn.cursor()
    now = datetime.now()  # Lấy thời gian hiện tại
    timestamp = now.strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute("INSERT INTO attendance_logs (employee_name, attendance_type, timestamp) VALUES (%s, %s, %s)", (employee_name, attendance_type, timestamp))
    conn.commit()
    conn.close()

# Route nhận diện khuôn mặt
@app.route('/recognize', methods=['POST'])
def recognize():
    try:
        data = request.json
        img_data = data['image']  # Chuỗi base64 từ client
        attendance_type = data['type']

        # Kiểm tra nếu không có dữ liệu khuôn mặt nào đã tải
        if len(employee_faces) == 0:
            return jsonify({"status": "error", "message": "Không có dữ liệu khuôn mặt nhân viên. Kiểm tra thư mục employees."}), 500

        # Giải mã ảnh từ base64
        try:
            img_data = base64.b64decode(img_data)
            np_arr = np.frombuffer(img_data, np.uint8)
            img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

            if img is None:
                raise ValueError("Không thể giải mã ảnh từ chuỗi Base64")
        except Exception as e:
            return jsonify({"status": "fail", "message": f"Lỗi khi giải mã ảnh: {str(e)}"}), 400

        # Nhận diện khuôn mặt
        face_locations = face_recognition.face_locations(img)
        face_encodings = face_recognition.face_encodings(img, face_locations)

        if len(face_encodings) > 0:
            for face_encoding in face_encodings:
                matches = face_recognition.compare_faces(employee_faces, face_encoding)
                face_distances = face_recognition.face_distance(employee_faces, face_encoding)

                # Kiểm tra nếu có ít nhất một khuôn mặt để so sánh
                if face_distances.size > 0:
                    best_match_index = np.argmin(face_distances)
                    if matches[best_match_index]:
                        employee_name = employee_names[best_match_index]
                        log_attendance(employee_name, attendance_type)
                        return jsonify({
                            "status": "success",
                            "message": f"Nhân viên {employee_name} đã {'chấm công vào' if attendance_type == 'in' else 'chấm công ra'} thành công!"
                        }), 200

        return jsonify({"status": "fail", "message": "Không tìm thấy khuôn mặt hoặc không khớp với nhân viên nào."}), 404

    except Exception as e:
        return jsonify({"status": "error", "message": f"Lỗi: {str(e)}"}), 500

# Route thêm nhân viên
@app.route('/add-employee', methods=['POST'])
def add_employee():
    data = request.json
    name = data['name']
    employee_id = data['employeeId']
    photos = data['photos']

    # Tạo thư mục cho nhân viên nếu chưa tồn tại
    employee_folder = os.path.join(EMPLOYEE_DIR, name)
    if not os.path.exists(employee_folder):
        os.makedirs(employee_folder)

    # Lưu các ảnh đã chụp
    for i, photo in enumerate(photos):
        # Giải mã ảnh từ base64
        img_data = base64.b64decode(photo.split(',')[1])
        with open(os.path.join(employee_folder, f"{name}_{employee_id}_{i+1}.jpg"), "wb") as f:
            f.write(img_data)

    # Lưu thông tin nhân viên vào cơ sở dữ liệu
    conn = mysql.connector.connect(
        host="localhost:3306",
        user="ouvuepwe_hieu",
        password="Hieu1601",
        database="ouvuepwe_membershiphp"
    )
    cursor = conn.cursor()
    cursor.execute("INSERT INTO employees (name, employee_id) VALUES (%s, %s)", (name, employee_id))
    conn.commit()
    conn.close()

    return jsonify({"status": "success", "message": f"Nhân viên {name} đã được thêm thành công!"})

if __name__ == '__main__':
    app.run()

