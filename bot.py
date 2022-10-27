import tweepy
import os
import time
import io
import re
import json
from stability_sdk import client
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation
from PIL import Image
from pydalle import Dalle
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())


API_KEY = os.environ.get('API_KEY')
API_KEY_SECRET = os.environ.get('API_KEY_SECRET')
BEARER_TOKEN = os.environ.get('BEARER_TOKEN')
ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN')
ACCESS_TOKEN_SECRET = os.environ.get('ACCESS_TOKEN_SECRET')
CLIENT_ID = os.environ.get('CLIENT_ID')
CLIENT_SECRET = os.environ.get('CLIENT_SECRET')
STABILITY_KEY = os.environ.get('STABILITY_KEY')
OPENAI_USERNAME = os.environ.get('OPENAI_USERNAME')
OPENAI_PASSWORD = os.environ.get('OPENAI_PASSWORD')

check = False


class tweet_listener(tweepy.StreamingClient):
    def on_tweet(self, tweet):
        RT_check = "RT"
        if RT_check in tweet.text:
            time.sleep(1)
        else:
            global check
            global id
            #global handle
            id = tweet.id
            tweet_id = tweet.id

            print(tweet.text)
            print(id)
            check = True
            print (check)
            return id
    
    def on_error(self, status):
        print(status)
        return




def api_call():
    auth = tweepy.OAuthHandler(API_KEY, API_KEY_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth)
    return tweepy.API(auth)



def pull(api, tweet_id):
        global text
        print(f"Pull funct")
        #print(tweet_id)
        tweet = api.get_status(tweet_id, tweet_mode='extended')
        result = tweet.full_text
        print ("result", result)

        text = re.sub(r'http\S+', '_', result)
        print (text)
        return text


#Stable diffusion image generator
def img(tweet):
    print("making image")
    try:
        stability_api = client.StabilityInference(
                key= STABILITY_KEY,
                verbose=True,
            )
        answers = stability_api.generate(
                prompt= tweet,
            )
        for resp in answers:
                for artifact in resp.artifacts:
                    if artifact.finish_reason == generation.FILTER:
                        warnings.warn(
                            "Your request activated the API's safety filters and could not be processed."
                            "Please modify the prompt and try again.")
                    if artifact.type == generation.ARTIFACT_IMAGE:
                        pic = io.BytesIO(artifact.binary)
                        img = Image.open(io.BytesIO(artifact.binary))
                        img.save("image_name.jpg")
                        img.show()
                        print("completed image")

    except:
        time.sleep(1)


def output(API, tweet_id):
    API.update_status_with_media(status=" https://twitter.com/awarixo/status/"+ str(id),filename="image_name.jpg")

    print("TWEET SENT")


def main():
    global check
    global id
    global text

    api = api_call()
    printer = tweet_listener(BEARER_TOKEN)

    result = printer.get_rules()
    print(result)

    print("ran")
    thread = printer.filter(threaded=True)
    print("thread created")
    print (check)

    id_fetch = id
    print(id_fetch)

    while True:
        while check == True: 
            #if check == True:
                print("ID FETCH now live")   
                img_with_tweet_check = "_"
                pulled_tweet = pull(api, id)
                if img_with_tweet_check in text:
                    check = False
                    print("image tweet so no output")
                else:
                    #Image generation and saving 
                    img(pulled_tweet)
                    time.sleep(8)
                    output(api, id_fetch)
                    check = False
    
    print("skipped")




if __name__ == '__main__':
    main()
