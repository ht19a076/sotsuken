import cv2
import time
from datetime import datetime
import boto3
import json
import os
sns = boto3.client("sns")
SNS_TOPIC_ARN = os.environ["SNS_TOPIC_ARN"]
def main():
  
    
    base_path = "/home/pi/Videos/"
  
    cam = cv2.VideoCapture(-1)
  
    # カメラデバイスが見つからない場合、終了
    if not cam.isOpened():
        return
  
    fps = int(cam.get(cv2.CAP_PROP_FPS))
    size = (int(cam.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    f=20
    while True:
        ret1, frame1 = cam.read()
        ret2, frame2 = cam.read()
        ret3, frame3 = cam.read()
          
        if ret1 and ret2 and ret3:
            #グレースケールに変換
            gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
            gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
            gray3 = cv2.cvtColor(frame3, cv2.COLOR_BGR2GRAY)
    
            diff1 = cv2.absdiff(gray2,gray1)
            diff2 = cv2.absdiff(gray3,gray2)
  
            diff_and = cv2.bitwise_and(diff1, diff2)
  
            th = cv2.threshold(diff_and, 50, 255, cv2.THRESH_BINARY)[1]
  
            wh_pixels = cv2.countNonZero(th)
            if f==30:
                date=datetime.now()
                s3 = boto3.resource('s3')
                bucket_name = 'raspi-test-ht19a076'
                s3.Bucket(bucket_name).upload_file('/home/pi/Videos/video.mp4','{date}.mp4'.format(date=date))
                f=20
                subject="異常発生"
                message="異常発生 https://s3.console.aws.amazon.com/s3/buckets/raspi-test-ht19a076?region=ap-northeast-1&tab=objects"
                sns.publish(
                TopicArn=SNS_TOPIC_ARN,
                Message=message,
                Subject=subject
                )
                time.sleep(5)
            
    
  
  
            #閾値を超えたら動画撮
            if wh_pixels>0:
                
                date = datetime.now().strftime("%Y%m%d_%H%M%S")
                print(date + " whitePixels:"+str(wh_pixels))
  
                fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
                out = cv2.VideoWriter(base_path +'video.mp4',fourcc, fps, size)
                
                while wh_pixels>0:
                    ret_rec, frame_rec = cam.read()
                    ret4, frame4 = cam.read()
                    ret5, frame5 = cam.read()
                    ret6, frame6 = cam.read()
          
                    if ret4 and ret5 and ret6:
                        #グレースケールに変換
                        gray4 = cv2.cvtColor(frame4, cv2.COLOR_BGR2GRAY)
                        gray5 = cv2.cvtColor(frame5, cv2.COLOR_BGR2GRAY)
                        gray6 = cv2.cvtColor(frame6, cv2.COLOR_BGR2GRAY)
    
                        diff3 = cv2.absdiff(gray5,gray4)
                        diff4 = cv2.absdiff(gray6,gray5)
  
                        diff_and1 = cv2.bitwise_and(diff3, diff4)
  
                        th1 = cv2.threshold(diff_and1, 50, 255, cv2.THRESH_BINARY)[1]
                        
                        wh_pixels = cv2.countNonZero(th1)
                        f=30
                        if ret_rec:
                            out.write(frame_rec)
                            
                        continue

                out.release()
    cam.release()
  
if __name__ == '__main__':
    main()
  