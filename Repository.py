'''
Homework 10


Name: Aditya Rajkumar Munot
Date: 3th November 2018
'''


import os
from collections import defaultdict
from prettytable import PrettyTable
import unittest
import sqlite3


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
                        raise ValueError("Number of fields in the file is \
                        not equal to expected number of fileds")
                    else:
                        yield fields


class Repository:
    """Store all information about students and instructors """

    def __init__(self, wdir, ddir, ptables=True):
        # directory with the students, instructors, and grades files
        self._wdir = wdir
        # key: cwid value: instance of class Student
        self._students = dict()
        # key: cwid value: instance of class instructor
        self._instructors = dict()

        self._majors = dict()

        db = sqlite3.connect(ddir)

        self._get_instructors(os.path.join(wdir, 'instructors.txt'))
        self._get_majors(os.path.join(wdir, 'majors.txt'))
        self._get_students(os.path.join(wdir, 'students.txt'))
        self._get_grades(os.path.join(wdir, 'grades.txt'))

        if ptables:

            print("\nMajors Summary")
            self.major_table()

            print("\nStudent Summary")
            self.student_table()

            print("\nInstructors summary")
            self.instructor_table(db)

    def _get_students(self, path):
        """ read students from path and add the to self.students """
        try:
            for cwid, name, major in file_reader(path, 3, 'cwid\tname\tmajor'):
                if cwid in self._students:
                    print(f"Already exits {cwid}")
                else:
                    self._students[cwid] = Student(
                        cwid, name, major, self._majors[major])
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

    def _get_majors(self, path):
        """ read majors from path and add the to self._majors"""
        try:
            for mj, fg, cour in file_reader(path, 3, 'major\tflag\tcourse'):
                if mj in self._majors:
                    self._majors[mj].add_course(fg, cour)
                else:
                    self._majors[mj] = Major(mj)
                    self._majors[mj].add_course(fg, cour)
        except ValueError as err:
            print(err)

    def major_table(self):
        """ print a PrettyTable with a summary of all students """
        pt = PrettyTable(field_names=['Major', 'Required', 'Elective'])
        for major in self._majors.values():
            pt.add_row(major.pt_row())

        print(pt)

    def student_table(self):
        """ print a PrettyTable with a summary of all students """
        pt = PrettyTable(field_names=['CWID', 'Name', 'Major', 'Completed Courses', 'Remaining Required Courses', 'Remaining Elective Courses'])
        for student in self._students.values():
            pt.add_row(student.pt_row())

        print(pt)

    def instructor_table(self, db):
        """ print a PrettyTable with a summary of all students """
        pt = PrettyTable(
            field_names=['CWID', 'Name', 'Dept', 'Course', 'Students'])
        """for Instructor in self._instructors.values():
            for row in Instructor.pt_row():
                pt.add_row(row)"""
        query = """ select i.CWID, i.Name, i.Dept, g.Course, count(g.Course) as students
                    from instructors i join grades g on i.CWID = g.Instructor_CWID
                    group by Grade; """
        for row in db.execute(query):
            pt.add_row(row)
        print(pt)


class Student:
    """ Represent a single student"""

    def __init__(self, cwid, name, major, in_major):
        self._cwid = cwid
        self._name = name
        self._major = major
        self._inmajor = in_major
        self._courses = dict()  # key: courses value: str with grade

    def add_course(self, course, grade):
        gradeList = ['A', 'A-', 'B+', 'B', 'B-', 'C+', 'C']
        if grade in gradeList:
            self._courses[course] = grade

    def pt_row(self):

        comp_cur, rem_reqcur, rem_elecur = self._inmajor.grade_check(self._courses)
        return[self._cwid, self._name, self._major, sorted(comp_cur), rem_reqcur, rem_elecur]


class Instructor:
    """ represent an instructor """

    def __init__(self, cwid, name, dept):
        self._cwid = cwid
        self._name = name
        self._dept = dept
        # key: course value: number of students
        self._courses = defaultdict(int)

    def add_student(self, course):
        self._courses[course] += 1

    def pt_row(self):
        for course, students in self._courses.items():
            yield[self._cwid, self._name, self._dept, course, students]


