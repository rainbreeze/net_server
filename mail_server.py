import socket
import pymysql

DB_CONFIG = {
    'host': 'localhost',
    'user': 'jihoon',
    'password': '1234',
    'database': 'domain_db',
    'charset': 'utf8mb4'
}

HOST = '0.0.0.0'
PORT = 11000  # 테스트용 포트

def handle_client(conn):
    conn.sendall(b'+OK POP3 server ready\r\n')

    db = pymysql.connect(**DB_CONFIG)
    cursor = db.cursor()

    authenticated = False
    user = None
    deleted_ids = set()

    try:
        while True:
            data = conn.recv(1024).decode('utf-8').strip()
            if not data:
                break

            print(f"Received: {data}")
            parts = data.split()
            cmd = parts[0].upper()

            if cmd == 'USER' and len(parts) == 2:
                user = parts[1]
                # 사용자 존재 여부 확인
                cursor.execute("SELECT COUNT(*) FROM mails WHERE username=%s", (user,))
                if cursor.fetchone()[0] >= 0:  # 단순히 사용자 확인용 (메일이 없어도 OK)
                    conn.sendall(b'+OK User accepted\r\n')
                else:
                    conn.sendall(b'-ERR No such user\r\n')

            elif cmd == 'PASS' and len(parts) == 2:
                # 단순 비밀번호 확인 (실제로는 DB에 비밀번호 저장 후 확인)
                if user and parts[1] == 'password':
                    authenticated = True
                    conn.sendall(b'+OK Authenticated\r\n')
                else:
                    conn.sendall(b'-ERR Authentication failed\r\n')

            elif cmd == 'STAT' and authenticated:
                # 삭제 표시 안 된 메일 개수 및 총 크기 반환
                cursor.execute("SELECT COUNT(*), COALESCE(SUM(LENGTH(body)), 0) FROM mails WHERE username=%s AND is_deleted=FALSE", (user,))
                count, size = cursor.fetchone()
                conn.sendall(f'+OK {count} {size}\r\n'.encode())

            elif cmd == 'LIST' and authenticated:
                cursor.execute("SELECT id, LENGTH(body) FROM mails WHERE username=%s AND is_deleted=FALSE", (user,))
                mails = cursor.fetchall()
                response = f'+OK {len(mails)} messages\r\n'
                for mail_id, size in mails:
                    response += f'{mail_id} {size}\r\n'
                response += '.\r\n'
                conn.sendall(response.encode())

            elif cmd == 'RETR' and authenticated and len(parts) == 2:
                mail_id = parts[1]
                cursor.execute("SELECT body FROM mails WHERE id=%s AND username=%s AND is_deleted=FALSE", (mail_id, user))
                result = cursor.fetchone()
                if result:
                    body = result[0]
                    conn.sendall(f'+OK {len(body)} octets\r\n{body}\r\n.\r\n'.encode())
                else:
                    conn.sendall(b'-ERR No such message\r\n')

            elif cmd == 'DELE' and authenticated and len(parts) == 2:
                mail_id = parts[1]
                # 삭제 표시만 한다 (is_deleted = True)
                cursor.execute("UPDATE mails SET is_deleted=TRUE WHERE id=%s AND username=%s", (mail_id, user))
                if cursor.rowcount > 0:
                    db.commit()
                    deleted_ids.add(mail_id)
                    conn.sendall(b'+OK Message deleted\r\n')
                else:
                    conn.sendall(b'-ERR No such message\r\n')

            elif cmd == 'QUIT':
                # 실제 삭제 반영 후 종료
                # (여기선 이미 DB에 바로 반영했으니 추가 작업 없음)
                conn.sendall(b'+OK Goodbye\r\n')
                break

            else:
                conn.sendall(b'-ERR Unknown or unsupported command\r\n')

    except Exception as e:
        print(f"Error: {e}")
        conn.sendall(f'-ERR Server error: {str(e)}\r\n'.encode())
    finally:
        cursor.close()
        db.close()
        conn.close()
        print("Connection closed")

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    print(f"POP3-like server running on {HOST}:{PORT}")

    while True:
        conn, addr = server_socket.accept()
        print(f"Client connected: {addr}")
        handle_client(conn)

if __name__ == "__main__":
    main()
