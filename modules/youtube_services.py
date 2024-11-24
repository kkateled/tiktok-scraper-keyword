import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import googleapiclient.http
import os


class YouTube:
    def __init__(self):
        self.scopes = ["https://www.googleapis.com/auth/youtube.upload"]

    def authenticate(self, client_secret):
        """returns ID youtube chanel"""
        try:
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(client_secret, self.scopes)
            credentials = flow.run_local_server(port=8080)
            youtube_id = googleapiclient.discovery.build("youtube", "v3", credentials=credentials)
            return youtube_id
        except Exception as e:
            print(f"Authentication error: {e}")
            return None

    def upload_video(self, youtube_id, media_file):
        """return ID uploaded video"""
        if youtube_id is None:
            print("Error: YouTube client is not authorized")
            return

        if not os.path.exists(media_file):
            print("Error: Media file does not exist")
            return

        try:
            body = {
                "snippet": {
                    "title": "test"
                },
                "status": {
                    "privacyStatus": "private"
                }
            }

            request = youtube_id.videos().insert(
                part="snippet,status",
                body=body,
                media_body=googleapiclient.http.MediaFileUpload(media_file, resumable=True)
            )

            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    print(f"Upload {int(status.progress() * 100)}% complete")

            if response is not None and 'id' in response:
                print(f"Video uploaded with ID: {response['id']}")
                return response['id']
            else:
                print("Error: No response or video ID returned")

        except googleapiclient.errors.HttpError as error:
            print(f"There was an error loading: {error}")
            return
        except Exception as error:
            print(f"An unexpected error occurred: {error}")


