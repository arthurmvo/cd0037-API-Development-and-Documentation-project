import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from random import *
import werkzeug.exceptions

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

# pagination for the questions


def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    questions = [question.format() for question in selection]
    current_questions = questions[start:end]
    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
    """
    Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
        return response
    
    """
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories')
    def get_categories():
        categories = Category.query.all()
        cat_dict = {}
        
        for category in categories:
            cat_dict[category.id] = category.type

        return jsonify({
            'success': True,
            'categories':cat_dict
        })
        
    """
    @TODO:
    REQUEST ALL QUESTIONS AND CREATE A NEW QUESTION
    """
    @app.route('/questions', methods=['GET','POST'])
    def get_questions():
        
        if request.method == 'GET':
            try:
                questions = Question.query.order_by(Question.id).all()
                num_questions = len(questions)
                pag_questions = paginate_questions(request, questions)
                
                if len(pag_questions)==0:
                    abort(404)
                
                categories = Category.query.all()
                cat_dict = {}
            
                for category in categories:
                    cat_dict[category.id] = category.type
                
                
                return jsonify({
                    'success': True,
                    'questions': pag_questions,
                    'total_questions': num_questions,
                    'categories': cat_dict
                })
            except werkzeug.exceptions.NotFound:  # Handle 404 errors
                abort(404)
            except Exception as e:
                print(e)
                abort(422)
        
        else:
            try:
                body = request.get_json()
                if not ('question' in body and 'answer' in body and
                    'difficulty' in body and 'category' in body):
                    abort(422)
                
                new_question = Question(question = body.get('question'), 
                                        answer=body.get('answer'), 
                                        difficulty= body.get('difficulty'), 
                                        category= body.get('category'))

                new_question.insert()

                # send back the current questions, to update front end
                selection = Question.query.order_by(Question.id).all()
                current_questions = paginate_questions(request, selection)

                return jsonify({
                    'success': True,
                    'created': new_question.id,
                    'questions': current_questions,
                    'total_questions': len(selection)
                })
            
            except Exception as e:
                print(e)
                abort(422)
            

    """
    DELETE QUESTION
    """
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.filter_by(id = question_id).one_or_none()
            
            if question is None:
                abort(404)
            
            question.delete()
            
            return jsonify({
                'success': True,
            })

        except Exception as e:
            print(e)
            abort(404)
            
    """
    SEARCH QUESTIONS
    """
    @app.route('/questions/search', methods=['POST'])
    def search_question():
        body = request.get_json()
        search_term = body.get('searchTerm')
        questions = Question.query.filter(Question.question.ilike('%' + search_term + '%')).all()
        
        if questions:
            currentQuestions = paginate_questions(request, questions)
            return jsonify({
                'success': True,
                'questions': currentQuestions,
                'total_questions': len(questions)
            })
        else:
            abort(404)


    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:id>/questions')
    def category_questions(id):
        #Retrieve the category
        category = Category.query.filter_by(id=id).one_or_none()
        
        questions = Question.query.filter_by(category=id).all()
        current_questions = paginate_questions(request, questions)
        if questions:
            return jsonify({
                'success': True,
                'questions': current_questions,
                'total_questions': len(questions),
                'current_category': category.type
            })
        else:
            abort(404)

    """
    PLAY QUIZ
    """
    @app.route('/quizzes', methods = ['POST'])
    def play_quiz():
        try:
            data = request.get_json()
            
            previous_questions = data.get('previous_questions')
            category = data.get('quiz_category')
            
            if category['type'] == 'click':
                
                questions = Question.query.filter(Question.id.notin_(previous_questions)).all()
            
            else:
                questions = Question.query.filter_by(category = category['id']).filter(
                    Question.id.notin_(previous_questions)).all()
            
            new_question = questions[random.randint(0,len(questions))] if len(questions)>0 else None

            return jsonify({
                'success' : True,
                'question' : new_question
            })
        except Exception as e:
            print(e)
            abort(422)

    """
        ERROR HANDLERS
    """
    @app.errorhandler(400)
    def bad_request_error(error):
        return jsonify({
            'success': False,
            'error': 400,
            'message': 'bad request'
        }), 400
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success':False,
            'error': 400,
            'message': 'not found'
        }), 404
    
    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            'success' : False,
            'error': 422,
            'message': 'unprocessable'
        }), 422
    
    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            'success': False,
            'error': 500,
            'message': 'internal server error'
        }), 500
    return app

