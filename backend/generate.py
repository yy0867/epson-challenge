import json
import os
from datetime import datetime

from dotenv import load_dotenv
from openai import OpenAI

from generate_request import GenerateRequest
from prompt import prompt_template

load_dotenv()


def fill_prompt(input: str):
    prompt = prompt_template.replace("{INPUT}", input)
    return prompt


def fill_template(inference_output):
    with open('html_template.html', 'r', encoding='utf-8') as file:
        html_template = file.read()

    json_file = 'information.json'
    with open(json_file, 'r') as f:
        information = json.load(f)

    today = datetime.today()
    formatted_date = today.strftime("%Y. %m. %d")

    print(inference_output)
    html_template = html_template.replace("{copies}", str(inference_output["프린트 매수"]))

    html_template = html_template.replace("{날짜}", str(formatted_date))
    html_template = html_template.replace("큰 꿈을 키우며 사랑이 가득한 해동교육", information["header_left"])
    html_template = html_template.replace("해 동 알 림 마 당", information["header_center"])
    html_template = html_template.replace(
        "♠ 부산광역시 해운대구 우동 1로 104(우동) ☎ 740-7200 ☞ http://www.haedong.es.kr", information["contact"])
    html_template = html_template.replace("해동초등학교장", information["footer"])
    html_template = html_template.replace("김세영", information["teacher"])
    html_template = html_template.replace("{제목}", inference_output["제목"])
    html_template = html_template.replace("{본문}", inference_output["본문"])
    html_template = html_template.replace("{일시}", inference_output["일시"])
    html_template = html_template.replace("{장소}", inference_output["장소"])

    time_table = inference_output["일정"]
    table_html = ""
    for row in time_table:
        table_html += f'''
        <tr>
            <td style="text-align: center;">{row['시간']}</td>
            <td style="text-align: center;">{row['프로그램']}</td>
        </tr>
        '''

    html_template = html_template.replace("{테이블}", table_html)
    event_information = "\n".join(
        [f"{item}<br>" for idx, item in enumerate(inference_output["안내사항"], start=1)])
    html_template = html_template.replace("{안내 사항}", event_information)

    return html_template


def inference(input: str):
    client = OpenAI(api_key=os.getenv("OPENAI_KEY"))

    response = client.chat.completions.create(
        model="gpt-4o",
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant designed to output JSON."
            },
            {
                "role": "user",
                "content": input
            }
        ])

    return json.loads(response.choices[0].message.content)


def generate_file(generate_request: GenerateRequest):
    prompt = fill_prompt(generate_request.input)
    output = inference(prompt)
    html_content = fill_template(output)
    with open("file_to_show.html", "w", encoding="utf-8") as f:
        f.write(html_content)
