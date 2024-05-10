import sqlite3
import gradio as gr
import pandas as pd
import random
from gradio_videogallery import videogallery
from apscheduler.schedulers.background import BackgroundScheduler

DB_FILE = "./survey.db"

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
    db.close()

def get_surveys(db):
    surveys = db.execute("SELECT * FROM survey").fetchall()
    total_surveys = db.execute("SELECT COUNT(*) FROM survey").fetchone()[0]
    #  surveys = [{"name": name, "age": age} for name, age in surveys]
    surveys = pd.DataFrame(surveys, columns=["id", "date_created", "name", "age", "model"])
    return surveys, total_surveys

def insert_survey(name, age, model):
    db = sqlite3.connect(DB_FILE)
    db.execute("INSERT INTO survey (name, age, model) VALUES (?, ?, ?)", (name, age, model))
    db.commit()
    surveys, total_surveys = get_surveys(db)
    db.close()
    return surveys, total_surveys

def validate_survey(name, age, model):
    if not name:
        raise gr.Error("Name is required")
    if not age:
        raise gr.Error("Age is required")
    if not model:
        raise gr.Error("Model is required")
    return insert_survey(name, age, model)

def load_surveys():
    db = sqlite3.connect(DB_FILE)
    surveys, total_surveys = get_surveys(db)
    db.close()
    return surveys, total_surveys

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

def generate_videos():
    return videogallery().example_inputs()

with gr.Blocks(theme=gr.themes.Soft()) as SurveyDemo:
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

    with gr.Tab(label="Survey"):
        gr.Markdown("## User Study")
        name = gr.Textbox(label="Name", placeholder="Enter your name")
        age = gr.Textbox(label="Age", placeholder="Enter your age")
        gallery = gr.Gallery(label="Gallery", elem_id="gallery", columns=[3], rows=[1], object_fit="contain", height="auto")
        #  videogallery(value=generate_videos(), label="Video Gallery")
        selected = gr.Number(show_label=False)
        submit = gr.Button(value="Submit")
        data = gr.Dataframe(headers=["Name", "Age", "Model"], visible=True)
        count = gr.Number(label="Total Surveys")

        def get_select_index(evt: gr.SelectData):
            return evt.index
        gallery.select(get_select_index, None, selected)

        #  submit.click(insert_survey, [name, age, selected], [data, count])
        submit.click(validate_survey, [name, age, selected], [data, count])

        SurveyDemo.load(generate_images, None, [gallery])
        SurveyDemo.load(load_surveys, None, [data, count])

def backup_data():
    surveys, total_surveys = load_surveys()
    surveys.to_csv("./survey.csv", index=False)

scheduler = BackgroundScheduler()
scheduler.add_job(backup_data, trigger='interval', seconds=60)
scheduler.start()

SurveyDemo.launch(share=True)
