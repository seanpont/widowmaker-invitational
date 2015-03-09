import unittest

from google.appengine.ext import testbed
import webtest

from lib import router
from main import *


class UnitTest(unittest.TestCase):
    # noinspection PyMethodOverriding
    def setUp(self):
        # Testbed stubs
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_blobstore_stub()
        self.testbed.init_mail_stub()
        self.testbed.init_memcache_stub()
        self.testbed.init_user_stub()
        self.mail_stub = self.testbed.get_stub(testbed.MAIL_SERVICE_NAME)
        self.user_stub = self.testbed.get_stub(testbed.USER_SERVICE_NAME)
        self.app = webtest.TestApp(webapp2.WSGIApplication(router.ROUTES))

    def tearDown(self):
        self.testbed.deactivate()

    def test_model_user(self):
        name, email = "Sean Pont", "SeanPont@gmail.com"
        user = User.get_by_email(email)
        self.assertEqual(user, None)
        user = User.create(name, email)
        self.assertIsNot(user, None)
        self.assertEqual(user.email, email.lower())
        user2 = User.get_by_email(email)
        self.assertEqual(user, user2)
        user3 = User.create("Shirtless Sean", email)
        self.assertEqual(user3.email, email.lower())

    def test_admin_config(self):
        self.app.post(ConfigHandler.path, '{"mail_sender": "seanpont@gmail.com", "invite_code": "mhbb"}')
        config = Config.get()
        self.assertEqual(config.mail_sender, "seanpont@gmail.com")
        self.assertEqual(config.invite_code, "mhbb")

    def test_registration(self):
        name, email, code = "Sean Pont", "seanpont@gmail.com", "mhbb"
        response = self.app.post(RegistrationHandler.path, '{"name": "%s", "email": "%s", "code": "%s"}' % (name, email, code))
        self.assertEqual(response.status_int, 200)
        user = User.get_by_email(email)
        self.assertIsNotNone(user)
        messages = self.mail_stub.get_sent_messages(email)
        self.assertEqual(len(messages), 1)


    #
    # def test_verification_handler(self):
    #     user = self.sign_in()
    #     self.assertEqual(user.email, self.email.lower())
    #
    # # ----- CLASSROOMS -----------------------------------------------------------------
    #
    # def create_classroom(self):
    #     return self.post('/api/classroom', {'name': self.classroom_name})
    #
    # def get_classroom(self, classroom):
    #     return self.get('/api/classroom/%s' % classroom.id)
    #
    # def test_classrooms_handler(self):
    #     self.sign_in()
    #     classrooms = self.get('/api/classroom')
    #     self.assertEqual(len(classrooms), 0)
    #     classroom = self.create_classroom()
    #     self.assertEqual(classroom.name, self.classroom_name)
    #     classrooms = self.get('/api/classroom')
    #     self.assertEqual(len(classrooms), 1)
    #     self.assertEqual(classrooms[0].name, self.classroom_name)
    #     classroom = self.get_classroom(classroom)
    #     self.assertIsNotNone(classroom)
    #     self.assertEqual(classroom.students, [])
    #     self.assertEqual(classroom.assignments, [])
    #
    # # ----- STUDENTS -----------------------------------------------------------------
    #
    # def test_student_handler(self):
    #     self.sign_in()
    #     classroom = self.create_classroom()
    #     student = self.post('/api/student', {'name': self.student_name, 'classroom_id': classroom.id})
    #     self.assertIsNotNone(student)
    #     self.assertEqual(student.name, self.student_name)
    #     classroom = self.get_classroom(classroom)
    #     self.assertEqual(classroom.students[0].name, self.student_name)
    #
    # # ----- ASSIGNMENTS -----------------------------------------------------------------
    #
    # def create_assignment(self, classroom, category='Quiz', due_date='2014-09-15', points=20):
    #     return self.post('/api/classroom/%s/assignment' % classroom.id, {
    #         'category': category,
    #         'due_date': due_date,
    #         'points': points
    #     })
    #
    # def test_assignments_handler(self):
    #     self.sign_in()
    #     classroom = self.create_classroom()
    #     assignment = self.create_assignment(classroom, 'Quiz', '2014-09-15', 20)
    #     self.assertIsNotNone(assignment)
    #     self.assertEqual(assignment.due_date, '2014-09-15')
    #     classroom = self.get_classroom(classroom)
    #     self.assertEqual(len(classroom.assignments), 1)
    #     student = self.post('/api/student', {'name': self.student_name, 'classroom_id': classroom.id})
    #     assignment.grades[student.id] = 18.0
    #     # update the assignment -- add a grade
    #     updated_assignment = self.post('/api/classroom/%s/assignment/%s' % (classroom.id, assignment.id), assignment)
    #     updated_assignment['updated_at'] = assignment.updated_at
    #     self.assertEqual(updated_assignment, assignment)
    #
    # def test_assignment_weights(self):
    #     self.sign_in()
    #     classroom = self.create_classroom()
    #     self.create_assignment(classroom, category='Quiz')
    #     self.create_assignment(classroom, category='Homework')
    #     self.create_assignment(classroom, category='Test')
    #     self.create_assignment(classroom, category='Quiz')
    #     classroom = self.get_classroom(classroom)
    #     print classroom
    #     self.assertEqual(len(classroom.grade_weights), 3)
    #     expected = {
    #         'Quiz': 100,
    #         'Homework': 100,
    #         'Test': 100
    #     }
    #     self.assertEqual(classroom.grade_weights, expected)
    #     classroom['name'] = 'Phoenix II'
    #     classroom['grade_weights'] = {
    #         'Quiz': 20,
    #         'Homework': 20,
    #         'Test': 60
    #     }
    #     logging.info(classroom)
    #     classroom = self.post('/api/classroom/%s' % classroom.id, classroom)
    #     self.assertEqual(classroom.name, 'Phoenix II')
    #     self.assertEqual(classroom.grade_weights['Quiz'], 20)
    #     self.assertEqual(classroom.grade_weights['Homework'], 20)
    #     self.assertEqual(classroom.grade_weights['Test'], 60)