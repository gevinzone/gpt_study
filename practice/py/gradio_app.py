import os

from openai import AzureOpenAI
import gradio as gr

deployment = "gpt-4o"

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)


def get_response(inputs):
    response = client.chat.completions.create(
        model=deployment,
        messages=inputs,
        temperature=0.8,
        max_tokens=256,
    )
    return response.choices[0].message.content


def history_to_prompt(chat_history):  # 将对话内容保存在一个List里
    # print(chat_history)
    message = [{"role": "system", "content": "You are an AI assistant."}]
    for round_trip in chat_history:  # 将List里的内容，组成 ChatCompletion的 messages部分，{role，content} dict
        message.append({"role": "user", "content": round_trip[0]})
        message.append({"role": "assistant", "content": round_trip[1]})
    return message


def respond(message, chat_history):
    his_msg = history_to_prompt(chat_history)  # 并装历史会话，ChatCompletion的 messages部分格式
    his_msg.append({"role": "user", "content": message})  # 放入当前用户问题
    print(his_msg)

    bot_message = get_response(his_msg)
    chat_history.append((message, bot_message))  # 保存历史对话记录，用于显示
    return "", chat_history


if __name__ == "__main__":
    with gr.Blocks() as demo:
        chatbot = gr.Chatbot(height=240)  # just to fit the notebook
        msg = gr.Textbox(label="Prompt")
        btn = gr.Button("提交")
        clear = gr.ClearButton(components=[msg, chatbot], value="Clear console")

        btn.click(respond, inputs=[msg, chatbot], outputs=[msg, chatbot])
        msg.submit(respond, inputs=[msg, chatbot], outputs=[msg, chatbot])  #Press enter to submit
    gr.close_all()
    demo.launch(share=False, debug=True)
