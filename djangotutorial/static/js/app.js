import OpenAI from "openai";

const openai = new OpenAI(
    {
        // 若没有配置环境变量，请用您子业务空间的百炼API Key将下行替换为：apiKey: "sk-xxx",
        apiKey: "sk-8dd36f6d2c814e25b1ee094d495af305",
        baseURL: "https://dashscope.aliyuncs.com/compatible-mode/v1"
    }
);

async function main(question) {
    const completion = await openai.chat.completions.create({
        model: "qwen-plus",  //此处以qwen-plus为例，可按需更换模型名称（须完成模型授权，且是标准模型）。支持模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
        messages: [
            { role: "system", content: "You are a helpful assistant." },
            { role: "user", content: question }
        ],
    });
    console.log(JSON.stringify(completion.choices[0].message.content, null, 2));
}

main("你是谁？");

console.log('Hello, Node.js!');
// const express = require('express');
// const app = express();



// app.get('/', (req, res) => {
//     res.send('Hello, Express!');
// });

// app.listen(3000, () => {
//     console.log('Server is running on http://localhost:3000');
// });