// Quiz page
import React, { useEffect, useState } from "react";
import { fetchQuiz } from "../services/api";

function QuizPage() {
  const [quiz, setQuiz] = useState("");

  useEffect(() => {
    fetchQuiz("UPSC Polity", "hard", "mcq").then((res) =>
      setQuiz(res.data.quiz)
    );
  }, []);

  return (
    <div>
      <h2>Quiz</h2>
      <pre>{quiz}</pre>
    </div>
  );
}

export default QuizPage;
