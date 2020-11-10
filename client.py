import socket
import pyzed.sl as sl
import cv2
import numpy as np


def get_image_by_zed_camera(zed):
    left_image = sl.Mat()
    right_image = sl.Mat()
    # Runtime parameters
    runtime_params = sl.RuntimeParameters()
    runtime_params.sensing_mode = sl.SENSING_MODE.SENSING_MODE_STANDARD
    while 1:
        if zed.grab(runtime_params) == sl.ERROR_CODE.SUCCESS:
            # print("=> Successfully retrieved image! ")
            zed.retrieve_image(left_image, sl.VIEW.VIEW_LEFT)
            zed.retrieve_image(right_image, sl.VIEW.VIEW_RIGHT)
            break
    left_img = left_image.get_data()
    right_img = right_image.get_data()

    return left_img, right_img

if __name__ == '__main__':
    # initialize socket
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_ip = '192.168.3.36'
    server_port = 30000
    global server_addr
    server_addr = (server_ip, server_port)
    # connect to server
    tcp_socket.connect(server_addr)

    # initialize camera
    init_params = sl.InitParameters()
    init_params.svo_real_time_mode = True
    init_params.coordinate_units = sl.UNIT.UNIT_MILLIMETER
    init_params.camera_resolution = sl.RESOLUTION.RESOLUTION_HD1080
    init_params.camera_fps = 30
    zed = sl.Camera()



    # start camera
    err = zed.open(init_params)
    if err != sl.ERROR_CODE.SUCCESS:
        print('Failed to open ZED!!!')
        zed.close()
        exit(1)
    else:
        print('=> starting to capture image ...')

    # capture image
    left_img, right_img = get_image_by_zed_camera(zed)
    bino_img = np.vstack((left_img, right_img))

    cv2.namedWindow('binocular image', cv2.WINDOW_GUI_EXPANDED)
    cv2.imshow('binocular image', bino_img)
    cv2.waitKey()

    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 30]

    result, imgencode = cv2.imencode('.jpg', bino_img, encode_param)

    # 建立矩阵
    data = np.array(imgencode)
    # 将numpy矩阵转换成字符形式，以便在网络中传输
    stringData = data.tostring()

    # 先发送要发送的数据的长度
    # ljust() 方法返回一个原字符串左对齐,并使用空格填充至指定长度的新字符串
    tcp_socket.send(str.encode(str(len(stringData)).ljust(16)));
    # 发送数据
    tcp_socket.send(stringData);
    # 读取服务器返回值
    receive = tcp_socket.recv(1024)
    if len(receive): print(str(receive, encoding='utf-8'))

    tcp_socket.close()