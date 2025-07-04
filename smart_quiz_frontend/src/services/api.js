//Axios wrapper for FastAPI calls
import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:8000/quiz", // change after deploy
});

export const fetchQuiz = (topic, difficulty = "medium", q_type = "mcq") =>
  api.get("/generate", {
    params: { topic, difficulty, q_type },
  });
