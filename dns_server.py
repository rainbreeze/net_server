import socket
import pymysql  # pip install pymysql

# DB 설정
DB_CONFIG = {
    'host': 'localhost',
    'user': 'jihoon',
    'password': '1234',
    'database': 'domain_db',
    'charset': 'utf8mb4'
}

# 서버 설정
HOST = '0.0.0.0'
PORT = 12345

def handle_client(conn):
    try:
        data = conn.recv(1024).decode('utf-8').strip()
        print(f"[>] 받은 데이터: {data}")

        if not data:
            response = "오류: 빈 데이터입니다."
            conn.sendall(response.encode('utf-8'))
            return

        # DB 연결
        db = pymysql.connect(**DB_CONFIG)
        cursor = db.cursor()

        parts = data.split()
        command = parts[0]

        if command == 'write' and len(parts) == 3:
            domain, ip = parts[1], parts[2]

            cursor.execute("SELECT * FROM domains WHERE domain=%s", (domain,))
            if cursor.fetchone():
                response = f"오류: 이미 등록된 도메인입니다. ({domain})"
            else:
                cursor.execute("INSERT INTO domains (domain, ip) VALUES (%s, %s)", (domain, ip))
                db.commit()
                response = f"성공: 도메인 등록 완료 ({domain} → {ip})"

        elif command == 'read' and len(parts) == 2:
            domain = parts[1]
            cursor.execute("SELECT ip FROM domains WHERE domain=%s", (domain,))
            result = cursor.fetchone()
            if result:
                response = f"{domain} → {result[0]}"
            else:
                response = f"오류: 해당 도메인이 존재하지 않습니다. ({domain})"

        else:
            response = "오류: 명령 형식이 잘못되었습니다.\n예시: write example.com 1.2.3.4 / read example.com"

        conn.sendall(response.encode('utf-8'))

    except Exception as e:
        error_msg = f"[!] 서버 오류: {str(e)}"
        print(error_msg)
        conn.sendall(error_msg.encode('utf-8'))
    finally:
        conn.close()
        print("[*] 연결 종료")


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    print(f"[*] 서버 시작: {HOST}:{PORT}")

    while True:
        conn, addr = server_socket.accept()
        print(f"[+] 클라이언트 연결됨: {addr}")
        handle_client(conn)


if __name__ == "__main__":
    main()
