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
        self.database_path = "postgresql://{}:{}@{}:5432/{}".format(
    'postgres', 'arthur', 'localhost', self.database_name)
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
    
    def test_paginate_categories(self):
        #Tests the pagination method for the categories
        response = self.client().get('/categories')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        
    
    def test_paginate_questions(self):
        #Tests the pagination method
        response = self.client().get('/questions')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_404_request_beyond_valid_page(self):
        """ Tests error if user tries to access nonexistent page """
        response = self.client().get('/questions?page=1000')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'not found')


    def test_create_question(self):
        new_question = {
            'question' : "This is a test question",
            'answer' : "Hope it passes!",
            'category' : 1,
            'difficulty' : 1
        }
        
        current_questions = len(Question.query.all())
        response = self.client().post('/questions', json=new_question)
        
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['total_questions'], current_questions + 1)    

    def test_422_create_question(self):
        current_questions = Question.query.all()
        current_questions_id = [question.id for question in current_questions]
        response = self.client().post('/questions', json={})
        data = json.loads(response.data)
        
        after_questions = Question.query.all()
        after_questions_id = [question.id for question in after_questions]
        
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(current_questions_id, after_questions_id)
    
    
    def test_delete_question(self):
        new_question = Question(
            question = "This is a test question",
            answer = "Hope it passes!",
            category = 1,
            difficulty= 1
        )
        
        new_question.insert()
        current_questions = len(Question.query.all())
        
        response = self.client().delete('/questions/{}'.format(new_question.id))

        data = json.loads(response.data)
        
        after_questions = len(Question.query.all())
        deleted_question = Question.query.filter_by(id = new_question.id).one_or_none()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(after_questions, current_questions - 1)
        self.assertEqual(deleted_question, None)
    
    def test_422_delete_question(self):
        current_questions = Question.query.all()
        current_questions_id = [question.id for question in current_questions]
        
        response = self.client().post('/questions/{}'.format({''}))
        data = json.loads(response.data)
        after_questions = Question.query.all()
        after_questions_id = [question.id for question in after_questions]
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(current_questions_id, after_questions_id)
    
    def test_search_question(self):
        
        response = self.client().post('/questions/search', json={
            'searchTerm': 'palace'})
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertIsNotNone(data['questions'])
        self.assertIsNotNone(data['total_questions'])
    
    def test_404_search(self):
        response = self.client().post('/questions/search', json={
            'searchTerm': 'XAAAAAAA'})
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "not found")
    
    def test_get_category_questions(self):
        response = self.client().get('/categories/1/questions')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['current_category'])
    
    def test_404_get_category_questions(self):
        response = self.client().get('categories/100000/questions')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "not found")
    
    def test_play_quiz(self):
        quiz_round = {'previous_questions': [], 'quiz_category': {
            'type': 'Geography', 'id': 15}}
        response = self.client().post('/quizzes', json=quiz_round)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_422_get_quiz(self):
        """test 422 error if quiz game fails"""
        response = self.client().post('/quizzes', json={})
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')
        
    
# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()