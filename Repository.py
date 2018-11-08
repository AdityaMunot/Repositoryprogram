import os
from collections import defaultdict
from prettytable import PrettyTable
import unittest


def file_reader(path, num_fields, expect, sep='\t'):
    try:
        fp = open(path, "r", encoding="utf-8")
    except FileNotFoundError:
        raise FloatingPointError(" can't open:", path)

    else:
        with fp:
            for n, line in enumerate(fp):
                if n == 0 and line == expect:
                    continue  # skip header row
                else:
                    fields = line.strip()
                    fields = fields.split(sep)
                    if len(fields) != num_fields:
                        raise ValueError("Number of fields in the file is not equal to expected number of fileds")
                    else:
                        yield fields


class Repository:
    """Store all information about students and instructors """

    def __init__(self, wdir, ptables=True):
        self._wdir = wdir  # directory with the students, instructors, and grades files
        self._students = dict()  # key: cwid value: instance of class Student
        self._instructors = dict()  # key: cwid value: instance of class instructor

        self._get_students(os.path.join(wdir, 'students.txt'))
        self._get_instructors(os.path.join(wdir, 'instructors.txt'))
        self._get_grades(os.path.join(wdir, 'grades.txt'))

        if ptables:
            print("\nStudent Summary")
            self.student_table()

            print("\nInstructors summary")
            self.instructor_table()

    def _get_students(self, path):
        """ read students from path and add the to self.students """
        try:
            for cwid, name, major in file_reader(path, 3, 'cwid\tname\tmajor'):
                if cwid in self._students:
                    print(f"Already exits {cwid}")
                else:
                    self._students[cwid] = Student(cwid, name, major)
        except ValueError as err:
            print(err)

    def _get_instructors(self, path):
        """ read instructors from path and add the to self.instructor"""
        try:
            for cwid, name, dept in file_reader(path, 3, 'cwid\tname\tdepartment'):
                if cwid in self._instructors:
                    print(f"Already exits {cwid}")
                else:
                    self._instructors[cwid] = Instructor(cwid, name, dept)
        except ValueError as err:
            print(err)

    def _get_grades(self, path):
        """ read grades from path and add to """
        try:
            for Scwid, course, lg, Icwid in file_reader(path, 4, 'Student CWID\tCourse\tLetterGrade\tInstructor CWID'):
                if Scwid in self._students:
                    self._students[Scwid].add_course(course, lg)
                else:
                    print(f"Warning: student cwid {Scwid} not exist")

                if Icwid in self._instructors:
                    self._instructors[Icwid].add_student(course)
                else:
                    print(f"Warning: Instructor cwid {Icwid} not exist")

        except ValueError as err:
            print(err)

    def student_table(self):
        """ print a PrettyTable with a summary of all students """
        pt = PrettyTable(field_names=['CWID', 'Name', 'Major', 'Completed Courses'])
        for student in self._students.values():
            pt.add_row(student.pt_row())

        print(pt)

    def instructor_table(self):
        """ print a PrettyTable with a summary of all students """
        pt = PrettyTable(
            field_names=['CWID', 'Name', 'Dept', 'Course', 'Students'])
        for Instructor in self._instructors.values():
            for row in Instructor.pt_row():
                pt.add_row(row)

        print(pt)


class Student:
    """ Represent a single student"""

    def __init__(self, cwid, name, major):
        self._cwid = cwid
        self._name = name
        self._major = major
        self._courses = dict()  # key: courses value: str with grade

    def add_course(self, course, grade):
        self._courses[course] = grade

    def pt_row(self):
        return[self._cwid, self._name, self._major, sorted(self._courses.keys())]


class Instructor:
    """ represent an instructor """

    def __init__(self, cwid, name, dept):
        self._cwid = cwid
        self._name = name
        self._dept = dept
        self._courses = defaultdict(int)  # key: course value: number of students

    def add_student(self, course):
        self._courses[course] += 1

    def pt_row(self):
        for course, students in self._courses.items():
            yield[self._cwid, self._name, self._dept, course, students]


def main():
    wdir = 'E:\Py Project\SSW-810\sit'
    stevens = Repository(wdir)


class RepositoryTest(unittest.TestCase):
    def test_stevens(self):
        wdir = 'E:\Py Project\SSW-810\sit'
        stevens = Repository(wdir, False)
        expect_student = [["10103", "Baldwin, C", "SFEN", ['CS 501', 'SSW 564', 'SSW 567', 'SSW 687']],
                        ["10115", "Wyatt, X", "SFEN", ['CS 545', 'SSW 564', 'SSW 567', 'SSW 687']],
                        ["10172", "Forbes, I", "SFEN", ['SSW 555', 'SSW 567']],
                        ["10175", "Erickson, D", "SFEN", ['SSW 564', 'SSW 567', 'SSW 687']],
                        ["10183", "Chapman, O", "SFEN", ['SSW 689']],
                        ["11399", "Cordova, I", "SYEN", ['SSW 540']],
                        ["11461", "Wright, U", "SYEN", ['SYS 611', 'SYS 750', 'SYS 800']],
                        ["11658", "Kelly, P", "SYEN", ['SSW 540']],
                        ["11714", "Morton, A", "SYEN", ['SYS 611', 'SYS 645']],
                        ["11788", "Fuller, E", "SYEN", ['SSW 540']]]
        expect_instructor = [["98765", "Einstein, A", "SFEN", "SSW 567", 4],
        ["98765", "Einstein, A", "SFEN", "SSW 540", 3],
         ["98764", "Feynman, R", "SFEN", "SSW 564", 3],
         ["98764", "Feynman, R", "SFEN", "SSW 687", 3],
         ["98764", "Feynman, R", "SFEN", "CS 501", 1],
         ["98764", "Feynman, R", "SFEN", "CS 545", 1],
         ["98763", "Newton, I", "SFEN", "SSW 555", 1],
         ["98763", "Newton, I", "SFEN", "SSW 689", 1],
         ["98760", "Darwin, C", "SYEN", "SYS 800", 1],
         ["98760", "Darwin, C", "SYEN", "SYS 750", 1],
         ["98760", "Darwin, C", "SYEN", "SYS 611", 2],
         ["98760", "Darwin, C", "SYEN", "SYS 645", 1]]

        pstudent = [s.pt_row() for s in stevens._students.values()]
        pinstructor = [row for Instructor in stevens._instructors.values() for row in Instructor.pt_row()]

        self.assertEqual(pstudent, expect_student)
        self.assertEqual(pinstructor, expect_instructor)

if __name__ == '__main__':
    main()
    unittest.main(exit=False, verbosity=2)
