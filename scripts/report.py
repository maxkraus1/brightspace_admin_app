"""This module contains functions that create pdf reports.

The simple() function is for general reporting needs, while other functions
are specific to different use cases.
"""

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='Normal_INDENT',
                          parent=styles['Normal'],
                          leftIndent=20,
                          leading=15
                          ))

def simple(filename, title, body):
    """takes string objects for filename, title, and body and produces a
    simple PDF report to the filename
    """
    report = SimpleDocTemplate(filename)
    report_tile = Paragraph(title, styles["Title"])
    report_body = Paragraph(body, styles["Normal"])
    empty_line = Spacer(1,20)
    report.build([report_tile, empty_line, report_body])

def rubric_assessments(filename, assessments, rubrics_data):
    """takes a filename, RubricAssessments and Rubrics JSON array loaded to a
    Python list and produces a PDF report to the filename
    """

    if filename[-4:] != '.pdf':
        filename += '.pdf'
    report = SimpleDocTemplate(filename)
    story = []

    for rubric in assessments:
        body = ""
        heading = ""
        data = next(d for d in rubrics_data if \
        d["RubricId"] == rubric["RubricId"])
        # handles multiple criteria groups
        criteria = []
        levels = []
        for group in data["CriteriaGroups"]:
            criteria += group['Criteria']
            levels += group['Levels']

        # error handling for different formats from different API calls
        try:
            overall_level = next(o for o in data["OverallLevels"] if \
            o["Id"] == rubric["OverallLevel"]["LevelId"])
            overall_score = rubric['OverallScore']
            overall_feedback = rubric["OverallFeedback"]["Html"]
            no_overall = 0
        except:
            try:
                overall_level = next(o for o in data["OverallLevels"] if \
                o["Id"] == rubric["OverallOutcome"]["LevelId"])
                overall_score = rubric['OverallOutcome']['Score']
                overall_feedback = rubric['OverallOutcome']['Feedback']['Html']
                no_overall = 0
            except:
                no_overall = 1

        for outcome in rubric["CriteriaOutcome"]:
            criterion = next(c for c in criteria if \
            c["Id"] == outcome["CriterionId"])
            body += "<b>{}</b><br />".format(criterion["Name"])
            try:
                level = next(l for l in levels if l["Id"] == outcome["LevelId"])
                body += "Level: {}<br />".format(level["Name"])
            except:
                body += "No Level<br />"
            body += "Score: {}<br />".format(str(outcome["Score"]))
            if outcome["Feedback"]["Html"] != '':
                body += "Feedback: {}<br />".format(outcome["Feedback"]["Html"])
            body += "<br />"
        # error handling for blank rubrics
        if body != "":
            story.append(Paragraph(data["Name"], styles["h2"]))
            if "GradeObjectName" in rubric.keys():
                heading += "Grade Object Name: {}<br />".format(rubric["GradeObjectName"])
            if no_overall == 0:
                heading += "Overall Level: {}<br />".format(overall_level["Name"])
                heading += "Overall Score: {}<br />".format(overall_score)
                if overall_feedback != '':
                    heading += "Overall Feedback: {}<br />".format(
                                                            overall_feedback)
                heading += "<br />"
                story.append(Paragraph(heading, styles["h3"]))
            story.append(Paragraph(body, styles["Normal_INDENT"]))
            story.append(Spacer(1, 20))
    if story:
        report.build(story)
    else:
        story.append(Paragraph('No rubric assessments found'))
        report.build(story)
        print(f'[WARNING] no rubric assessments for {filename}')
