import speech_recognition as sr
import pyttsx3
import openai
import face
import sendEmail

openai.api_base = 'https://api.chatanywhere.com.cn'
openai.api_key = 'sk-K2kmaIsLhynwlQIeCl4OXELsA4xyUe03eaRwFoIXR7w5Kqbz'
# 初始化语音识别器和语音合成器
recognizer = sr.Recognizer()
engine = pyttsx3.init()


def listen():
    with sr.Microphone() as source:
        print("请开始说话...")
        audio = recognizer.listen(source)
    try:
        text = recognizer.recognize_google(audio, language='zh-CN')
        print("User:", text)
        return text
    except sr.UnknownValueError:
        print("抱歉，无法识别你说的话")
        return "未识别到语音"
    except sr.RequestError:
        print("抱歉，发生了一些错误")
    return ""

# 语音输出
def speak(text):
	print("Chatgpt:", text)
	engine.say(text)
	engine.runAndWait()

def main():
	while True:  # 常驻开机循环
		call_text = listen()  # call_text为唤醒变量
		while "语音助手" in call_text:  # 说“语音助手”，说“退出”之前，会一直循环
			speak("您好，我是您的智能语音助手，现在可以说出您的问题")
			while True:
				input_text = listen()  # input_text为对话时语音输入的变量
				if "退出" in input_text:
					speak("好的，您若有任何需要，请再次呼唤语音助手，再见！")
					call_text = ""
					break
				if "未识别到语音" in input_text:
					speak("抱歉，我无法识别到您的提问")
				else:
					# 根据输入做出相应回答
					# 这里可以根据你的需求添加更多的对话逻辑
					chat_prompt = input_text
					gpt_35_api_stream(chat_prompt)
		if "关机" in call_text and not "确认" in call_text:
			speak("关机之后，再次见到我需要重新运行程序，请您确认是否关机。若要关机请说确认关机")

			call_text = call_text + "未识别到语音"
		if "确认" in call_text:  # 确认是否关机，退出主循环
			speak("好的，再见")
			break
		if not "未识别到语音" in call_text:
			speak("现在默认处于待机模式。若想开启对话，请呼唤语音助手。")


def gpt_35_api_stream(messages: list):
	try:
		response = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=messages,
            stream=True,
        )
		completion = {'role': '', 'content': ''}
		for event in response:
			if event['choices'][0]['finish_reason'] == 'stop':
				speak(completion["content"])
				break
			for delta_k, delta_v in event['choices'][0]['delta'].items():
				completion[delta_k] += delta_v

			messages.append(completion)  # 直接在传入参数 messages 中追加消息
		return (True, '')
	except Exception as err:
		return (False, f'OpenAI API 异常: {err}')


if __name__ == '__main__':
    messages = []
    name = face.checkFace()
    if name == "Unknown":
        print("人脸识别验证失败", name)
        exit(0)
    else:
        print("人脸识别成功")
    sendEmail.send_email(name)
    while True:
        text = input("请输入你的问题:")
        # text = listen()
        if text == "":
            continue
        completion = {}
        completion['role'] = 'user'  # "{'role': '', 'content': ''}"
        completion['content'] = text
        messages.append(completion)  # = [{'role': 'user', 'content': text}, ]
        gpt_35_api_stream(messages)
