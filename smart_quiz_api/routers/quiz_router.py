from fastapi import (
    APIRouter, Depends, HTTPException, Query, Body,
    BackgroundTasks, Request
)
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime, timezone
import logging

from smart_quiz_api.models import (
    Quiz, QuizQuestion, UserAnswer, GradingTask, Feedback, User
)
from smart_quiz_api.models.enum import GradingStatusEnum, QuizType
from smart_quiz_api.schema import (
    QuizCreate, QuizOut, FeedbackCreate, FeedbackOut
)
from smart_quiz_api.database import get_db
from smart_quiz_api.services.openai_service import (
    render_prompt, safe_openai_chat, grade_answer,
    generate_explanation, estimate_confidence
)
from smart_quiz_api.services.scraper_services import generate_quiz_from_url
from smart_quiz_api.services.firebase import get_current_user

# Set up logger
logger = logging.getLogger(__name__)

router = APIRouter()


# === Generate quiz using OpenAI ===
@router.get("/generate/ai", response_model=Dict[str, Any])
async def generate_ai_quiz(
    request: Request,
    topic: str = Query(...),
    difficulty: str = Query("medium"),
    quiz_type: str = Query("mcq")
):
    # Convert quiz_type to proper enum value
    quiz_type_upper = quiz_type.upper()
    if quiz_type_upper not in ["MCQ", "TF", "IMAGE"]:
        quiz_type_upper = "MCQ"  # Default to MCQ if invalid

    # Cast to proper type for render_prompt
    quiz_type_enum: QuizType = quiz_type_upper  # type: ignore
    prompt = render_prompt(topic, difficulty, quiz_type_enum)
    ai_response = safe_openai_chat(prompt)
    
    try:
        from smart_quiz_api.services.openai_service import parse_ai_quiz_response
        parsed_questions = parse_ai_quiz_response(ai_response, quiz_type_upper)
        
        return {
            "topic": topic,
            "difficulty": difficulty,
            "quiz_type": quiz_type_upper,
            "questions": parsed_questions
        }
    except Exception as e:
        logger.error(f"Error parsing AI response: {e}")
        # Return raw response if parsing fails
        return {
            "topic": topic,
            "difficulty": difficulty,
            "quiz_type": quiz_type_upper,
            "generated_quiz": ai_response
        }


# === Generate quiz from a URL ===
@router.get("/generate/from-url", response_model=Dict[str, Any])
async def generate_quiz_from_article(
    request: Request,
    url: str = Query(...),
    quiz_type: str = Query("mcq")
):
    # Convert quiz_type to proper enum value
    quiz_type_upper = quiz_type.upper()
    if quiz_type_upper not in ["MCQ", "TF", "IMAGE"]:
        quiz_type_upper = "MCQ"  # Default to MCQ if invalid
        
    # Cast to proper type for generate_quiz_from_url
    quiz_type_enum: QuizType = quiz_type_upper  # type: ignore
    quiz_data = generate_quiz_from_url(url, quiz_type_enum)
    return quiz_data


