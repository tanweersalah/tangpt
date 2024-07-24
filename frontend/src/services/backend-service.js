// movieService.js

import axios from "axios";

export default class BackendService {
  constructor() {
    this.apiUrl = "http://tangpt.tanflix.me/api/invoke";
  }

  async getGptResponse(input_message) {
    const body = {
      message: input_message,
    };

    try {
      const response = await axios.post(this.apiUrl, body, {
        headers: {
          "Content-Type": "application/json", // Setting the request content type
        },
      });

      console.log(response.data); // Logging the response data
      return response.data;
    } catch (error) {
      console.error("Error:", error);
    }
  }
}
