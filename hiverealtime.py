#from email.mime import image
#from tkinter import Frame
import cv2
import requests # Used to call most Hive APIs
#import threading
import json

base_sync = 'https://api.thehive.ai/api/v2/task/sync'
sectrect_json = json.load(open("SECRETS.json"))
vis_API_Key = sectrect_json['vis_API_Key']
vis_threshold = 0.7 # Confidence score threshold
banned_classes = ['knife_in_hand']#, 'yes_middle_finger']
# A selection of classes to moderate from the hypothetical model response shown above.


def videocapture():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Unable to connect to camera.")
        return
    count = 0
    while cap.isOpened():
        ret, frame = cap.read()
        frame = cv2.flip(frame,1)
        if ret:
            count = count + 1
            if count == 60:
                policy, score = moderate_post_sync(frame)
                count = 0
                cv2.putText(frame, policy, (20, 140), cv2.FONT_HERSHEY_SIMPLEX ,1, (0, 0, 0), 2)
            #cv2.imshow("demo", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            

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
    
            
#videocapture()
            