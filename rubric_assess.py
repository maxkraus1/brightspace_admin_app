"""Generates a Report based on a Rubric Assessments Advanced Data Set CSV file

Function parse_data() takes a python list of student X numbers to pull the
rubric assessments for each student in the CSV report. The intended case is
one course per report.

This script is made somewhat obsolete by dwnld.rubrics_report() in the
APIscripts repository
"""

import csv
from reportlab.platypus import SimpleDocTemplate, Paragraph, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generate_report(filename, activities_dict):
    """helper function to generate a report for each student in parse_data()"""
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Normal_INDENT',
                              parent=styles['Normal'],
                              leftIndent=20,
                              leading=15
                              ))
    report = SimpleDocTemplate(filename)
    story = []
    for act in activities_dict.keys():
        story.append(Paragraph(act, styles['h2']))
        story.append(Paragraph("Overall Level: {}<br /><br />".format(
                                activities_dict[act]['Overall Level']),
                                styles['h3']))
        for crit in activities_dict[act]['Criteria']:
            body = "<b>{}</b><br />".format(crit['Name'])
            body += "Level: {}<br />".format(crit['Level'])
            body += "Points: {}<br /><br />".format(crit['Points'])
            story.append(Paragraph(body, styles['Normal_INDENT']))

        if len(activities_dict[act]['Criteria']) > 5:
            story.append(PageBreak())

    report.build(story)


def parse_data(xnum_list, csvfile):
    """parses a Rubric Assessments advanced data set csv file and
    returns a list of dicts with key report info for each user in xnum_list"""
    reader = csv.DictReader(open(csvfile, newline='', encoding='utf-8'))
    for user in xnum_list:
        data = [row for row in reader if row['Username'] == user]
        filename = "{}_{}_RubricAssessments.pdf".format(data[0]['Last Name'],
                                                        data[0]['First Name'])
        activities = {}
        for row in data:
            act_name = row['Activity Name']
            overall_level = row['Overall Level Achieved']
            criterion = {'Name': row['Criterion'],
                         'Level': row['Level'],
                         'Points': row['Points']
                         }
            if act_name in activities.keys():
                activities[act_name]['Criteria'].append(criterion)
            else:
                activities[act_name] = {'Overall Level': overall_level,
                                        'Criteria': [criterion]
                                        }

        generate_report(filename, activities)