class Major:
    """ represent Majors """

    def __init__(self, major, passing=None):
        self._major = major
        self._required = set()
        self._elective = set()
        if passing is None:
            self._passing_grades = {'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C'}
        else:
            self._passing_grades = passing

    def add_course(self, fl, course):

        if fl == 'R':
            self._required.add(course)
        elif fl == 'E':
            self._elective.add(course)
        else:
            raise ValueError(f"unexcepted flag {fl} in majors.txt")

    def grade_check(self, courses):
        """ """
        comp_cur = {cur for cur, gd in courses.items() if gd in self._passing_grades}
        if comp_cur == "{}":
            return[comp_cur, self._required, self._elective]
        else:
            rem_reqcur = self._required - comp_cur
            if self._elective.intersection(comp_cur):
                rem_elecur = None
            else:
                rem_elecur = self._elective

            return[comp_cur, rem_reqcur, rem_elecur]

    def pt_row(self):

        return[self._major, self._required, self._elective]


def main():
    # wdir = 'E:\Py Project\SSW-810\sit'
    wdir = input('Enter the text file or csv file directory: ')
    # ddir = 'E:\sqlite\repository.db'
    ddir = input('Enter the database directory: ')
    stevens = Repository(wdir, ddir)


class RepositoryTest(unittest.TestCase):
    def test_stevens(self):
        wdir = 'E:\Py Project\SSW-810\sit'
        ddir = 'E:\sqlite\\repository.db'
        stevens = Repository(wdir, ddir, False)
        expect_student = [["10103", "Baldwin, C", "SFEN", ['CS 501', 'SSW 564', 'SSW 567', 'SSW 687'], {'SSW 555', 'SSW 540'}, None],
                        ["10115", "Wyatt, X", "SFEN", ['CS 545', 'SSW 564', 'SSW 567', 'SSW 687'], {'SSW 555', 'SSW 540'}, None],
                        ["10172", "Forbes, I", "SFEN", ['SSW 555', 'SSW 567'], {'SSW 564', 'SSW 540'}, {'CS 545', 'CS 501', 'CS 513'}],
                        ["10175", "Erickson, D", "SFEN", ['SSW 564', 'SSW 567', 'SSW 687'], {'SSW 555', 'SSW 540'}, {'CS 545', 'CS 501', 'CS 513'}],
                        ["10183", "Chapman, O", "SFEN", ['SSW 689'], {'SSW 567', 'SSW 555', 'SSW 564', 'SSW 540'}, {'CS 545', 'CS 501', 'CS 513'}],
                        ["11399", "Cordova, I", "SYEN", ['SSW 540'], {'SYS 612', 'SYS 800', 'SYS 671'}, None],
                        ["11461", "Wright, U", "SYEN", ['SYS 611', 'SYS 750', 'SYS 800'], {'SYS 671', 'SYS 612'}, {'SSW 565', 'SSW 540', 'SSW 810'}],
                        ["11658", "Kelly, P", "SYEN", [], {'SYS 800', 'SYS 612', 'SYS 671'}, {'SSW 565', 'SSW 540', 'SSW 810'}],
                        ["11714", "Morton, A", "SYEN", ['SYS 611', 'SYS 645'], {'SYS 671', 'SYS 612', 'SYS 800'}, {'SSW 565', 'SSW 540', 'SSW 810'}],
                        ["11788", "Fuller, E", "SYEN", ['SSW 540'], {'SYS 671', 'SYS 612', 'SYS 800'}, None]]
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

        expect_major = [["SFEN", {'SSW 540', 'SSW 564', 'SSW 567', 'SSW 555'}, {'CS 545', 'CS 501', 'CS 513'}], ["SYEN", {'SYS 612', 'SYS 800', 'SYS 671'}, {'SSW 810', 'SSW 565', 'SSW 540'}]]

        pstudent = [s.pt_row() for s in stevens._students.values()]
        pinstructor = [row for Instructor in stevens._instructors.values() for row in Instructor.pt_row()]
        pmajor = [m.pt_row() for m in stevens._majors.values()]

        self.assertEqual(pmajor, expect_major)
        self.assertEqual(pstudent, expect_student)
        self.assertEqual(pinstructor, expect_instructor)

if __name__ == '__main__':
    main()
    unittest.main(exit=False, verbosity=2)
