import streamlit as  st
from googleapiclient.discovery import build
import pandas as pd

# config setup
api_key='AIzaSyCDXG8Tgq1IOpRf9sD_XuIbdGnc8PrNmho'
channel_ids=['UC8butISFwT-Wl7EV0hUK0BQ',  #w3schools
             'UCBwmMxybNva6P_5VmxjzwqA',  #apnacollege
             'UCCezIgC97PvUuR4_gbFUs5g',  #Corey Schafer
             'UCNU_lfiiWBdtULKOw6X0Dig',  #Krish Naik 
             'UCkw4JCwteGrDHIsyIIKo4tQ'   #Edureka 
            ]
youtube=build('youtube','v3',developerKey=api_key)

# Function to get Channel's stats
def get_channel_stats(youtube,channel_ids):
    all_data=[]
    request=youtube.channels().list(
        part="snippet,contentDetails,statistics",
        id=','.join(channel_ids))
    response=request.execute()
    
    for i in range(len(response['items'])):
        data=dict(Channel_name=response['items'][i]['snippet']['title'],
              Subscribers=response['items'][i]['statistics']['subscriberCount'],
              ViewCount=response['items'][i]['statistics']['viewCount'],
              videoCount=response['items'][i]['statistics']['videoCount'],
              playlist_id =response['items'][i]['contentDetails']['relatedPlaylists']['uploads']
                 )

        all_data.append(data)
    
    return all_data

channel_statistics= get_channel_stats(youtube,channel_ids)
channel_data=pd.DataFrame(channel_statistics)

channel_data['Subscribers']=pd.to_numeric(channel_data['Subscribers'])
channel_data['ViewCount']=pd.to_numeric(channel_data['ViewCount'])
channel_data['videoCount']=pd.to_numeric(channel_data['videoCount']  ) 

st.write("# Youtube Analysis")

st.write("## Channel Data")
st.write(channel_data)

st.write("### Subscribers")
st.bar_chart(data=channel_data,x='Channel_name',y='Subscribers',horizontal=True)
st.write("### Views")
st.bar_chart(channel_data['ViewCount'])

# Function to get video ids
playlist_id=channel_data.loc[channel_data['Channel_name']=='Apna College','playlist_id'].iloc[0]
# print(playlist_id)

def get_video_ids(youtube, playlist_id):
    # Initial API request to fetch playlist items
    request = youtube.playlistItems().list(
        part='contentDetails',
        playlistId=playlist_id,
        maxResults=50
    )
    response = request.execute()

    video_ids = []

    # Extract video IDs from the first page of results
    for item in response['items']:
        video_ids.append(item['contentDetails']['videoId'])

    # Pagination logic
    next_page_token = response.get('nextPageToken')
    while next_page_token:
        request = youtube.playlistItems().list(
            part='contentDetails',
            playlistId=playlist_id,
            maxResults=50,
            pageToken=next_page_token
        )
        response = request.execute()
        for item in response['items']:
            video_ids.append(item['contentDetails']['videoId'])
        next_page_token = response.get('nextPageToken')

    return video_ids  # Return the list of video IDs

video_ids=get_video_ids(youtube,playlist_id)

# Function to get video details
def get_video_details(youtube, video_ids):
    all_videos_stats = []

    for i in range(0, len(video_ids), 50):  # Process in chunks of 50
        request = youtube.videos().list(
            part='snippet,statistics',
            id=','.join(video_ids[i:i+50])  # Correct slicing
        )
        response = request.execute()  # Corrected typo in variable name

        for video in response.get('items', []):  # Use .get() to handle missing keys gracefully
            video_stats = {
                'Title': video['snippet']['title'],
                'Published_date': video['snippet']['publishedAt'],
                'Views': video['statistics'].get('viewCount', 0),  # Use .get() with defaults
                'Likes': video['statistics'].get('likeCount', 0),
                'Dislikes': video['statistics'].get('dislikeCount', 0),
                'Comments': video['statistics'].get('commentCount', 0),
            }
            all_videos_stats.append(video_stats)

    return all_videos_stats

video_details=get_video_details(youtube,video_ids)

video_data=pd.DataFrame(video_details)

video_data['Published_date']=pd.to_datetime(video_data['Published_date']).dt.date
video_data['Views']=pd.to_numeric(video_data['Views'])
video_data['Likes']=pd.to_numeric(video_data['Likes'])
video_data['Dislikes']=pd.to_numeric(video_data['Dislikes'])
video_data['Comments']=pd.to_numeric(video_data['Comments'])

top10_videos=video_data.sort_values(by='Views',ascending=False).head(10)

st.write("## Apna College Top 10 Videos")
st.write(top10_videos)
st.write("### Top 10 videos by view")
st.bar_chart(top10_videos['Views'])

video_data['Month']=pd.to_datetime(video_data['Published_date']).dt.strftime('%b')
videos_per_month=video_data.groupby('Month', as_index=False).size()

sort_order=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
videos_per_month.index=pd.CategoricalIndex(videos_per_month['Month'],categories=sort_order,ordered=True)

st.write(videos_per_month)
# st.bar_chart(videos_per_month["Size"])



# st.text_input("Youtu")

