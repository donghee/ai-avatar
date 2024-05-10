import sqlite3
import gradio as gr
import pandas as pd
import random
from pathlib import Path
from gradio_videogallery import videogallery
from apscheduler.schedulers.background import BackgroundScheduler

#DB_FILE = "./survey.db"
DB_FILE = "./result.db"

db = sqlite3.connect(DB_FILE)
try:
    db.execute("SELECT * FROM survey").fetchall()
    db.close()
except Exception as e:
    db.execute(
        '''
        CREATE TABLE survey (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                             create_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                             name TEXT, age INTEGER, model TEXT)
        ''')
    db.commit()
    db.execute(
        '''
        CREATE TABLE user_study (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                             create_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                             name TEXT, metric_a TEXT, metric_b TEXT, metric_c TEXT)
        ''')
    db.commit()
    db.close()

gr.set_static_paths(paths=["data/"])

def get_surveys(db):
    surveys = db.execute("SELECT * FROM survey").fetchall()
    total_surveys = db.execute("SELECT COUNT(*) FROM survey").fetchone()[0]
    #  surveys = [{"name": name, "age": age} for name, age in surveys]
    surveys = pd.DataFrame(surveys, columns=["id", "date_created", "name", "age", "model"])
    return surveys, total_surveys


def get_user_studies(db):
    user_studies = db.execute("SELECT * FROM user_study").fetchall()
    total_studies = db.execute("SELECT COUNT(*) FROM user_study").fetchone()[0]
    user_studies = pd.DataFrame(user_studies, columns=["id", "date_created", "name", "metric_a", "metric_b", "metric_c"])
    return user_studies, total_studies

def insert_survey(name, age, model):
    db = sqlite3.connect(DB_FILE)
    db.execute("INSERT INTO survey (name, age, model) VALUES (?, ?, ?)", (name, age, model))
    db.commit()
    surveys, total_surveys = get_surveys(db)
    db.close()
    return surveys, total_surveys

def insert_user_study(name, metric_a, metric_b, metric_c):
    db = sqlite3.connect(DB_FILE)
    db.execute("INSERT INTO user_study (name, metric_a, metric_b, metric_c) VALUES (?, ?, ?, ?)", (name, metric_a, metric_b, metric_c))
    db.commit()
    db.close()

def validate_survey(name, age, model):
    if not name:
        raise gr.Error("Name is required")
    if not age:
        raise gr.Error("Age is required")
    if not model:
        raise gr.Error("Model is required")
    return insert_survey(name, age, model)

def validate_user_study(metric_a, metric_b, metric_c, name):
    if not metric_a:
        raise gr.Error("Metric A is required")
    if not metric_b:
        raise gr.Error("Metric B is required")
    if not metric_c:
        raise gr.Error("Metric C is required")
    if not name:
        raise gr.Error("Name is required")
    return insert_user_study(name, metric_a, metric_b, metric_c)

def load_surveys():
    db = sqlite3.connect(DB_FILE)
    surveys, total_surveys = get_surveys(db)
    db.close()
    return surveys, total_surveys

def load_user_studies():
    db = sqlite3.connect(DB_FILE)
    user_studies, total_user_studies = get_user_studies(db)
    db.close()
    return user_studies, total_user_studies

insert_survey("John", 25, "model1")
insert_survey("Alice", 30, "model2")
# print(load_surveys())

def generate_images():
    images = [
        (random.choice(
            [
                "http://www.marketingtool.online/en/face-generator/img/faces/avatar-1151ce9f4b2043de0d2e3b7826127998.jpg",
                "http://www.marketingtool.online/en/face-generator/img/faces/avatar-116b5e92936b766b7fdfc242649337f7.jpg",
                "http://www.marketingtool.online/en/face-generator/img/faces/avatar-1163530ca19b5cebe1b002b8ec67b6fc.jpg",
                "http://www.marketingtool.online/en/face-generator/img/faces/avatar-1116395d6e6a6581eef8b8038f4c8e55.jpg",
                "http://www.marketingtool.online/en/face-generator/img/faces/avatar-11319be65db395d0e8e6855d18ddcef0.jpg",
            ]
        ), f"model {i}")
        for i in range(3)
    ]
    print(images)
    return images

