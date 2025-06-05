import socket

# 서버 주소 및 포트 설정
HOST = '0.0.0.0'   # 모든 IP로부터의 접속 허용
PORT = 12345       # 사용할 포트 번호

def main():
    # 1. 소켓 생성 (socket syscall 발생)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("[*] 소켓 생성 완료")

    # 2. 소켓에 주소 바인딩 (bind syscall 발생)
    server_socket.bind((HOST, PORT))
    print(f"[*] 바인딩 완료: {HOST}:{PORT}")

    # 3. 연결 대기 (listen syscall 발생)
    server_socket.listen(5)
    print("[*] 연결 대기 중...")

    while True:
        # 4. 클라이언트 접속 수락 (accept syscall 발생)
        conn, addr = server_socket.accept()
        print(f"[+] 클라이언트 연결됨: {addr}")

        try:
            # 5. 데이터 수신 (recv syscall 발생)
            data = conn.recv(1024).decode('utf-8').strip()
            print(f"[>] 받은 데이터: {data}")

            if not data.islower():
                response = "오류: 소문자만 입력하세요."
            else:
                ascii_codes = [str(ord(ch)) for ch in data]
                response = ' '.join(ascii_codes)

            # 6. 데이터 전송 (send syscall 발생)
            conn.sendall(response.encode('utf-8'))
            print(f"[<] 전송한 응답: {response}")

        except Exception as e:
            print(f"[!] 오류 발생: {e}")
        finally:
            # 7. 연결 종료 (close syscall 발생)
            conn.close()
            print("[*] 연결 종료")

if __name__ == "__main__":
    main()