# === Create a new quiz ===
@router.post("/", response_model=QuizOut)
def create_quiz(
    quiz_data: QuizCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Use the validated enum values from schema properties
    quiz = Quiz(
        user_id=current_user.id,
        title=quiz_data.title,
        category=quiz_data.topic,
        difficulty=quiz_data.difficulty_enum,  # Use validated enum from property
        duration_seconds=len(quiz_data.questions) * 30,
        start_time=datetime.now(timezone.utc),
        end_time=None,
        scraped_at=None
    )
    db.add(quiz)
    db.commit()
    db.refresh(quiz)

    for q in quiz_data.questions:
        question = QuizQuestion(
            quiz_id=quiz.id,
            question_text=q.text,
            options="|".join([a.text for a in q.answers]),
            correct_answer=q.correct_answer,
            question_type=quiz_data.question_type_enum,  # Use validated enum from property
            confidence=1.0,
            is_correct=False
        )
        db.add(question)

    db.commit()
    return quiz


# === List all quizzes ===
@router.get("/", response_model=List[QuizOut])
def list_quizzes(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    quizzes = db.query(Quiz).offset(skip).limit(limit).all()
    
    # Prepare response with quiz_type for each quiz
    result: List[Dict[str, Any]] = []
    for quiz in quizzes:
        quiz_data = dict(quiz.__dict__)
        
        # Get the first question to determine quiz_type
        first_question = db.query(QuizQuestion).filter(QuizQuestion.quiz_id == quiz.id).first()
        quiz_data["quiz_type"] = "mcq"  # Default value
        if first_question is not None:
            try:
                quiz_data["quiz_type"] = first_question.question_type.value
            except (AttributeError, TypeError):
                pass  # Keep the default value
            
        result.append(quiz_data)
    
    return result


# === List quizzes by user ===
@router.get("/user/{user_id}", response_model=List[QuizOut])
def list_user_quizzes(user_id: str, db: Session = Depends(get_db)):
    quizzes = db.query(Quiz).filter(Quiz.user_id == user_id).all()
    
    # Prepare response with quiz_type for each quiz
    result: List[Dict[str, Any]] = []
    for quiz in quizzes:
        quiz_data = dict(quiz.__dict__)
        
        # Get the first question to determine quiz_type
        first_question = db.query(QuizQuestion).filter(QuizQuestion.quiz_id == quiz.id).first()
        quiz_data["quiz_type"] = "mcq"  # Default value
        if first_question is not None:
            try:
                quiz_data["quiz_type"] = first_question.question_type.value
            except (AttributeError, TypeError):
                pass  # Keep the default value
            
        result.append(quiz_data)
    
    return result


# === Retrieve quiz by ID ===
@router.get("/{quiz_id}", response_model=QuizOut)
def get_quiz(quiz_id: int, db: Session = Depends(get_db)):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    # Get the first question to determine quiz_type
    first_question = db.query(QuizQuestion).filter(QuizQuestion.quiz_id == quiz.id).first()
    quiz_data = dict(quiz.__dict__)
    
    # Add quiz_type to the response based on the first question's type
    quiz_data["quiz_type"] = "mcq"  # Default value
    if first_question is not None:
        try:
            quiz_data["quiz_type"] = first_question.question_type.value
        except (AttributeError, TypeError):
            pass  # Keep the default value
    
    return quiz_data


# === Update an existing quiz ===
@router.put("/{quiz_id}", response_model=QuizOut)
def update_quiz(quiz_id: int, updated_data: QuizCreate, db: Session = Depends(get_db)):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    # Update quiz attributes
    setattr(quiz, 'title', updated_data.title)
    setattr(quiz, 'category', updated_data.topic)
    setattr(quiz, 'difficulty', updated_data.difficulty_enum)  # Use validated enum from property
    setattr(quiz, 'duration_seconds', len(updated_data.questions) * 30)
    quiz.updated_at = datetime.now(timezone.utc)

    # Delete existing questions
    db.query(QuizQuestion).filter(QuizQuestion.quiz_id == quiz.id).delete()

    # Add new questions
    for q in updated_data.questions:
        question = QuizQuestion(
            quiz_id=quiz.id,
            question_text=q.text,
            options="|".join([a.text for a in q.answers]),
            correct_answer=q.correct_answer,
            question_type=updated_data.question_type_enum,  # Use validated enum from property
            confidence=1.0,
            is_correct=False
        )
        db.add(question)

    db.commit()
    db.refresh(quiz)
    return quiz


# === Delete a quiz ===
@router.delete("/{quiz_id}", response_model=Dict[str, str])
def delete_quiz(quiz_id: int, db: Session = Depends(get_db)):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    db.delete(quiz)
    db.commit()
    return {"detail": f"Quiz {quiz_id} deleted successfully"}


# === Submit answers to a quiz ===
@router.post("/{quiz_id}/submit", response_model=Dict[str, Any])
def submit_quiz_answers(
    quiz_id: int,
    answers: List[Dict[str, Any]] = Body(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    results: List[Dict[str, Any]] = []
    total = 0
    correct = 0

    for ans in answers:
        question_id = ans["question_id"]
        selected_answer = ans["selected_answer"]
        user_id = current_user.id

        question = db.query(QuizQuestion).filter(QuizQuestion.id == question_id).first()
        if not question:
            continue

        if selected_answer not in question.options.split("|"):
            raise HTTPException(status_code=400, detail=f"Invalid answer for question ID {question_id}")

        grading = grade_answer(selected_answer, str(question.correct_answer))
        is_correct = grading["is_correct"]

        user_answer = UserAnswer(
            user_id=user_id,
            question_id=question_id,
            selected_answer=selected_answer,
            is_correct=is_correct
        )
        db.add(user_answer)

        # Create grading task with proper enum
        grading_task = GradingTask(
            quiz_id=quiz.id,
            user_id=user_id,
            status=GradingStatusEnum.COMPLETED,
            started_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc),
            error_message=None
        )
        db.add(grading_task)

        db.commit()
        db.refresh(user_answer)

        # Convert UserAnswer to dict for response
        results.append({
            "id": user_answer.id,
            "question_id": user_answer.question_id,
            "selected_answer": user_answer.selected_answer,
            "is_correct": user_answer.is_correct
        })
        total += 1
        if is_correct:
            correct += 1

    # Mark quiz completed
    setattr(quiz, 'end_time', datetime.now(timezone.utc))
    db.commit()

    score_pct = round((correct / total) * 100, 2) if total > 0 else 0

    response: Dict[str, Any] = {
        "summary": {
            "total": total,
            "correct": correct,
            "score_percentage": score_pct
        },
        "answers": results
    }
    return response


# === Submit feedback on a quiz ===
@router.post("/{quiz_id}/feedback", response_model=FeedbackOut)
def submit_feedback(
    quiz_id: int,
    feedback_data: FeedbackCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    feedback = Feedback(
        quiz_id=quiz_id,
        user_id=current_user.id,
        question_id=None,
        message=feedback_data.message,
        submitted_on=datetime.now(timezone.utc)
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return feedback


# === Get AI-generated explanation ===
@router.get("/{quiz_id}/explain", response_model=Dict[str, str])
def explain_quiz(quiz_id: int, db: Session = Depends(get_db)):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz or not quiz.questions:
        raise HTTPException(status_code=404, detail="Quiz or questions not found")

    quiz_text = "\n".join([q.question_text for q in quiz.questions])
    explanation = generate_explanation(quiz_text)
    return {"explanation": explanation}


# === Get AI-estimated confidence score ===
@router.get("/{quiz_id}/confidence", response_model=Dict[str, float])
def confidence_score(quiz_id: int, db: Session = Depends(get_db)):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz or not quiz.questions:
        raise HTTPException(status_code=404, detail="Quiz or questions not found")

    quiz_text = "\n".join([q.question_text for q in quiz.questions])
    score = estimate_confidence(quiz_text)
    return {"confidence_score": score}
