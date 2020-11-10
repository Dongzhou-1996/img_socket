# server

import socket
import time
import numpy as np
import cv2


def recvall(sock, count):
    buf = b''  # buf是一个byte类型
    while count:
        # 接受TCP套接字的数据。数据以字符串形式返回，count指定要接收的最大数据量.
        newbuf = sock.recv(count)
        if not newbuf: return None
        buf += newbuf
        count -= len(newbuf)
    return buf

if __name__ == '__main__':

    server_ip = '192.168.3.36'
    server_port = 30000
    global server_addr
    server_addr = (server_ip, server_port)

    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # s = socket.socket()
    tcp_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    tcp_socket.bind(server_addr)
    tcp_socket.listen(5)

    client_socket, client_addr = tcp_socket.accept()
    print('got connected from', client_addr)

    start = time.time()  # 用于计算帧率信息
    length = recvall(client_socket, 16)  # 获得图片文件的长度,16代表获取长度
    stringData = recvall(client_socket, int(length))  # 根据获得的文件长度，获取图片文件
    data = np.frombuffer(stringData, np.uint8)  # 将获取到的字符流数据转换成1维数组
    dec_img = cv2.imdecode(data, cv2.IMREAD_COLOR)  # 将数组解码成图像
    end = time.time()
    seconds = end - start
    fps = 1.0 / seconds
    cv2.imwrite('test.jpg', dec_img)

    client_socket.send(bytes(str(fps), encoding='utf-8'))

    client_socket.close()
    tcp_socket.close()
