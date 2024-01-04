const axios = require("axios").default;

await axios.post(`https://api.telegram.org/bot${process.env.BOT_TOKEN}/sendMessage`, {
  chat_id: JSON.parse(event.body).message.chat.id,
  text: "I got your message!",
});
