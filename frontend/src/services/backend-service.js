// movieService.js

import axios from "axios";

export default class BackendService {
  constructor() {
    this.apiUrl = "https://tangpt.tanflix.me/api/chat";
  }

  async getGptResponse(
    input_message,
    session_id,
    llm = "GROQ",
    model_name = "llama-3.1-8b-instant"
  ) {
    const body = {
      message: input_message,
      session_id: session_id,
      llm: llm,
      model_name: model_name,
    };

    const response = await axios.post(this.apiUrl, body, {
      headers: {
        "Content-Type": "application/json", // Setting the request content type
      },
    });

    console.log(response.status); // Logging the response data
    return response;
  }
}
