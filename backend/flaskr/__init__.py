import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  CORS(app)

  PAGE_SIZE = 10

  @app.after_request
  def after_request(response):
    response.headers.add("Access-Control-Allow-Headers", "Content-type, Authorization")
    response.headers.add("Access-Control-Allow-Methods", "POST, PUT, GET, PATCH, OPTIONS, DELETE")
    return response

  def paginate(request, resource):
    page = request.args.get("page", 1, type=int) 
    start = (page-1) * PAGE_SIZE
    end = start + PAGE_SIZE 
    if start >= len(resource):
      abort(404)
    return resource[start:end]


  @app.route("/categories")
  def get_categories():
    if request.method == "POST":
      abort(405)
    categories = Category.query.all() 
    if categories:
      categories = [c.format() for c in categories] 
    else:
      abort(404) 
    return jsonify({
      "categories": categories,
      "total_categories": len(categories)
    })


  @app.route("/questions", methods=["GET"])
  def get_questions():
    questions = Question.query.all()
    if not questions:
      abort(404)
    questions = [q.format() for q in paginate(request, questions)]
    categories = Category.query.all() 
    if not categories:
      abort(404) 
    categories = [c.format() for c in categories] 
    return jsonify({
      "questions": questions, 
      "total_questions": len(questions),
      "current_category": None, 
      "categories": categories
    })


  @app.route("/questions/<int:id>", methods=["DELETE"])
  def delete_question(id):
    if not id:
      abort(404) 
    question = Question.query.filter(Question.id == id).one_or_none() 
    if not question:
      abort(404) 
    try:
      question.delete() 
    except:
      abort(422) 
    return jsonify({
      "deleted": question.id
    })


  @app.route("/questions", methods=["POST"])
  def create_question():
    body = request.get_json() 
    lst = ["question", "answer", "difficulty", "category"]
    for item in lst:
      if item not in body:
        abort(400)
    try:
      question = body.get("question", None) 
      category = body.get("category", None)
      difficulty = body.get("difficulty", None) 
      answer = body.get("answer", None) 
      category = Category.query.filter(Category.id == category).one_or_none()
      if not category:
        abort(422)
      q = Question(question=question, category=category.id, difficulty=difficulty, answer=answer)
      q.insert()
      questions = Question.query.all()
    except:
      abort(422) 
    return jsonify({
      "created": q.id, 
      "total_questions": len(questions),
      "success": True
    }), 201
    

  @app.route("/questions/search", methods=["POST"])
  def question_search():
    category = request.args.get("category", None)
    current_category = None 
    try:
      if category:
        category = Category.query.filter(Category.id == int(category)).first() 
        if category: 
          current_category = category.format()
    except:
      current_category = None
    term = request.get_json()
    if not term:
      abort(400)
    term = term.get("searchTerm", None) 
    if not term:
      abort(400) 
    questions = Question.query.filter(Question.question.ilike(f"%term%")).all()
    return jsonify({
      "questions": [q.format() for q in questions],
      "total_questions": len(questions),
      "current_category": current_category
    })

  @app.route("/categories/<int:id>/questions")
  def get_question_by_category(id):
    if not id:
      abort(400)
    category = Category.query.filter(Category.id == id).one_or_none() 
    if not category:
      abort(404) 
    questions = Question.query.filter(Question.category == category.id).all() 
    return jsonify({
      "questions": [q.format() for q in questions],
      "total_questions": len(questions),
      "current_category": category.format()
    })

  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route("/quizzes", methods=["POST"])
  def get_next():
    body = request.get_json()
    prev = body.get("previous_questions", None)
    category = body.get("quiz_category", None)
    if prev is None or category is None:
      abort(404)
    category = category.get("type", None)
    if category is not None and category == "click":
      category = "All"
    else:
      category = Category.query.filter(Category.id == category["id"]).one_or_none() 
    
    prev_questions = Question.query.filter(Question.id.in_(prev)).all()
    if category == "All":
      candidate_questions = Question.query.filter(Question.id.notin_(prev)).all()
    else:
      candidate_questions = Question.query.filter(Question.id.notin_(prev)).filter(Question.category == category.id).all()
    if candidate_questions:
      question = random.choice(candidate_questions).format() 
    else:
      question = None 
    print(prev_questions, category)
    return jsonify({
      "question": question
    })

  
  @app.errorhandler(405)
  def method_not_allowed(error):
    return jsonify({
      "success": False, 
      "error": 405, 
      "message": "Method not Allowed"
    }), 405


  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      "success": False, 
      "error": 404, 
      "message": "Not Found"
    }), 404

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      "success": False, 
      "error": 422, 
      "message": "Unprocessable"
    }), 422

  @app.errorhandler(400)
  def unprocessable(error):
    return jsonify({
      "success": False, 
      "error": 400, 
      "message": "Bad Request"
    }), 400
    
  return app

