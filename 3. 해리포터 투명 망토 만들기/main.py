# 사용할 패키지
import cv2 # 이미지 처리 패키지
import numpy as np # 행렬 연산 패키지
import time, argparse

parser = argparse.ArgumentParser()
parser.add_argument('--video', help='Input video path')
args = parser.parse_args()

cap = cv2.VideoCapture(args.video if args.video else 0)
# 비디오를 불러오거나 비디오가 없으면 웹캠을 사용

time.sleep(3)
# 카메라가 켜지는 데에 시간이 소요 되므로 3초간 멈춘 후 웹캠을 키도록 설정

# Grap background image from first part of the video
# ** 중요 **
# : 동영상 앞부분 5초 정도는 사람이 없는 배경만 촬영
for i in range(60):
  ret, background = cap.read() # 사람이 없는 60프레임 동안에는 background에 이미지 미리 저장해줌

# 결과값을 기록하기 위한 코드
# (동영상으로 저장됨)
fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
out = cv2.VideoWriter('videos/output3.mp4', fourcc, cap.get(cv2.CAP_PROP_FPS), (background.shape[1], background.shape[0]))
out2 = cv2.VideoWriter('videos/original3.mp4', fourcc, cap.get(cv2.CAP_PROP_FPS), (background.shape[1], background.shape[0]))

# 동영상이나 웹캠에서 프레임 읽어옴
while(cap.isOpened()):
  ret, img = cap.read() # 한 프레임씩 읽어옴, img에 저장
  if not ret:
    break
  
  # Convert the color space from BGR to HSV
  # 컬러 시스템 변경, 이유: BGR보다 HSV가 색을 표현하는 방식이 사람이 인식하는 색깔의 수치와 가장 비슷함
  # (ex - 사람이 빨간색이라고 느끼는 것을 HSV가 빨간색이라고 잘 표현할 수 있음)
  #H: Hue 색조 / S: Saturation 채도 / V: Value 명도(밝기)
  hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

  # # Generate mask to detect red color
  # # 범위를 한 번에 쓸 수 없어서 나눠서 작성
  # # 빨간색 범위: 0-10, 170-180
  # lower_red = np.array([0, 120, 70])
  # upper_red = np.array([10, 255, 255])
  # mask1 = cv2.inRange(hsv, lower_red, upper_red)
  # # cv2.inRange(): 범위 안에 해당하는 값들로 마스크 생성
  # # lower_red 와 upper_red 사이의 값들은 255로 만들고, 그 이외의 것들은 0으로 만들어라
  #
  # lower_red = np.array([170, 120, 70])
  # upper_red = np.array([180, 255, 255])
  # mask2 = cv2.inRange(hsv, lower_red, upper_red)
  #
  # mask1 = mask1 + mask2

  # 흰색 투명하게 만들기
  lower_white = np.array([0, 0, 110])
  upper_white = np.array([180, 255, 255])
  mask1 = cv2.inRange(hsv, lower_white, upper_white)

  # # 검정색 투명하게 만들기
  # lower_black = np.array([0, 0, 0])
  # upper_black = np.array([255, 255, 80])
  # mask1 = cv2.inRange(hsv, lower_black, upper_black)

  '''
  # Refining the mask corresponding to the detected red color
  https://docs.opencv.org/3.0-beta/doc/py_tutorials/py_imgproc/py_morphological_ops/py_morphological_ops.html
  '''

  # 마스크를 색깔로만 뽑으면 노이즈 발생, 비어있는 곳 발생 --> 이런 것들을 정제해주는 함수
  # Remove noise
  mask_cloak = cv2.morphologyEx(mask1, op=cv2.MORPH_OPEN, kernel=np.ones((3, 3), np.uint8), iterations=2)
  # cv2.morphologyEx: 점 같이 생긴 노이즈 제거해줌
  mask_cloak = cv2.dilate(mask_cloak, kernel=np.ones((3, 3), np.uint8), iterations=1)
  # cv2.dilate: 픽셀을 약간 늘려줌
  mask_bg = cv2.bitwise_not(mask_cloak)

  cv2.imshow('mask_cloak', mask_cloak)

  # Generate the final output
  res1 = cv2.bitwise_and(background, background, mask=mask_cloak)
  # cv2.bitwise_and: 두 개의 행렬이 0이 아닌 것만 통과됨(즉, 마스크 영역만 남음(And 연산))
  # background에서 segmetation할 mask만큼 뽑아냄
  res2 = cv2.bitwise_and(img, img, mask=mask_bg)
  # 카메라나 비디오로부터 들어온 이미지를 마스크를 제외한 만큼 가져옴
  # (background에서 마스크를 제외한 만큼 가져옴)
  result = cv2.addWeighted(src1=res1, alpha=1, src2=res2, beta=1, gamma=0)
  # cv2.addWeighted: 두 개의 이미지를 합친다
  # res1과 res2를 합쳐서 result에 저장

  cv2.imshow('res2', res2) # 이미지를 윈도우에 띄우기

  # cv2.imshow('ori', img)
  cv2.imshow('result', result)
  out.write(result)
  out2.write(img)

  if cv2.waitKey(1) == ord('q'):
    break

out.release()
out2.release()
cap.release()
