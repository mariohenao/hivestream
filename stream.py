import cv2
import streamlit as st
#import time
import requests
import json

#import hiverealtime as hrt

base_sync = 'https://api.thehive.ai/api/v2/task/sync'

sectrect_json = json.load(open("SECRETS.json"))
vis_API_Key = sectrect_json['vis_API_Key']
vis_threshold = 0.7 # Confidence score threshold
banned_classes = ['knife_in_hand']

def moderate_post_sync(frame):
   # Example Request (visual, synchronous endpoint, content hosted at URL):
   headers = {'Authorization': f'Token {vis_API_Key}'} # Example for visual moderation tasks
   retval, buffer = cv2.imencode('.jpg', frame)
   payload = {"image": buffer}
   
   model_response = requests.post('https://api.thehive.ai/api/v2/task/sync', headers=headers, files=payload)
   if model_response.status_code == 200:
       response_dict = model_response.json()
       policy, score = handle_hive_response(response_dict)
   return policy, score



def handle_hive_response(response_dict):
    scores_dict = {x['class']:x['score'] for x in response_dict['status'][0]['response']['output'][0]['classes']}
    # For a video input, you may want to iterate over timestamps for each frame and take the max score for each class. 
    for class_i in banned_classes:
        if scores_dict[class_i] >= vis_threshold:
             # Insert your actual moderation actions here
            print(str(class_i) + ': ' + str(scores_dict[class_i]))
            return class_i, scores_dict[class_i]
            break
    return class_i, 0.00

st.title("CoMo Live")
run = st.checkbox("Run stream")
FRAME_WINDOW = st.image([])
cam = cv2.VideoCapture(0)

#Start hive
#videocapture()

t = st.empty()
while run:

    #cap = cv2.VideoCapture(0)
    if not cam.isOpened():
        print("Unable to connect to camera.")
        break
    count = 0
    policy = 'knife_in_hand'
    score = 0.00
    while cam.isOpened():
        ret, frame = cam.read()
        #frame = cv2.flip(frame,1)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        FRAME_WINDOW.image(frame)
        if ret:
            count = count + 1
            t.write(f'{policy}: {score}')
            #time.sleep(0.2)
            if count == 60:
                policy, score = moderate_post_sync(frame)
                count = 0
                t.write(f'{policy}: {round(score, 2)}')
                #time.sleep(0.2)

                #cv2.putText(frame, policy, (20, 140), cv2.FONT_HERSHEY_SIMPLEX ,1, (0, 0, 0), 2)
            #cv2.imshow("demo", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break


    #ret, frame = cam.read()
    #frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    #FRAME_WINDOW.image(frame)
    
    # t.write('Counter: ' + str(counter))
    # count += 1
    # if (count > 100) :
    #     run = False
    # time.sleep(0.2)
else:
    st.write('Stopped streaming.')