#def generate_videos():
#    return videogallery().example_inputs()

def generate_videos():
    test_video = f"test00" + random.choice(["1", "2", "3", "4"])
    videos = [
                f"data/{test_video}/{test_video}_modelA.mp4",
                f"data/{test_video}/{test_video}_modelB.mp4",
                f"data/{test_video}/{test_video}_modelC.mp4",
                f"data/{test_video}/{test_video}_modelD.mp4",
                f"data/{test_video}/{test_video}_modelE.mp4",
             ]
    return videos

def replay_videos():
    return [gr.Video(autoplay=True, value=video) for video in generate_videos()]

def video_inference(video_model, voice_model, image_input, sound_input, text_input, pose_video_input):
    # ref https://github.com/bjoernpl/llama_gradio_interface/blob/main/example.py
    print(image_input, type(image_input))
    print(sound_input, type(sound_input))
    print(text_input, type(text_input))
    print(pose_video_input, type(pose_video_input))
    return pose_video_input

css = """
.radio-group .warp {
    display: flex !important;
}
.radio-group label {
    flex: 1 1 auto;
}
"""

with gr.Blocks(theme=gr.themes.Soft(), css=css) as SurveyDemo:
    gr.Markdown("# AI Avatar")
    with gr.Tab(label="AI framework"):
        gr.Markdown("## AI Framework")
        with gr.Row():
            with gr.Column():
                gr.Markdown("### Input")
                video_model = gr.Textbox(label="Video Model", placeholder="Enter model name")
                voice_model = gr.Textbox(label="Voice Model", placeholder="Enter model name")
                image_input = gr.Image(label="Source Image")
                sound_input = gr.Audio(label="Source Voice")
                text_input = gr.Textbox(label="Source Text", placeholder="Enter text")
                pose_video_input = gr.Video(label="Pose Video")
                submit = gr.Button(value="Submit")
            with gr.Column():
                gr.Markdown("### Result")
                video_output = gr.Video(label="Output Video")
            submit.click(video_inference, [video_model, voice_model, image_input, sound_input, text_input, pose_video_input], [video_output])

    with gr.Tab(label="User Study"):
        gr.Markdown("## User Study")
        with gr.Row():
            video0 = gr.Video(autoplay=True, label="ModelA")
            video1 = gr.Video(autoplay=True, label="ModelB")
            video2 = gr.Video(autoplay=True, label="ModelC")
            video3 = gr.Video(autoplay=True, label="ModelD")
            video4 = gr.Video(autoplay=True, label="ModelE")

        metric_a = gr.Radio(["A", "B", "C", "D", "E"], label="Metric A", info="영상 선명도", elem_classes="radio-group")
        metric_b = gr.Radio(["A", "B", "C", "D", "E"], label="Metric B", info="입술 동기화", elem_classes="radio-group")
        metric_c = gr.Radio(["A", "B", "C", "D", "E"], label="Metric C", info="영상 품질", elem_classes="radio-group")

        with gr.Row():
            with gr.Column():
                name = gr.Textbox(label="Name", placeholder="Enter your name")
            with gr.Column():
                retry = gr.Button(value="Retry", scale=2)
            with gr.Column():
                check = gr.Button(value="Check", scale=2)

        SurveyDemo.load(generate_videos, None, [video0, video1, video2, video3, video4])
        retry.click(replay_videos, None, [video0, video1, video2, video3, video4])
        check.click(validate_user_study, [metric_a, metric_b, metric_c, name], None)

    with gr.Tab(label="Result"):
        gr.Markdown("## Result of User Study")
        data = gr.Dataframe(headers=["Name", "MetricA", "MetricB", "MetricC"], visible=True)
        count = gr.Number(label="Total User Studies")

        SurveyDemo.load(load_user_studies, None, [data, count])


def backup_data():
    user_studies, _ = load_user_studies()
    user_studies.to_csv("./result.csv", index=False)

scheduler = BackgroundScheduler()
scheduler.add_job(backup_data, trigger='interval', seconds=1)
scheduler.start()

SurveyDemo.launch(share=True)
