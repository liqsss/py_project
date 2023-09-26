import face_recognition
import cv2
import os
import copy

class FaceRecognition:
    def __init__(self):
        self.known_faces_dir = "known_faces"
        self.known_face_encodings = []
        self.known_face_names = []
        self.video_capture = cv2.VideoCapture(0)

    def  capImage(self):
        judge = self.video_capture.isOpened()
        i = 0
        while judge:
            ret, frame = self.video_capture.read()
            cv2.imshow("frame", frame)

            keyword = cv2.waitKey(1)
            i = i + 1
            name = "./known_faces/pic_" + str(i) + ".jpg"
            if keyword == ord('s'):  # 按s保存当前图片
                cv2.imwrite(name, frame)
            elif keyword == ord('q'):  # 按q退出
                break

    def readKnownImage(self):
        for file in os.listdir(self.known_faces_dir):
            image = face_recognition.load_image_file(os.path.join(self.known_faces_dir, file))
            encoding = face_recognition.face_encodings(image)[0]
            self.known_face_encodings.append(encoding)
            self.known_face_names.append(os.path.splitext(file)[0])

    def Recognition(self):
        while True:
            ret, frame = self.video_capture.read()
            if ret != True:
                print("相机数据读取失败")
                break
            rgb_frame = copy.deepcopy(frame[:, :, ::-1])  #将帧从BGR 转换为RGB,需要进行深拷贝，否则，编码出错
            # 写入文件，在读出来同样可以解决数据拷贝的问题
            # cv2.imwrite("./temp/new.jpg", rgb_frame) # 保存为图片
            # face_image = face_recognition.load_image_file("./temp/new.jpg") # 打开保存的图片，进行编码就可以
            face_locations = face_recognition.face_locations(rgb_frame)  #检测人脸位置
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)  #将人脸位置进行编码

            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)  #将当前人脸与已知人脸进行比较
                name = "Unknown"
                if True in matches:
                    first_match_index = matches.index(True)
                    name = self.known_face_names[first_match_index]

                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255), 1)
                if name != "Unknown":
                    return name
            cv2.imshow('Video', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.video_capture.release()  #释放摄像头资源
        cv2.destroyAllWindows()  #关闭视频窗口
        return name

def checkFace():
    face = FaceRecognition()
    face.readKnownImage()
    return face.Recognition()

if __name__ == "__main__":
    if checkFace() != "Unknown":
        print("验证成功")