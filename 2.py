import socket

HOST = '127.0.0.1'  # 서버 IP 또는 localhost
PORT = 11000        # 서버 포트

def print_manual():
    manual = """
=== POP3-like 서버 명령어 메뉴얼 ===
USER <username>    : 사용자 이름 입력 (인증 시작)
PASS <password>    : 비밀번호 입력 (인증 완료)
STAT               : 메일함 상태 확인 (메일 개수 및 크기)
LIST               : 메일 목록 및 크기 확인
RETR <번호>        : 특정 메일 내용 읽기
DELE <번호>        : 특정 메일 삭제 표시
QUIT               : 연결 종료 (삭제 반영 후)

=== 추천 명령어 시나리오 ===
1) USER user1
2) PASS password
3) STAT
4) LIST
5) RETR 1
6) DELE 1
7) QUIT
"""
    print(manual)

def send_cmd(sock, cmd):
    print(f">>> {cmd}")
    sock.sendall((cmd + "\r\n").encode())
    data = sock.recv(4096).decode()
    print(data)
    return data

def main():
    print_manual()  # 실행 시 메뉴얼 출력

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((HOST, PORT))

        # 서버 환영 메시지 받기
        welcome = sock.recv(1024).decode()
        print(welcome)

        # 여기서 직접 명령어를 하나씩 입력해도 되고,
        # 자동으로 명령어 순서대로 보내도록 하려면 아래 주석 해제 후 사용하세요.

        # send_cmd(sock, "USER user1")
        # send_cmd(sock, "PASS password")
        # send_cmd(sock, "STAT")
        # send_cmd(sock, "LIST")
        # send_cmd(sock, "RETR 1")
        # send_cmd(sock, "DELE 1")
        # send_cmd(sock, "QUIT")

        # 또는 수동으로 명령어 입력받기 (무한 루프)
        while True:
            cmd = input("명령어 입력 (종료는 QUIT): ").strip()
            if not cmd:
                continue
            send_cmd(sock, cmd)
            if cmd.upper() == 'QUIT':
                break

if __name__ == "__main__":
    main()
