import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres:///{}".format(self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_get_categories_success(self):
        res = self.client().get("/categories")
        data = json.loads(res.data)


        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["categories"])
        self.assertTrue(data["total_categories"])
    
    def test_get_categories_fail(self):
        res = self.client().post("/categories")
        data = json.loads(res.data) 

        self.assertEqual(res.status_code, 405)
        self.assertTrue(data["success"] == False)
    
    #questions 
    
    def test_get_questions_fail(self):
        res = self.client().get("/questions?page=3000")
        data = json.loads(res.data) 

        self.assertEqual(res.status_code, 404)
        self.assertTrue(data["success"] == False)

    def test_get_questions_success(self):
        res = self.client().get("/questions") 
        data = json.loads(res.data) 

        self.assertTrue(data)

    
    def test_create_question_success(self):
        res = self.client().post("/questions", json = {"question": "first", "answer": "first answer", "difficulty": 1, "category": 2}) 
        data = json.loads(res.data)


        self.assertEqual(res.status_code, 201) 
    
    def test_create_question_fails_without_category(self):
        res = self.client().post("/questions", json = {"question": "first", "answer": "first answer", "difficulty": 1}) 
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400) 

    def test_create_question_fails(self):
        res = self.client().post("/questions", json = {"question": "first", "answer": "first answer", "difficulty": 1, "category": 200}) 
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422) 

    def test_delete_question_success(self):
        question = Question.query.first()
        res = self.client().delete(f"/questions/{question.id}") 

        self.assertEqual(res.status_code, 200)

    def test_delete_question_fails(self):
        res = self.client().delete(f"/questions/-2") 

        self.assertEqual(res.status_code, 404)  

    
    def test_search_question_success(self):
        res = self.client().post("/questions/search", json={"searchTerm": "a"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data["questions"]) >= 0) 

    def test_search_question_fails(self):
        res = self.client().post("/questions/search")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)

    def test_get_question_by_category(self):
        res = self.client().get("/categories/2/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data["questions"]) >= 0)

    def test_get_question_by_category(self):
        res = self.client().get("/categories/600/questions")

        self.assertEqual(res.status_code, 404)


    def test_get_random_question(self):
        res = self.client().post("/quizzes", json={"previous_questions": [1,2], "quiz_category": {"type": "click", "id": 0}})
        data = json.loads(res.data) 

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["question"] is None or data["question"])   

    def test_get_random_question(self):
        res = self.client().post("/quizzes", json={"previous_questions": None, "quiz_category": {"type": "click", "id": 0}})


        self.assertEqual(res.status_code, 404)
  

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()